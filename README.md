# GitHub Intelligence Engine 🚀

An intelligent analytics platform that provides deep insights into GitHub repositories, user activity, and development trends using AI-powered analysis.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Tech Stack](#tech-stack)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## ✨ Features

- **Repository Analytics**: Deep insights into repository health, contributions, and activity
- **User Profiling**: Comprehensive developer profiles with contribution patterns
- **Trend Analysis**: Track and predict emerging trends in repositories
- **AI-Powered Insights**: OpenAI integration for intelligent code analysis
- **Interactive Dashboard**: Modern React dashboard with real-time updates
- **Export Capabilities**: Export data in CSV and JSON formats
- **OAuth Integration**: Secure GitHub OAuth authentication

## 🏗️ Architecture
github-intelligence-engine/
├── backend/ # FastAPI backend with AI integration
├── frontend/ # React TypeScript frontend
├── database/ # PostgreSQL database schemas
├── docker/ # Docker configuration
└── docs/ # Documentation

text

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- Docker (optional)

### Environment Setup

1. **Clone the repository**
```bash
git clone https://github.com/AshokYekkanti754/Github-Intelligence-System.git
cd Github-Intelligence-System
Set up environment variables

bash
# Copy example environment files
cp backend/.env.example backend/.env
cp database/.env.example database/.env
cp frontend/.env.example frontend/.env

# Edit .env files with your actual credentials
# ⚠️ Never commit .env files to version control
Required API Keys

GitHub Personal Access Token

OpenAI API Key

Backend Setup
bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
Frontend Setup
bash
cd frontend
npm install
npm run dev
Using Docker
bash
docker-compose up -d
📊 API Documentation
Once backend is running, access interactive API docs at:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

Main Endpoints
Method	Endpoint	Description
GET	/api/repository/{owner}/{repo}	Get repository analysis
GET	/api/user/{username}	Get user profile analysis
POST	/api/analyze	Trigger AI analysis
GET	/api/trends	Get trending repositories
GET	/api/export/{format}	Export analysis data
🔒 Security
Critical Security Rules
NEVER commit .env files to version control

Always use .env.example as templates

Revoke exposed keys immediately

Use environment variables for all secrets

What's in .gitignore
gitignore
.env
*.env
!.env.example
backend/.env
database/.env
frontend/.env
If You Accidentally Commit Secrets
Revoke the exposed keys immediately

Remove from git history: git filter-branch

Generate new keys

Update local .env files

🛠️ Tech Stack
Backend
Framework: FastAPI (Python)

Database: PostgreSQL with SQLAlchemy

AI Integration: OpenAI GPT API

Authentication: OAuth 2.0 + JWT

Frontend
Framework: React 18 with TypeScript

Styling: Tailwind CSS

Charts: Recharts

HTTP Client: Axios

DevOps
Containerization: Docker & Docker Compose

Version Control: Git + GitHub

📝 Configuration
Required Environment Variables
backend/.env

env
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your_jwt_secret_here
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret
database/.env

env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=github_intelligence
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
frontend/.env

env
VITE_API_URL=http://localhost:8000/api
VITE_GITHUB_CLIENT_ID=your_oauth_client_id
VITE_APP_NAME=GitHub Intelligence Engine
🧪 Testing
bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
🐛 Troubleshooting
Common Issues and Solutions
Issue: Backend won't start

bash
# Check if .env file exists and has required variables
# Verify database connection
# Check if port 8000 is available
netstat -an | findstr :8000
Issue: GitHub API rate limiting

bash
# Use authenticated requests with valid token
# Implement exponential backoff for retries
# Check rate limit status:
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
Issue: OpenAI API errors

bash
# Verify API key is valid
# Check if you have credits
# Review rate limits at platform.openai.com
Issue: Push blocked by GitHub

bash
# Remove secrets from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all
  
# Force push clean history
git push origin main --force
🤝 Contributing
Fork the repository

Create a feature branch

bash
git checkout -b feature/amazing-feature
Commit your changes

bash
git commit -m 'Add amazing feature'
Push to branch

bash
git push origin feature/amazing-feature
Open a Pull Request

Development Guidelines
✅ Follow PEP 8 for Python code

✅ Use TypeScript strict mode for frontend

✅ Write tests for new features

✅ Update documentation for API changes

❌ Never commit secrets or .env files

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Author
Ashok Yekkanti

GitHub: @AshokYekkanti754

Email: ashokyekkanti737@gmail.com

🙏 Acknowledgments
GitHub for providing the REST API

OpenAI for GPT integration

FastAPI and React communities

📧 Contact
For questions or support, please open an issue on GitHub.

⭐ Star this repository if you find it useful!

text

## **Where Each Part Goes - File Breakdown**

### **📄 README.md (Root folder)**
**Location:** `C:\Users\ashok\Documents\GIE_Project\github-intelligence-engine\README.md`

**The ENTIRE content above goes into this ONE file.** Don't split it - it's a single README.md file.

### **📄 .gitignore (Root folder)**
**Location:** `C:\Users\ashok\Documents\GIE_Project\github-intelligence-engine\.gitignore`

**Content:**
```gitignore
# Environment files - NEVER COMMIT
.env
*.env
*.env.*
!.env.example
backend/.env
database/.env
frontend/.env
__pycache__/
*.pyc
.venv/
venv/
node_modules/
.DS_Store
.vscode/
.idea/
📄 backend/.env.example
Location: C:\Users\ashok\Documents\GIE_Project\github-intelligence-engine\backend\.env.example

Content:

env
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your_jwt_secret_here
GITHUB_CLIENT_ID=your_oauth_client_id
GITHUB_CLIENT_SECRET=your_oauth_client_secret
📄 database/.env.example
Location: C:\Users\ashok\Documents\GIE_Project\github-intelligence-engine\database\.env.example

Content:

env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=github_intelligence
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
📄 frontend/.env.example
Location: C:\Users\ashok\Documents\GIE_Project\github-intelligence-engine\frontend\.env.example

Content:

env
VITE_API_URL=http://localhost:8000/api
VITE_GITHUB_CLIENT_ID=your_oauth_client_id
VITE_APP_NAME=GitHub Intelligence Engine
Quick Creation Script (Run This)
powershell
# ============================================
# CREATE ALL FILES IN CORRECT LOCATIONS
# ============================================

Write-Host "Creating all files in correct locations..." -ForegroundColor Green

# 1. Create README.md (root)
Write-Host "Creating README.md..." -ForegroundColor Yellow
$readmeContent = @'
# GitHub Intelligence Engine 🚀

An intelligent analytics platform that provides deep insights into GitHub repositories, user activity, and development trends using AI-powered analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+

### Environment Setup

1. Clone the repository
2. Copy `.env.example` files to `.env` in each folder
3. Add your actual secrets to `.env` files
4. **Never commit `.env` files to GitHub**

### Required API Keys
- [GitHub Personal Access Token](https://github.com/settings/tokens)
- [OpenAI API Key](https://platform.openai.com/api-keys)

## 🔒 Security

**CRITICAL RULES:**
- ❌ NEVER commit `.env` files
- ✅ Always use `.env.example` as templates
- 🔑 Revoke exposed keys immediately
- 📝 Use environment variables for all secrets

## 📝 Configuration

Copy these templates to `.env` files:

**backend/.env**
GITHUB_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here

text

**database/.env**
POSTGRES_PASSWORD=your_password

text

**frontend/.env**
VITE_API_URL=http://localhost:8000/api

text

## 🐛 Troubleshooting

### Push blocked by GitHub?
1. Revoke exposed keys
2. Remove secrets from git history
3. Generate new keys
4. Push clean history

## 📄 License

MIT License - see LICENSE file

## 👤 Author

Ashok Yekkanti - [@AshokYekkanti754](https://github.com/AshokYekkanti754)

---
**⭐ Star this repo if useful!**
'@
$readmeContent | Out-File -FilePath "README.md" -Encoding utf8

# 2. Create .gitignore (root)
Write-Host "Creating .gitignore..." -ForegroundColor Yellow
@"
.env
*.env
!.env.example
backend/.env
database/.env
frontend/.env
__pycache__/
*.pyc
.venv/
node_modules/
.DS_Store
.vscode/
.idea/
"@ | Out-File -FilePath ".gitignore" -Encoding utf8

# 3. Create backend/.env.example
Write-Host "Creating backend/.env.example..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "backend" -Force | Out-Null
@"
GITHUB_TOKEN=your_github_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your_secret_key_here
"@ | Out-File -FilePath "backend\.env.example" -Encoding utf8

# 4. Create database/.env.example
Write-Host "Creating database/.env.example..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "database" -Force | Out-Null
@"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=github_intelligence
"@ | Out-File -FilePath "database\.env.example" -Encoding utf8

# 5. Create frontend/.env.example
Write-Host "Creating frontend/.env.example..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "frontend" -Force | Out-Null
@"
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=GitHub Intelligence Engine
"@ | Out-File -FilePath "frontend\.env.example" -Encoding utf8

Write-Host "`n✅ All files created in correct locations!" -ForegroundColor Green
Write-Host "`nFile structure:" -ForegroundColor Cyan
Write-Host "  📄 README.md (root)" -ForegroundColor White
Write-Host "  📄 .gitignore (root)" -ForegroundColor White
Write-Host "  📄 backend/.env.example" -ForegroundColor White
Write-Host "  📄 database/.env.example" -ForegroundColor White
Write-Host "  📄 frontend/.env.example" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. git add ." -ForegroundColor White
Write-Host "2. git commit -m 'Add README and configuration files'" -ForegroundColor White
Write-Host "3. git push" -ForegroundColor White
Summary - What Goes Where
File	Location	What it contains
README.md	Root folder	Complete project documentation (all the markdown above)
.gitignore	Root folder	List of files Git should ignore
.env.example	backend/ folder	Template for backend secrets (placeholders)
.env.example	database/ folder	Template for database secrets (placeholders)
.env.example	frontend/ folder	Template for frontend secrets (placeholders)
