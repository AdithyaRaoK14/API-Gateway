import { useState, useEffect, useCallback } from "react";
import {
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from "recharts";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

const css = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg:       #080c14;
    --surface:  #0d1321;
    --border:   #1a2540;
    --accent:   #00d4ff;
    --accent2:  #7c3aed;
    --green:    #00e5a0;
    --red:      #ff4060;
    --amber:    #ffb020;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --font-mono: 'JetBrains Mono', monospace;
    --font-disp: 'Syne', sans-serif;
  }

  body { background: var(--bg); color: var(--text); font-family: var(--font-mono); }

  .app { min-height: 100vh; display: flex; flex-direction: column; }

  /* ── Header ── */
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 18px 32px;
    background: linear-gradient(90deg, rgba(0,212,255,.06) 0%, transparent 60%);
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0; z-index: 100;
    backdrop-filter: blur(12px);
  }
  .logo { font-family: var(--font-disp); font-size: 1.1rem; font-weight: 800;
    letter-spacing: -.5px; color: var(--accent); display: flex; align-items: center; gap: 10px; }
  .logo-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--accent);
    box-shadow: 0 0 12px var(--accent); animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(.8)} }

  .header-right { display: flex; align-items: center; gap: 16px; }
  .live-badge {
    font-size: .65rem; font-weight: 700; letter-spacing: 1.5px;
    padding: 4px 10px; border-radius: 20px;
    background: rgba(0,229,160,.1); color: var(--green);
    border: 1px solid rgba(0,229,160,.3);
  }
  .refresh-btn {
    background: rgba(0,212,255,.08); border: 1px solid rgba(0,212,255,.2);
    color: var(--accent); padding: 6px 16px; border-radius: 6px;
    cursor: pointer; font-family: var(--font-mono); font-size: .75rem;
    transition: all .2s;
  }
  .refresh-btn:hover { background: rgba(0,212,255,.15); }

  /* ── Login ── */
  .login-wrap {
    flex: 1; display: flex; align-items: center; justify-content: center;
  }
  .login-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 16px; padding: 48px 40px; width: 380px;
    box-shadow: 0 0 60px rgba(0,212,255,.05);
  }
  .login-title { font-family: var(--font-disp); font-size: 1.6rem; font-weight: 800;
    margin-bottom: 8px; color: var(--accent); }
  .login-sub { color: var(--muted); font-size: .8rem; margin-bottom: 32px; }
  .field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
  .field label { font-size: .72rem; color: var(--muted); letter-spacing: .5px; text-transform: uppercase; }
  .field input {
    background: rgba(255,255,255,.04); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; color: var(--text);
    font-family: var(--font-mono); font-size: .85rem; outline: none;
    transition: border-color .2s;
  }
  .field input:focus { border-color: var(--accent); }
  .login-btn {
    width: 100%; padding: 12px; background: var(--accent); color: #080c14;
    border: none; border-radius: 8px; font-family: var(--font-disp);
    font-weight: 800; font-size: .9rem; cursor: pointer; margin-top: 8px;
    transition: all .2s; letter-spacing: .5px;
  }
  .login-btn:hover { background: #33ddff; }
  .error-msg { color: var(--red); font-size: .75rem; margin-top: 12px; text-align: center; }

  /* ── Layout ── */
  .main { flex: 1; display: flex; }
  .sidebar {
    width: 200px; min-height: calc(100vh - 61px);
    background: var(--surface); border-right: 1px solid var(--border);
    padding: 24px 0; display: flex; flex-direction: column; gap: 4px;
    position: sticky; top: 61px; height: calc(100vh - 61px);
  }
  .nav-section { font-size: .6rem; color: var(--muted); letter-spacing: 2px;
    padding: 12px 20px 6px; text-transform: uppercase; }
  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 20px; cursor: pointer; font-size: .78rem;
    color: var(--muted); transition: all .15s; border-left: 2px solid transparent;
  }
  .nav-item:hover { color: var(--text); background: rgba(255,255,255,.03); }
  .nav-item.active {
    color: var(--accent); background: rgba(0,212,255,.06);
    border-left-color: var(--accent);
  }
  .nav-icon { font-size: 1rem; width: 20px; text-align: center; }

  .content { flex: 1; padding: 32px; overflow-y: auto; }
  .page-title { font-family: var(--font-disp); font-size: 1.4rem; font-weight: 800;
    margin-bottom: 4px; }
  .page-sub { color: var(--muted); font-size: .78rem; margin-bottom: 28px; }

  /* ── Stat cards ── */
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr));
    gap: 16px; margin-bottom: 28px; }
  .stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px 24px;
    position: relative; overflow: hidden; transition: border-color .2s;
  }
  .stat-card:hover { border-color: rgba(0,212,255,.3); }
  .stat-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-color, var(--accent)), transparent);
    opacity: .5;
  }
  .stat-label { font-size: .68rem; color: var(--muted); letter-spacing: 1px;
    text-transform: uppercase; margin-bottom: 8px; }
  .stat-value { font-family: var(--font-disp); font-size: 2rem; font-weight: 800;
    color: var(--accent-color, var(--accent)); line-height: 1; }
  .stat-sub { font-size: .7rem; color: var(--muted); margin-top: 6px; }

  /* ── Charts ── */
  .charts-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
  .chart-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
  }
  .chart-title { font-family: var(--font-disp); font-size: .9rem; font-weight: 600;
    margin-bottom: 20px; color: var(--text); display: flex; align-items: center; gap: 8px; }
  .chart-title span { font-size: .7rem; color: var(--muted); font-family: var(--font-mono);
    font-weight: 400; }

  /* ── Table ── */
  .table-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 24px; overflow: hidden;
  }
  .table-header { padding: 20px 24px; border-bottom: 1px solid var(--border);
    font-family: var(--font-disp); font-size: .9rem; font-weight: 600; }
  table { width: 100%; border-collapse: collapse; }
  th { padding: 10px 16px; text-align: left; font-size: .65rem; color: var(--muted);
    letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid var(--border); }
  td { padding: 10px 16px; font-size: .75rem; border-bottom: 1px solid rgba(26,37,64,.5); }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,.02); }

  /* ── Badges ── */
  .badge {
    display: inline-block; padding: 2px 8px; border-radius: 4px;
    font-size: .65rem; font-weight: 700; letter-spacing: .5px;
  }
  .badge-green { background: rgba(0,229,160,.1); color: var(--green); }
  .badge-red   { background: rgba(255,64,96,.1);  color: var(--red); }
  .badge-amber { background: rgba(255,176,32,.1); color: var(--amber); }
  .badge-blue  { background: rgba(0,212,255,.1);  color: var(--accent); }

  /* ── Service health ── */
  .services-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px,1fr));
    gap: 16px; margin-bottom: 24px; }
  .service-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 10px;
  }
  .service-top { display: flex; justify-content: space-between; align-items: center; }
  .service-name { font-family: var(--font-disp); font-weight: 600; font-size: .95rem; }
  .health-dot { width: 10px; height: 10px; border-radius: 50%; }
  .health-dot.up { background: var(--green); box-shadow: 0 0 8px var(--green); }
  .health-dot.down { background: var(--red); box-shadow: 0 0 8px var(--red); }
  .service-url { font-size: .7rem; color: var(--muted); }
  .service-prefix { font-size: .7rem; }

  /* ── API Keys ── */
  .key-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 12px; padding: 24px; margin-bottom: 24px;
  }
  .key-row {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 0; border-bottom: 1px solid var(--border);
  }
  .key-row:last-child { border-bottom: none; }
  .key-name { font-weight: 600; font-size: .85rem; flex: 1; }
  .key-prefix {
    font-size: .75rem; color: var(--muted);
    background: rgba(255,255,255,.04); padding: 3px 10px; border-radius: 4px;
  }
  .revoke-btn {
    background: rgba(255,64,96,.08); border: 1px solid rgba(255,64,96,.2);
    color: var(--red); padding: 4px 12px; border-radius: 6px;
    cursor: pointer; font-size: .72rem; font-family: var(--font-mono);
    transition: all .2s;
  }
  .revoke-btn:hover { background: rgba(255,64,96,.15); }
  .create-key-form { display: flex; gap: 12px; margin-bottom: 20px; }
  .create-key-form input {
    flex: 1; background: rgba(255,255,255,.04); border: 1px solid var(--border);
    border-radius: 8px; padding: 9px 14px; color: var(--text);
    font-family: var(--font-mono); font-size: .82rem; outline: none;
  }
  .create-key-form input:focus { border-color: var(--accent); }
  .create-btn {
    background: rgba(0,229,160,.1); border: 1px solid rgba(0,229,160,.3);
    color: var(--green); padding: 9px 20px; border-radius: 8px;
    cursor: pointer; font-family: var(--font-mono); font-size: .78rem; white-space: nowrap;
    transition: all .2s;
  }
  .create-btn:hover { background: rgba(0,229,160,.18); }
  .new-key-reveal {
    background: rgba(0,229,160,.06); border: 1px solid rgba(0,229,160,.2);
    border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;
    font-size: .78rem; word-break: break-all;
  }
  .new-key-reveal strong { color: var(--green); display: block; margin-bottom: 6px; font-size: .7rem; }

  /* ── Loading / empty ── */
  .loading { color: var(--muted); font-size: .82rem; padding: 40px; text-align: center; }
  .empty { color: var(--muted); font-size: .78rem; padding: 32px; text-align: center; }

  /* ── Custom tooltip ── */
  .custom-tooltip {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px 14px; font-size: .75rem;
  }
  .custom-tooltip .label { color: var(--muted); margin-bottom: 4px; }
  .custom-tooltip .value { color: var(--accent); font-weight: 700; }

  @media (max-width: 900px) {
    .sidebar { display: none; }
    .charts-row { grid-template-columns: 1fr; }
  }
`;

// ── Helpers ─────────────────────────────────────────────────────────────
function statusBadge(code) {
  if (!code) return null;
  if (code < 300) return <span className="badge badge-green">{code}</span>;
  if (code < 400) return <span className="badge badge-blue">{code}</span>;
  if (code === 429) return <span className="badge badge-amber">{code}</span>;
  return <span className="badge badge-red">{code}</span>;
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <div className="label">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="value" style={{ color: p.color }}>{p.name}: {p.value}</div>
      ))}
    </div>
  );
};

const PIE_COLORS = { "2xx": "#00e5a0", "4xx": "#ffb020", "5xx": "#ff4060", "3xx": "#00d4ff" };

// ── Pages ────────────────────────────────────────────────────────────────
function OverviewPage({ token }) {
  const [data, setData] = useState({ summary: null, traffic: [], statusBreakdown: [], topRoutes: [] });
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const h = { Authorization: `Bearer ${token}` };
      const [sum, traffic, status, routes] = await Promise.all([
        fetch(`${API}/analytics/summary`, { headers: h }).then(r => r.json()),
        fetch(`${API}/analytics/traffic`, { headers: h }).then(r => r.json()),
        fetch(`${API}/analytics/status-breakdown`, { headers: h }).then(r => r.json()),
        fetch(`${API}/analytics/top-routes`, { headers: h }).then(r => r.json()),
      ]);
      const pieData = Object.entries(
        status.reduce((acc, s) => {
          const bucket = s.status_code < 300 ? "2xx" : s.status_code < 400 ? "3xx" : s.status_code < 500 ? "4xx" : "5xx";
          acc[bucket] = (acc[bucket] || 0) + s.count;
          return acc;
        }, {})
      ).map(([name, value]) => ({ name, value }));

      setData({ summary: sum, traffic: Array.isArray(traffic) ? traffic : [], statusBreakdown: pieData, topRoutes: Array.isArray(routes) ? routes : [] });
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [token]);

  useEffect(() => { load(); const id = setInterval(load, 10000); return () => clearInterval(id); }, [load]);

  if (loading) return <div className="loading">Loading metrics…</div>;
  const s = data.summary || {};

  return (
    <div>
      <div className="page-title">Overview</div>
      <div className="page-sub">Live gateway metrics · auto-refreshes every 10s</div>

      <div className="stats-grid">
        {[
          { label: "Total Requests", value: s.total_requests ?? 0, color: "var(--accent)", sub: "all time" },
          { label: "Success Rate", value: `${s.success_rate ?? 0}%`, color: "var(--green)", sub: "2xx responses" },
          { label: "Errors", value: s.error_count ?? 0, color: "var(--red)", sub: "4xx + 5xx" },
          { label: "Avg Latency", value: `${s.avg_latency_ms ?? 0}ms`, color: "var(--amber)", sub: "all routes" },
          { label: "Rate Limited", value: s.rate_limit_violations ?? 0, color: "#7c3aed", sub: "429 responses" },
        ].map(({ label, value, color, sub }) => (
          <div key={label} className="stat-card" style={{ "--accent-color": color }}>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
            <div className="stat-sub">{sub}</div>
          </div>
        ))}
      </div>

      <div className="charts-row">
        <div className="chart-card">
          <div className="chart-title">Traffic <span>requests / minute</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={data.traffic}>
              <defs>
                <linearGradient id="tGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#00d4ff" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="#00d4ff" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2540" />
              <XAxis dataKey="time" tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="requests" stroke="#00d4ff" fill="url(#tGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <div className="chart-title">Status Breakdown <span>response codes</span></div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={data.statusBreakdown} cx="50%" cy="50%" outerRadius={80}
                dataKey="value" label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}>
                {data.statusBreakdown.map((entry, i) => (
                  <Cell key={i} fill={PIE_COLORS[entry.name] || "#64748b"} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-title">Top Routes <span>by request count</span></div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={data.topRoutes} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#1a2540" horizontal={false} />
            <XAxis type="number" tick={{ fill: "#64748b", fontSize: 10 }} />
            <YAxis dataKey="path" type="category" tick={{ fill: "#64748b", fontSize: 10 }} width={120} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" fill="#7c3aed" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function ServicesPage({ token }) {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API}/analytics/services-health`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setServices).catch(console.error).finally(() => setLoading(false));
  }, [token]);

  if (loading) return <div className="loading">Loading services…</div>;

  return (
    <div>
      <div className="page-title">Service Registry</div>
      <div className="page-sub">Registered backend services and health status</div>
      {services.length === 0 ? (
        <div className="empty">No services registered. Register one via POST /services/</div>
      ) : (
        <div className="services-grid">
          {services.map(s => (
            <div key={s.name} className="service-card">
              <div className="service-top">
                <div className="service-name">{s.name}</div>
                <div className={`health-dot ${s.is_healthy ? "up" : "down"}`} title={s.is_healthy ? "Healthy" : "Down"} />
              </div>
              <div className="service-url">{s.url}</div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="badge badge-blue">{s.prefix}</span>
                <span style={{ fontSize: ".68rem", color: "var(--muted)" }}>{s.rate_limit}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function LogsPage({ token, errorOnly }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const endpoint = errorOnly ? "/analytics/errors" : "/analytics/recent";
    fetch(`${API}${endpoint}`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setLogs).catch(console.error).finally(() => setLoading(false));
  }, [token, errorOnly]);

  if (loading) return <div className="loading">Loading logs…</div>;

  return (
    <div>
      <div className="page-title">{errorOnly ? "Error Logs" : "Request Logs"}</div>
      <div className="page-sub">{errorOnly ? "4xx and 5xx responses" : "Last 50 requests through the gateway"}</div>
      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th>Path</th><th>Method</th><th>Status</th>
              <th>Latency</th><th>User</th><th>Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr><td colSpan={6} style={{ textAlign: "center", color: "var(--muted)", padding: "32px" }}>No logs yet</td></tr>
            ) : logs.map((l, i) => (
              <tr key={i}>
                <td style={{ color: "var(--accent)", fontFamily: "var(--font-mono)" }}>{l.path}</td>
                <td><span className="badge badge-blue">{l.method}</span></td>
                <td>{statusBadge(l.status)}</td>
                <td style={{ color: l.latency_ms > 500 ? "var(--red)" : "var(--muted)" }}>{l.latency_ms}ms</td>
                <td style={{ color: "var(--muted)", fontSize: ".7rem" }}>{l.user || "anon"}</td>
                <td style={{ color: "var(--muted)", fontSize: ".7rem" }}>{l.time?.slice(11, 19)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function APIKeysPage({ token }) {
  const [keys, setKeys] = useState([]);
  const [name, setName] = useState("");
  const [newKey, setNewKey] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadKeys = useCallback(() => {
    fetch(`${API}/api-keys/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(setKeys).catch(console.error).finally(() => setLoading(false));
  }, [token]);

  useEffect(() => { loadKeys(); }, [loadKeys]);

  const create = async () => {
    if (!name.trim()) return;
    const r = await fetch(`${API}/api-keys/`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const data = await r.json();
    setNewKey(data.key);
    setName("");
    loadKeys();
  };

  const revoke = async (id) => {
    await fetch(`${API}/api-keys/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    loadKeys();
  };

  return (
    <div>
      <div className="page-title">API Keys</div>
      <div className="page-sub">Manage programmatic access — supports Authorization: Bearer or X-API-Key header</div>

      {newKey && (
        <div className="new-key-reveal">
          <strong>⚠️ Copy this key now — it won't be shown again</strong>
          {newKey}
        </div>
      )}

      <div className="key-card">
        <div className="create-key-form">
          <input value={name} onChange={e => setName(e.target.value)}
            placeholder="Key name (e.g. ci-pipeline, mobile-app)"
            onKeyDown={e => e.key === "Enter" && create()} />
          <button className="create-btn" onClick={create}>+ Generate Key</button>
        </div>

        {loading ? <div className="loading">Loading…</div> :
          keys.length === 0 ? <div className="empty">No API keys yet</div> :
          keys.map(k => (
            <div key={k.id} className="key-row">
              <div className="key-name">{k.name}</div>
              <div className="key-prefix">{k.prefix}…</div>
              <div style={{ color: "var(--muted)", fontSize: ".7rem" }}>{k.created_at?.slice(0, 10)}</div>
              <button className="revoke-btn" onClick={() => revoke(k.id)}>Revoke</button>
            </div>
          ))
        }
      </div>
    </div>
  );
}

// ── Nav config ──────────────────────────────────────────────────────────
const NAV = [
  { id: "overview",  icon: "◈", label: "Overview" },
  { id: "services",  icon: "⬡", label: "Services" },
  { id: "logs",      icon: "≡", label: "Request Logs" },
  { id: "errors",    icon: "⚠", label: "Errors" },
  { id: "api-keys",  icon: "⌗", label: "API Keys" },
];

// ── Root App ─────────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("gw_token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginErr, setLoginErr] = useState("");
  const [page, setPage] = useState("overview");
  const [refreshKey, setRefreshKey] = useState(0);

  const login = async () => {
    setLoginErr("");
    try {
      const r = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await r.json();
      if (!r.ok) { setLoginErr(data.detail || "Login failed"); return; }
      sessionStorage.setItem("gw_token", data.token);
      setToken(data.token);
    } catch (e) { setLoginErr("Cannot reach gateway"); }
  };

  const logout = () => { sessionStorage.removeItem("gw_token"); setToken(""); };

  if (!token) {
    return (
      <>
        <style>{css}</style>
        <div className="app">
          <div className="header">
            <div className="logo"><div className="logo-dot" />API Gateway</div>
          </div>
          <div className="login-wrap">
            <div className="login-card">
              <div className="login-title">Sign in</div>
              <div className="login-sub">Access the gateway dashboard</div>
              <div className="field">
                <label>Username</label>
                <input value={username} onChange={e => setUsername(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && login()} autoFocus />
              </div>
              <div className="field">
                <label>Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)}
                  onKeyDown={e => e.key === "Enter" && login()} />
              </div>
              <button className="login-btn" onClick={login}>Login →</button>
              {loginErr && <div className="error-msg">{loginErr}</div>}
            </div>
          </div>
        </div>
      </>
    );
  }

  const renderPage = () => {
    switch (page) {
      case "overview":  return <OverviewPage token={token} key={refreshKey} />;
      case "services":  return <ServicesPage token={token} key={refreshKey} />;
      case "logs":      return <LogsPage token={token} errorOnly={false} key={refreshKey} />;
      case "errors":    return <LogsPage token={token} errorOnly={true} key={refreshKey} />;
      case "api-keys":  return <APIKeysPage token={token} key={refreshKey} />;
      default:          return <OverviewPage token={token} key={refreshKey} />;
    }
  };

  return (
    <>
      <style>{css}</style>
      <div className="app">
        <div className="header">
          <div className="logo"><div className="logo-dot" />API Gateway</div>
          <div className="header-right">
            <span className="live-badge">● LIVE</span>
            <button className="refresh-btn" onClick={() => setRefreshKey(k => k + 1)}>↻ Refresh</button>
            <button className="refresh-btn" onClick={logout} style={{ color: "var(--muted)" }}>Logout</button>
          </div>
        </div>
        <div className="main">
          <div className="sidebar">
            <div className="nav-section">Navigation</div>
            {NAV.map(({ id, icon, label }) => (
              <div key={id} className={`nav-item ${page === id ? "active" : ""}`} onClick={() => setPage(id)}>
                <span className="nav-icon">{icon}</span>{label}
              </div>
            ))}
          </div>
          <div className="content">{renderPage()}</div>
        </div>
      </div>
    </>
  );
}
