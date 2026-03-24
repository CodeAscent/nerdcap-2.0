import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { useThemeStore } from './store/themeStore';
import PrivateRoute from './components/PrivateRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Proposals from './pages/Proposals';
import NewProposal from './pages/NewProposal';
import ProposalDetail from './pages/ProposalDetail';
import Recommendations from './pages/Recommendations';
import Predictions from './pages/Predictions';
import ApiHealth from './pages/ApiHealth';
import Users from './pages/Users';
import Settings from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  const { theme } = useThemeStore();

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
      document.documentElement.classList.add('light');
      document.documentElement.classList.remove('dark');
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      document.documentElement.classList.add('dark');
      document.documentElement.classList.remove('light');
    }
  }, [theme]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<Login />} />

          {/* Protected — all roles */}
          <Route element={<PrivateRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/proposals" element={<Proposals />} />
            <Route path="/proposals/new" element={<NewProposal />} />
            <Route path="/proposals/:id" element={<ProposalDetail />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/api-health" element={<ApiHealth />} />
            <Route path="/users" element={<Users />} />
            <Route path="/settings" element={<Settings />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
