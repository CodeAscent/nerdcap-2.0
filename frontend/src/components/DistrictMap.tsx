import { useMemo, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import apDistrictsData from '../data/apDistricts.json';

interface DistrictDataItem {
  district: string;
  total_proposals?: number;
  total_mw?: number;
}

interface DistrictMapProps {
  districtData: DistrictDataItem[];
  onDistrictClick?: (district: string) => void;
  metric?: 'proposals' | 'mw';
}

function getColor(value: number, max: number): string {
  const ratio = max > 0 ? value / max : 0;
  if (ratio === 0) return '#1e293b';
  if (ratio < 0.2) return '#1e3a5f';
  if (ratio < 0.4) return '#2563eb';
  if (ratio < 0.6) return '#3b82f6';
  if (ratio < 0.8) return '#60a5fa';
  return '#93c5fd';
}

export default function DistrictMap({
  districtData,
  onDistrictClick,
  metric = 'proposals',
}: DistrictMapProps) {
  const [hoveredDistrict, setHoveredDistrict] = useState<string | null>(null);

  const dataMap = useMemo(() => {
    const map: Record<string, DistrictDataItem> = {};
    districtData.forEach((item) => {
      map[item.district.toLowerCase()] = item;
    });
    return map;
  }, [districtData]);

  const maxValue = useMemo(() => {
    if (districtData.length === 0) return 1;
    return Math.max(
      ...districtData.map((d) =>
        metric === 'mw' ? d.total_mw || 0 : d.total_proposals || 0
      )
    );
  }, [districtData, metric]);

  const getValue = (district: string): number => {
    const data = dataMap[district.toLowerCase()];
    if (!data) return 0;
    return metric === 'mw' ? data.total_mw || 0 : data.total_proposals || 0;
  };

  const styleFeature = (
    feature: GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>
  ) => {
    const districtName = feature.properties?.district || '';
    const value = getValue(districtName);
    const fillColor = getColor(value, maxValue);
    const isHovered = hoveredDistrict === districtName;

    return {
      fillColor,
      fillOpacity: isHovered ? 0.9 : 0.7,
      color: isHovered ? '#f59e0b' : '#475569',
      weight: isHovered ? 2 : 1,
      opacity: 1,
    };
  };

  const onEachFeature = (
    feature: GeoJSON.Feature<GeoJSON.Geometry, GeoJSON.GeoJsonProperties>,
    layer: L.Layer
  ) => {
    const districtName = feature.properties?.district || '';
    const data = dataMap[districtName.toLowerCase()];

    const tooltipContent = `
      <div style="font-family: system-ui; padding: 4px;">
        <div style="font-weight: 600; color: #f1f5f9; margin-bottom: 4px;">${districtName}</div>
        <div style="color: #94a3b8; font-size: 12px;">
          Proposals: <span style="color: #60a5fa;">${data?.total_proposals || 0}</span>
        </div>
        <div style="color: #94a3b8; font-size: 12px;">
          Total MW: <span style="color: #4ade80;">${data?.total_mw || 0}</span>
        </div>
      </div>
    `;

    layer.bindTooltip(tooltipContent, {
      sticky: true,
      direction: 'top',
      className: 'district-tooltip',
      offset: [0, -10],
    });

    layer.on({
      mouseover: () => {
        setHoveredDistrict(districtName);
        layer.openTooltip();
      },
      mouseout: () => {
        setHoveredDistrict(null);
        layer.closeTooltip();
      },
      click: () => {
        if (onDistrictClick) {
          onDistrictClick(districtName);
        }
      },
    });
  };

  const mapCenter: [number, number] = [15.9, 79.5];
  const mapZoom = 6;

  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden">
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        scrollWheelZoom={false}
        zoomControl={false}
        attributionControl={false}
        className="w-full h-full rounded-xl z-0 bg-slate-900"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          opacity={0.5}
        />
        <GeoJSON
          key={JSON.stringify(districtData) + hoveredDistrict}
          data={apDistrictsData as GeoJSON.GeoJsonObject}
          style={styleFeature}
          onEachFeature={onEachFeature}
        />
      </MapContainer>

      <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur-sm rounded-lg p-3 text-xs">
        <div className="text-slate-400 mb-2 font-medium">
          {metric === 'mw' ? 'Capacity (MW)' : 'Proposals'}
        </div>
        <div className="flex items-center gap-1">
          <div className="w-4 h-3 rounded" style={{ background: '#1e293b' }} />
          <span className="text-slate-500 mr-2">0</span>
          <div className="w-4 h-3 rounded" style={{ background: '#1e3a5f' }} />
          <div className="w-4 h-3 rounded" style={{ background: '#2563eb' }} />
          <div className="w-4 h-3 rounded" style={{ background: '#3b82f6' }} />
          <div className="w-4 h-3 rounded" style={{ background: '#60a5fa' }} />
          <div className="w-4 h-3 rounded" style={{ background: '#93c5fd' }} />
          <span className="text-slate-400 ml-1">{maxValue}</span>
        </div>
      </div>

      {hoveredDistrict && (
        <div className="absolute top-3 left-3 bg-slate-900/90 backdrop-blur-sm rounded-lg px-3 py-2">
          <span className="text-sm font-medium text-slate-200">{hoveredDistrict}</span>
        </div>
      )}
    </div>
  );
}
