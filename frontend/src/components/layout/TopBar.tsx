import { Bell, Sun } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export default function TopBar() {
  const { user } = useAuthStore();

  const roleColors: Record<string, string> = {
    admin:     'badge-red',
    officer:   'badge-blue',
    developer: 'badge-green',
  };

  return (
    <header className="h-14 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between shrink-0">
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500">
          Ooumph Agentic AI Ecosystem · Andhra Pradesh
        </span>
      </div>
      <div className="flex items-center gap-3">
        <button className="btn-ghost p-2">
          <Bell size={16} />
        </button>
        <div className={`${roleColors[user?.role || 'developer']} capitalize`}>
          {user?.role}
        </div>
      </div>
    </header>
  );
}
