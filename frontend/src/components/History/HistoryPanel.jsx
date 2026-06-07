import React, { useState, useEffect } from 'react';

const HistoryPanel = ({ token }) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedHistory, setSelectedHistory] = useState(null);

  useEffect(() => {
    if (token) {
      fetchHistory();
    }
  }, [token]);

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/history', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setHistory(data.history);
    } catch (error) {
      console.error('Failed to fetch history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-4">📜 Your Analysis History</h3>
        <div className="text-center py-8 text-gray-400">Loading history...</div>
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="bg-gray-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-4">📜 Your Analysis History</h3>
        <div className="text-center py-8 text-gray-400">
          No analyses yet. Search for GitHub profiles to build your history!
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-2xl p-6">
      <h3 className="text-xl font-bold mb-4">📜 Your Analysis History</h3>
      <div className="space-y-3">
        {history.map((item) => (
          <div
            key={item.id}
            className="border border-gray-700 rounded-lg p-4 hover:bg-gray-700/50 cursor-pointer transition"
            onClick={() => setSelectedHistory(item)}
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
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoryPanel;