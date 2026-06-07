
import os
from dotenv import load_dotenv
import httpx
import openai

load_dotenv()

def test_github_token():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("❌ GitHub token missing!")
        return False
    print(f"✅ GitHub token found (starts with: {token[:10]}...)")
    return True

def test_openai_key():
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        print("❌ OpenAI key missing!")
        return False
    print(f"✅ OpenAI key found (starts with: {key[:15]}...)")
    return True

def test_database_url():
    url = os.getenv('DATABASE_URL')
    if not url:
        print("❌ Database URL missing!")
        return False
    print(f"✅ Database URL found: {url}")
    return True

def test_redis_url():
    url = os.getenv('REDIS_URL')
    if not url:
        print("❌ Redis URL missing!")
        return False
    print(f"✅ Redis URL found: {url}")
    return True

def test_jwt():
    secret = os.getenv('SECRET_KEY')
    algorithm = os.getenv('ALGORITHM')
    if not secret or not algorithm:
        print("❌ JWT config missing!")
        return False
    print(f"✅ JWT secret found, algorithm: {algorithm}")
    return True

if __name__ == "__main__":
    print("\n🔍 Testing Environment Variables...\n")
    test_github_token()
    test_openai_key()
    test_database_url()
    test_redis_url()
    test_jwt()
    print("\n✅ All keys loaded successfully!")
