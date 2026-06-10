import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import { AuthProvider, useAuthContext } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import NetworkPage from './pages/NetworkPage';
import AuditPage from './pages/AuditPage';
import Chat from './components/Chat';

const ProtectedRoute: React.FC<{ children: React.ReactNode, requiredRole?: string }> = ({ children, requiredRole }) => {
  const { user, loading, hasPermission } = useAuthContext();

  if (loading) return <div className="text-white">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (requiredRole && !hasPermission(requiredRole as any)) return <Navigate to="/dashboard" />;

  return <>{children}</>;
};

const Navigation: React.FC = () => {
  const { user, logout } = useAuthContext();
  
  if (!user) return null;

  return (
    <nav className="bg-gray-800 p-4 text-white flex justify-between items-center h-16 border-b border-gray-700">
      <div className="flex space-x-6">
        <span className="font-bold text-xl text-blue-500">DRISHTI</span>
        <Link to="/dashboard" className="hover:text-blue-400">Dashboard</Link>
        <Link to="/chat" className="hover:text-blue-400">Chat</Link>
        {user.role !== 'constable' && (
          <Link to="/network" className="hover:text-blue-400">Network</Link>
        )}
        {user.role === 'admin' && (
          <Link to="/audit" className="hover:text-blue-400">Audit Logs</Link>
        )}
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-400">{user.email} ({user.role})</span>
        <button onClick={logout} className="px-3 py-1 bg-red-600 rounded hover:bg-red-700 text-sm">Logout</button>
      </div>
    </nav>
  );
};

const AppContent: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 font-sans">
      <Navigation />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
        <Route path="/network" element={<ProtectedRoute requiredRole="inspector"><NetworkPage /></ProtectedRoute>} />
        <Route path="/audit" element={<ProtectedRoute requiredRole="admin"><AuditPage /></ProtectedRoute>} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
};

export default App;
