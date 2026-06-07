import sqlalchemy
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import joinedload

from app.database.models import Base, User, OAuthSession, Analysis, SearchHistory, SavedProfile, PortfolioHistory

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manage database connections and operations"""
    
    def __init__(self):
        # Get database URL from environment
        self.database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres:postgres@localhost:5432/github_intelligence'
        )
        
        # Create engine
        self.engine = create_engine(
            self.database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=os.getenv('SQL_ECHO', 'False').lower() == 'true'
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create all tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    # ============ User Operations ============
    
    def get_or_create_user(self, github_id: int, username: str, email: str = None, 
                          avatar_url: str = None, name: str = None,
                          access_token: str = None) -> dict:
        """Get existing user or create new one"""
        with self.get_session() as session:
            user = session.query(User).filter(User.github_id == github_id).first()
            
            if user:
                # Update existing user
                user.username = username
                user.email = email or user.email
                user.avatar_url = avatar_url or user.avatar_url
                user.name = name or user.name
                user.last_login = datetime.utcnow()
                
                if access_token:
                    user.github_access_token = access_token
                
                session.commit()
                logger.info(f"🔄 Updated user: {username}")
            else:
                # Create new user
                user = User(
                    github_id=github_id,
                    username=username,
                    email=email,
                    avatar_url=avatar_url,
                    name=name,
                    github_access_token=access_token,
                    last_login=datetime.utcnow()
                )
                session.add(user)
                session.commit()
                logger.info(f"✅ Created new user: {username}")
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "name": user.name,
                "github_access_token": user.github_access_token
            }
    
    def get_user_by_token(self, session_token: str) -> Optional[dict]:
        """Get user by session token"""
        with self.get_session() as session:
            oauth_session = session.query(OAuthSession).filter(
                OAuthSession.session_token == session_token,
                OAuthSession.is_active == True,
                OAuthSession.expires_at > datetime.utcnow()
            ).first()
            
            if not oauth_session:
                return None
            
            user = session.query(User).filter(User.id == oauth_session.user_id).first()
            
            if not user:
                return None
            
            # Convert to plain dictionary BEFORE session closes
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "name": user.name,
                "github_access_token": user.github_access_token
            }
            
            return user_data
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by GitHub username"""
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()
    
    # ============ OAuth Session Operations ============
    
    def create_oauth_session(self, user_id: int, session_token: str, 
                            expires_in: int = 86400,  # 24 hours default
                            ip_address: str = None, user_agent: str = None) -> OAuthSession:
        """Create new OAuth session"""
        with self.get_session() as session:
            # Deactivate old sessions for this user
            session.query(OAuthSession).filter(
                OAuthSession.user_id == user_id,
                OAuthSession.is_active == True
            ).update({"is_active": False})
            
            # Create new session
            oauth_session = OAuthSession(
                user_id=user_id,
                session_token=session_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in)
            )
            session.add(oauth_session)
            session.commit()
            
            logger.info(f"✅ Created OAuth session for user_id: {user_id}")
            return oauth_session
    
    def invalidate_session(self, session_token: str):
        """Invalidate a session (logout)"""
        with self.get_session() as session:
            session.query(OAuthSession).filter(
                OAuthSession.session_token == session_token
            ).update({"is_active": False})
            session.commit()
            logger.info(f"✅ Invalidated session: {session_token[:20]}...")
    
    # ============ Analysis Operations ============
    
    def save_analysis(self, user_id: Optional[int], analysis_data: Dict[str, Any]) -> Analysis:
        """Save analysis results to database"""
        with self.get_session() as session:
            analysis = Analysis(
                user_id=user_id,
                analyzed_username=analysis_data.get('username'),
                portfolio_score=analysis_data.get('portfolio_score', 0),
                total_repos=analysis_data.get('total_repos', 0),
                public_repos=analysis_data.get('public_repos', 0),
                private_repos=analysis_data.get('private_repos', 0),
                total_stars=analysis_data.get('total_stars', 0),
                followers=analysis_data.get('followers', 0),
                following=analysis_data.get('following', 0),
                top_languages=analysis_data.get('top_languages', []),
                repo_ranking=analysis_data.get('repo_ranking', []),
                ai_insights=analysis_data.get('ai_insights', {}),
                was_authenticated=analysis_data.get('is_authenticated', False),
                analysis_duration_ms=analysis_data.get('duration_ms')
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            
            logger.info(f"✅ Saved analysis for user: {analysis_data.get('username')}")
            return analysis
    
    def get_user_analyses(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get analysis history for a user"""
        with self.get_session() as session:
            analyses = session.query(Analysis).filter(
                Analysis.user_id == user_id
            ).order_by(Analysis.created_at.desc()).limit(limit).all()
            
            return [a.to_dict() for a in analyses]
    
    def get_username_history(self, username: str, limit: int = 10) -> List[Dict]:
        """Get analysis history for a specific GitHub username"""
        with self.get_session() as session:
            analyses = session.query(Analysis).filter(
                Analysis.analyzed_username == username
            ).order_by(Analysis.created_at.desc()).limit(limit).all()
            
            return [a.to_dict() for a in analyses]
    
    # ============ Search History Operations ============
    
    def log_search(self, username: str, user_id: Optional[int] = None,
                  ip_address: str = None, user_agent: str = None):
        """Log a search query"""
        with self.get_session() as session:
            search = SearchHistory(
                username=username,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(search)
            session.commit()
            logger.info(f"📝 Logged search for: {username}")
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get most searched GitHub usernames"""
        with self.get_session() as session:
            from sqlalchemy import func
            
            results = session.query(
                SearchHistory.username,
                func.count(SearchHistory.id).label('search_count')
            ).group_by(SearchHistory.username).order_by(
                func.count(SearchHistory.id).desc()
            ).limit(limit).all()
            
            return [{"username": r[0], "count": r[1]} for r in results]
    
    # ============ Saved Profiles Operations ============
    
    def save_profile(self, user_id: int, username: str, notes: str = None, notify: bool = False) -> SavedProfile:
        """Save a profile to user's list"""
        with self.get_session() as session:
            # Check if already saved
            existing = session.query(SavedProfile).filter(
                SavedProfile.user_id == user_id,
                SavedProfile.saved_username == username
            ).first()
            
            if existing:
                # Update existing
                existing.notes = notes or existing.notes
                existing.notify_on_change = notify
                existing.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing)
                logger.info(f"🔄 Updated saved profile {username} for user {user_id}")
                return existing
            
            # Create new
            saved = SavedProfile(
                user_id=user_id,
                saved_username=username,
                notes=notes,
                notify_on_change=notify
            )
            session.add(saved)
            session.commit()
            session.refresh(saved)
            logger.info(f"💾 Saved profile {username} for user {user_id}")
            return saved
    
    def get_saved_profiles(self, user_id: int) -> List[Dict]:
        """Get all saved profiles for a user"""
        with self.get_session() as session:
            profiles = session.query(SavedProfile).filter(
                SavedProfile.user_id == user_id
            ).order_by(SavedProfile.created_at.desc()).all()
            
            return [
                {
                    "id": p.id,
                    "username": p.saved_username,
                    "notes": p.notes,
                    "notify": p.notify_on_change,
                    "saved_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None
                }
                for p in profiles
            ]
    
    def unsave_profile(self, user_id: int, username: str) -> bool:
        """Remove a saved profile"""
        with self.get_session() as session:
            result = session.query(SavedProfile).filter(
                SavedProfile.user_id == user_id,
                SavedProfile.saved_username == username
            ).delete()
            session.commit()
            
            if result:
                logger.info(f"🗑️ Removed saved profile {username} for user {user_id}")
            return result > 0
    
    # ============ Portfolio History Operations ============
    
    def record_portfolio_score(self, username: str, score: float, analysis_id: int = None):
        """Record portfolio score for trend tracking"""
        with self.get_session() as session:
            history = PortfolioHistory(
                username=username,
                portfolio_score=score,
                analysis_id=analysis_id
            )
            session.add(history)
            session.commit()
            logger.info(f"📊 Recorded score {score} for {username}")
    
    def get_portfolio_trend(self, username: str, days: int = 30) -> List[Dict]:
        """Get portfolio score trend over time"""
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            history = session.query(PortfolioHistory).filter(
                PortfolioHistory.username == username,
                PortfolioHistory.recorded_at >= cutoff
            ).order_by(PortfolioHistory.recorded_at).all()
            
            return [
                {
                    "score": h.portfolio_score,
                    "date": h.recorded_at.isoformat()
                }
                for h in history
            ]
    
    # ============ Analytics Operations ============
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_session() as session:
            from sqlalchemy import func
            
            total_users = session.query(func.count(User.id)).scalar()
            total_analyses = session.query(func.count(Analysis.id)).scalar()
            total_searches = session.query(func.count(SearchHistory.id)).scalar()
            avg_score = session.query(func.avg(Analysis.portfolio_score)).scalar()
            
            return {
                "total_users": total_users or 0,
                "total_analyses": total_analyses or 0,
                "total_searches": total_searches or 0,
                "average_portfolio_score": float(avg_score) if avg_score else 0,
                "unique_usernames_analyzed": session.query(func.count(Analysis.analyzed_username.distinct())).scalar() or 0
            }
    
    def cleanup_old_sessions(self, days: int = 7):
        """Clean up expired or old sessions"""
        with self.get_session() as session:
            cutoff = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(OAuthSession).filter(
                OAuthSession.expires_at < cutoff
            ).delete()
            session.commit()
            
            if deleted:
                logger.info(f"🧹 Cleaned up {deleted} old sessions")
            return deleted
    
    # ============ Debug Operations ============
    
    def debug_get_user_by_token(self, session_token: str):
        """Debug function to check token lookup"""
        with self.get_session() as session:
            # Check if session exists
            oauth_session = session.query(OAuthSession).filter(
                OAuthSession.session_token == session_token
            ).first()
            
            if oauth_session:
                print(f"Found session: user_id={oauth_session.user_id}, active={oauth_session.is_active}, expires={oauth_session.expires_at}")
                user = session.query(User).filter(User.id == oauth_session.user_id).first()
                if user:
                    print(f"Found user: {user.username}, id={user.id}")
                    return {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                else:
                    print("User not found for session")
            else:
                print("Session not found")
                # Check if any sessions exist
                all_sessions = session.query(OAuthSession).all()
                print(f"Total sessions in DB: {len(all_sessions)}")
                for s in all_sessions[:5]:
                    print(f"  Session: {s.session_token[:50]}... user_id={s.user_id}")
            
            return None

# Create global database manager instance
db_manager = DatabaseManager()