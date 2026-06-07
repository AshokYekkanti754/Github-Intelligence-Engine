import React, { useState, useEffect } from 'react';

const LoginButton = ({ onLogin, onLogout }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Check if user is already logged in
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('github_token');
      if (token) {
        try {
          const response = await fetch('http://localhost:8000/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            setUser(data);
            if (onLogin) onLogin(token);
          } else {
            localStorage.removeItem('github_token');
          }
        } catch (error) {
          console.error('Auth check failed:', error);
        }
      }
    };
    
    checkAuth();
  }, []);

  const handleLogin = () => {
    setLoading(true);
    // Redirect to GitHub OAuth
    window.location.href = 'http://localhost:8000/auth/github/login';
  };

  const handleLogout = async () => {
    const token = localStorage.getItem('github_token');
    if (token) {
      try {
        await fetch('http://localhost:8000/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }
    
    localStorage.removeItem('github_token');
    setUser(null);
    if (onLogout) onLogout();
  };

  if (loading) {
    return (
      <button className="px-4 py-2 bg-gray-600 rounded-lg cursor-wait">
        Loading...
      </button>
    );
  }

  if (user) {
    return (
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          <img 
            src={user.user_info?.avatar_url} 
            alt={user.username}
            className="w-8 h-8 rounded-full"
          />
          <span className="text-sm text-gray-300">
            {user.username}
          </span>
        </div>
        <button
          onClick={handleLogout}
          className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded-lg text-sm transition"
        >
          Logout
        </button>
      </div>
    );
  }

  return (
    <button
      onClick={handleLogin}
      className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg flex items-center gap-2 transition"
    >
      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12c0 4.42 2.87 8.17 6.84 9.49.5.09.68-.22.68-.48 0-.24-.01-.88-.01-1.72-2.78.6-3.37-1.34-3.37-1.34-.46-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.61.07-.61 1.01.07 1.54 1.03 1.54 1.03.9 1.52 2.36 1.08 2.93.83.09-.65.35-1.09.64-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.64 0 0 .84-.27 2.75 1.02.8-.22 1.65-.33 2.5-.33.85 0 1.7.11 2.5.33 1.91-1.29 2.75-1.02 2.75-1.02.55 1.37.2 2.39.1 2.64.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.94.36.31.68.92.68 1.85 0 1.34-.01 2.42-.01 2.75 0 .27.18.58.69.48C19.13 20.17 22 16.42 22 12c0-5.52-4.48-10-10-10z"/>
      </svg>
      Sign in with GitHub
    </button>
  );
};

export default LoginButton;