from typing import List, Dict, Any

class PortfolioScorer:
    @staticmethod
    def calculate_score(user_data: Dict, repos: List[Dict]) -> int:
        """Calculate portfolio score from 0-100"""
        scores = []
        
        # 1. Account age & activity (30%)
        account_age_score = PortfolioScorer._account_age_score(user_data)
        scores.append(("Account Age", account_age_score, 0.3))
        
        # 2. Repository quality (25%)
        repo_quality = PortfolioScorer._repo_quality_score(repos)
        scores.append(("Repo Quality", repo_quality, 0.25))
        
        # 3. Popularity (20%)
        popularity = PortfolioScorer._popularity_score(repos)
        scores.append(("Popularity", popularity, 0.20))
        
        # 4. Language diversity (15%)
        language_score = PortfolioScorer._language_diversity_score(repos)
        scores.append(("Languages", language_score, 0.15))
        
        # 5. Documentation (10%)
        documentation = PortfolioScorer._documentation_score(repos)
        scores.append(("Documentation", documentation, 0.10))
        
        total = sum(score * weight for _, score, weight in scores)
        return int(total)
    
    @staticmethod
    def _account_age_score(user_data: Dict) -> int:
        """Score based on account age and public activity"""
        public_repos = user_data.get('public_repos', 0)
        followers = user_data.get('followers', 0)
        
        repo_score = min(public_repos * 2, 50)
        follower_score = min(followers, 50)
        
        return repo_score + follower_score
    
    @staticmethod
    def _repo_quality_score(repos: List[Dict]) -> int:
        """Score based on repository quality"""
        if not repos:
            return 0
        
        quality_score = 0
        for repo in repos[:10]:  # Top 10 repos
            # Check if it's original (not a fork)
            if not repo.get('fork', False):
                quality_score += 10
            
            # Has description
            if repo.get('description'):
                quality_score += 5
                
            # Has topics
            if repo.get('topics'):
                quality_score += 5
        
        return min(quality_score, 100)
    
    @staticmethod
    def _popularity_score(repos: List[Dict]) -> int:
        """Score based on stars and forks"""
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        star_score = min(total_stars, 60)
        fork_score = min(total_forks, 40)
        
        return star_score + fork_score
    
    @staticmethod
    def _language_diversity_score(repos: List[Dict]) -> int:
        """Score based on number of different languages used"""
        languages = set()
        for repo in repos:
            if repo.get('language'):
                languages.add(repo['language'])
        
        language_count = len(languages)
        return min(language_count * 10, 100)
    
    @staticmethod
    def _documentation_score(repos: List[Dict]) -> int:
        """Score based on README and description quality"""
        score = 0
        for repo in repos[:5]:
            if repo.get('description'):
                score += 10
            if repo.get('has_wiki', False):
                score += 5
            if repo.get('homepage'):
                score += 5
        
        return min(score, 100)
    
    @staticmethod
    def rank_repos(repos: List[Dict]) -> List[Dict]:
        """Rank repositories by quality score"""
        ranked = []
        for repo in repos:
            rank_score = 0
            rank_score += repo.get('stargazers_count', 0) * 3
            rank_score += repo.get('forks_count', 0) * 2
            rank_score += 50 if not repo.get('fork', False) else 0
            rank_score += 20 if repo.get('description') else 0
            
            ranked.append({
                'name': repo['name'],
                'stars': repo.get('stargazers_count', 0),
                'forks': repo.get('forks_count', 0),
                'language': repo.get('language', 'Unknown'),
                'rank_score': rank_score,
                'url': repo['html_url']
            })
        
        ranked.sort(key=lambda x: x['rank_score'], reverse=True)
        return ranked[:10]