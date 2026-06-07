import React, { useState, useEffect } from 'react'
import LoginButton from './components/Auth/LoginButton'
import NotificationSettings from './components/Settings/NotificationSettings'
import './index.css'

function App() {
  const [username, setUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activeTab, setActiveTab] = useState('analyze')
  const [history, setHistory] = useState([])
  const [savedProfiles, setSavedProfiles] = useState([])
  const [stats, setStats] = useState(null)
  const [savingProfile, setSavingProfile] = useState(false)

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    
    if (token) {
      localStorage.setItem('github_token', token);
      setAccessToken(token);
      setIsAuthenticated(true);
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      const savedToken = localStorage.getItem('github_token');
      if (savedToken) {
        setAccessToken(savedToken);
        setIsAuthenticated(true);
        fetchUserInfo(savedToken);
      }
    }
    
    // Fetch platform stats
    fetchStats();
  }, []);

  const fetchUserInfo = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        console.log('User info:', data);
      }
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const fetchHistory = async () => {
    if (!accessToken) return;
    try {
      const response = await fetch('http://localhost:8000/api/history', {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const data = await response.json();
      setHistory(data.history);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    }
  };

const fetchSavedProfiles = async () => {
  if (!accessToken) return;
  try {
    console.log('Fetching saved profiles...');
    const response = await fetch('http://localhost:8000/api/saved', {
      headers: { 
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    console.log('Saved profiles response:', data);
    
    if (response.ok && data.success) {
      setSavedProfiles(data.profiles || []);
    } else if (response.ok) {
      setSavedProfiles(data.profiles || []);
    } else {
      console.error('Failed to fetch saved profiles:', data);
      setSavedProfiles([]);
    }
  } catch (error) {
    console.error('Failed to fetch saved profiles:', error);
    setSavedProfiles([]);
  }
};

const saveCurrentProfile = async () => {
  if (!result || !accessToken) {
    alert('Please login and analyze a profile first');
    return;
  }
  
  setSavingProfile(true);
  try {
    console.log('Saving profile:', result.username);
    console.log('With token:', accessToken);
    
    const response = await fetch('http://localhost:8000/api/saved', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        username: result.username,
        notes: `Saved on ${new Date().toLocaleString()}`,
        notify: true
      })
    });
    
    const data = await response.json();
    console.log('Save response:', data);
    
    if (response.ok) {
      alert(`✅ Profile @${result.username} saved! You'll receive notifications about changes.`);
      // Refresh saved profiles
      if (activeTab === 'settings') {
        fetchSavedProfiles();
      }
    } else {
      alert(`Failed to save: ${data.detail || data.message || 'Unknown error'}`);
    }
  } catch (error) {
    console.error('Failed to save profile:', error);
    alert(`Failed to save profile: ${error.message}`);
  } finally {
    setSavingProfile(false);
  }
};


  const handleLogin = (token) => {
    setAccessToken(token);
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('github_token');
    setAccessToken(null);
    setIsAuthenticated(false);
    setResult(null);
    setHistory([]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!username.trim()) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken && { 'Authorization': `Bearer ${accessToken}` })
        },
        body: JSON.stringify({ 
          username: username.trim(),
          access_token: accessToken 
        })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to analyze profile')
      }
      
      const data = await response.json()
      setResult(data)
      
      // Refresh history if authenticated
      if (accessToken) {
        fetchHistory();
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  // Switch tabs and load data
  useEffect(() => {
    if (activeTab === 'history' && accessToken) {
      fetchHistory();
    } else if (activeTab === 'settings' && accessToken) {
      fetchSavedProfiles();
    }
  }, [activeTab, accessToken]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header with Login */}
        <div className="flex justify-between items-center mb-8">
          <div className="text-center flex-1">
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent mb-2">
              GitHub Intelligence Engine
            </h1>
            <p className="text-gray-400 text-lg">
              AI-powered analysis of your GitHub portfolio
            </p>
          </div>
          <div className="flex gap-2 items-center">
            {isAuthenticated && (
              <>
                <button
                  onClick={() => setActiveTab('analyze')}
                  className={`px-3 py-1 rounded-lg transition ${activeTab === 'analyze' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                >
                  🔍 Analyze
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-3 py-1 rounded-lg transition ${activeTab === 'history' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                >
                  📜 History
                </button>
                <button
                  onClick={() => setActiveTab('settings')}
                  className={`px-3 py-1 rounded-lg transition ${activeTab === 'settings' ? 'bg-blue-600' : 'hover:bg-gray-700'}`}
                >
                  ⚙️ Settings
                </button>
              </>
            )}
            <LoginButton onLogin={handleLogin} onLogout={handleLogout} />
          </div>
        </div>

        {/* Platform Stats Banner */}
        {stats && (
          <div className="max-w-4xl mx-auto mb-6 bg-gray-800/50 rounded-lg p-3 text-center text-sm text-gray-300">
            <span className="mx-3">📊 {stats.total_analyses || 0} analyses</span>
            <span className="mx-3">👥 {stats.total_users || 0} users</span>
            <span className="mx-3">⭐ Avg score: {Math.round(stats.average_portfolio_score || 0)}/100</span>
          </div>
        )}

        {/* Auth Status Banner */}
        {isAuthenticated && (
          <div className="max-w-2xl mx-auto mb-6 bg-green-900/30 border border-green-500 rounded-lg p-3 text-center text-green-300 text-sm">
            ✅ Authenticated with GitHub - Access to private repositories enabled!
          </div>
        )}

        {/* Main Content */}
        {activeTab === 'analyze' && (
          <>
            {/* Search Form */}
            <div className="max-w-2xl mx-auto mb-12">
              <form onSubmit={handleSubmit} className="flex gap-4">
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter GitHub username (e.g., octocat, torvalds)"
                  className="flex-1 px-6 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-blue-500 text-white text-lg"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 transition disabled:opacity-50"
                >
                  {loading ? 'Analyzing...' : 'Analyze'}
                </button>
              </form>
            </div>

            {/* Error Message */}
            {error && (
              <div className="max-w-2xl mx-auto mb-8 bg-red-900/50 border border-red-500 text-red-200 px-6 py-4 rounded-lg">
                {error}
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                <p className="text-gray-400 mt-4">Fetching GitHub data...</p>
                <p className="text-gray-500 text-sm mt-2">Analyzing with AI...</p>
              </div>
            )}

            {/* Results Dashboard */}
            {result && !loading && (
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Export and Save Buttons */}
                <div className="flex justify-between items-center">
                  {/* <div className="flex gap-2">
                    <ExportButton username={result.username} exportType="analysis" token={accessToken} />
                    <ExportButton username={result.username} exportType="trend" token={accessToken} />
                  </div> */}
                  {isAuthenticated && (
                    <button
                      onClick={saveCurrentProfile}
                      disabled={savingProfile}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition flex items-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                      {savingProfile ? 'Saving...' : 'Save Profile'}
                    </button>
                  )}
                </div>

                {/* Auth Badge on Results */}
                {result.is_authenticated && result.private_repos > 0 && (
                  <div className="bg-purple-900/30 border border-purple-500 rounded-lg p-3 text-center">
                    <span className="text-purple-300">
                      🔒 Includes {result.private_repos} private {result.private_repos === 1 ? 'repository' : 'repositories'}
                    </span>
                  </div>
                )}

                {/* Profile Header */}
                <div className="bg-gray-800 rounded-2xl p-6 flex items-center gap-6">
                  <img 
                    src={result.avatar_url} 
                    alt={result.name}
                    className="w-24 h-24 rounded-full border-4 border-blue-500"
                  />
                  <div>
                    <h2 className="text-2xl font-bold">{result.name}</h2>
                    <p className="text-gray-400">@{result.username}</p>
                    {result.bio && <p className="text-gray-300 mt-2">{result.bio}</p>}
                  </div>
                </div>

                {/* Score Card */}
                <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center">
                  <h3 className="text-xl font-bold mb-2">Portfolio Score</h3>
                  <div className="text-7xl font-bold mb-2">{result.portfolio_score}/100</div>
                  <div className="w-full bg-white/30 rounded-full h-2 mt-4">
                    <div 
                      className="bg-white rounded-full h-2 transition-all duration-1000"
                      style={{ width: `${result.portfolio_score}%` }}
                    ></div>
                  </div>
                  <p className="mt-4 text-blue-100">
                    Skill Level: {result.ai_insights?.skill_level || 'Analyzing...'}
                  </p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-blue-500">{result.total_repos}</div>
                    <div className="text-gray-400 text-sm">
                      Total Repos
                      {result.private_repos > 0 && (
                        <span className="text-purple-400 text-xs block">({result.private_repos} private)</span>
                      )}
                    </div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-yellow-500">{result.total_stars}</div>
                    <div className="text-gray-400 text-sm">Total Stars</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-green-500">{result.followers}</div>
                    <div className="text-gray-400 text-sm">Followers</div>
                  </div>
                  <div className="bg-gray-800 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-purple-500">{result.following}</div>
                    <div className="text-gray-400 text-sm">Following</div>
                  </div>
                </div>

                {/* AI Summary Card */}
                <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-2xl p-6 border border-purple-500">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <span>🤖</span> AI Profile Summary
                  </h3>
                  <p className="text-gray-200 leading-relaxed">
                    {result.ai_insights?.summary || 'Analysis in progress...'}
                  </p>
                </div>

                {/* Strengths & Weaknesses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-green-900/20 border border-green-500 rounded-2xl p-6">
                    <h3 className="text-xl font-bold mb-3 text-green-400">✅ Strengths</h3>
                    <ul className="space-y-2">
                      {result.ai_insights?.all_strengths && result.ai_insights.all_strengths.length > 0 ? (
                        result.ai_insights.all_strengths.map((strength, idx) => (
                          <li key={idx} className="text-gray-300">• {strength}</li>
                        ))
                      ) : (
                        <li className="text-gray-300">• {result.ai_insights?.strength || 'Analyzing...'}</li>
                      )}
                    </ul>
                  </div>

                  <div className="bg-yellow-900/20 border border-yellow-500 rounded-2xl p-6">
                    <h3 className="text-xl font-bold mb-3 text-yellow-400">📈 Areas for Improvement</h3>
                    <ul className="space-y-2">
                      {result.ai_insights?.all_recommendations && result.ai_insights.all_recommendations.length > 0 ? (
                        result.ai_insights.all_recommendations.map((rec, idx) => (
                          <li key={idx} className="text-gray-300">• {rec}</li>
                        ))
                      ) : (
                        <li className="text-gray-300">• {result.ai_insights?.improvement || 'Keep learning!'}</li>
                      )}
                    </ul>
                  </div>
                </div>

                {/* Career Advice */}
                <div className="bg-blue-900/20 border border-blue-500 rounded-2xl p-6">
                  <h3 className="text-xl font-bold mb-3 text-blue-400">💼 Career Advice</h3>
                  <p className="text-gray-200">{result.ai_insights?.career_advice || 'Continue building your portfolio'}</p>
                </div>

                {/* Top Languages */}
                {result.top_languages && result.top_languages.length > 0 && (
                  <div className="bg-gray-800 rounded-2xl p-6">
                    <h3 className="text-xl font-bold mb-4">📊 Top Languages</h3>
                    <div className="flex flex-wrap gap-2">
                      {result.top_languages.map((lang, idx) => (
                        <span key={idx} className="px-3 py-1 bg-blue-600/30 rounded-full text-blue-300">
                          {lang}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Top Repositories */}
                {result.repo_ranking && result.repo_ranking.length > 0 && (
                  <div className="bg-gray-800 rounded-2xl p-6">
                    <h3 className="text-xl font-bold mb-4">🏆 Top Repositories</h3>
                    <div className="space-y-4">
                      {result.repo_ranking.slice(0, 5).map((repo, idx) => (
                        <div key={repo.name} className="border-b border-gray-700 pb-4 last:border-0">
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <span className="text-yellow-500 font-bold">#{idx + 1}</span>
                                <a 
                                  href={repo.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="text-blue-400 hover:underline font-semibold text-lg"
                                >
                                  {repo.name}
                                </a>
                              </div>
                              <div className="flex gap-4 mt-2 text-sm text-gray-400">
                                <span>⭐ {repo.stars} stars</span>
                                <span>🍴 {repo.forks} forks</span>
                                <span>💻 {repo.language || 'N/A'}</span>
                              </div>
                              {repo.description && (
                                <p className="text-gray-500 text-sm mt-2">{repo.description.substring(0, 100)}</p>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Analysis Time */}
                {result.duration_ms && (
                  <div className="text-center text-gray-500 text-sm">
                    Analysis completed in {result.duration_ms}ms
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* History Tab */}
        {activeTab === 'history' && isAuthenticated && (
          <div className="max-w-4xl mx-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">📜 Your Analysis History</h2>
              <ExportButton exportType="history" token={accessToken} />
            </div>
            
            <div className="bg-gray-800 rounded-2xl p-6">
              {history.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  No analyses yet. Search for GitHub profiles to build your history!
                </div>
              ) : (
                <div className="space-y-3">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="border border-gray-700 rounded-lg p-4 hover:bg-gray-700/50 cursor-pointer transition"
                      onClick={() => {
                        setActiveTab('analyze');
                        setUsername(item.analyzed_username);
                        handleSubmit(new Event('submit'));
                      }}
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="font-semibold text-blue-400">@{item.analyzed_username}</span>
                          <span className="text-gray-400 text-sm ml-2">
                            Score: {item.portfolio_score}/100
                          </span>
                        </div>
                        <div className="text-gray-500 text-sm">
                          {new Date(item.analyzed_at).toLocaleDateString()}
                        </div>
                      </div>
                      {item.was_authenticated && (
                        <div className="text-xs text-purple-400 mt-1">🔒 Private repos included</div>
                      )}
                      {item.top_languages && item.top_languages.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {item.top_languages.slice(0, 3).map(lang => (
                            <span key={lang} className="text-xs px-2 py-1 bg-gray-700 rounded">{lang}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && isAuthenticated && (
          <div className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">⚙️ Settings</h2>
            <NotificationSettings token={accessToken} />
            
            {/* Saved Profiles Section */}
            <div className="mt-6 bg-gray-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold mb-4">⭐ Saved Profiles</h3>
              {savedProfiles.length === 0 ? (
                <p className="text-gray-400 text-center py-4">
                  No saved profiles yet. Search for a profile and click "Save Profile" to track it!
                </p>
              ) : (
                <div className="space-y-3">
                  {savedProfiles.map(profile => (
                    <div key={profile.id} className="flex justify-between items-center p-3 bg-gray-700/50 rounded-lg">
                      <div>
                        <span className="font-medium text-blue-400">@{profile.username}</span>
                        {profile.notes && <p className="text-xs text-gray-400">{profile.notes}</p>}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setActiveTab('analyze');
                            setUsername(profile.username);
                            handleSubmit(new Event('submit'));
                          }}
                          className="px-3 py-1 bg-blue-600 rounded text-sm hover:bg-blue-700"
                        >
                          Analyze
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App