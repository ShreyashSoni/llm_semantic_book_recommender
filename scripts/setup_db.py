"""Initialize the database with tables and optionally create a default user."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.database import create_tables, get_db_session, User
from src.config import get_settings

def setup_database(create_default_user: bool = True):
    """Set up the database with tables and optional default user.
    
    Args:
        create_default_user: Whether to create a default user
    """
    print("🔧 Setting up database...")
    
    # Get settings to ensure directories exist
    settings = get_settings()
    print(f"📁 Database path: {settings.database_path}")
    
    # Create tables
    print("📋 Creating database tables...")
    create_tables()
    print("✅ Tables created successfully")
    
    # Create default user if requested
    if create_default_user:
        with get_db_session() as db:
            # Check if default user already exists
            existing_user = db.query(User).filter_by(username="default").first()
            
            if existing_user:
                print(f"👤 Default user already exists (ID: {existing_user.id})")
            else:
                # Create default user
                default_user = User(username="default")
                db.add(default_user)
                db.commit()
                print(f"👤 Created default user (ID: {default_user.id})")
    
    print("🎉 Database setup complete!")


if __name__ == "__main__":
    setup_database()