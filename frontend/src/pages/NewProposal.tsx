import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { proposalsApi, parcelsApi, developersApi } from '../api/client';
import { useAuthStore } from '../store/authStore';
import { MapPin, Send, Loader2, Info } from 'lucide-react';

const DISTRICTS = [
  'Kurnool', 'Anantapur', 'Kadapa', 'Nellore', 'Guntur',
  'Krishna', 'West Godavari', 'East Godavari', 'Visakhapatnam',
  'Vizianagaram', 'Srikakulam', 'Prakasam', 'Chittoor',
];

export default function NewProposal() {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  const location = useLocation();
  const state = location.state as { projectType?: 'solar' | 'wind' | 'hybrid'; capacityMw?: number; district?: string; developerId?: string } | null;

  const [projectType, setProjectType] = useState<'solar' | 'wind' | 'hybrid'>(state?.projectType || 'solar');
  const [capacityMw, setCapacityMw] = useState(state?.capacityMw || 100);
  const [district, setDistrict] = useState(state?.district || 'Kurnool');
  const [boundaryJson, setBoundaryJson] = useState('');
  const [error, setError] = useState('');
  const [selectedDeveloperId, setSelectedDeveloperId] = useState(state?.developerId || '');

  // Fetch developers to populate selector
  const { data: parcelsData } = useQuery({
    queryKey: ['land-parcels', district],
    queryFn: () => parcelsApi.list(district),
  });

  // Fetch developers
  const { data: developersData } = useQuery({
    queryKey: ['developers'],
    queryFn: () => developersApi.list(),
  });
  const developers = developersData?.data || [];
  const defaultDeveloperId = developers.find((d: any) => d.email === user?.email)?.id || developers[0]?.id;

  const parcels = parcelsData?.data || [];

  // Default sample boundary for Kurnool (so demo works without drawing)
  const sampleBoundaries: Record<string, object> = {
    Kurnool: { type: 'Polygon', coordinates: [[[78.47, 15.48], [78.52, 15.48], [78.52, 15.45], [78.47, 15.45], [78.47, 15.48]]] },
    Anantapur: { type: 'Polygon', coordinates: [[[77.72, 14.42], [77.77, 14.42], [77.77, 14.38], [77.72, 14.38], [77.72, 14.42]]] },
    Kadapa: { type: 'Polygon', coordinates: [[[79.01, 14.72], [79.06, 14.72], [79.06, 14.68], [79.01, 14.68], [79.01, 14.72]]] },
  };

  const createMutation = useMutation({
    mutationFn: (payload: object) => proposalsApi.create(payload as Record<string, unknown>),
    onSuccess: (res) => {
      navigate(`/proposals/${res.data.id}`);
    },
    onError: (err: unknown) => {
      const e = err as { response?: { data?: { detail?: string } } };
      setError(e?.response?.data?.detail || 'Failed to create proposal');
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    let boundary: object;
    try {
      boundary = boundaryJson ? JSON.parse(boundaryJson) : (sampleBoundaries[district] || sampleBoundaries['Kurnool']);
    } catch {
      setError('Invalid GeoJSON boundary. Please check the format.');
      return;
    }

    // Use selected, or default based on role
    const finalDeveloperId = selectedDeveloperId || defaultDeveloperId;
    if (!finalDeveloperId) {
      setError('Wait for developers to load or register a developer account.');
      return;
    }

    createMutation.mutate({
      developer_id: finalDeveloperId,
      project_type: projectType,
      capacity_mw: capacityMw,
      district,
      boundary_geojson: boundary,
    });
  };

  // Compute area estimate
  const areaNeeded = projectType === 'solar' ? capacityMw * 2 : capacityMw * 4;

  return (
    <div className="max-w-2xl space-y-6 animate-fade-up">
      <div>
        <h1 className="page-title">New Proposal</h1>
        <p className="text-sm text-slate-500 mt-0.5">Submit a renewable energy land allocation proposal for AI analysis</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Project Type */}
        <div className="card">
          <h3 className="section-title mb-4">Project Details</h3>
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Project Type</label>
              <div className="flex gap-2">
                {(['solar', 'wind', 'hybrid'] as const).map(type => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setProjectType(type)}
                    className={`flex-1 py-2 rounded-xl text-sm font-semibold transition-all border ${
                      projectType === type
                        ? 'bg-nredcap-700 border-nredcap-500 text-white'
                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {type === 'solar' ? '☀️' : type === 'wind' ? '💨' : '⚡'} {type.charAt(0).toUpperCase() + type.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="label">Capacity (MW)</label>
              <input
                type="number"
                className="input"
                min={1}
                max={5000}
                value={capacityMw}
                onChange={e => setCapacityMw(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <div className="mt-4">
            <label className="label">Target District</label>
            <select className="select" value={district} onChange={e => setDistrict(e.target.value)}>
              {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          
          <div className="mt-4">
            <label className="label">Developer</label>
            <select className="select" value={selectedDeveloperId || defaultDeveloperId || ''} onChange={e => setSelectedDeveloperId(e.target.value)}>
              {developers.map((d: any) => <option key={d.id} value={d.id}>{d.company} ({d.name})</option>)}
            </select>
            {user?.role === 'developer' && <p className="text-xs text-slate-500 mt-1">Found matching developer profile for your email.</p>}
          </div>

          {/* Area estimate hint */}
          <div className="flex items-center gap-2 mt-3 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700">
            <Info size={12} className="text-blue-400 shrink-0" />
            <p className="text-xs text-slate-400">
              Estimated land required: <span className="text-slate-200 font-semibold">~{areaNeeded} hectares</span>
              {' '}({capacityMw} MW × {projectType === 'solar' ? '2' : '4'} ha/MW for {projectType})
            </p>
          </div>
        </div>

        {/* Available parcels */}
        {parcels.length > 0 && (
          <div className="card">
            <h3 className="section-title mb-3">
              <MapPin size={15} className="text-nredcap-400" />
              Available Parcels in {district}
            </h3>
            <div className="grid gap-2">
              {(parcels as Array<{id: string; name: string; area_ha: number; ownership_type: string; land_use_type?: string}>).slice(0, 4).map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setBoundaryJson(JSON.stringify(sampleBoundaries[district] || sampleBoundaries['Kurnool']))}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-nredcap-700 transition-all text-left"
                >
                  <MapPin size={13} className="text-nredcap-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-200 truncate">{p.name}</p>
                    <p className="text-xs text-slate-500">{p.area_ha} ha · {p.ownership_type} · {p.land_use_type || 'barren'}</p>
                  </div>
                  <span className={p.area_ha >= areaNeeded ? 'badge-green' : 'badge-amber'}>
                    {p.area_ha >= areaNeeded ? '✓ Sufficient' : 'Small'}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Boundary */}
        <div className="card">
          <h3 className="section-title mb-4">
            <MapPin size={15} className="text-gov-400" />
            Boundary GeoJSON
          </h3>
          <p className="text-xs text-slate-500 mb-3">
            Paste a GeoJSON Polygon for the proposed project boundary. Leave empty to use a sample boundary for the selected district.
          </p>
          <textarea
            className="input min-h-[120px] font-mono text-xs resize-none"
            placeholder={`{"type": "Polygon", "coordinates": [[[lon, lat], ...]]}`}
            value={boundaryJson}
            onChange={e => setBoundaryJson(e.target.value)}
          />
          {!boundaryJson && (
            <p className="text-xs text-nredcap-500 mt-2">
              ✓ Will use sample boundary for {district} district
            </p>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-2 bg-red-900/30 border border-red-700/50 rounded-xl px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {/* Submit */}
        <button type="submit" className="btn-primary w-full justify-center" disabled={createMutation.isPending}>
          {createMutation.isPending ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          Submit Proposal for AI Analysis
        </button>
      </form>
    </div>
  );
}
