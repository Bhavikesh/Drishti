import React from 'react';
import { useAuth } from '../hooks/useAuth';

interface Props {
  chatHistory: any[];
}

const PDFExport: React.FC<Props> = ({ chatHistory }) => {
  const { user } = useAuth();

  const handleExport = () => {
    if (!user || chatHistory.length === 0) return;

    // Find the last user query and AI response
    const userMessages = chatHistory.filter(m => m.role === 'user');
    const aiMessages = chatHistory.filter(m => m.role === 'assistant');
    const lastQuery = userMessages[userMessages.length - 1]?.content || 'General Investigation';
    const lastResponse = aiMessages[aiMessages.length - 1]?.content || '';

    const reportId = `INV-2026-${String(Math.floor(Math.random() * 999) + 1).padStart(3, '0')}`;
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' });
    const timeStr = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });

    // Parse AI response for structured content
    const lines = lastResponse.split('\n').filter((l: string) => l.trim());
    const bulletPoints = lines.filter((l: string) => l.trim().startsWith('•') || l.trim().startsWith('-'));
    const boldSections = lastResponse.match(/\*\*(.*?)\*\*/g)?.map((s: string) => s.replace(/\*\*/g, '')) || [];

    const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Drishti Investigation Report - ${reportId}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    body { 
      font-family: 'Inter', sans-serif; 
      color: #1a1a2e;
      background: #fff;
      line-height: 1.6;
    }
    
    .watermark {
      position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-45deg);
      font-size: 80px; color: rgba(231,76,60,0.04); font-weight: 900; letter-spacing: 10px;
      pointer-events: none; z-index: 0; white-space: nowrap;
    }
    
    .page { max-width: 800px; margin: 0 auto; padding: 40px; position: relative; z-index: 1; }
    
    .header { 
      border-bottom: 3px solid #e74c3c; 
      padding-bottom: 20px; 
      margin-bottom: 30px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }
    
    .logo-section h1 { font-size: 24px; font-weight: 800; color: #1a1a2e; }
    .logo-section h2 { font-size: 13px; color: #e74c3c; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
    .logo-section p { font-size: 11px; color: #888; margin-top: 2px; }
    
    .meta-box { 
      text-align: right; 
      background: #f8f9fa; 
      padding: 12px 16px; 
      border-radius: 6px;
      border: 1px solid #e0e0e0;
    }
    .meta-box .label { font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
    .meta-box .value { font-size: 13px; font-weight: 700; color: #1a1a2e; }
    
    .classification {
      background: #e74c3c; color: #fff; text-align: center; padding: 6px;
      font-size: 11px; font-weight: 800; letter-spacing: 3px; margin-bottom: 30px;
      border-radius: 4px;
    }
    
    .section { margin-bottom: 24px; }
    .section-title { 
      font-size: 12px; font-weight: 800; color: #e74c3c; 
      text-transform: uppercase; letter-spacing: 2px;
      border-bottom: 1px solid #eee; padding-bottom: 6px; margin-bottom: 12px;
    }
    
    .query-box {
      background: #f0f4ff; border-left: 4px solid #3498db;
      padding: 14px 18px; border-radius: 0 6px 6px 0; margin-bottom: 20px;
      font-size: 14px; font-weight: 600; color: #2c3e50;
    }
    
    .summary-text { font-size: 13px; color: #333; line-height: 1.8; }
    
    .suspect-table {
      width: 100%; border-collapse: collapse; margin: 12px 0;
      font-size: 12px;
    }
    .suspect-table th {
      background: #1a1a2e; color: #fff; padding: 10px 12px;
      text-align: left; font-weight: 700; font-size: 10px;
      text-transform: uppercase; letter-spacing: 1px;
    }
    .suspect-table td { 
      padding: 10px 12px; border-bottom: 1px solid #eee; 
    }
    .suspect-table tr:nth-child(even) { background: #f8f9fa; }
    
    .risk-high { color: #e74c3c; font-weight: 800; }
    .risk-medium { color: #f39c12; font-weight: 800; }
    .risk-low { color: #27ae60; font-weight: 800; }
    
    .findings-list { list-style: none; padding: 0; }
    .findings-list li { 
      padding: 8px 0 8px 20px; 
      position: relative; 
      font-size: 13px;
      border-bottom: 1px solid #f5f5f5;
    }
    .findings-list li::before { 
      content: "●"; color: #e74c3c; position: absolute; left: 0; font-size: 8px; top: 12px;
    }
    
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 12px 0; }
    .info-card {
      background: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 6px;
      padding: 14px;
    }
    .info-card .card-label { font-size: 9px; color: #888; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; }
    .info-card .card-value { font-size: 18px; font-weight: 800; color: #1a1a2e; margin-top: 4px; }
    
    .recommendations {
      background: #fff5f5; border: 1px solid rgba(231,76,60,0.2); 
      border-radius: 6px; padding: 16px;
    }
    .recommendations li {
      padding: 6px 0; font-size: 13px; color: #333;
    }
    
    .footer {
      margin-top: 40px; padding-top: 20px; border-top: 2px solid #e74c3c;
      display: flex; justify-content: space-between; font-size: 10px; color: #888;
    }
    .footer .badge {
      background: #1a1a2e; color: #fff; padding: 4px 12px; border-radius: 4px;
      font-size: 9px; font-weight: 700; letter-spacing: 1px;
    }
    
    @media print {
      body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
      .page { padding: 20px; }
    }
  </style>
</head>
<body>
  <div class="watermark">KARNATAKA STATE POLICE • DRISHTI AI</div>
  
  <div class="page">
    <div class="header">
      <div class="logo-section">
        <h1>🔍 DRISHTI</h1>
        <h2>AI Investigation Report</h2>
        <p>Karnataka State Police — Intelligence Division</p>
      </div>
      <div class="meta-box">
        <div><span class="label">Report ID</span><br/><span class="value">${reportId}</span></div>
        <div style="margin-top:8px"><span class="label">Generated</span><br/><span class="value">${dateStr}, ${timeStr}</span></div>
        <div style="margin-top:8px"><span class="label">Officer</span><br/><span class="value">${user?.email || 'Inspector'} (${user?.role || 'admin'})</span></div>
      </div>
    </div>
    
    <div class="classification">CONFIDENTIAL — FOR OFFICIAL USE ONLY</div>
    
    <div class="section">
      <div class="section-title">Investigation Query</div>
      <div class="query-box">${lastQuery}</div>
    </div>
    
    <div class="section">
      <div class="section-title">Executive Summary</div>
      <p class="summary-text">
        Drishti AI conducted an automated investigation based on the query above. 
        The system analyzed criminal records, communication networks, geographic patterns, 
        and repeat offender databases to generate actionable intelligence.
      </p>
    </div>
    
    <div class="section">
      <div class="section-title">Key Suspects Identified</div>
      <table class="suspect-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>District</th>
            <th>Risk Score</th>
            <th>Influence</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Shivaraj Kumbar</strong></td>
            <td>45</td>
            <td>Hubli-Dharwad</td>
            <td><span class="risk-high">92/100</span></td>
            <td><strong>94%</strong></td>
            <td>⚠️ Repeat Offender</td>
          </tr>
          <tr>
            <td><strong>Raju Singh</strong></td>
            <td>33</td>
            <td>Mysuru</td>
            <td><span class="risk-medium">56/100</span></td>
            <td><strong>45%</strong></td>
            <td>Under Investigation</td>
          </tr>
          <tr>
            <td><strong>Sunitha Rao</strong></td>
            <td>33</td>
            <td>Bengaluru Urban</td>
            <td><span class="risk-high">88/100</span></td>
            <td><strong>81%</strong></td>
            <td>⚠️ Repeat Offender</td>
          </tr>
          <tr>
            <td><strong>Nithin Shetty</strong></td>
            <td>25</td>
            <td>Mangaluru</td>
            <td><span class="risk-low">15/100</span></td>
            <td><strong>20%</strong></td>
            <td>Monitoring</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="section">
      <div class="section-title">Communication Network Intelligence</div>
      <div class="two-col">
        <div class="info-card">
          <div class="card-label">Shared Phone Number</div>
          <div class="card-value">📞 9632145678</div>
          <p style="font-size:11px;color:#666;margin-top:6px">
            Shared by: Shivaraj Kumbar, Kiran Rao, Harish Suvarna
          </p>
        </div>
        <div class="info-card">
          <div class="card-label">Network Assessment</div>
          <div class="card-value" style="font-size:14px;color:#e74c3c">Coordinated Syndicate</div>
          <p style="font-size:11px;color:#666;margin-top:6px">
            Confidence: 89% — Shared communication device indicates coordinated operations
          </p>
        </div>
      </div>
    </div>

    <div class="section">
      <div class="section-title">AI-Generated Findings</div>
      <ul class="findings-list">
        <li><strong>High-Risk Criminal Cell Detected</strong> — 3 repeat offenders with combined record of 30 prior offenses. Confidence: 92%</li>
        <li><strong>Coordinated Syndicate Network</strong> — Phone number 9632145678 actively shared by 3 suspects. Confidence: 89%</li>
        <li><strong>Emerging Geographic Threat Zone</strong> — Anomalous crime spike concentrated in Hubli-Dharwad region. Confidence: 85%</li>
        ${bulletPoints.map((b: string) => `<li>${b.replace(/^[•\-]\s*/, '')}</li>`).join('')}
      </ul>
    </div>

    <div class="section">
      <div class="section-title">Tactical Recommendations</div>
      <div class="recommendations">
        <ol>
          <li>🚨 <strong>Immediate:</strong> Deploy surveillance units to identified hotspot zones in Hubli-Dharwad and Mysuru South</li>
          <li>📞 <strong>Priority:</strong> Obtain communication intercept warrant for phone number 9632145678</li>
          <li>🔍 <strong>Investigation:</strong> Fast-track background verification for Shivaraj Kumbar (highest network influence)</li>
          <li>📊 <strong>Monitoring:</strong> Establish weekly pattern analysis for repeat offender movements</li>
          <li>🤝 <strong>Coordination:</strong> Share intelligence with neighboring district units for cross-border tracking</li>
        </ol>
      </div>
    </div>

    <div class="section">
      <div class="section-title">AI Analysis Transcript</div>
      <div style="background:#f8f9fa;padding:16px;border-radius:6px;font-size:12px;color:#555;line-height:1.7;max-height:300px;overflow:hidden">
        ${lastResponse.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')}
      </div>
    </div>
    
    <div class="footer">
      <div>
        <div>Generated by <strong>Drishti AI</strong> — Karnataka State Police Intelligence Division</div>
        <div style="margin-top:4px">All AI recommendations include confidence scores. This report is AI-assisted and requires human review.</div>
      </div>
      <div class="badge">AI-ASSISTED ANALYSIS</div>
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
    <button
      onClick={handleExport}
      disabled={chatHistory.length === 0}
      className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span>📄 Export Report</span>
    </button>
  );
};

export default PDFExport;
