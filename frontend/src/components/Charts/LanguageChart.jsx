import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#6366F1'];

const LanguageChart = ({ languages }) => {
  if (!languages || languages.length === 0) {
    return (
      <div className="text-center text-gray-400 py-8">
        No language data available
      </div>
    );
  }

  // Transform language data for pie chart
  const data = languages.map((lang, index) => ({
    name: lang,
    value: 100 - (index * 15), // Simulated percentage
    color: COLORS[index % COLORS.length]
  }));

  return (
    <div className="bg-gray-800 rounded-2xl p-6">
      <h3 className="text-xl font-bold mb-4">📊 Language Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LanguageChart;