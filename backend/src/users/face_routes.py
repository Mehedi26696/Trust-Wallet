from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlmodel import Session

import os
import sys
from PIL import Image

# DeepFace for state-of-the-art face recognition
try:
    from deepface import DeepFace
    HAS_DEEPFACE = True
except Exception:
    HAS_DEEPFACE = False

from ..auth.auth_service import get_current_user
from ..models.user import User
from ..utils.database import get_session
from ..utils.supabase_client import supabase_client

router = APIRouter()







@router.post("/face/enroll")
async def enroll_face(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Enroll user's face image. Stores the image and a perceptual hash for basic matching.
    Accepts multipart/form-data with field name 'file'.
    """
    
    # Debug logging
    print(f"Face enrollment request: user={current_user.id}, content_type={file.content_type}", file=sys.stderr)
    
    # Accept common image types or no type (will validate later)
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/octet-stream"}
    if file.content_type and file.content_type not in allowed_types:
        print(f"Rejected content type: {file.content_type}", file=sys.stderr)
        raise HTTPException(status_code=400, detail="Unsupported image type")

    try:
        # Read the image
        data = await file.read()
        print(f"Read {len(data)} bytes from file", file=sys.stderr)
        
        if not data:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Validate it's actually an image
        try:
            from io import BytesIO
            img = Image.open(BytesIO(data))
            img.verify()
            print(f"Image verified: format={img.format if hasattr(img, 'format') else 'unknown'}", file=sys.stderr)
        except Exception as e:
            print(f"Image validation failed: {str(e)}", file=sys.stderr)
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # Upload to Supabase Storage
        bucket_name = "face"
        path_in_bucket = f"{current_user.id}.jpg"
        
        print(f"Uploading to Supabase bucket '{bucket_name}', path '{path_in_bucket}'", file=sys.stderr)
        upload_res = supabase_client.upload_file(
            bucket=bucket_name,
            path=path_in_bucket,
            file=data,
            content_type=file.content_type or "image/jpeg"
        )
        
        if not upload_res:
             # Try to get public URL even if upload "failed" (sometimes it fails if already exists and x-upsert logic differs)
             # But here we use x-upsert: true in the client.
             raise Exception("Failed to upload image to Supabase Storage")

        # Get public URL or just store the bucket path
        # Storing the bucket path "face/userid.jpg" is more portable
        supabase_path = f"{bucket_name}/{path_in_bucket}"
        current_user.face_image_path = supabase_path
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        print(f"User face record updated successfully with Supabase path: {supabase_path}", file=sys.stderr)

        return {
            "status": "ok",
            "enrolled": True,
            "file_size": len(data),
            "supabase_path": supabase_path
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        print(f"Face enrollment error: {str(e)}", file=sys.stderr)
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to enroll face: {str(e)}")


@router.post("/face/verify")
async def verify_face(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Verify uploaded face against enrolled image.
    Uses perceptual hash distance as a lightweight proxy (not true biometrics).
    Returns verified: true/false.
    """
    # enrolled_path is now likely "face/userid.jpg"
    supabase_path = current_user.face_image_path
    if not supabase_path:
        raise HTTPException(status_code=400, detail="No enrolled face on record")

    # If DeepFace not available, return error
    if not HAS_DEEPFACE:
        raise HTTPException(status_code=500, detail="Face recognition service not available")

    import tempfile
    
    enrolled_temp = None
    verify_temp = None
    
    try:
        # 1. Download enrolled image from Supabase to a temp file
        try:
            parts = supabase_path.split("/")
            bucket = parts[0]
            blob_path = "/".join(parts[1:])
            
            enrolled_data = supabase_client.download_file(bucket, blob_path)
            if not enrolled_data:
                raise Exception("Failed to download enrolled image from Supabase")
                
            enrolled_temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            enrolled_temp.write(enrolled_data)
            enrolled_temp.close()
        except Exception as e:
            print(f"Download error: {e}", file=sys.stderr)
            raise HTTPException(status_code=500, detail="Failed to retrieve enrolled face")

        # 2. Save current upload to another temp file
        data = await file.read()
        if not data:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        verify_temp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        verify_temp.write(data)
        verify_temp.close()

        # 3. Use DeepFace for verification
        try:
            result = DeepFace.verify(
                img1_path=enrolled_temp.name, 
                img2_path=verify_temp.name, 
                model_name="Facenet512", 
                enforce_detection=True
            )
            
            is_verified = result.get("verified", False)
            distance = result.get("distance", 999)
            
            if is_verified:
                from datetime import datetime, timezone
                from ..utils.fraud_detector import clear_user_fraud_block
                
                current_user.last_face_verified_at = datetime.now(timezone.utc)
                session.add(current_user)
                
                # Resolve pending fraud alerts to unblock the account
                cleared = clear_user_fraud_block(session, current_user.id)
                if cleared:
                    print(f"✅ [UNBLOCK] Resolved fraud alerts for user {current_user.id} after face success", file=sys.stderr)
                
                session.commit()
                print(f"Face verified for user {current_user.id}, updating last_face_verified_at", file=sys.stderr)
                
            return {"verified": is_verified, "distance": float(distance), "method": "deepface"}
        except Exception as e:
            print(f"DeepFace error: {e}", file=sys.stderr)
            raise HTTPException(status_code=400, detail=f"Face verification failed: {str(e)}")
            
    finally:
        # Cleanup
        if enrolled_temp and os.path.exists(enrolled_temp.name):
            os.remove(enrolled_temp.name)
        if verify_temp and os.path.exists(verify_temp.name):
            os.remove(verify_temp.name)
