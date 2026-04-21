import { userData } from '../data/mockData';
import { Settings, CreditCard, Bell, Shield, LogOut } from 'lucide-react';
import './Profile.css';

const Profile = () => {
  return (
    <div className="page-container">
      <div className="profile-wrapper animate-fade-in">
        <div className="profile-header">
          <img src={userData.avatar} alt={userData.name} className="profile-avatar-large" />
          <div className="profile-info">
            <h1>{userData.name}</h1>
            <p>{userData.email}</p>
            <p>Member since {userData.memberSince}</p>
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
          <button className="btn btn-secondary" style={{ color: '#ef4444' }}>
            <LogOut size={20} />
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
