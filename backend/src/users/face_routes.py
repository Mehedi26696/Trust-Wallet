from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlmodel import Session
from typing import Optional
import os
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

router = APIRouter()


def _faces_dir() -> str:
    """Get or create the faces directory. Returns absolute path."""
    # Go from backend/src/users to backend root
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    path = os.path.join(base_dir, "backend", "media", "faces")
    os.makedirs(path, exist_ok=True)
    return path


def _get_face_embedding(image_path: str) -> Optional[dict]:
    """Get face embedding using DeepFace.
    Returns embedding dict with 'embedding' key or None if face not found.
    """
    if not HAS_DEEPFACE:
        return None
    try:
        # Use Facenet512 model for robust embeddings
        embedding = DeepFace.represent(img_path=image_path, model_name="Facenet512", enforce_detection=True)
        if embedding and len(embedding) > 0:
            return embedding[0]  # Returns dict with 'embedding' key
        return None
    except Exception:
        return None

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
    import sys
    print(f"DeepFace available: {HAS_DEEPFACE}", file=sys.stderr)
    
    # Debug logging
    print(f"Face enrollment request: user={current_user.id}, content_type={file.content_type}", file=sys.stderr)
    
    # Accept common image types or no type (will validate later)
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/octet-stream"}
    if file.content_type and file.content_type not in allowed_types:
        print(f"Rejected content type: {file.content_type}", file=sys.stderr)
        raise HTTPException(status_code=400, detail="Unsupported image type")

    faces_dir = _faces_dir()
    filename = f"{current_user.id}.jpg"
    save_path = os.path.join(faces_dir, filename)

    try:
        # Read and save the image
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
        
        # Write file to disk
        with open(save_path, "wb") as f:
            f.write(data)
        print(f"File written to: {save_path}", file=sys.stderr)
        
        # Verify file was written
        if not os.path.exists(save_path):
            raise Exception(f"Failed to write file to {save_path}")
        
        file_size = os.path.getsize(save_path)
        if file_size == 0:
            raise Exception("File was written but is empty")
        
        print(f"File size on disk: {file_size} bytes", file=sys.stderr)

        # Compute embedding with DeepFace (for reference, not stored yet)
        embedding_result = _get_face_embedding(save_path)
        print(f"Face embedding computed: {bool(embedding_result)}", file=sys.stderr)

        # Update user record with relative path for portability
        relative_path = os.path.relpath(save_path, os.path.abspath("."))
        current_user.face_image_path = relative_path
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        
        print(f"User face record updated successfully", file=sys.stderr)

        return {
            "status": "ok",
            "enrolled": True,
            "file_size": file_size,
            "path": relative_path
        }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        print(f"Face enrollment error: {str(e)}", file=sys.stderr)
        session.rollback()
        # Clean up file if write failed
        try:
            if os.path.exists(save_path):
                os.remove(save_path)
        except Exception:
            pass
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
    # Resolve relative path to absolute path
    enrolled_path = current_user.face_image_path
    if enrolled_path:
        # If it's a relative path, make it absolute from current working directory
        if not os.path.isabs(enrolled_path):
            enrolled_path = os.path.abspath(enrolled_path)
    
    if not enrolled_path or not os.path.exists(enrolled_path):
        raise HTTPException(status_code=400, detail="No enrolled face on record")

    # Be lenient and validate via decoder later
    allowed_types = {"image/jpeg", "image/png", "image/jpg", "application/octet-stream"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    # If DeepFace not available, return error
    if not HAS_DEEPFACE:
        raise HTTPException(status_code=500, detail="Face recognition service not available")

    try:
        # Save temp file for verification
        faces_dir = _faces_dir()
        temp_path = os.path.join(faces_dir, f"verify_{current_user.id}.jpg")
        data = await file.read()
        
        if not data:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        with open(temp_path, "wb") as f:
            f.write(data)

        # Use DeepFace for verification
        try:
            # Use verify method which compares two faces and returns similarity metrics
            result = DeepFace.verify(img1_path=enrolled_path, img2_path=temp_path, 
                                    model_name="Facenet512", enforce_detection=True)
            try:
                os.remove(temp_path)
            except Exception:
                pass
            # result is dict with 'verified' (bool), 'distance' (float), 'threshold' (float), 'model', 'detector_backend'
            is_verified = result.get("verified", False)
            distance = result.get("distance", 999)
            return {"verified": is_verified, "distance": float(distance), "method": "deepface"}
        except Exception as e:
            try:
                os.remove(temp_path)
            except Exception:
                pass
            raise HTTPException(status_code=400, detail=f"Face verification failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify face: {str(e)}")
