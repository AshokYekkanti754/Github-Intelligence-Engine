-- Create database
CREATE DATABASE github_intelligence;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    github_username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis results table
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    portfolio_score INTEGER,
    analysis_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Repositories table
CREATE TABLE repositories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    repo_name VARCHAR(255),
    repo_url TEXT,
    stars INTEGER,
    forks INTEGER,
    language VARCHAR(100),
    quality_score INTEGER,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_users_github_username ON users(github_username);
CREATE INDEX idx_analyses_user_id ON analyses(user_id);
CREATE INDEX idx_repositories_user_id ON repositories(user_id);