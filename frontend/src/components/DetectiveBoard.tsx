import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { investigationAPI } from '../services/api';
import { Search, AlertTriangle, MapPin, Phone, User, FileText, Lightbulb, Loader2, X, GripVertical, ChevronDown, ChevronUp } from 'lucide-react';

/* ────────────── Types ────────────── */
interface BoardNode {
  id: string;
  type: 'suspect' | 'evidence' | 'location' | 'phone' | 'clue';
  label: string;
  details: Record<string, any>;
  x?: number;
  y?: number;
}

interface BoardEdge {
  from: string;
  to: string;
  label: string;
  type: string;
}

interface BoardData {
  nodes: BoardNode[];
  edges: BoardEdge[];
  brief: {
    title: string;
    findings: string[];
    risk_level: string;
    action: string;
  };
  summary: Record<string, number>;
  query: string;
}

/* ────────────── Helpers ────────────── */
const NODE_COLORS: Record<string, { bg: string; border: string; text: string; glow: string }> = {
  suspect:  { bg: '#1a1a2e', border: '#e74c3c', text: '#fff', glow: 'rgba(231,76,60,0.35)' },
  evidence: { bg: '#f5f0e1', border: '#8b7355', text: '#2c2c2c', glow: 'rgba(139,115,85,0.25)' },
  location: { bg: '#1a2636', border: '#3498db', text: '#fff', glow: 'rgba(52,152,219,0.35)' },
  phone:    { bg: '#1a2e1a', border: '#2ecc71', text: '#fff', glow: 'rgba(46,204,113,0.35)' },
  clue:     { bg: '#fef3cd', border: '#f39c12', text: '#2c2c2c', glow: 'rgba(243,156,18,0.4)' },
};

const NODE_ICONS: Record<string, React.ReactNode> = {
  suspect:  <User size={16} />,
  evidence: <FileText size={16} />,
  location: <MapPin size={16} />,
  phone:    <Phone size={16} />,
  clue:     <Lightbulb size={16} />,
};

function layoutNodes(nodes: BoardNode[], w: number, h: number): BoardNode[] {
  const pad = 40;
  const suspects  = nodes.filter(n => n.type === 'suspect');
  const evidence  = nodes.filter(n => n.type === 'evidence');
  const locations = nodes.filter(n => n.type === 'location');
  const phones    = nodes.filter(n => n.type === 'phone');
  const clues     = nodes.filter(n => n.type === 'clue');

  const place = (arr: BoardNode[], yCenter: number, xStart: number, xEnd: number) => {
    const count = arr.length || 1;
    const spacing = (xEnd - xStart) / (count + 1);
    arr.forEach((n, i) => {
      n.x = xStart + spacing * (i + 1) + (Math.random() * 30 - 15);
      n.y = yCenter + (Math.random() * 40 - 20);
    });
  };

  place(suspects, pad + 80, pad, w - pad);
  place(evidence, h * 0.38, pad, w - pad);
  place(locations, h * 0.62, pad, w * 0.5);
  place(phones, h * 0.62, w * 0.5, w - pad);
  place(clues, h - pad - 80, pad + 60, w - pad - 60);

  return nodes;
}

/* ────────────── Pin component ────────────── */
const Pin: React.FC<{ color: string }> = ({ color }) => (
  <svg width="16" height="16" viewBox="0 0 16 16" style={{ position: 'absolute', top: -7, left: '50%', transform: 'translateX(-50%)', zIndex: 10 }}>
    <circle cx="8" cy="8" r="6" fill={color} stroke="#fff" strokeWidth="2" />
    <circle cx="8" cy="8" r="2.5" fill="#fff" opacity="0.7" />
  </svg>
);

/* ────────────── Card component ────────────── */
const NodeCard: React.FC<{
  node: BoardNode;
  onMouseDown: (e: React.MouseEvent) => void;
  selected: boolean;
  dimmed: boolean;
  onClick: () => void;
  onTimelineClick?: (e: React.MouseEvent, nodeId: string) => void;
}> = ({ node, onMouseDown, selected, dimmed, onClick, onTimelineClick }) => {
  const style = NODE_COLORS[node.type] || NODE_COLORS.evidence;
  const isClue = node.type === 'clue';
  const isEvidence = node.type === 'evidence';
  const isSuspect = node.type === 'suspect';

  return (
    <div
      onMouseDown={onMouseDown}
      onClick={(e) => { e.stopPropagation(); onClick(); }}
      style={{
        position: 'absolute',
        left: node.x,
        top: node.y,
        width: isClue ? 220 : isEvidence ? 200 : 180,
        background: style.bg,
        border: `2px solid ${style.border}`,
        borderRadius: isClue ? 4 : isEvidence ? 2 : 8,
        padding: '14px 12px 10px',
        cursor: 'grab',
        zIndex: selected ? 50 : 5,
        opacity: dimmed ? 0.25 : 1,
        boxShadow: selected
          ? `0 0 20px ${style.glow}, 0 4px 20px rgba(0,0,0,0.4)`
          : `0 2px 8px rgba(0,0,0,0.3)`,
        transform: isEvidence ? `rotate(${(Math.random() * 4 - 2)}deg)` : isClue ? `rotate(${(Math.random() * 3 - 1.5)}deg)` : 'none',
        transition: 'box-shadow 0.2s ease',
        userSelect: 'none',
        fontFamily: isEvidence ? "'Courier New', monospace" : "'Inter', sans-serif",
      }}
    >
      <Pin color={style.border} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <span style={{ color: style.border }}>{NODE_ICONS[node.type]}</span>
        <span style={{
          color: style.text,
          fontWeight: 700,
          fontSize: isClue ? 11 : 12,
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
          lineHeight: '1.3',
          flex: 1,
        }}>
          {node.label}
        </span>
        <GripVertical size={12} style={{ color: style.border, opacity: 0.5 }} />
      </div>

      {/* Body */}
      <div style={{ color: style.text, fontSize: 10, opacity: 0.85, lineHeight: '1.5' }}>
        {isSuspect && (
          <>
            <div>Age: {node.details.age} · {node.details.gender}</div>
            <div>📞 {node.details.phone}</div>
            
            <div style={{ marginTop: 8, padding: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                <span style={{ fontWeight: 600 }}>Risk Score:</span>
                <span style={{ 
                  fontWeight: 700, 
                  color: node.details.risk_score > 80 ? '#e74c3c' : node.details.risk_score > 60 ? '#f39c12' : '#2ecc71' 
                }}>
                  {node.details.risk_score}/100
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontWeight: 600 }}>Influence:</span>
                <span style={{ fontWeight: 700 }}>{node.details.influence_score}%</span>
              </div>
            </div>

            {node.details.repeat_offender && (
              <div style={{ color: '#e74c3c', fontWeight: 700, marginTop: 4, fontSize: 9 }}>⚠ REPEAT OFFENDER ({node.details.history_count} offenses)</div>
            )}

            <button 
              onClick={(e) => onTimelineClick && onTimelineClick(e, node.id)}
              style={{
                width: '100%', marginTop: 8, padding: '4px', background: 'rgba(231,76,60,0.1)',
                border: '1px solid #e74c3c', color: '#e74c3c', fontSize: 9, fontWeight: 700,
                borderRadius: 4, cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 4
              }}
            >
              📅 VIEW TIMELINE
            </button>
          </>
        )}
        {node.type === 'evidence' && (
          <>
            <div style={{ fontStyle: 'italic', marginBottom: 4 }}>
              {node.details.description?.slice(0, 100)}...
            </div>
            <div style={{ fontSize: 9, opacity: 0.7 }}>
              📅 {node.details.date} · {node.details.district}
            </div>
            <div style={{
              display: 'inline-block',
              background: node.details.status === 'Solved' ? '#27ae60' : node.details.status === 'Cold Case' ? '#7f8c8d' : '#e67e22',
              color: '#fff',
              padding: '1px 6px',
              borderRadius: 3,
              fontSize: 9,
              marginTop: 3,
            }}>
              {node.details.status}
            </div>
          </>
        )}
        {node.type === 'location' && (
          <div>📍 {node.details.district}</div>
        )}
        {node.type === 'phone' && (
          <>
            <div>Shared by {node.details.count} suspects:</div>
            <div style={{ fontWeight: 600 }}>{node.details.shared_by?.join(', ')}</div>
          </>
        )}
        {node.type === 'clue' && (
          <>
            <div style={{ fontStyle: 'italic', fontWeight: 500 }}>
              {node.details.description?.slice(0, 140)}...
            </div>
            <div style={{ marginTop: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{
                background: node.details.priority === 'HIGH' ? '#e74c3c' : '#e67e22',
                color: '#fff',
                padding: '1px 6px',
                borderRadius: 3,
                fontSize: 9,
                fontWeight: 700,
              }}>
                {node.details.priority}
              </span>
              <span style={{ fontSize: 10, fontWeight: 700 }}>
                Confidence: {node.details.confidence}%
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

/* ────────────── Main Detective Board ────────────── */
const DetectiveBoard: React.FC = () => {
  const location = useLocation();
  const initialQuery = location.state?.query || '';
  
  const [query, setQuery] = useState(initialQuery);
  const [boardData, setBoardData] = useState<BoardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [timelineNodeId, setTimelineNodeId] = useState<string | null>(null);
  const [isBriefOpen, setIsBriefOpen] = useState(true);
  const [nodes, setNodes] = useState<BoardNode[]>([]);
  const boardRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<{ id: string; startX: number; startY: number; nodeX: number; nodeY: number } | null>(null);

  const presetQueries = [
    'Show burglary gang active in Mysuru',
    'Which repeat offenders share communication channels?',
    'Identify emerging crime hotspots',
    'Who are the most connected criminals?'
  ];

  const handleSearch = async (q?: string) => {
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError('');
    setSelectedNode(null);

    try {
      const data = await investigationAPI.getBoard(searchQuery);
      setBoardData(data);
      const w = boardRef.current?.clientWidth || 1200;
      const h = boardRef.current?.clientHeight || 700;
      setNodes(layoutNodes([...data.nodes], w, h));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Investigation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Auto search if navigated from chat with a query
  useEffect(() => {
    if (initialQuery) {
      handleSearch(initialQuery);
    }
  }, [initialQuery]);

  /* ── Drag handling ── */
  const handleMouseDown = useCallback((nodeId: string, e: React.MouseEvent) => {
    e.preventDefault();
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    dragRef.current = {
      id: nodeId,
      startX: e.clientX,
      startY: e.clientY,
      nodeX: node.x || 0,
      nodeY: node.y || 0,
    };
  }, [nodes]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!dragRef.current) return;
      const dx = e.clientX - dragRef.current.startX;
      const dy = e.clientY - dragRef.current.startY;
      setNodes(prev =>
        prev.map(n =>
          n.id === dragRef.current!.id
            ? { ...n, x: dragRef.current!.nodeX + dx, y: dragRef.current!.nodeY + dy }
            : n
        )
      );
    };
    const handleMouseUp = () => { dragRef.current = null; };
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  /* ── Get node center for edge drawing ── */
  const getNodeCenter = (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return null;
    const w = node.type === 'clue' ? 220 : node.type === 'evidence' ? 200 : 170;
    return { x: (node.x || 0) + w / 2, y: (node.y || 0) + 50 };
  };

  return (
    <div style={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column', background: '#0d1117' }}>

      {/* ── Search Bar ── */}
      <div style={{
        padding: '12px 20px',
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        borderBottom: '1px solid rgba(231,76,60,0.3)',
        display: 'flex',
        gap: 12,
        alignItems: 'center',
        flexWrap: 'wrap',
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8,
          background: 'rgba(255,255,255,0.07)', borderRadius: 8, padding: '0 12px', flex: 1, minWidth: 280,
          border: '1px solid rgba(231,76,60,0.3)',
        }}>
          <Search size={18} color="#e74c3c" />
          <input
            type="text"
            placeholder="Investigate: e.g. Mysuru Burglary Gang, Drug network..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearch()}
            style={{
              flex: 1, border: 'none', outline: 'none', background: 'transparent',
              color: '#fff', padding: '10px 0', fontSize: 14, fontFamily: "'Inter', sans-serif",
            }}
          />
          {query && <X size={16} color="#888" style={{ cursor: 'pointer' }} onClick={() => setQuery('')} />}
        </div>
        <button
          onClick={() => handleSearch()}
          disabled={loading || !query.trim()}
          style={{
            background: loading ? '#555' : 'linear-gradient(135deg, #c0392b, #e74c3c)',
            color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px',
            cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 700, fontSize: 13,
            display: 'flex', alignItems: 'center', gap: 6,
            boxShadow: '0 2px 10px rgba(231,76,60,0.3)',
          }}
        >
          {loading ? <Loader2 size={16} className="spin" /> : <Search size={16} />}
          {loading ? 'Investigating...' : 'Investigate'}
        </button>

        {/* Preset chips */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {presetQueries.map(pq => (
            <button
              key={pq}
              onClick={() => { setQuery(pq); handleSearch(pq); }}
              style={{
                background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.15)',
                color: '#ccc', borderRadius: 16, padding: '4px 12px', fontSize: 11,
                cursor: 'pointer', transition: 'all 0.2s',
              }}
              onMouseEnter={e => { (e.target as HTMLElement).style.background = 'rgba(231,76,60,0.2)'; (e.target as HTMLElement).style.borderColor = '#e74c3c'; }}
              onMouseLeave={e => { (e.target as HTMLElement).style.background = 'rgba(255,255,255,0.06)'; (e.target as HTMLElement).style.borderColor = 'rgba(255,255,255,0.15)'; }}
            >
              {pq}
            </button>
          ))}
        </div>
      </div>

      {/* ── Summary Bar ── */}
      {boardData && (
        <div style={{
          display: 'flex', gap: 20, padding: '8px 20px',
          background: 'rgba(231,76,60,0.08)', borderBottom: '1px solid rgba(231,76,60,0.15)',
          fontSize: 12, color: '#ccc',
        }}>
          <span>🕵️ <strong>{boardData.summary.total_suspects}</strong> Suspects</span>
          <span>📋 <strong>{boardData.summary.total_crimes}</strong> Crimes</span>
          <span>📍 <strong>{boardData.summary.total_locations}</strong> Locations</span>
          <span>📞 <strong>{boardData.summary.shared_phone_networks}</strong> Phone Networks</span>
          <span>💡 <strong>{boardData.summary.ai_clues}</strong> AI Clues</span>
        </div>
      )}

      {/* ── Intelligence Brief Card (Centerpiece) ── */}
      {boardData && (
        <div style={{
          position: 'absolute', top: 130, right: 30, width: isBriefOpen ? 280 : 'auto',
          background: 'rgba(20, 25, 30, 0.95)', border: '1px solid #4a69bd', borderRadius: 8,
          padding: '16px', zIndex: 40,
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
          backdropFilter: 'blur(10px)',
          fontFamily: "'Inter', sans-serif",
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onClick={() => setIsBriefOpen(!isBriefOpen)}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ color: '#4a69bd', fontWeight: 800, fontSize: 11, letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: 6 }}>
              <FileText size={14} /> INTELLIGENCE BRIEF
            </div>
            {isBriefOpen ? <ChevronUp size={16} color="#aaa" /> : <ChevronDown size={16} color="#aaa" />}
          </div>

          {isBriefOpen && (
            <div style={{ marginTop: 12 }} onClick={(e) => e.stopPropagation()}>
              <div style={{ color: '#fff', fontSize: 14, fontWeight: 700, marginBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 8 }}>
                {boardData.brief.title}
              </div>
              <div style={{ fontSize: 11, color: '#ccc', marginBottom: 12, lineHeight: '1.6' }}>
                <div style={{ color: '#aaa', fontWeight: 600, marginBottom: 4 }}>Key Findings:</div>
                {boardData.brief.findings.map((f, i) => (
                  <div key={i} style={{ display: 'flex', gap: 6 }}>
                    <span style={{ color: '#4a69bd' }}>•</span> {f}
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, background: 'rgba(255,255,255,0.05)', padding: '6px 10px', borderRadius: 4 }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: '#aaa' }}>Risk Level:</span>
                <span style={{ fontSize: 11, fontWeight: 800, color: boardData.brief.risk_level === 'HIGH' ? '#e74c3c' : '#f39c12' }}>{boardData.brief.risk_level}</span>
              </div>
              <div style={{ fontSize: 11 }}>
                <div style={{ color: '#e74c3c', fontWeight: 700, marginBottom: 2 }}>Recommended Action:</div>
                <div style={{ color: '#fff' }}>{boardData.brief.action}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ── The Board ── */}
      <div
        ref={boardRef}
        onClick={() => setSelectedNode(null)}
        style={{
          flex: 1,
          position: 'relative',
          overflow: 'hidden',
          /* Corkboard texture */
          background: `
            radial-gradient(ellipse at 20% 50%, rgba(139,90,43,0.15) 0%, transparent 70%),
            radial-gradient(ellipse at 80% 30%, rgba(139,90,43,0.1) 0%, transparent 70%),
            linear-gradient(135deg, #1a1510 0%, #2c2318 30%, #1e1a14 60%, #24201a 100%)
          `,
          backgroundSize: '100% 100%',
        }}
      >
        {/* Cork texture overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          pointerEvents: 'none',
        }} />

        {/* Empty state */}
        {!boardData && !loading && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            color: '#666', textAlign: 'center',
          }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>🕵️‍♂️</div>
            <div style={{ fontSize: 22, fontWeight: 700, color: '#888', marginBottom: 8 }}>
              AI Detective Board
            </div>
            <div style={{ fontSize: 14, maxWidth: 400 }}>
              Enter an investigation query above to auto-discover suspects,
              evidence, locations, and hidden connections from the crime database.
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            background: 'rgba(0,0,0,0.6)', zIndex: 100,
          }}>
            <Loader2 size={48} color="#e74c3c" style={{ animation: 'spin 1s linear infinite' }} />
            <div style={{ color: '#e74c3c', fontSize: 18, fontWeight: 700, marginTop: 16 }}>
              🔍 Investigating "{query}"...
            </div>
            <div style={{ color: '#999', fontSize: 13, marginTop: 6 }}>
              Searching database · Extracting suspects · Building connections · Generating clues
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            position: 'absolute', top: 20, left: '50%', transform: 'translateX(-50%)',
            background: '#c0392b', color: '#fff', padding: '10px 20px', borderRadius: 8,
            display: 'flex', alignItems: 'center', gap: 8, zIndex: 100,
          }}>
            <AlertTriangle size={18} /> {error}
          </div>
        )}

        {/* ── Timeline Panel (When a suspect's timeline is requested) ── */}
        {timelineNodeId && (
          <div style={{
            position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: 450,
            background: 'rgba(15, 20, 25, 0.98)', border: '1px solid #e74c3c', borderRadius: 8,
            padding: '20px', zIndex: 100,
            boxShadow: '0 20px 50px rgba(0,0,0,0.6), 0 0 0 9999px rgba(0,0,0,0.5)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 12 }}>
              <User size={20} color="#e74c3c" />
              <span style={{ color: '#fff', fontWeight: 700, fontSize: 15 }}>
                TIMELINE RECONSTRUCTION: {nodes.find(n => n.id === timelineNodeId)?.label}
              </span>
              <X 
                size={20} 
                color="#888" 
                style={{ marginLeft: 'auto', cursor: 'pointer' }} 
                onClick={(e) => { e.stopPropagation(); setTimelineNodeId(null); }} 
              />
            </div>
            
            <div style={{ color: '#ccc', fontSize: 12, maxHeight: 300, overflowY: 'auto', paddingRight: 8 }}>
              {(() => {
                // Find all crimes connected to this suspect
                const connectedEdges = boardData?.edges.filter(e => e.from === timelineNodeId || e.to === timelineNodeId) || [];
                const crimeNodes = nodes.filter(n => n.type === 'evidence' && connectedEdges.some(e => e.from === n.id || e.to === n.id));
                
                if (crimeNodes.length === 0) return <div style={{ textAlign: 'center', padding: '20px 0' }}>No timeline data available.</div>;

                // Sort by date ascending
                const sorted = crimeNodes.sort((a, b) => new Date(a.details.date).getTime() - new Date(b.details.date).getTime());

                return sorted.map((c, i) => (
                  <div key={i} style={{ display: 'flex', gap: 16, marginBottom: 16, position: 'relative' }}>
                    {/* Timeline line */}
                    {i < sorted.length - 1 && <div style={{ position: 'absolute', left: 4, top: 16, bottom: -16, width: 2, background: 'rgba(231,76,60,0.3)' }} />}
                    
                    <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#e74c3c', flexShrink: 0, marginTop: 4, zIndex: 2 }} />
                    <div>
                      <div style={{ color: '#e74c3c', fontWeight: 700, marginBottom: 4 }}>{c.details.date}</div>
                      <div style={{ color: '#fff', fontWeight: 600, marginBottom: 2 }}>{c.label}</div>
                      <div style={{ color: '#aaa', fontStyle: 'italic' }}>{c.details.description}</div>
                      <div style={{ fontSize: 10, color: '#888', marginTop: 4 }}>📍 {c.details.station}, {c.details.district}</div>
                    </div>
                  </div>
                ));
              })()}
            </div>
          </div>
        )}

        {/* ── AI Reasoning Panel (When a clue is selected) ── */}
        {selectedNode && nodes.find(n => n.id === selectedNode)?.type === 'clue' && (
          <div style={{
            position: 'absolute', bottom: 20, right: 20, width: 350,
            background: 'rgba(15, 20, 25, 0.95)', border: '1px solid #f39c12', borderRadius: 8,
            padding: '16px 20px', zIndex: 60,
            boxShadow: '0 10px 30px rgba(0,0,0,0.5), 0 0 15px rgba(243,156,18,0.2)',
            backdropFilter: 'blur(10px)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 8 }}>
              <Lightbulb size={18} color="#f39c12" />
              <span style={{ color: '#fff', fontWeight: 700, fontSize: 13, letterSpacing: '0.5px' }}>
                AI INVESTIGATIVE REASONING
              </span>
              <X 
                size={16} 
                color="#888" 
                style={{ marginLeft: 'auto', cursor: 'pointer' }} 
                onClick={(e) => { e.stopPropagation(); setSelectedNode(null); }} 
              />
            </div>
            
            <div style={{ color: '#ccc', fontSize: 12, lineHeight: '1.6', marginBottom: 12 }}>
              {(() => {
                const node = nodes.find(n => n.id === selectedNode)!;
                if (!node.details.reasoning || node.details.reasoning.length === 0) {
                  return <div style={{ fontStyle: 'italic' }}>Reasoning generated based on aggregate database patterns.</div>;
                }
                return node.details.reasoning.map((reason: string, i: number) => (
                  <div key={i} style={{ display: 'flex', gap: 8, marginBottom: 6 }}>
                    <span style={{ color: '#f39c12', fontWeight: 700 }}>{i + 1}.</span>
                    <span>{reason}</span>
                  </div>
                ));
              })()}
            </div>
            
            <div style={{ background: 'rgba(243,156,18,0.1)', padding: '6px 10px', borderRadius: 4, display: 'flex', justifyContent: 'space-between', fontSize: 11, fontWeight: 700 }}>
              <span style={{ color: '#f39c12' }}>CONFIDENCE LEVEL</span>
              <span style={{ color: '#fff' }}>{nodes.find(n => n.id === selectedNode)?.details.confidence}%</span>
            </div>
          </div>
        )}

        {/* ── SVG layer for red strings ── */}
        {boardData && (
          <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 2 }}>
            <defs>
              <filter id="string-glow">
                <feGaussianBlur stdDeviation="2" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>
            {boardData.edges.map((edge, i) => {
              const from = getNodeCenter(edge.from);
              const to = getNodeCenter(edge.to);
              if (!from || !to) return null;

              // If a node is selected, check if this edge is connected to it
              const isConnectedToSelected = selectedNode === edge.from || selectedNode === edge.to;
              const isHighlighted = selectedNode ? isConnectedToSelected : false;
              const isDimmed = selectedNode ? !isConnectedToSelected : false;

              // Curved line control point
              const midX = (from.x + to.x) / 2 + (Math.random() * 20 - 10);
              const midY = (from.y + to.y) / 2 - 15;
              
              const strengthColor = (edge as any).strength === 'HIGH' ? '#e74c3c' : (edge as any).strength === 'MEDIUM' ? '#f39c12' : '#3498db';

              return (
                <g key={i} style={{ opacity: isDimmed ? 0.1 : 1, transition: 'opacity 0.3s' }}>
                  <path
                    d={`M ${from.x} ${from.y} Q ${midX} ${midY} ${to.x} ${to.y}`}
                    stroke={isHighlighted ? '#ff4444' : '#cc3333'}
                    strokeWidth={isHighlighted ? 2.5 : 1.2}
                    fill="none"
                    opacity={isHighlighted ? 1 : 0.5}
                    filter={isHighlighted ? 'url(#string-glow)' : undefined}
                    strokeDasharray={edge.type === 'phone_link' ? '6,4' : 'none'}
                  />
                  {/* Edge label */}
                  {(isHighlighted || !selectedNode) && (
                    <g>
                      <rect 
                        x={midX - 45} y={midY - 14} 
                        width="90" height="20" 
                        fill="#111" rx="4" stroke={strengthColor} strokeWidth="1" 
                      />
                      <text
                        x={midX}
                        y={midY - 4}
                        fill="#ddd"
                        fontSize={8}
                        textAnchor="middle"
                        fontWeight={700}
                        style={{ textTransform: 'uppercase', letterSpacing: '0.5px' }}
                      >
                        {edge.label}
                      </text>
                      <text
                        x={midX}
                        y={midY + 4}
                        fill={strengthColor}
                        fontSize={6}
                        textAnchor="middle"
                        fontWeight={800}
                      >
                        STR: {(edge as any).strength || 'MEDIUM'}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}
          </svg>
        )}

        {/* ── Node cards ── */}
        {nodes.map(node => {
          // Determine if node should be dimmed when a selection exists
          let isDimmed = false;
          if (selectedNode && selectedNode !== node.id) {
            // Check if node is connected to selectedNode
            const isConnected = boardData?.edges.some(e => 
              (e.from === selectedNode && e.to === node.id) || 
              (e.to === selectedNode && e.from === node.id)
            );
            isDimmed = !isConnected;
          }

          return (
            <NodeCard
              key={node.id}
              node={node}
              selected={selectedNode === node.id}
              dimmed={isDimmed}
              onClick={() => setSelectedNode(node.id === selectedNode ? null : node.id)}
              onMouseDown={(e) => handleMouseDown(node.id, e)}
              onTimelineClick={(e, id) => { e.stopPropagation(); setTimelineNodeId(id); }}
            />
          );
        })}
      </div>

      {/* Spin animation */}
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        .spin { animation: spin 1s linear infinite; }
      `}</style>
    </div>
  );
};

export default DetectiveBoard;
