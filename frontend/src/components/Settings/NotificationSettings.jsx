import React, { useState, useEffect } from 'react';

const NotificationSettings = ({ token }) => {
  const [savedProfiles, setSavedProfiles] = useState([]);
  const [emailStatus, setEmailStatus] = useState(null);

  useEffect(() => {
    if (token) {
      fetchSavedProfiles();
    }
  }, [token]);

  const fetchSavedProfiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/saved', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setSavedProfiles(data.profiles);
    } catch (error) {
      console.error('Failed to fetch saved profiles:', error);
    }
  };

  const toggleNotification = async (profileId, currentNotify) => {
    // This would need a PATCH endpoint - simplified for demo
    alert('Feature: Update notification settings for saved profiles');
  };

  const testNotification = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/notifications/test', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (response.ok) {
        setEmailStatus({ type: 'success', message: 'Test email sent! Check your inbox.' });
        setTimeout(() => setEmailStatus(null), 3000);
      } else {
        throw new Error('Failed to send');
      }
    } catch (error) {
      setEmailStatus({ type: 'error', message: 'Failed to send test email. Check email configuration.' });
      setTimeout(() => setEmailStatus(null), 3000);
    }
  };

  return (
    <div className="bg-gray-800 rounded-2xl p-6">
      <h3 className="text-xl font-bold mb-4">📧 Email Notifications</h3>
      
      {emailStatus && (
        <div className={`mb-4 p-3 rounded-lg ${emailStatus.type === 'success' ? 'bg-green-900/50 text-green-300' : 'bg-red-900/50 text-red-300'}`}>
          {emailStatus.message}
        </div>
      )}
      
      <div className="mb-6">
        <button
          onClick={testNotification}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
        >
          Send Test Email
        </button>
        <p className="text-sm text-gray-400 mt-2">
          Test your email configuration. You'll receive a test notification.
        </p>
      </div>
      
      <div>
        <h4 className="font-semibold mb-3">Saved Profiles</h4>
        {savedProfiles.length === 0 ? (
          <p className="text-gray-400 text-sm">No saved profiles yet. Search and save profiles to get notifications!</p>
        ) : (
          <div className="space-y-3">
            {savedProfiles.map(profile => (
              <div key={profile.id} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <span className="font-medium">@{profile.username}</span>
                  {profile.notes && <p className="text-xs text-gray-400">{profile.notes}</p>}
                </div>
                <label className="flex items-center gap-2">
                  <span className="text-sm text-gray-300">Notify me</span>
                  <input
                    type="checkbox"
                    checked={profile.notify}
                    onChange={() => toggleNotification(profile.id, profile.notify)}
                    className="w-4 h-4"
                  />
                </label>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="mt-6 p-4 bg-blue-900/30 rounded-lg border border-blue-500">
        <h4 className="font-semibold mb-2">📬 Weekly Digest</h4>
        <p className="text-sm text-gray-300">
          Get a weekly email summary of your saved profiles including score changes, new repositories, and achievements.
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Digests are sent every Monday morning.
        </p>
      </div>
    </div>
  );
};

export default NotificationSettings;