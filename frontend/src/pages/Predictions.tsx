import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { predictionsApi } from '../api/client';
import { TrendingUp, Zap, Leaf, Map, Loader2 } from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';

const DISTRICTS = ['Kurnool', 'Anantapur', 'Kadapa', 'Nellore', 'Guntur'];

export default function Predictions() {
  const [selectedDistrict, setSelectedDistrict] = useState('Kurnool');

  const { data: gapData, isFetching: gapFetching } = useQuery({
    queryKey: ['demand-supply-gap'],
    queryFn: () => predictionsApi.demandSupplyGap(),
  });

  const { data: gridData, isFetching: gridFetching } = useQuery({
    queryKey: ['grid-congestion', selectedDistrict],
    queryFn: () => predictionsApi.gridCongestion(selectedDistrict),
  });

  const gap = gapData?.data;
  const grid = gridData?.data;

  // Forecast line data
  const gridForecast = grid ? [
    { period: 'Now', utilization: grid.current_utilization_pct },
    { period: '12mo', utilization: grid.forecast_12_months },
    { period: '24mo', utilization: grid.forecast_24_months },
  ] : [];

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h1 className="page-title">Predictions & Forecasting</h1>
        <p className="text-sm text-slate-500 mt-0.5">AI-powered conflict risk, grid congestion, and demand-supply forecasting</p>
      </div>

      {/* Demand-Supply Gap */}
      <div className="card">
        <h3 className="section-title mb-4">
          <Map size={16} className="text-gov-400" />
          Demand-Supply Gap Analysis
        </h3>
        {gapFetching ? (
          <div className="flex items-center justify-center h-20"><Loader2 size={18} className="animate-spin text-slate-600" /></div>
        ) : gap ? (
          <div className="grid sm:grid-cols-2 gap-4">
            {gap.scarcity_risk_districts?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Scarcity Risk Districts</p>
                <div className="space-y-2">
                  {(gap.scarcity_risk_districts as Array<{district: string; risk: string; gap_mw: number}>).map((d) => (
                    <div key={d.district} className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-800">
                      <span className="text-sm text-slate-300">{d.district}</span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500">{d.gap_mw} MW gap</span>
                        <span className={d.risk === 'high' ? 'badge-red' : d.risk === 'medium' ? 'badge-amber' : 'badge-green'}>
                          {d.risk}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {gap.surplus_districts?.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Surplus Districts</p>
                <div className="space-y-2">
                  {(gap.surplus_districts as Array<{district: string; unallocated_potential_mw: number}>).map((d) => (
                    <div key={d.district} className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-800">
                      <span className="text-sm text-slate-300">{d.district}</span>
                      <span className="text-xs text-nredcap-400">{d.unallocated_potential_mw} MW available</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Grid Congestion Forecast */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="section-title">
            <Zap size={16} className="text-amber-400" />
            Grid Congestion Forecast
          </h3>
          <select className="select w-40 text-xs py-1.5" value={selectedDistrict} onChange={e => setSelectedDistrict(e.target.value)}>
            {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        {gridFetching ? (
          <div className="flex items-center justify-center h-48"><Loader2 size={18} className="animate-spin text-slate-600" /></div>
        ) : gridForecast.length > 0 ? (
          <div className="space-y-4">
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={gridForecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 11 }} unit="%" />
                <Tooltip contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '12px', fontSize: 12 }} />
                <Line type="monotone" dataKey="utilization" stroke="#f59e0b" strokeWidth={2} dot={{ fill: '#f59e0b', r: 5 }} name="Utilization %" />
              </LineChart>
            </ResponsiveContainer>
            {grid && (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: 'Current', value: `${grid.current_utilization_pct}%` },
                  { label: '12-mo Forecast', value: `${grid.forecast_12_months}%` },
                  { label: 'Congestion Risk', value: grid.congestion_risk },
                  { label: 'DISCOM', value: 'APSPDCL' },
                ].map(({ label, value }) => (
                  <div key={label} className="bg-slate-800 rounded-xl px-3 py-2.5">
                    <p className="text-xs text-slate-500">{label}</p>
                    <p className="text-sm font-bold text-slate-200 mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : null}
      </div>

      {/* Overall assessment */}
      {gap?.overall_assessment && (
        <div className="card border-gov-800/40 bg-gov-950/20">
          <h3 className="section-title mb-3">
            <TrendingUp size={15} className="text-gov-400" />
            Overall Assessment
          </h3>
          <p className="text-sm text-slate-300 leading-relaxed">{gap.overall_assessment}</p>
          {gap.proactive_land_banking_recommendations?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs text-slate-500 uppercase tracking-wide mb-2">Land Banking Recommendations</p>
              <ul className="space-y-1.5">
                {(gap.proactive_land_banking_recommendations as string[]).map((rec: string, i: number) => (
                  <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                    <Leaf size={11} className="text-nredcap-500 shrink-0 mt-0.5" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
