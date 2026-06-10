import React from 'react';

const AuditPage: React.FC = () => {
  // Mock data for audit logs
  const logs = [
    { id: 1, user: "admin@ksp.gov.in", query: "Show me recent thefts", timestamp: "2023-11-20 10:00:00", ip: "192.168.1.5" },
    { id: 2, user: "inspector@ksp.gov.in", query: "ಮೈಸೂರಿನಲ್ಲಿ ಅಪರಾಧ ಪ್ರಮಾಣ", timestamp: "2023-11-20 10:15:00", ip: "192.168.1.10" }
  ];

  return (
    <div className="p-6 bg-gray-900 min-h-[calc(100vh-64px)] text-white">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">System Audit Logs</h1>
        <button className="px-4 py-2 bg-green-600 rounded hover:bg-green-700">
          Export CSV
        </button>
      </div>
      
      <div className="bg-gray-800 rounded-lg shadow overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-6 py-3">Timestamp</th>
              <th className="px-6 py-3">User</th>
              <th className="px-6 py-3">Query</th>
              <th className="px-6 py-3">IP Address</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id} className="border-t border-gray-700">
                <td className="px-6 py-4">{log.timestamp}</td>
                <td className="px-6 py-4">{log.user}</td>
                <td className="px-6 py-4">{log.query}</td>
                <td className="px-6 py-4">{log.ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditPage;
