import { useAuthContext } from '../contexts/AuthContext';
import { authAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export const useAuth = () => {
  const { user, loading, login, logout, hasPermission } = useAuthContext();
  const navigate = useNavigate();

  const handleLogin = async (email: string, password: string) => {
    try {
      const { access_token } = await authAPI.login(email, password);
      localStorage.setItem('token', access_token);
      const userData = await authAPI.me();
      login(access_token, userData);
      navigate('/dashboard');
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return {
    user,
    loading,
    login: handleLogin,
    logout: handleLogout,
    hasPermission,
    getCurrentUser: () => user
  };
};
