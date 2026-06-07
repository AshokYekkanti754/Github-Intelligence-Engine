import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from app.database.manager import db_manager
from app.email.service import email_service
from app.github.client import GitHubClient
from app.analytics.scorers import PortfolioScorer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

github_client = GitHubClient()
scorer = PortfolioScorer()

async def check_saved_profiles_updates():
    """Check for changes in saved profiles and send notifications"""
    logger.info("🔍 Checking saved profiles for updates...")
    
    with db_manager.get_session() as session:
        from app.database.models import SavedProfile, User, PortfolioHistory
        
        # Get all saved profiles with notifications enabled
        saved_profiles = session.query(SavedProfile).filter(
            SavedProfile.notify_on_change == True
        ).all()
        
        notifications_sent = 0
        
        for saved in saved_profiles:
            # Get user who saved this profile
            user = session.query(User).filter(User.id == saved.user_id).first()
            if not user or not user.email:
                continue
            
            # Get latest portfolio history
            latest_history = session.query(PortfolioHistory).filter(
                PortfolioHistory.username == saved.saved_username
            ).order_by(PortfolioHistory.recorded_at.desc()).first()
            
            # Get previous score (from 7 days ago)
            week_ago = datetime.utcnow() - timedelta(days=7)
            previous_history = session.query(PortfolioHistory).filter(
                PortfolioHistory.username == saved.saved_username,
                PortfolioHistory.recorded_at <= week_ago
            ).order_by(PortfolioHistory.recorded_at.desc()).first()
            
            if latest_history and previous_history:
                old_score = previous_history.portfolio_score
                new_score = latest_history.portfolio_score
                
                # Send notification if score changed significantly (>5 points)
                if abs(new_score - old_score) >= 5:
                    await email_service.send_profile_update_notification(
                        user_email=user.email,
                        username=user.username,
                        profile_name=saved.saved_username,
                        old_score=int(old_score),
                        new_score=int(new_score),
                        changes={}
                    )
                    notifications_sent += 1
                    logger.info(f"📧 Sent notification for {saved.saved_username}")
        
        logger.info(f"✅ Sent {notifications_sent} notifications")

async def generate_weekly_digests():
    """Generate and send weekly digest emails to all users"""
    logger.info("📧 Generating weekly digests...")
    
    with db_manager.get_session() as session:
        from app.database.models import User, SavedProfile, PortfolioHistory
        
        # Get all users with saved profiles and email
        users = session.query(User).filter(
            User.email.isnot(None),
            User.email != ""
        ).all()
        
        week_end = datetime.utcnow()
        week_start = week_end - timedelta(days=7)
        week_range = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        
        digests_sent = 0
        
        for user in users:
            # Get user's saved profiles
            saved_profiles = session.query(SavedProfile).filter(
                SavedProfile.user_id == user.id
            ).all()
            
            if not saved_profiles:
                continue
            
            profiles_data = []
            
            for saved in saved_profiles:
                # Get current score
                current = session.query(PortfolioHistory).filter(
                    PortfolioHistory.username == saved.saved_username
                ).order_by(PortfolioHistory.recorded_at.desc()).first()
                
                # Get score from previous week
                previous = session.query(PortfolioHistory).filter(
                    PortfolioHistory.username == saved.saved_username,
                    PortfolioHistory.recorded_at >= week_start,
                    PortfolioHistory.recorded_at <= week_end
                ).first()
                
                # Get new repos (simplified - in production would track actual changes)
                try:
                    repos = await github_client.get_repos(saved.saved_username)
                    new_repos = repos[:5]  # Simplified
                except:
                    new_repos = []
                
                profiles_data.append({
                    "username": saved.saved_username,
                    "current_score": int(current.portfolio_score) if current else 0,
                    "score_change": int(current.portfolio_score - (previous.portfolio_score if previous else current.portfolio_score)) if current else 0,
                    "new_repos": new_repos,
                    "top_achievement": f"Reached {int(current.portfolio_score)} points!" if current else "Keep coding!"
                })
            
            if profiles_data:
                await email_service.send_weekly_digest(
                    user_email=user.email,
                    username=user.username,
                    profiles_data=profiles_data,
                    week_range=week_range
                )
                digests_sent += 1
                logger.info(f"📧 Sent weekly digest to {user.email}")
        
        logger.info(f"✅ Sent {digests_sent} weekly digests")

async def run_scheduled_tasks():
    """Run scheduled tasks (to be called by cron or background worker)"""
    await check_saved_profiles_updates()
    await generate_weekly_digests()