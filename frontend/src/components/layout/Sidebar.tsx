import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, FileText, Plus, Map, Star,
  Lightbulb, TrendingUp, Server, LogOut, Wind, Leaf
} from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { clsx } from 'clsx';

const navItems = [
  { to: '/dashboard',       icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/proposals',       icon: FileText,        label: 'Proposals' },
  { to: '/proposals/new',   icon: Plus,            label: 'New Proposal' },
  { to: '/recommendations', icon: Star,            label: 'Recommendations' },
  { to: '/predictions',     icon: TrendingUp,      label: 'Predictions' },
  { to: '/api-health',      icon: Server,          label: 'API Status' },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-nredcap-500 to-gov-600 flex items-center justify-center shadow-lg">
            <Leaf size={18} className="text-white" />
          </div>
          <div>
            <p className="font-bold text-sm text-slate-100 leading-tight">NREDCAP</p>
            <p className="text-[10px] text-slate-500 leading-tight">AI Land Allocation</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx('nav-link', isActive && 'active')
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* User + logout */}
      <div className="px-3 py-4 border-t border-slate-800 space-y-2">
        <div className="card-glass px-3 py-2.5">
          <p className="text-xs font-semibold text-slate-300 truncate">{user?.full_name || user?.email}</p>
          <p className="text-[10px] text-slate-500 capitalize">{user?.role} · {user?.department || 'NREDCAP'}</p>
        </div>
        <button onClick={handleLogout} className="btn-ghost w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-900/20">
          <LogOut size={14} />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
