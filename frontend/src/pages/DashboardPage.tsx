import React, { useEffect, useState } from 'react';
import { predictionsAPI } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const DashboardPage: React.FC = () => {
  const [forecast, setForecast] = useState<any[]>([]);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [explanation, setExplanation] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch real stats from Supabase
        const sRes = await predictionsAPI.getStats();
        setStats(sRes);

        const fRes = await predictionsAPI.getForecast('Bengaluru Urban', 30);
        setForecast(fRes.forecast || []);
        
        const hRes = await predictionsAPI.getHotspots('Theft');
        setHotspots(hRes.hotspots || []);
        setExplanation(hRes.explanation || null);
        
        const aRes = await predictionsAPI.getAlerts();
        setAlerts(aRes.alerts || []);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white">
      <h1 className="text-3xl font-bold mb-2">CrimeMind AI Dashboard</h1>
      <p className="text-gray-400 mb-6">Intelligent Crime Investigation Copilot — Karnataka State Police</p>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 p-4 rounded-lg shadow border-l-4 border-blue-500">
          <h3 className="text-gray-400 text-sm">Total Crimes</h3>
          <p className="text-2xl font-bold">{stats.total_crimes?.toLocaleString() || '—'}</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow border-l-4 border-green-500">
          <h3 className="text-gray-400 text-sm">Resolution Rate</h3>
          <p className="text-2xl font-bold text-green-500">{stats.resolution_rate || '—'}%</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow border-l-4 border-yellow-500">
          <h3 className="text-gray-400 text-sm">Active Cases</h3>
          <p className="text-2xl font-bold text-yellow-500">{stats.active_cases?.toLocaleString() || '—'}</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow border-l-4 border-red-500">
          <h3 className="text-gray-400 text-sm">Repeat Offenders</h3>
          <p className="text-2xl font-bold text-red-500">{stats.repeat_offenders || '—'}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Crime Trend Chart */}
        <div className="lg:col-span-2 bg-gray-800 p-4 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Crime Trends & Forecast (30 Days)</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer>
              <LineChart data={forecast}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="ds" stroke="#9CA3AF" tickFormatter={(v) => v ? new Date(v).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : ''} />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                <Line type="monotone" dataKey="yhat" stroke="#3B82F6" strokeWidth={2} dot={false} name="Predicted" />
                <Line type="monotone" dataKey="yhat_upper" stroke="#EF4444" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Upper Bound" />
                <Line type="monotone" dataKey="yhat_lower" stroke="#10B981" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Lower Bound" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hotspots & Alerts */}
        <div className="space-y-6">
          <div className="bg-gray-800 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-red-400">⚠️ Active Alerts</h2>
            <ul className="space-y-3">
              {alerts.slice(0, 5).map((alert, idx) => (
                <li key={idx} className={`p-3 rounded ${alert.severity === 'high' ? 'bg-red-900/50 border-l-4 border-red-500' : alert.severity === 'medium' ? 'bg-yellow-900/50 border-l-4 border-yellow-500' : 'bg-gray-700 border-l-4 border-gray-500'}`}>
                  <span className="font-bold">{alert.district}:</span> {alert.message}
                </li>
              ))}
              {alerts.length === 0 && <li className="text-gray-500">No active alerts</li>}
            </ul>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">🔥 Top Hotspots (Theft)</h2>
            <ul className="space-y-2">
              {hotspots.slice(0, 5).map((h, idx) => (
                <li key={idx} className="flex justify-between items-center bg-gray-700 p-2 rounded">
                  <div>
                    <span className="font-medium">{h.station}</span>
                    <span className="text-xs text-gray-400 ml-2">{h.district}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs px-2 py-1 rounded ${h.risk === 'HIGH' ? 'bg-red-600' : h.risk === 'MEDIUM' ? 'bg-yellow-600' : 'bg-green-600'}`}>
                      {h.risk}
                    </span>
                    <span className="bg-gray-600 px-2 py-1 rounded text-sm">{h.count}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Explainable AI Section */}
          {explanation && (
            <div className="bg-gray-800 p-4 rounded-lg shadow border border-blue-500/30">
              <h2 className="text-lg font-semibold mb-3 text-blue-400">🧠 AI Explanation</h2>
              <div className="space-y-2 text-sm">
                <p>Trend: <span className={`font-bold ${explanation.trend === 'increasing' ? 'text-red-400' : 'text-green-400'}`}>{explanation.trend?.toUpperCase()}</span></p>
                <p>Change: <span className="font-bold">{explanation.change_percent}</span></p>
                <ul className="space-y-1 mt-2">
                  {explanation.reasons?.map((r: string, i: number) => (
                    <li key={i} className="text-gray-300 flex items-start">
                      <span className="text-blue-400 mr-2">•</span> {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
