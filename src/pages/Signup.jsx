import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { RecommendationContext } from '../RecommendationContext';
import './Auth.css';

const Signup = () => {
  const navigate = useNavigate();
  const { register, signup, authLoading } = useContext(RecommendationContext);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
    setError('');
    setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      let result;
      // For signup, we can use either register (with password) or signup (without password) depending on API definition
      if (formData.password) {
        result = await register(formData.name, formData.email, formData.password);
      } else {
        result = await signup(formData.email, formData.name);
      }

      if (result.success) {
        setSuccess('Account created successfully!');
        setTimeout(() => {
          navigate('/');
        }, 1500);
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
    }
  };

  return (
    <div className="page-container auth-container animate-fade-in">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Create Account</h1>
          <p>Sign up to discover new movies</p>
        </div>

        {error && (
          <div className="auth-message auth-error">
            {error}
          </div>
        )}

        {success && (
          <div className="auth-message auth-success">
            {success}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Full Name</label>
            <input
              type="text"
              id="name"
              name="name"
              className="auth-input"
              placeholder="John Doe"
              value={formData.name}
              onChange={handleChange}
              required
              disabled={authLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              className="auth-input"
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              required
              disabled={authLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              className="auth-input"
              placeholder="••••••••"
              value={formData.password}
              onChange={handleChange}
              disabled={authLoading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary auth-submit"
            disabled={authLoading}
          >
            {authLoading ? 'Please wait...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Already have an account? <Link to="/login" className="auth-link">Log In</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Signup;
