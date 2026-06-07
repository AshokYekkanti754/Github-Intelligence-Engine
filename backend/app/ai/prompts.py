# AI Prompts for GitHub analysis

def get_profile_analysis_prompt(username: str, name: str, bio: str, 
                                  public_repos: int, followers: int, 
                                  following: int, total_stars: int,
                                  top_languages: list, top_repos: list) -> str:
    """Generate prompt for profile analysis"""
    
    repos_text = ""
    for i, repo in enumerate(top_repos[:3], 1):
        repos_text += f"{i}. {repo['name']} - {repo['stars']} stars, {repo['forks']} forks, Language: {repo['language']}\n"
    
    languages_text = ", ".join(top_languages) if top_languages else "Not enough data"
    
    prompt = f"""You are an expert GitHub portfolio analyzer. Analyze this developer's GitHub profile and provide insights.

Developer Information:
- Username: {username}
- Name: {name if name else 'Not provided'}
- Bio: {bio if bio else 'No bio provided'}
- Public Repositories: {public_repos}
- Followers: {followers}
- Following: {following}
- Total Stars Across Repos: {total_stars}

Top Languages: {languages_text}

Top Repositories:
{repos_text}

Please provide a JSON response with the following structure:
{{
    "strengths": ["strength1", "strength2", "strength3"],
    "weaknesses": ["weakness1", "weakness2"],
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"],
    "skill_level": "Beginner/Intermediate/Advanced/Expert",
    "best_project": "name of best project with explanation",
    "career_advice": "Specific career advice based on their profile",
    "summary": "One paragraph summary of this developer"
}}

Base your analysis on:
1. Repository quality and popularity (stars/forks)
2. Language diversity and technology stack
3. Community engagement (followers)
4. Profile completeness
5. Open source contribution patterns

Be honest but constructive. If the profile is new/low activity, acknowledge it and provide growth advice."""
    
    return prompt


def get_repo_analysis_prompt(repo_name: str, description: str, stars: int, 
                               forks: int, language: str, has_wiki: bool) -> str:
    """Generate prompt for individual repository analysis"""
    
    prompt = f"""Analyze this GitHub repository and provide insights:

Repository: {repo_name}
Description: {description if description else 'No description provided'}
Stars: {stars}
Forks: {forks}
Language: {language}
Has Wiki: {has_wiki}

Provide a brief analysis including:
1. Project quality assessment
2. Difficulty level for contributors
3. Portfolio value (how good this looks on a resume)
4. One specific improvement suggestion

Keep response concise and actionable."""
    
    return prompt


def get_improvement_suggestions_prompt(portfolio_score: int, strengths: list, 
                                         weaknesses: list, top_languages: list) -> str:
    """Generate prompt for improvement suggestions"""
    
    prompt = f"""Based on this GitHub portfolio with score {portfolio_score}/100:

Strengths: {', '.join(strengths) if strengths else 'Not enough data'}
Areas for improvement: {', '.join(weaknesses) if weaknesses else 'Unknown'}
Top languages: {', '.join(top_languages) if top_languages else 'None'}

Provide 3 specific, actionable suggestions to improve their GitHub portfolio.
Each suggestion should include:
- What to do
- Why it matters
- How to implement it

Focus on:
1. Increasing project visibility
2. Improving code quality
3. Building community engagement
4. Documentation improvements

Make suggestions personalized based on their current tech stack."""
    
    return prompt