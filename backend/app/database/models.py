import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    """User model for authenticated users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    name = Column(String(200), nullable=True)
    company = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    
    # OAuth tokens (encrypted in production)
    github_access_token = Column(Text, nullable=True)
    github_refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
    oauth_sessions = relationship("OAuthSession", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "github_id": self.github_id,
            "username": self.username,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "name": self.name,
            "company": self.company,
            "location": self.location,
            "bio": self.bio,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

class OAuthSession(Base):
    """Store OAuth sessions"""
    __tablename__ = "oauth_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(500), unique=True, index=True, nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="oauth_sessions")

class Analysis(Base):
    """Store analysis results for users"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # Can be null for anonymous
    analyzed_username = Column(String(100), nullable=False, index=True)
    
    # Analysis results
    portfolio_score = Column(Float, nullable=False)
    total_repos = Column(Integer, default=0)
    public_repos = Column(Integer, default=0)
    private_repos = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    followers = Column(Integer, default=0)
    following = Column(Integer, default=0)
    
    # Data storage
    top_languages = Column(JSON, default=list)
    repo_ranking = Column(JSON, default=list)
    ai_insights = Column(JSON, default=dict)
    
    # Metadata
    was_authenticated = Column(Boolean, default=False)
    analysis_duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    
    def to_dict(self):
        return {
            "id": self.id,
            "analyzed_username": self.analyzed_username,
            "portfolio_score": self.portfolio_score,
            "total_repos": self.total_repos,
            "public_repos": self.public_repos,
            "private_repos": self.private_repos,
            "total_stars": self.total_stars,
            "followers": self.followers,
            "following": self.following,
            "top_languages": self.top_languages,
            "repo_ranking": self.repo_ranking[:5] if self.repo_ranking else [],  # Top 5 only
            "ai_insights": self.ai_insights,
            "was_authenticated": self.was_authenticated,
            "analyzed_at": self.created_at.isoformat() if self.created_at else None
        }

class SearchHistory(Base):
    """Track all searches (including anonymous)"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SavedProfile(Base):
    """Users can save profiles they want to track"""
    __tablename__ = "saved_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    saved_username = Column(String(100), nullable=False, index=True)
    notes = Column(Text, nullable=True)
    notify_on_change = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Composite unique constraint
    __table_args__ = (sqlalchemy.UniqueConstraint('user_id', 'saved_username', name='unique_user_saved_profile'),)

class PortfolioHistory(Base):
    """Track portfolio score changes over time"""
    __tablename__ = "portfolio_history"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    portfolio_score = Column(Float, nullable=False)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=True)
    recorded_at = Column(DateTime, server_default=func.now())