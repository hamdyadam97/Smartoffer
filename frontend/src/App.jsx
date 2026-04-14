import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useCBVAuthStore } from './stores/cbvAuthStore';
import Login from './pages/Login';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Students from './pages/Students';
import Courses from './pages/Courses';
import Registrations from './pages/Registrations';
import Payments from './pages/Payments';
import Offers from './pages/Offers';
import Reports from './pages/Reports';
import Branches from './pages/Branches';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, fetchUser, isLoading } = useCBVAuthStore();

  useEffect(() => {
    fetchUser();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="students" element={<Students />} />
          <Route path="courses" element={<Courses />} />
          <Route path="registrations" element={<Registrations />} />
          <Route path="payments" element={<Payments />} />
          <Route path="offers" element={<Offers />} />
          <Route path="reports" element={<Reports />} />
          <Route path="branches" element={<Branches />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
