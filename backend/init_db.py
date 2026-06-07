#!/usr/bin/env python
"""Initialize the database with tables and sample data"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.manager import db_manager
from app.database.models import User, Analysis
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database tables"""
    try:
        logger.info("🚀 Initializing database...")
        
        # Create all tables
        db_manager.create_tables()
        
        # Verify connection
        with db_manager.get_session() as session:
            # Test query
            result = session.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
        
        logger.info("✅ Database initialization complete!")
        
        # Print stats
        stats = db_manager.get_stats()
        logger.info(f"📊 Current stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    init_database()