import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ActivityChart = ({ repos }) => {
  if (!repos || repos.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8">
        No activity data available
      </div>
    );
  }

  // Get top 5 repos by stars
  const data = repos.slice(0, 5).map(repo => ({
    name: repo.name.length > 15 ? repo.name.substring(0, 12) + '...' : repo.name,
    stars: repo.stars,
    forks: repo.forks
  }));

  return (
    <div className="bg-gray-800 rounded-2xl p-6">
      <h3 className="text-xl font-bold mb-4">📈 Repository Activity</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
            labelStyle={{ color: '#fff' }}
          />
          <Bar dataKey="stars" fill="#3B82F6" name="⭐ Stars" />
          <Bar dataKey="forks" fill="#10B981" name="🍴 Forks" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ActivityChart;