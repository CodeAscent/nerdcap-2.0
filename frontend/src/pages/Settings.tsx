import { useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { Settings as SettingsIcon, Database, Server, Key, Globe, Bell } from 'lucide-react';

interface SystemSetting {
  key: string;
  value: string;
  description: string;
  category: string;
}

export default function Settings() {
  const { user: currentUser } = useAuthStore();

  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: async () => {
      const res = await api.get('/api/health');
      return res.data;
    },
  });

  const { data: stubs, isLoading: stubsLoading } = useQuery({
    queryKey: ['stubs-status'],
    queryFn: async () => {
      const res = await api.get('/api/stubs/status');
      return res.data;
    },
  });

  if (currentUser?.role !== 'admin') {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-bold text-slate-300">Access Denied</h2>
        <p className="text-slate-500 mt-2">Only administrators can access system settings.</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <SettingsIcon size={24} />
          System Settings
        </h1>
        <p className="text-sm text-slate-500 mt-1">Configure system parameters and view status</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="section-title flex items-center gap-2">
            <Server size={18} />
            System Health
          </h2>
          <div className="space-y-4 mt-4">
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Version</span>
              <span className="text-slate-200 font-mono">{health?.version || '-'}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Environment</span>
              <span className="text-slate-200 font-mono">{health?.environment || '-'}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Status</span>
              <span className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                {health?.status || 'Unknown'}
              </span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="section-title flex items-center gap-2">
            <Database size={18} />
            Government API Stubs
          </h2>
          <div className="space-y-3 mt-4">
            {stubsLoading ? (
              <div className="animate-pulse space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-4 bg-slate-700 rounded" />
                ))}
              </div>
            ) : (
              Object.entries(stubs?.stubs || {}).map(([name, status]: [string, unknown]) => (
                <div key={name} className="flex justify-between items-center py-2 border-b border-slate-800">
                  <span className="text-slate-400 capitalize">{name.replace(/_/g, ' ')}</span>
                  <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    status === 'active'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {String(status)}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card p-6">
          <h2 className="section-title flex items-center gap-2">
            <Key size={18} />
            API Configuration
          </h2>
          <div className="space-y-4 mt-4">
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">OpenAI API</span>
              <span className="text-green-400">Configured</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Database</span>
              <span className="text-green-400">PostgreSQL + PostGIS</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Redis Cache</span>
              <span className="text-yellow-400">Optional</span>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="section-title flex items-center gap-2">
            <Globe size={18} />
            GIS Settings
          </h2>
          <div className="space-y-4 mt-4">
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">PostGIS Version</span>
              <span className="text-slate-200">3.x</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Coordinate System</span>
              <span className="text-slate-200">EPSG:4326</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-slate-800">
              <span className="text-slate-400">Satellite Analysis</span>
              <span className="text-green-400">Enabled (Simulated)</span>
            </div>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h2 className="section-title flex items-center gap-2">
          <Bell size={18} />
          Notification Settings
        </h2>
        <p className="text-slate-500 mt-2">Configure system notifications and alerts (Coming Soon)</p>
        <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
          <p className="text-sm text-slate-400">
            This section will allow administrators to configure:
          </p>
          <ul className="mt-2 text-sm text-slate-500 space-y-1">
            <li>• Email notifications for proposal status changes</li>
            <li>• Alert thresholds for conflict detection</li>
            <li>• Integration with external notification services</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
