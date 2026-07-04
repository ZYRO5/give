import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import CampaignsPage from './pages/CampaignsPage';
import DonorsPage from './pages/DonorsPage';
import DonationsPage from './pages/DonationsPage';
import ReportsPage from './pages/ReportsPage';
import { useAuthStore } from './utils/store';
import './styles/index.css';

interface ProtectedRouteProps {
  element: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ element }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  return isAuthenticated ? <>{element}</> : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute element={<Dashboard />} />} />
        <Route path="/campaigns" element={<ProtectedRoute element={<CampaignsPage />} />} />
        <Route path="/donors" element={<ProtectedRoute element={<DonorsPage />} />} />
        <Route path="/donations" element={<ProtectedRoute element={<DonationsPage />} />} />
        <Route path="/reports" element={<ProtectedRoute element={<ReportsPage />} />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
