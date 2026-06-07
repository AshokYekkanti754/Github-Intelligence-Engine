import httpx
import os
from typing import Dict, List, Any

class GitHubClient:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv('GITHUB_TOKEN')
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def get_user(self, username: str) -> Dict[str, Any]:
        """Fetch GitHub user profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{username}",
                headers=self.headers
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
    
    async def get_repos(self, username: str) -> List[Dict[str, Any]]:
        """Fetch all repositories for a user"""
        async with httpx.AsyncClient() as client:
            repos = []
            page = 1
            while True:
                response = await client.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={"page": page, "per_page": 100, "sort": "updated"}
                )
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                repos.extend(data)
                page += 1
            return repos
    
    async def get_repo_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get languages used in a repository"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/languages",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()