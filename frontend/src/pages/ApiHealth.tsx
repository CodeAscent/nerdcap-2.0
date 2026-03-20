import { useQuery } from '@tanstack/react-query';
import { systemApi } from '../api/client';
import { CheckCircle2, XCircle, Server, RefreshCw, Info } from 'lucide-react';

export default function ApiHealth() {
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['stubs-status'],
    queryFn: () => systemApi.stubsStatus(),
    refetchInterval: 10000,
  });

  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: () => systemApi.health(),
  });

  const stubs = data?.data || {};
  const health = healthData?.data;

  return (
    <div className="space-y-6 animate-fade-up">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Government API Status</h1>
          <p className="text-sm text-slate-500 mt-0.5">All 6 departmental API stubs — replace with real keys when available</p>
        </div>
        <button onClick={() => refetch()} className="btn-secondary" disabled={isFetching}>
          <RefreshCw size={14} className={isFetching ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Backend health */}
      {health && (
        <div className="card flex items-center gap-4">
          <Server size={18} className="text-nredcap-400" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-slate-200">Backend API</p>
            <p className="text-xs text-slate-500">{health.app} v{health.version} · {health.environment}</p>
          </div>
          <span className="badge-green">
            <CheckCircle2 size={12} />
            Healthy
          </span>
        </div>
      )}

      {/* Stub cards */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => <div key={i} className="h-36 bg-slate-800 rounded-2xl animate-pulse" />)}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(stubs).map(([key, dept]: [string, unknown]) => {
            const d = dept as { name: string; description: string; is_live: boolean; status: string };
            return (
              <div key={key} className="card hover:border-slate-700 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-slate-800 flex items-center justify-center">
                    <Server size={16} className={d.is_live ? 'text-nredcap-400' : 'text-amber-400'} />
                  </div>
                  <span className={d.is_live ? 'badge-green' : 'badge-amber'}>
                    {d.is_live ? (
                      <><CheckCircle2 size={10} /> LIVE</>
                    ) : (
                      <><XCircle size={10} /> STUB</>
                    )}
                  </span>
                </div>
                <h3 className="font-semibold text-sm text-slate-200 mb-1">{d.name}</h3>
                <p className="text-xs text-slate-500 leading-relaxed">{d.description}</p>
                {!d.is_live && (
                  <div className="flex items-start gap-1.5 mt-3 pt-3 border-t border-slate-800">
                    <Info size={11} className="text-amber-500 shrink-0 mt-0.5" />
                    <p className="text-[10px] text-amber-600">Running in stub mode — returns realistic mock data. Replace with real API key to go live.</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Legend */}
      <div className="card-glass">
        <p className="text-xs text-slate-500">
          <span className="font-semibold text-slate-400">Note: </span>
          All stubs return deterministic mock data seeded from the parcel/proposal ID. 
          Each stub is designed for a drop-in replacement — set <code className="text-nredcap-400 bg-slate-800 px-1 py-0.5 rounded">USE_STUBS=false</code> in <code className="text-nredcap-400 bg-slate-800 px-1 py-0.5 rounded">.env</code> and provide the real API endpoints when government keys become available.
        </p>
      </div>
    </div>
  );
}
