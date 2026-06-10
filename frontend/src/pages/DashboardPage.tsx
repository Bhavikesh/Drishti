import React, { useEffect, useState } from 'react';
import { predictionsAPI } from '../services/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const DashboardPage: React.FC = () => {
  const [forecast, setForecast] = useState<any[]>([]);
  const [hotspots, setHotspots] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fRes = await predictionsAPI.getForecast('Bengaluru', 30);
        setForecast(fRes.forecast || []);
        
        const hRes = await predictionsAPI.getHotspots('theft');
        setHotspots(hRes.hotspots || []);
        
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
      <h1 className="text-3xl font-bold mb-6">Drishti Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-gray-400">Total Crimes</h3>
          <p className="text-2xl font-bold">12,345</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-gray-400">Resolution Rate</h3>
          <p className="text-2xl font-bold text-green-500">68%</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-gray-400">Active Cases</h3>
          <p className="text-2xl font-bold text-yellow-500">3,942</p>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg shadow">
          <h3 className="text-gray-400">Officers Online</h3>
          <p className="text-2xl font-bold text-blue-500">142</p>
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
                <XAxis dataKey="ds" stroke="#9CA3AF" tickFormatter={(v) => v ? new Date(v).toLocaleDateString() : ''} />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Line type="monotone" dataKey="yhat" stroke="#3B82F6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Hotspots & Alerts */}
        <div className="space-y-6">
          <div className="bg-gray-800 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4 text-red-400">Anomaly Alerts</h2>
            <ul className="space-y-3">
              {alerts.map((alert, idx) => (
                <li key={idx} className={`p-3 rounded ${alert.severity === 'high' ? 'bg-red-900/50 border-l-4 border-red-500' : 'bg-yellow-900/50 border-l-4 border-yellow-500'}`}>
                  <span className="font-bold">{alert.district}:</span> {alert.message}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="bg-gray-800 p-4 rounded-lg shadow">
            <h2 className="text-xl font-semibold mb-4">Top Hotspots (Theft)</h2>
            <ul className="space-y-2">
              {hotspots.map((h, idx) => (
                <li key={idx} className="flex justify-between items-center bg-gray-700 p-2 rounded">
                  <span>{h.station}</span>
                  <span className="bg-gray-600 px-2 py-1 rounded text-sm">{h.count} cases</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
