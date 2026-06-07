import openai
import os
from typing import Dict, Any, List
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

class LLMClient:
    def __init__(self):
        self.model = "gpt-3.5-turbo"  # You can use "gpt-4" if you have access
        
    async def generate_profile_insights(self, user_data: Dict, repos: List, 
                                         portfolio_score: int, top_languages: List,
                                         top_repos: List) -> Dict[str, Any]:
        """Generate AI insights for a GitHub profile"""
        
        from app.ai.prompts import get_profile_analysis_prompt
        
        # Prepare data for prompt
        username = user_data.get('login', '')
        name = user_data.get('name', '')
        bio = user_data.get('bio', '')
        public_repos = user_data.get('public_repos', 0)
        followers = user_data.get('followers', 0)
        following = user_data.get('following', 0)
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        
        # Get prompt
        prompt = get_profile_analysis_prompt(
            username, name, bio, public_repos, followers, 
            following, total_stars, top_languages, top_repos
        )
        
        try:
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert GitHub portfolio analyzer. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            content = response.choices[0].message.content
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
            else:
                insights = json.loads(content)
            
            return insights
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback insights if API fails
            return self._get_fallback_insights(portfolio_score, top_languages)
    
    async def generate_repo_analysis(self, repo: Dict) -> str:
        """Generate analysis for a single repository"""
        
        from app.ai.prompts import get_repo_analysis_prompt
        
        prompt = get_repo_analysis_prompt(
            repo.get('name', ''),
            repo.get('description', ''),
            repo.get('stars', 0),
            repo.get('forks', 0),
            repo.get('language', 'Unknown'),
            repo.get('has_wiki', False)
        )
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code reviewer and mentor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"OpenAI API error for repo analysis: {e}")
            return "AI analysis temporarily unavailable. Check your OpenAI API key."
    
    def _get_fallback_insights(self, portfolio_score: int, top_languages: List) -> Dict:
        """Fallback insights when OpenAI API fails"""
        
        if portfolio_score >= 80:
            strengths = ["High-quality projects", "Strong community engagement", "Consistent contributions"]
            weaknesses = ["Could increase documentation", "Consider more diverse projects"]
            recommendations = ["Write more tutorials", "Contribute to popular open source projects"]
            skill_level = "Expert"
            career_advice = "You're ready for senior roles. Start mentoring others."
        elif portfolio_score >= 60:
            strengths = ["Good project variety", "Active contributor", "Solid foundation"]
            weaknesses = ["Inconsistent activity", "Limited documentation"]
            recommendations = ["Improve README files", "Add more comments to code"]
            skill_level = "Intermediate"
            career_advice = "Keep building. Consider contributing to open source."
        elif portfolio_score >= 40:
            strengths = ["Getting started with GitHub", "Has some projects"]
            weaknesses = ["Low activity", "Few followers", "Limited project variety"]
            recommendations = ["Create more projects", "Engage with community", "Improve documentation"]
            skill_level = "Beginner"
            career_advice = "Focus on learning fundamentals and building projects."
        else:
            strengths = ["Starting their GitHub journey"]
            weaknesses = ["Profile needs more activity", "Few repositories"]
            recommendations = ["Create first repository", "Learn Git basics", "Follow coding tutorials"]
            skill_level = "Beginner"
            career_advice = "Start with small projects and build consistency."
        
        best_project = "Your most popular project based on stars"
        summary = f"This developer has a {skill_level.lower()} level profile with a score of {portfolio_score}/100. Primary technologies include {', '.join(top_languages[:3]) if top_languages else 'various languages'}."
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "skill_level": skill_level,
            "best_project": best_project,
            "career_advice": career_advice,
            "summary": summary
        }