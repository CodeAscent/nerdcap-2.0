import { Bell, Moon, Sun } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';
import { useThemeStore } from '../../store/themeStore';

export default function TopBar() {
  const { user } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();

  const roleColors: Record<string, string> = {
    admin: 'badge-red',
    officer: 'badge-blue',
    developer: 'badge-green',
  };

  return (
    <header className="h-14 bg-slate-900 border-b border-slate-800 px-6 flex items-center justify-between shrink-0 transition-colors">
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500">
          Ooumph Agentic AI Ecosystem · Andhra Pradesh
        </span>
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-full transition-all"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className={`${roleColors[user?.role || 'developer']} capitalize`}>
          {user?.role}
        </div>
      </div>
    </header>
  );
}
