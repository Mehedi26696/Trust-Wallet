"""
Async Supabase client and utilities for advanced features.
Provides access to Supabase Auth, Real-time, and Storage features with async support.
"""

from typing import Optional
from supabase import create_client, Client
from supabase._async.client import AsyncClient, create_client as create_async_client
from ..config import settings


class SupabaseClient:
    """Async wrapper for Supabase client with real-time capabilities."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.async_client: Optional[AsyncClient] = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize sync Supabase client if configured."""
        if settings.is_supabase_configured:
            try:
                # Initialize sync client for basic operations
                self.client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                
                print("✅ Supabase sync client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Supabase client: {e}")
                self.client = None
        else:
            print("⚠️ Supabase not configured, client not initialized")
    
    async def _initialize_async_client(self):
        """Initialize async Supabase client if configured."""
        if settings.is_supabase_configured and self.async_client is None:
            try:
                # Initialize async client for real-time features
                self.async_client = await create_async_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_ANON_KEY
                )
                
                print("✅ Supabase async client initialized successfully")
                return True
            except Exception as e:
                print(f"❌ Failed to initialize Supabase async client: {e}")
                self.async_client = None
                return False
        return self.async_client is not None
    
    @property
    def is_available(self) -> bool:
        """Check if Supabase client is available."""
        return self.client is not None
    
    @property
    def is_async_available(self) -> bool:
        """Check if async Supabase client is available."""
        return self.async_client is not None
    
    def get_admin_client(self) -> Optional[Client]:
        """Get Supabase client with service role key for admin operations."""
        if not settings.SUPABASE_SERVICE_ROLE_KEY:
            return None
        
        try:
            return create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
        except Exception as e:
            print(f"❌ Failed to create admin Supabase client: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Supabase connection."""
        if not self.is_available:
            return False
        
        try:
            # Test with a simple query to the users table
            response = self.client.table('user').select('id').limit(1).execute()
            return True
        except Exception as e:
            print(f"❌ Supabase connection test failed: {e}")
            return False
    
    async def setup_realtime_subscription(self, table_name: str, callback):
        """
        Set up real-time subscription for a table using async client.
        
        Args:
            table_name (str): Name of the table to subscribe to
            callback: Callback function for real-time updates
        """
        # Ensure async client is initialized
        if not await self._initialize_async_client():
            print(f"⚠️ Async Supabase client not available for real-time subscription: {table_name}")
            return None
        
        try:
            # Modern async Supabase real-time subscription API
            channel = self.async_client.channel(f"public:{table_name}")
            
            # Subscribe to INSERT, UPDATE, DELETE events using the correct method
            channel.on_postgres_changes(
                event="*",
                schema="public", 
                table=table_name,
                callback=callback
            )
            
            # Subscribe to the channel
            await channel.subscribe()
            
            print(f"✅ Real-time subscription set up for table: {table_name}")
            return channel
        except Exception as e:
            print(f"❌ Failed to set up real-time subscription for {table_name}: {e}")
            print(f"💡 Ensure Row Level Security (RLS) is configured in Supabase for table: {table_name}")
            return None
    
    def get_user_by_email_auth(self, email: str):
        """
        Get user from Supabase Auth (if using Supabase Auth).
        
        Args:
            email (str): User email
            
        Returns:
            User data from Supabase Auth
        """
        if not self.is_available:
            return None
        
        admin_client = self.get_admin_client()
        if not admin_client:
            return None
        
        try:
            response = admin_client.auth.admin.list_users()
            users = response.users if hasattr(response, 'users') else []
            
            for user in users:
                if user.email == email:
                    return user
            
            return None
        except Exception as e:
            print(f"❌ Failed to get user from Supabase Auth: {e}")
            return None


    def upload_file(self, bucket: str, path: str, file: bytes, content_type: str = "image/jpeg"):
        """
        Upload a file to a Supabase bucket. Uses admin client to bypass RLS.
        
        Args:
            bucket (str): Bucket name
            path (str): File path within bucket
            file (bytes): File content in bytes
            content_type (str): Content type header
            
        Returns:
            dict: Upload response
        """
        client = self.get_admin_client() or self.client
        if not client:
            return None
        
        try:
            return client.storage.from_(bucket).upload(
                path=path,
                file=file,
                file_options={"content-type": content_type, "upsert": True}
            )
        except Exception as e:
            print(f"❌ Failed to upload file to Supabase storage: {e}")
            return None

    def download_file(self, bucket: str, path: str) -> Optional[bytes]:
        """
        Download a file from a Supabase bucket. Uses admin client to bypass RLS.
        
        Args:
            bucket (str): Bucket name
            path (str): File path within bucket
            
        Returns:
            bytes: File content or None if failed
        """
        client = self.get_admin_client() or self.client
        if not client:
            return None
        
        try:
            return client.storage.from_(bucket).download(path)
        except Exception as e:
            print(f"❌ Failed to download file from Supabase storage: {e}")
            return None

    def get_public_url(self, bucket: str, path: str) -> Optional[str]:
        """
        Get public URL for a file in a Supabase bucket.
        
        Args:
            bucket (str): Bucket name
            path (str): File path within bucket
            
        Returns:
            str: Public URL or None if failed
        """
        client = self.client # Public URL doesn't need admin
        if not client:
            return None
        
        try:
            return client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            print(f"❌ Failed to get public URL from Supabase storage: {e}")
            return None


# Global Supabase client instance
supabase_client = SupabaseClient()


def get_supabase_client() -> SupabaseClient:
    """Get the global Supabase client instance."""
    return supabase_client


def is_supabase_available() -> bool:
    """Check if Supabase is available and configured."""
    return supabase_client.is_available


# Real-time event handlers (examples)
def handle_transaction_update(payload):
    """
    Handle real-time transaction updates.
    
    Args:
        payload: Real-time update payload from Supabase
    """
    print(f"🔄 Real-time transaction update: {payload}")
    
    # Add your custom logic here
    # e.g., send notifications, update cache, etc.


def handle_fraud_alert_update(payload):
    """
    Handle real-time fraud alert updates.
    
    Args:
        payload: Real-time update payload from Supabase
    """
    print(f"🚨 Real-time fraud alert update: {payload}")
    
    # Add your custom logic here
    # e.g., send admin notifications, update dashboard, etc.


async def setup_realtime_subscriptions():
    """Set up all real-time subscriptions for the application."""
    if not is_supabase_available():
        print("⚠️ Supabase not available, skipping real-time subscriptions")
        return
    
    print("🔄 Setting up Supabase async real-time subscriptions...")
    
    # Subscribe to transaction updates
    await supabase_client.setup_realtime_subscription('transaction', handle_transaction_update)
    
    # Subscribe to fraud alert updates
    await supabase_client.setup_realtime_subscription('fraudalert', handle_fraud_alert_update)
    
    print("✅ Async real-time subscriptions configured successfully!")
    print("🔴 Live monitoring active for transactions and fraud alerts")