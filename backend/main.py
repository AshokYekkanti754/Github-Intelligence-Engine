# Add to imports
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
import time
from datetime import datetime
from authlib.integrations.starlette_client import OAuthError
from fastapi import Query
# from app.export.service import export_service
from app.tasks.email_tasks import check_saved_profiles_updates, generate_weekly_digests

load_dotenv()

from app.github.client import GitHubClient
from app.analytics.scorers import PortfolioScorer
from app.ai.llm_client import LLMClient
from app.auth.oauth import oauth
from app.auth.jwt_handler import create_access_token, decode_access_token
from app.database.manager import db_manager
from starlette.middleware.sessions import SessionMiddleware

class AnalyzeRequest(BaseModel):
    username: str
    access_token: Optional[str] = None

class SaveProfileRequest(BaseModel):
    username: str
    notes: Optional[str] = None
    notify: bool = False

class UpdateProfileRequest(BaseModel):
    notes: Optional[str] = None
    notify: Optional[bool] = None

app = FastAPI(title="GitHub Intelligence Engine API")

# Add Session Middleware
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secret-key"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
github_client = GitHubClient()
scorer = PortfolioScorer()
llm_client = LLMClient()

class AnalyzeRequest(BaseModel):
    username: str
    access_token: Optional[str] = None

class SaveProfileRequest(BaseModel):
    username: str
    notes: Optional[str] = None
    notify: bool = False

@app.post("/api/saved")
async def save_profile(request: SaveProfileRequest, http_request: Request):
    """Save a GitHub profile to your list"""
    try:
        # Get token from header
        token = http_request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated - Please login first")
        
        # Get user from token
        user = db_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Save the profile
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "avatar_url": user["avatar_url"],
            "name": user["name"]
}
        
        return {
            "success": True,
            "message": f"Profile @{request.username} saved successfully",
            "profile": {
                "id": saved["id"],
                "username": saved["username"],
                "notes": saved["notes"],
                "notify": saved["notify"],
                "saved_at": saved["created_at"].isoformat() if saved["created_at"] else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save profile: {str(e)}")

@app.get("/api/saved")
async def get_saved_profiles(request: Request):
    """Get all saved profiles for authenticated user"""
    try:
        # Get token from header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user from token
        user = db_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Get saved profiles
        profiles = db_manager.get_saved_profiles(user["id"])
        
        return {
            "success": True,
            "profiles": profiles,
            "total": len(profiles)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting saved profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get saved profiles: {str(e)}")

@app.delete("/api/saved/{username}")
async def unsave_profile(username: str, request: Request):
    """Remove a saved profile"""
    try:
        # Get token from header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user from token
        user = db_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Remove saved profile
        deleted = db_manager.unsave_profile(user["id"], username)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Profile @{username} not found in your saved list")
        
        return {
            "success": True,
            "message": f"Profile @{username} removed from saved list"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error removing saved profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to remove profile: {str(e)}")

@app.put("/api/saved/{username}")
async def update_saved_profile(username: str, update: UpdateProfileRequest, request: Request):
    """Update saved profile settings (notes, notifications)"""
    try:
        # Get token from header
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Get user from token
        user = db_manager.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Update the profile
        with db_manager.get_session() as session:
            from app.database.models import SavedProfile
            
            profile = session.query(SavedProfile).filter(
                SavedProfile.user_id == user["id"],
                SavedProfile.saved_username == username
            ).first()
            
            if not profile:
                raise HTTPException(status_code=404, detail=f"Profile @{username} not found")
            
            if update.notes is not None:
                profile["notes"] = update.notes
            if update.notify is not None:
                profile["notify"] = update.notify
            
            profile["updated_at"] = datetime.utcnow()
            session.commit()
            
            return {
                "success": True,
                "message": f"Profile @{username} updated",
                "profile": {
                    "id": profile["id"],
                    "username": profile["username"],
                    "notes": profile["notes"],
                    "notify": profile["notify"]
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating saved profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.get("/")
async def root():
    return {"message": "GitHub Intelligence Engine API with Database"}

@app.get("/health")
async def health_check():
    # Check database health
    try:
        stats = db_manager.get_stats()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

# ============ OAuth Routes (Enhanced with DB) ============

@app.get("/auth/github/login")
async def github_login(request: Request):
    """Redirect to GitHub OAuth login"""
    redirect_uri = "http://localhost:8000/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/auth/github/callback")
async def github_callback(request: Request):
    """Handle GitHub OAuth callback with database storage"""

    try:
        # Get GitHub access token
        token = await oauth.github.authorize_access_token(request)

        # Get GitHub user info
        resp = await oauth.github.get("user", token=token)
        user_info = resp.json()

        # Get email
        email = user_info.get("email")

        if not email:
            emails_resp = await oauth.github.get(
                "user/emails",
                token=token
            )

            emails = emails_resp.json()

            for e in emails:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break

        # Save or update user in database
        user = db_manager.get_or_create_user(
            github_id=user_info["id"],
            username=user_info["login"],
            email=email,
            avatar_url=user_info.get("avatar_url"),
            name=user_info.get("name"),
            access_token=token.get("access_token")
        )

        # Create JWT token
        jwt_token = create_access_token({
            "github_id": user_info["id"],
            "username": user_info["login"],
            "email": email,
            "user_id": user["id"]
        })

        # Save OAuth session
        db_manager.create_oauth_session(
            user_id=user["id"],
            session_token=jwt_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        # Redirect to frontend
        redirect_url = (
            f"http://localhost:5173/auth/callback?token={jwt_token}"
        )

        return RedirectResponse(url=redirect_url)

    except Exception as e:
        print("❌ OAuth Callback Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/auth/me")
async def get_current_user(request: Request):
    """Get current authenticated user from database"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return JSONResponse(status_code=401, content={"error": "No token provided"})
    
    user = db_manager.get_user_by_token(token)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid or expired session"})
    
    return {
        "authenticated": True,
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "avatar_url": user["avatar_url"],
        "name": user["name"],
        "user_info": {
            "login": user["username"],
            "avatar_url": user["avatar_url"],
            "name": user["name"]
        }
    }

@app.get("/api/search-history")
async def get_search_history():
    return db_manager.get_popular_searches()

@app.post("/auth/logout")
async def logout(request: Request):
    """Logout user and invalidate session"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if token:
        db_manager.invalidate_session(token)
    
    return {"message": "Logged out successfully"}

# ============ Enhanced API with Database ============

@app.post("/api/analyze")
async def analyze_github(request: AnalyzeRequest, http_request: Request):
    """Analyze a GitHub profile with database storage"""
    
    start_time = time.time()
    
    print(f"🔍 Analyzing GitHub user: {request.username}")
    
    # Check if user is authenticated
    auth_token = request.access_token
    user_id = None
    is_authenticated = False
    
    header_token = http_request.headers.get('Authorization', '').replace('Bearer ', '')
    if header_token:
        user = db_manager.get_user_by_token(header_token)
        if user:
            user_id = user["id"]
            auth_token = user["github_access_token"]
            is_authenticated = True
            print(f"✅ Authenticated as: {user['username']}")
    
    # Log the search
    # db_manager.log_search(
    #     username=request.username,
    #     user_id=user_id,
    #     ip_address=http_request.client.host if http_request.client else None,
    #     user_agent=http_request.headers.get('user-agent')
    # )
    
    # Create GitHub client with optional auth token
    if auth_token:
        github_client.headers["Authorization"] = f"token {auth_token}"
    
    # Fetch user data
    user_data = await github_client.get_user(request.username)
    if not user_data:
        raise HTTPException(status_code=404, detail=f"User '{request.username}' not found")
    
    print(f"✅ Found user: {user_data.get('login')}")
    
    # Fetch repositories
    repos = await github_client.get_repos(request.username)
    print(f"📚 Found {len(repos)} repositories")
    
    # Calculate score
    portfolio_score = scorer.calculate_score(user_data, repos)
    
    # Rank repositories
    repo_ranking = scorer.rank_repos(repos)
    
    # Get top languages
    languages = {}
    for repo in repos[:20]:
        if repo.get('language'):
            lang = repo['language']
            languages[lang] = languages.get(lang, 0) + 1
    
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    top_languages_list = [lang for lang, count in top_languages]
    
    # Calculate total stars
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
    
    print("🤖 Generating AI insights...")
    
    # Generate AI insights
    try:
        ai_insights = await llm_client.generate_profile_insights(
            user_data, repos, portfolio_score, top_languages_list, repo_ranking
        )
    except Exception as e:
        print(f"AI generation failed: {e}")
        ai_insights = {
            "strengths": ["Active GitHub user", "Has public repositories"],
            "weaknesses": ["Limited AI analysis available"],
            "recommendations": ["Check OpenAI API configuration", "Try again later"],
            "skill_level": "Unknown",
            "best_project": repo_ranking[0]['name'] if repo_ranking else "None",
            "career_advice": "Keep contributing to GitHub!",
            "summary": f"{request.username} has {user_data.get('public_repos', 0)} repositories with {total_stars} total stars."
        }
    
    # Prepare analysis result
    analysis_result = {
        "username": request.username,
        "name": user_data.get('name', request.username),
        "avatar_url": user_data.get('avatar_url'),
        "bio": user_data.get('bio', ''),
        "portfolio_score": portfolio_score,
        "total_repos": len(repos),
        "public_repos": user_data.get('public_repos', 0),
        "private_repos": len(repos) - user_data.get('public_repos', 0) if is_authenticated else 0,
        "total_stars": total_stars,
        "followers": user_data.get('followers', 0),
        "following": user_data.get('following', 0),
        "top_languages": top_languages_list,
        "repo_ranking": repo_ranking,
        "is_authenticated": is_authenticated,
        "duration_ms": int((time.time() - start_time) * 1000),
        "ai_insights": {
            "strength": ai_insights.get('strengths', ['No data'])[0] if isinstance(ai_insights.get('strengths'), list) else ai_insights.get('strength', 'Analyzing...'),
            "improvement": ai_insights.get('recommendations', ['No data'])[0] if isinstance(ai_insights.get('recommendations'), list) else ai_insights.get('improvement', 'Keep learning!'),
            "top_repo": ai_insights.get('best_project', repo_ranking[0]['name'] if repo_ranking else "None"),
            "skill_level": ai_insights.get('skill_level', 'Intermediate'),
            "career_advice": ai_insights.get('career_advice', 'Continue building your portfolio'),
            "summary": ai_insights.get('summary', 'Profile analysis complete'),
            "all_strengths": ai_insights.get('strengths', []),
            "all_recommendations": ai_insights.get('recommendations', [])
        }
    }
    
    # Save analysis to database
    db_manager.save_analysis(user_id, analysis_result)
    
    # Record portfolio score for trend tracking
    db_manager.record_portfolio_score(request.username, portfolio_score)
    
    return analysis_result

# ============ New Database Routes ============

@app.get("/api/history")
async def get_my_history(request: Request, limit: int = Query(10, ge=1, le=50)):
    """Get analysis history for authenticated user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user = db_manager.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    history = db_manager.get_user_analyses(user["id"], limit)
    return {
        "user": user["username"],
        "history": history,
        "total": len(history)
    }

@app.get("/api/history/{username}")
async def get_username_history(username: str, limit: int = Query(10, ge=1, le=50)):
    """Get analysis history for a specific GitHub username"""
    history = db_manager.get_username_history(username, limit)
    return {
        "username": username,
        "history": history,
        "total": len(history)
    }

@app.post("/api/saved")
async def save_profile(request: SaveProfileRequest, http_request: Request):
    """Save a GitHub profile to your list"""
    token = http_request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user = db_manager.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    saved = db_manager.save_profile(
        user_id=user["id"],
        username=request.username,
        notes=request.notes,
        notify=request.notify
    )
    
    return {
        "message": f"Profile {request.username} saved successfully",
        "profile": {
            "id": saved["id"],
            "username": saved["username"],
            "notes": saved["notes"],
            "notify": saved["notify"]
        }
    }

@app.get("/api/saved")
async def get_saved_profiles(request: Request):
    """Get all saved profiles for authenticated user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user = db_manager.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profiles = db_manager.get_saved_profiles(user.id)
    return {
        "profiles": profiles,
        "total": len(profiles)
    }

@app.delete("/api/saved/{username}")
async def unsave_profile(username: str, request: Request):
    """Remove a saved profile"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user = db_manager.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    deleted = db_manager.unsave_profile(user.id, username)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Profile {username} not found in saved list")
    
    return {"message": f"Profile {username} removed from saved list"}

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    stats = db_manager.get_stats()
    
    # Get popular searches
    popular = db_manager.get_popular_searches(5)
    stats["popular_searches"] = popular
    
    return stats

@app.get("/api/trend/{username}")
async def get_portfolio_trend(username: str, days: int = Query(30, ge=1, le=365)):
    """Get portfolio score trend for a username"""
    trend = db_manager.get_portfolio_trend(username, days)
    return {
        "username": username,
        "days": days,
        "trend": trend,
        "points": len(trend)
    }




# ============ Email Management Routes ============

@app.post("/api/notifications/test")
async def test_notifications(request: Request):
    """Send test notification to current user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    user = db_manager.get_user_by_token(token)
    if not user or not user["email"]:
        raise HTTPException(status_code=400, detail="User has no email configured")
    
    from app.email.service import email_service
    
    # Send test email
    success = await email_service.send_email(
        to_email=user["email"],
        subject="GitHub Intelligence - Test Notification",
        html_content="""
        <h1>✅ Test Notification</h1>
        <p>This is a test email from GitHub Intelligence Engine.</p>
        <p>You'll receive real notifications when your saved profiles change!</p>
        """
    )
    
    if success:
        return {"message": f"Test email sent to {user['email']}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send test email")

@app.post("/api/notifications/run-digest")
async def run_digest_manually():
    """Manually trigger weekly digest generation (admin only)"""
    # In production, add admin authentication
    await generate_weekly_digests()
    return {"message": "Weekly digest generation triggered"}

@app.post("/api/notifications/check-updates")
async def check_updates():
    """Manually check for profile updates"""
    await check_saved_profiles_updates()
    return {"message": "Profile update check triggered"}