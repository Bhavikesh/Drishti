import React from 'react';

/* ── Rich mock audit data that makes the system feel alive ── */
const AUDIT_LOGS = [
  { id: 1, user: 'admin@ksp.gov.in', role: 'Admin', action: 'Network Analysis', query: 'Show burglary gang active in Mysuru', timestamp: '2026-06-13 10:22:14', ip: '10.0.12.5', status: 'success' },
  { id: 2, user: 'admin@ksp.gov.in', role: 'Admin', action: 'PDF Export', query: 'Investigation Report Generated', timestamp: '2026-06-13 10:31:07', ip: '10.0.12.5', status: 'success' },
  { id: 3, user: 'inspector@ksp.gov.in', role: 'Inspector', action: 'Hotspot Detection', query: 'Identify emerging crime hotspots', timestamp: '2026-06-13 11:10:33', ip: '10.0.14.22', status: 'success' },
  { id: 4, user: 'inspector@ksp.gov.in', role: 'Inspector', action: 'Chat Query', query: 'Who are the top repeat offenders?', timestamp: '2026-06-13 11:45:19', ip: '10.0.14.22', status: 'success' },
  { id: 5, user: 'sp@ksp.gov.in', role: 'SP', action: 'Network Analysis', query: 'Drug trafficking network in Bengaluru', timestamp: '2026-06-13 12:05:41', ip: '10.0.10.1', status: 'success' },
  { id: 6, user: 'constable@ksp.gov.in', role: 'Constable', action: 'Dashboard View', query: 'Accessed Crime Dashboard', timestamp: '2026-06-13 12:30:55', ip: '10.0.16.88', status: 'success' },
  { id: 7, user: 'inspector@ksp.gov.in', role: 'Inspector', action: 'Chat Query', query: 'ಮೈಸೂರಿನಲ್ಲಿ ಅಪರಾಧ ಪ್ರಮಾಣ', timestamp: '2026-06-13 13:12:08', ip: '10.0.14.22', status: 'success' },
  { id: 8, user: 'unknown@test.com', role: 'Unknown', action: 'Login Attempt', query: 'Failed authentication', timestamp: '2026-06-13 14:01:22', ip: '203.94.55.12', status: 'failed' },
  { id: 9, user: 'admin@ksp.gov.in', role: 'Admin', action: 'Suspect Analysis', query: 'Shivaraj Kumbar network analysis', timestamp: '2026-06-13 14:30:11', ip: '10.0.12.5', status: 'success' },
  { id: 10, user: 'sp@ksp.gov.in', role: 'SP', action: 'Prediction Model', query: 'Crime forecast for Bengaluru Urban', timestamp: '2026-06-13 15:05:33', ip: '10.0.10.1', status: 'success' },
];

const STATS = {
  total_queries: 54,
  reports_generated: 18,
  predictions_run: 26,
  network_analyses: 12,
  failed_logins: 2,
  unauthorized_attempts: 0,
};

const USER_SUMMARY = [
  { user: 'admin@ksp.gov.in', role: 'Admin', queries: 42, last_active: '15:05' },
  { user: 'inspector@ksp.gov.in', role: 'Inspector', queries: 28, last_active: '13:12' },
  { user: 'sp@ksp.gov.in', role: 'SP', queries: 15, last_active: '15:05' },
  { user: 'constable@ksp.gov.in', role: 'Constable', queries: 8, last_active: '12:30' },
];

const AuditPage: React.FC = () => {

  const handleExportAuditPDF = () => {
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });

    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Drishti AI Audit Report</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Inter', sans-serif; color: #1a1a2e; line-height: 1.6; }
    .page { max-width: 800px; margin: 0 auto; padding: 40px; }
    .header { border-bottom: 3px solid #3498db; padding-bottom: 20px; margin-bottom: 30px; display: flex; justify-content: space-between; }
    .header h1 { font-size: 24px; font-weight: 800; }
    .header h2 { font-size: 13px; color: #3498db; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
    .meta { text-align: right; font-size: 12px; color: #666; }
    .meta strong { color: #1a1a2e; }
    .classification { background: #3498db; color: #fff; text-align: center; padding: 6px; font-size: 11px; font-weight: 800; letter-spacing: 3px; margin-bottom: 30px; border-radius: 4px; }
    .section { margin-bottom: 24px; }
    .section-title { font-size: 12px; font-weight: 800; color: #3498db; text-transform: uppercase; letter-spacing: 2px; border-bottom: 1px solid #eee; padding-bottom: 6px; margin-bottom: 12px; }
    table { width: 100%; border-collapse: collapse; font-size: 11px; margin: 10px 0; }
    th { background: #1a1a2e; color: #fff; padding: 8px 10px; text-align: left; font-size: 9px; text-transform: uppercase; letter-spacing: 1px; }
    td { padding: 8px 10px; border-bottom: 1px solid #eee; }
    tr:nth-child(even) { background: #f8f9fa; }
    .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 12px 0; }
    .stat-card { background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 6px; padding: 12px; text-align: center; }
    .stat-card .label { font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
    .stat-card .value { font-size: 24px; font-weight: 800; color: #1a1a2e; }
    .alert-box { background: #fff5f5; border: 1px solid rgba(231,76,60,0.2); border-radius: 6px; padding: 14px; margin: 10px 0; }
    .success { color: #27ae60; font-weight: 700; }
    .failed { color: #e74c3c; font-weight: 700; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #3498db; font-size: 10px; color: #888; display: flex; justify-content: space-between; }
    .badge { background: #1a1a2e; color: #fff; padding: 4px 12px; border-radius: 4px; font-size: 9px; font-weight: 700; letter-spacing: 1px; }
    @media print { body { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
  </style>
</head>
<body>
  <div class="page">
    <div class="header">
      <div>
        <h1>🔍 DRISHTI</h1>
        <h2>System Audit & Compliance Report</h2>
        <p style="font-size:11px;color:#888">Karnataka State Police — Governance Division</p>
      </div>
      <div class="meta">
        <div><strong>Period:</strong> June 1 – June 13, 2026</div>
        <div><strong>Generated:</strong> ${dateStr}</div>
        <div><strong>Generated By:</strong> System Administrator</div>
      </div>
    </div>

    <div class="classification">INTERNAL — GOVERNANCE & ACCOUNTABILITY</div>

    <div class="section">
      <div class="section-title">AI Usage Statistics</div>
      <div class="stat-grid">
        <div class="stat-card"><div class="label">Total Queries</div><div class="value">${STATS.total_queries}</div></div>
        <div class="stat-card"><div class="label">Reports Generated</div><div class="value">${STATS.reports_generated}</div></div>
        <div class="stat-card"><div class="label">Predictions Run</div><div class="value">${STATS.predictions_run}</div></div>
        <div class="stat-card"><div class="label">Network Analyses</div><div class="value">${STATS.network_analyses}</div></div>
        <div class="stat-card"><div class="label">Failed Logins</div><div class="value" style="color:#e74c3c">${STATS.failed_logins}</div></div>
        <div class="stat-card"><div class="label">Unauthorized Access</div><div class="value" style="color:#27ae60">${STATS.unauthorized_attempts}</div></div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">User Activity Summary</div>
      <table>
        <thead><tr><th>User</th><th>Role</th><th>Queries</th><th>Last Active</th></tr></thead>
        <tbody>
          ${USER_SUMMARY.map(u => `<tr><td>${u.user}</td><td>${u.role}</td><td><strong>${u.queries}</strong></td><td>${u.last_active}</td></tr>`).join('')}
        </tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Investigation Activity Log</div>
      <table>
        <thead><tr><th>Timestamp</th><th>User</th><th>Action</th><th>Query</th><th>Status</th></tr></thead>
        <tbody>
          ${AUDIT_LOGS.map(l => `<tr><td>${l.timestamp}</td><td>${l.user}</td><td>${l.action}</td><td>${l.query}</td><td class="${l.status === 'success' ? 'success' : 'failed'}">${l.status.toUpperCase()}</td></tr>`).join('')}
        </tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Security Events</div>
      <div class="alert-box">
        <p><strong>Failed Login Attempts:</strong> <span style="color:#e74c3c;font-weight:800">2</span> — from IP 203.94.55.12 (flagged for monitoring)</p>
        <p style="margin-top:6px"><strong>Unauthorized Access Attempts:</strong> <span style="color:#27ae60;font-weight:800">0</span></p>
        <p style="margin-top:6px"><strong>Sensitive Queries Logged:</strong> Murder Network Analysis, Drug Trafficking Network, Cybercrime Investigation</p>
      </div>
    </div>

    <div class="section">
      <div class="section-title">System Accountability Statement</div>
      <p style="font-size:12px;color:#555;line-height:1.8">
        Every AI-generated recommendation within the Drishti platform includes confidence scores and is fully traceable
        to the originating query, user, and timestamp. All investigation outputs are logged and available for judicial review.
        The system maintains complete chain-of-custody documentation for all AI-assisted analyses.
      </p>
    </div>

    <div class="footer">
      <div>
        <div>Generated by <strong>Drishti AI</strong> — Karnataka State Police Audit Framework</div>
        <div style="margin-top:4px">This report is auto-generated. All activities are logged and traceable.</div>
      </div>
      <div class="badge">GOVERNANCE REPORT</div>
    </div>
  </div>
  <script>window.onload = () => window.print();</script>
</body>
</html>`;

    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(htmlContent);
      printWindow.document.close();
    }
  };

  return (
    <div className="p-6 bg-gray-900 min-h-[calc(100vh-64px)] text-white">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">System Audit Logs</h1>
          <p className="text-gray-400 text-sm mt-1">Governance, Accountability & Compliance Monitoring</p>
        </div>
        <button 
          onClick={handleExportAuditPDF}
          className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 flex items-center gap-2 font-semibold"
        >
          📄 Export Audit Report
        </button>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-6">
        {[
          { label: 'Total Queries', value: STATS.total_queries, color: 'blue' },
          { label: 'Reports Generated', value: STATS.reports_generated, color: 'green' },
          { label: 'Predictions Run', value: STATS.predictions_run, color: 'purple' },
          { label: 'Network Analyses', value: STATS.network_analyses, color: 'yellow' },
          { label: 'Failed Logins', value: STATS.failed_logins, color: 'red' },
          { label: 'Unauthorized', value: STATS.unauthorized_attempts, color: 'green' },
        ].map((s, i) => (
          <div key={i} className={`bg-gray-800 p-3 rounded-lg border-l-4 border-${s.color}-500`}>
            <div className="text-xs text-gray-400">{s.label}</div>
            <div className="text-2xl font-bold">{s.value}</div>
          </div>
        ))}
      </div>

      {/* User Summary */}
      <div className="bg-gray-800 rounded-lg shadow mb-6 overflow-hidden">
        <div className="px-6 py-3 bg-gray-750 border-b border-gray-700">
          <h2 className="text-lg font-semibold">👥 User Activity Summary</h2>
        </div>
        <table className="w-full text-left">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">User</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Queries</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Last Active</th>
            </tr>
          </thead>
          <tbody>
            {USER_SUMMARY.map((u, i) => (
              <tr key={i} className="border-t border-gray-700 hover:bg-gray-750">
                <td className="px-6 py-4 font-medium">{u.user}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${u.role === 'Admin' ? 'bg-red-900/50 text-red-400' : u.role === 'SP' ? 'bg-blue-900/50 text-blue-400' : u.role === 'Inspector' ? 'bg-yellow-900/50 text-yellow-400' : 'bg-gray-700 text-gray-300'}`}>
                    {u.role}
                  </span>
                </td>
                <td className="px-6 py-4 font-bold text-lg">{u.queries}</td>
                <td className="px-6 py-4 text-gray-400">{u.last_active}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Full Audit Log Table */}
      <div className="bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-3 border-b border-gray-700">
          <h2 className="text-lg font-semibold">📋 Investigation Activity Log</h2>
        </div>
        <table className="w-full text-left">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Timestamp</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">User</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Action</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Query / Details</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">IP</th>
              <th className="px-6 py-3 text-xs text-gray-300 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody>
            {AUDIT_LOGS.map(log => (
              <tr key={log.id} className="border-t border-gray-700 hover:bg-gray-750">
                <td className="px-6 py-4 text-sm text-gray-400 whitespace-nowrap">{log.timestamp}</td>
                <td className="px-6 py-4 text-sm">{log.user}</td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 bg-gray-700 rounded text-xs font-semibold">{log.action}</span>
                </td>
                <td className="px-6 py-4 text-sm max-w-xs truncate">{log.query}</td>
                <td className="px-6 py-4 text-xs text-gray-500 font-mono">{log.ip}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${log.status === 'success' ? 'bg-green-900/50 text-green-400' : 'bg-red-900/50 text-red-400'}`}>
                    {log.status.toUpperCase()}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Security & Accountability */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <div className="bg-gray-800 p-4 rounded-lg border border-red-500/20">
          <h3 className="text-sm font-bold text-red-400 mb-3">🔒 Security Events</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between"><span className="text-gray-400">Failed Login Attempts</span><span className="text-red-400 font-bold">2</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Unauthorized Access</span><span className="text-green-400 font-bold">0</span></div>
            <div className="flex justify-between"><span className="text-gray-400">Sensitive Queries Logged</span><span className="font-bold">3</span></div>
          </div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-blue-500/20">
          <h3 className="text-sm font-bold text-blue-400 mb-3">🛡️ Accountability</h3>
          <p className="text-xs text-gray-400 leading-relaxed">
            Every AI recommendation is logged with confidence scores and is fully traceable to the originating query, 
            user, and timestamp. All investigation outputs maintain complete chain-of-custody documentation for judicial review.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuditPage;
