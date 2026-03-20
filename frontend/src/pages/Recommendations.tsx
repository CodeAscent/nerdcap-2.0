import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { recommendationsApi } from '../api/client';
import { Star, Loader2, Map, Users, Lightbulb } from 'lucide-react';

const DISTRICTS = ['Kurnool', 'Anantapur', 'Kadapa', 'Nellore', 'Guntur'];

export default function Recommendations() {
  const [activeTab, setActiveTab] = useState<'sites' | 'developers' | 'insights'>('sites');
  const [projectType, setProjectType] = useState('solar');
  const [capacityMw, setCapacityMw] = useState(100);
  const [selectedDistricts, setSelectedDistricts] = useState<string[]>(['Kurnool', 'Anantapur']);
  const [parcelId, setParcelId] = useState('');

  const { data: sitesData, isFetching: sitesFetching } = useQuery({
    queryKey: ['rec-sites', projectType, capacityMw, selectedDistricts.join()],
    queryFn: () => recommendationsApi.sites(projectType, capacityMw, selectedDistricts),
    enabled: activeTab === 'sites',
  });

  const { data: developersData, isFetching: devFetching } = useQuery({
    queryKey: ['rec-developers', parcelId],
    queryFn: () => recommendationsApi.developers(parcelId),
    enabled: activeTab === 'developers' && parcelId.length === 36,
  });

  const { data: insightsData, isFetching: insightsFetching } = useQuery({
    queryKey: ['policy-insights'],
    queryFn: () => recommendationsApi.policyInsights(),
    enabled: activeTab === 'insights',
  });

  const sites = sitesData?.data || [];
  const developers = developersData?.data || [];
  const insights = insightsData?.data;

  const tabs = [
    { key: 'sites', label: 'Find Sites', icon: Map },
    { key: 'developers', label: 'Find Developers', icon: Users },
    { key: 'insights', label: 'Policy Insights', icon: Lightbulb },
  ] as const;

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h1 className="page-title">Recommendations</h1>
        <p className="text-sm text-slate-500 mt-0.5">AI-powered matchmaking for sites, developers, and policy insights</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-900 border border-slate-800 p-1 rounded-xl w-fit">
        {tabs.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === key
                ? 'bg-nredcap-700 text-white shadow-lg'
                : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Sites tab */}
      {activeTab === 'sites' && (
        <div className="space-y-4">
          <div className="card">
            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <label className="label">Project Type</label>
                <select className="select" value={projectType} onChange={e => setProjectType(e.target.value)}>
                  <option value="solar">Solar</option>
                  <option value="wind">Wind</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              <div>
                <label className="label">Capacity (MW)</label>
                <input type="number" className="input" min={1} value={capacityMw}
                  onChange={e => setCapacityMw(Number(e.target.value))} />
              </div>
              <div>
                <label className="label">Preferred Districts</label>
                <select className="select" multiple value={selectedDistricts}
                  onChange={e => setSelectedDistricts(Array.from(e.target.selectedOptions, o => o.value))}
                  size={3}>
                  {DISTRICTS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
            </div>
          </div>
          {sitesFetching ? (
            <div className="flex items-center justify-center h-32"><Loader2 size={20} className="animate-spin text-slate-600" /></div>
          ) : sites.length === 0 ? (
            <div className="card text-center text-slate-500 py-12">No site recommendations found. Try changing filters.</div>
          ) : (
            <div className="grid gap-3">
              {(sites as Array<{land_parcel_id: string; name: string; district: string; area_ha: number; match_score: number; trust_score_estimate: number; recommendation_reason: string}>).map((site, i) => (
                <div key={site.land_parcel_id} className="card hover:border-nredcap-800 transition-colors">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl font-extrabold text-slate-700 w-8 shrink-0">#{i+1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-slate-200">{site.name}</p>
                      <p className="text-xs text-slate-500 mt-0.5">{site.district} · {site.area_ha} ha</p>
                      <p className="text-xs text-slate-500 mt-2 leading-relaxed">{site.recommendation_reason}</p>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xl font-extrabold text-nredcap-400">{site.match_score.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">match score</div>
                      <div className="text-xs text-slate-400 mt-1">Trust ~{site.trust_score_estimate.toFixed(0)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Developers tab */}
      {activeTab === 'developers' && (
        <div className="space-y-4">
          <div className="card">
            <label className="label">Site / Parcel ID</label>
            <input type="text" className="input" placeholder="Enter land parcel UUID" value={parcelId}
              onChange={e => setParcelId(e.target.value)} />
          </div>
          {devFetching ? (
            <div className="flex items-center justify-center h-32"><Loader2 size={20} className="animate-spin text-slate-600" /></div>
          ) : !parcelId ? (
            <div className="card text-center text-slate-500 py-12">Enter a parcel ID to see developer recommendations</div>
          ) : (
            <div className="grid gap-3">
              {(developers as Array<{developer_id: string; name: string; company: string; trust_score: number; match_score: number; recommendation_reason: string}>).map((dev, i) => (
                <div key={dev.developer_id} className="card">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl font-extrabold text-slate-700 w-8 shrink-0">#{i+1}</span>
                    <div className="flex-1">
                      <p className="font-semibold text-slate-200">{dev.name}</p>
                      <p className="text-xs text-slate-500">{dev.company}</p>
                      <p className="text-xs text-slate-500 mt-2">{dev.recommendation_reason}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-extrabold text-gov-400">{dev.trust_score.toFixed(0)}</div>
                      <div className="text-xs text-slate-500">trust score</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Insights tab */}
      {activeTab === 'insights' && (
        <div className="space-y-4">
          {insightsFetching ? (
            <div className="flex items-center justify-center h-32"><Loader2 size={20} className="animate-spin text-slate-600" /></div>
          ) : insights ? (
            <>
              <div className="card border-gov-800/60 bg-gov-950/20">
                <h3 className="section-title mb-3"><Lightbulb size={15} className="text-amber-400" />Executive Summary</h3>
                <p className="text-sm text-slate-300 leading-relaxed">{insights.summary || 'No summary generated.'}</p>
              </div>
              {insights.key_insights?.length > 0 && (
                <div className="card">
                  <h3 className="section-title mb-3">Key Insights</h3>
                  <ul className="space-y-2">
                    {(insights.key_insights as string[]).map((ins: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                        <Star size={12} className="text-nredcap-400 shrink-0 mt-1" />
                        {ins}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="card text-center text-slate-500 py-12">Generating policy insights…</div>
          )}
        </div>
      )}
    </div>
  );
}
