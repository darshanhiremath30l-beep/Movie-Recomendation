import { useContext } from 'react';
import { RecommendationContext } from '../RecommendationContext';
import { Settings, CreditCard, Bell, Shield, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const Profile = () => {
  const { user, isAuthenticated, logout } = useContext(RecommendationContext);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="page-container" style={{ textAlign: 'center', paddingTop: '100px' }}>
        <h2>My Profile</h2>
        <p style={{ color: 'var(--text-muted)', marginTop: '20px' }}>Log in to view your profile settings.</p>
        <button className="btn btn-primary" style={{ marginTop: '20px' }} onClick={() => navigate('/login')}>
          Go to Login
        </button>
      </div>
    );
  }

  // Generate a dynamic avatar based on the user's name using DiceBear APIs
  const avatarUrl = user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(user.name)}&backgroundColor=1b1b29`;

  return (
    <div className="page-container">
      <div className="profile-wrapper animate-fade-in">
        <div className="profile-header">
          <img src={avatarUrl} alt={user.name} className="profile-avatar-large" style={{ borderRadius: '50%', background: '#1b1b29' }} />
          <div className="profile-info">
            <h1>{user.name}</h1>
            <p>{user.email}</p>
            <p>Member since {new Date().getFullYear()}</p>
          </div>
        </div>

        <h2 style={{ marginBottom: '24px' }}>Account Settings</h2>
        
        <div className="settings-grid">
          <div className="settings-card">
            <h3><Settings size={22} className="text-gradient" /> Profile Details</h3>
            <p>Update your personal information and avatar.</p>
          </div>
          <div className="settings-card">
            <h3><CreditCard size={22} className="text-gradient" /> Subscription</h3>
            <p>Manage your Premium plan and billing history.</p>
          </div>
          <div className="settings-card">
            <h3><Bell size={22} className="text-gradient" /> Notifications</h3>
            <p>Choose what updates you want to receive.</p>
          </div>
          <div className="settings-card">
            <h3><Shield size={22} className="text-gradient" /> Privacy & Security</h3>
            <p>Change password and privacy settings.</p>
          </div>
        </div>

        <div style={{ marginTop: '40px', textAlign: 'center' }}>
          <button className="btn btn-secondary" style={{ color: '#ef4444' }} onClick={handleLogout}>
            <LogOut size={20} />
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
