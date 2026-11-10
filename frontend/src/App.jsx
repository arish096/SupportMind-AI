
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  LayoutDashboard, MessageSquare, Ticket, Users, BarChart3,
  Settings, Search, Bell, Plus, Send, Bot, Headphones,
  BrainCircuit, Workflow, CheckCircle2, Clock3, AlertCircle,
  Menu, X, ArrowUpRight, Sparkles
} from "lucide-react";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid
} from "recharts";
import "./App.css";

const chartData = [
  { day: "Mon", tickets: 32, resolved: 24 },
  { day: "Tue", tickets: 45, resolved: 35 },
  { day: "Wed", tickets: 38, resolved: 30 },
  { day: "Thu", tickets: 58, resolved: 46 },
  { day: "Fri", tickets: 48, resolved: 40 },
  { day: "Sat", tickets: 65, resolved: 55 },
  { day: "Sun", tickets: 52, resolved: 44 },
];

const agents = [
  { name: "Customer Agent", detail: "Analyzing customer query", icon: Headphones, color: "#a78bfa" },
  { name: "Memory Agent", detail: "Retrieving customer history", icon: BrainCircuit, color: "#60a5fa" },
  { name: "Resolution Agent", detail: "Finding the best solution", icon: Workflow, color: "#34d399" },
  { name: "Review Agent", detail: "Checking response quality", icon: CheckCircle2, color: "#fbbf24" },
];




export default function App() {
  const [active, setActive] = useState("Overview");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([
    { role: "assistant", text: "Hello! I'm SupportMind AI. Describe your customer issue and I'll coordinate our AI agents to help resolve it." }
  ]);
  const [loading, setLoading] = useState(false);

  const [settings, setSettings] = useState({
  name: "Admin User",
  email: "admin@supportmind.ai",
  notifications: true,
  emailAlerts: true,
  aiReview: true,
  darkMode: true,
  language: "English",
});
const [settingsSaved, setSettingsSaved] = useState(false);
  const [tickets, setTickets] = useState([]);
  const [analytics, setAnalytics] = useState({});
  const [dataLoading, setDataLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  async function refreshDashboardData() {
    setDataLoading(true);
    setApiError("");
    try {
      const [ticketResponse, analyticsResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/tickets"),
        fetch("http://127.0.0.1:8000/analytics"),
      ]);

      if (!ticketResponse.ok) throw new Error("Could not load tickets.");
      if (!analyticsResponse.ok) throw new Error("Could not load analytics.");

      const ticketData = await ticketResponse.json();
      const analyticsData = await analyticsResponse.json();

      setTickets(Array.isArray(ticketData.tickets) ? ticketData.tickets : []);
      setAnalytics(analyticsData.analytics || {});
    } catch (error) {
      setApiError(`${error.message} Make sure the backend is running.`);
    } finally {
      setDataLoading(false);
    }
  }

  useEffect(() => {
    refreshDashboardData();
  }, []);

  async function reviewTicket(ticketId, approved) {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/tickets/${ticketId}/review`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            approved,
            reviewer: settings.name || "Human Reviewer",
          }),
        }
      );
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Review failed.");
      await refreshDashboardData();
    } catch (error) {
      setApiError(error.message);
    }
  }

function updateSetting(key, value) {
  setSettings((prev) => ({ ...prev, [key]: value }));
  setSettingsSaved(false);
}

  const navItems = [
    { label: "Overview", icon: LayoutDashboard },
    { label: "AI Support Chat", icon: MessageSquare },
    { label: "Tickets", icon: Ticket },
    { label: "Customers", icon: Users },
    { label: "Analytics", icon: BarChart3 },
  ];

  async function sendMessage(e) {
    e.preventDefault();
    if (!message.trim() || loading) return;

    const userMessage = message.trim();
    setChat((prev) => [...prev, { role: "user", text: userMessage }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          customer_id: `CUST-${Date.now()}`,
          message: userMessage,
        }),
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");

      setChat((prev) => [...prev, {
        role: "assistant",
        text: `${data.response || data.message || JSON.stringify(data)}\\n\\nTicket ID: ${data.ticket_id ?? "Not returned"} | Review: ${data.review_status || "Pending"}`,
      }]);
      await refreshDashboardData();
    } catch (error) {
      setChat((prev) => [...prev, {
        role: "assistant",
        text: `Connection error: ${error.message}. Make sure the backend is running at http://127.0.0.1:8000.`,
      }]);
    } finally {
      setLoading(false);
    }
  }

  const totalTickets = analytics.total_tickets ?? analytics.ticket_count ?? tickets.length;
  const approvedTickets = analytics.approved_tickets ?? analytics.approved_count ??
    tickets.filter((ticket) => String(ticket.status || "").toLowerCase() === "approved").length;
  const repeatIssues = analytics.repeat_issues ?? analytics.repeat_issue_count ?? 0;
  const avgResponseMs = analytics.average_response_time_ms ?? analytics.avg_response_time_ms ?? 0;
  const stats = [
    { label: "Total Tickets", value: String(totalTickets), change: "Live data", icon: Ticket, color: "#a78bfa" },
    { label: "Approved Tickets", value: String(approvedTickets), change: "Human reviewed", icon: CheckCircle2, color: "#34d399" },
    { label: "Repeat Issues", value: String(repeatIssues), change: "Learning metric", icon: Users, color: "#60a5fa" },
    { label: "Avg. Response Time", value: avgResponseMs ? `${(Number(avgResponseMs) / 1000).toFixed(1)}s` : "—", change: "Backend metric", icon: Clock3, color: "#fbbf24" },
  ];

  return (
    <div className="app-shell">
      {mobileOpen && <div className="mobile-overlay" onClick={() => setMobileOpen(false)} />}
      <aside className={`sidebar ${mobileOpen ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-icon"><Bot size={23} /></div>
          <div><strong>SupportMind</strong><span>AI CUSTOMER PLATFORM</span></div>
          <button className="mobile-close" onClick={() => setMobileOpen(false)}><X /></button>
        </div>

        <div className="workspace"><span className="workspace-dot" /> Workspace <span className="workspace-arrow">⌄</span></div>
        <p className="nav-heading">MENU</p>
        <nav>
          {navItems.map(({ label, icon: Icon }) => (
            <button key={label} className={`nav-link ${active === label ? "active" : ""}`}
              onClick={() => { setActive(label); setMobileOpen(false); }}>
              <Icon size={19} /> {label}
              {label === "Tickets" && <span className="nav-count">8</span>}
            </button>
          ))}
        </nav>

        <p className="nav-heading tools-heading">PREFERENCES</p>
        <button className="nav-link" onClick={() => setActive("Settings")}><Settings size={19} /> Settings</button>

        <div className="sidebar-bottom">
          <div className="upgrade-card">
            <div className="upgrade-icon"><Sparkles size={18} /></div>
            <strong>AI-powered support</strong>
            <p>Four intelligent agents. One seamless experience.</p>
          </div>
          <div className="profile">
            <div className="avatar">AI</div>
            <div><strong>Admin User</strong><span>Administrator</span></div>
            <Settings size={17} className="profile-settings" />
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button className="mobile-menu" onClick={() => setMobileOpen(true)}><Menu /></button>
            <div><span className="breadcrumb">Workspace /</span> <strong>{active}</strong></div>
          </div>
          <div className="topbar-actions">
            <div className="search-box"><Search size={17} /><input placeholder="Search anything..." /></div>
            <button className="icon-button notification"><Bell size={19} /><i /></button>
            <div className="top-avatar">AI</div>
          </div>
        </header>

        {active === "AI Support Chat" ? (
          <section className="chat-page">
            <div className="page-heading"><div><span className="eyebrow">INTELLIGENT ASSISTANCE</span><h1>AI Support Chat</h1><p>Talk to your coordinated AI support team.</p></div><span className="online-pill"><i /> System Online</span></div>
            <div className="chat-layout">
              <div className="chat-panel">
                <div className="chat-header"><div className="chat-bot-icon"><Bot /></div><div><strong>SupportMind Assistant</strong><span><i /> Powered by 4 AI agents</span></div></div>
                <div className="chat-messages">
                  {chat.map((item, i) => <div key={i} className={`message-row ${item.role}`}>
                    {item.role === "assistant" && <div className="message-avatar"><Bot size={17} /></div>}
                    <div className="message-bubble">{item.text}</div>
                  </div>)}
                  {loading && <div className="message-row assistant"><div className="message-avatar"><Bot size={17} /></div><div className="message-bubble typing">AI agents are working...</div></div>}
                </div>
                <form className="chat-input" onSubmit={sendMessage}>
                  <input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Describe your customer issue..." />
                  <button disabled={loading || !message.trim()}><Send size={18} /></button>
                </form>
                <p className="chat-disclaimer">AI can make mistakes. Please review important responses.</p>
              </div>
              <div className="agent-panel"><h3>Agent Workflow</h3><p className="panel-subtitle">Your intelligent support pipeline</p>
                {agents.map(({ name, detail, icon: Icon, color }, i) => <div className="agent-item" key={name}>
                  <div className="agent-icon" style={{ color, background: `${color}18` }}><Icon size={20} /></div>
                  <div><strong>{name}</strong><span>{detail}</span></div><span className="agent-number">{String(i + 1).padStart(2, "0")}</span>
                </div>)}
                <div className="workflow-note"><Sparkles size={17} /> All agents collaborate to deliver a reviewed response.</div>
              </div>
            </div>
          </section>
        ) : (
          <section className="dashboard-page">
            <div className="page-heading">
              <div><span className="eyebrow">MONDAY, NOVEMBER 09, 2026</span><h1>{active === "Overview" ? "Welcome back, Admin 👋" : active}</h1><p>Here's what's happening with your support operations today.</p></div>
              <button className="primary-button" onClick={() => setActive("AI Support Chat")}><Plus size={18} /> New Support Request</button>
            </div>
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 16 }}>
              <span style={{ color: apiError ? "#f87171" : "#34d399", fontSize: 13 }}>
                {apiError || (dataLoading ? "Syncing with backend..." : "Connected to SupportMind API")}
              </span>
              <button className="secondary-button" onClick={refreshDashboardData} disabled={dataLoading}>
                Refresh data
              </button>
            </div>

            {active === "Overview" || active === "Analytics" ? <>
              <div className="stats-grid">
                {stats.map(({ label, value, change, icon: Icon, color }, i) => <motion.div className="stat-card" key={label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                  <div className="stat-top"><span>{label}</span><div className="stat-icon" style={{ color, background: `${color}18` }}><Icon size={19} /></div></div>
                  <div className="stat-bottom"><strong>{value}</strong><span className="stat-change">{change} <ArrowUpRight size={14} /></span></div>
                  <span className="stat-caption">Compared to last week</span>
                </motion.div>)}
              </div>

              <div className="content-grid">
                <div className="panel chart-panel">
                  <div className="panel-header"><div><h3>Support Activity</h3><p>Illustrative weekly chart (daily history is not yet provided by the API)</p></div><span className="period-select">Last 7 days⌄</span></div>
                  <div className="chart-legend"><span><i className="legend-purple" /> Total Tickets</span><span><i className="legend-green" /> Resolved</span></div>
                  <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData}>
                    <defs><linearGradient id="purpleFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#9875f5" stopOpacity={0.3} /><stop offset="95%" stopColor="#9875f5" stopOpacity={0} /></linearGradient></defs>
                    <CartesianGrid stroke="#25283a" strokeDasharray="4 4" vertical={false} />
                    <XAxis dataKey="day" stroke="#777b91" tickLine={false} axisLine={false} />
                    <YAxis stroke="#777b91" tickLine={false} axisLine={false} />
                    <Tooltip contentStyle={{ background: "#171a29", border: "1px solid #30334a", borderRadius: 10 }} />
                    <Area type="monotone" dataKey="tickets" stroke="#a78bfa" fill="url(#purpleFill)" strokeWidth={2.5} />
                    <Area type="monotone" dataKey="resolved" stroke="#34d399" fill="transparent" strokeWidth={2} />
                  </AreaChart></ResponsiveContainer></div>
                </div>

                <div className="panel agents-overview"><div className="panel-header"><div><h3>AI Agent Network</h3><p>Intelligent workflow status</p></div><span className="online-pill"><i /> Active</span></div>
                  {agents.map(({ name, icon: Icon, color }, i) => <div className="mini-agent" key={name}><div className="mini-agent-icon" style={{ color, background: `${color}18` }}><Icon size={17} /></div><strong>{name}</strong><span className="active-dot" /></div>)}
                  <button className="text-button" onClick={() => setActive("AI Support Chat")}>Explore agent workflow <ArrowUpRight size={15} /></button>
                </div>
              </div>
            </> : active === "Tickets" || active === "Customers" ? (
              <div className="panel tickets-panel"><div className="panel-header"><div><h3>{active === "Tickets" ? "Recent Tickets" : "Recent Customers"}</h3><p>Latest support activity</p></div><button className="secondary-button"><Plus size={16} /> Add New</button></div>
                <div className="table-scroll"><table><thead><tr><th>ID</th><th>Customer</th><th>Issue</th><th>Status</th><th>Priority</th><th>Human Review</th></tr></thead><tbody>
                  {tickets.map((t) => {
                    const id = t.id ?? t.ticket_id;
                    const status = String(t.status || "pending_review").replaceAll("_", " ");
                    const customer = t.customer_id || "Customer";
                    const issue = t.issue || t.description || "Support request";
                    const priority = t.priority || "Medium";
                    const pending = String(t.status || "").toLowerCase().includes("pending");
                    return <tr key={id}>
                      <td className="ticket-id">#{id}</td>
                      <td>{customer}</td>
                      <td>{issue}</td>
                      <td><span className={`status status-${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span></td>
                      <td><span className={`priority priority-${priority.toLowerCase()}`}>{priority}</span></td>
                      <td>{pending && <div style={{ display: "flex", gap: 6 }}>
                        <button className="secondary-button" onClick={() => reviewTicket(id, true)}>Approve</button>
                        <button className="secondary-button" onClick={() => reviewTicket(id, false)}>Reject</button>
                      </div>}</td>
                    </tr>;
                  })}
                  {!tickets.length && <tr><td colSpan="6">{dataLoading ? "Loading tickets..." : "No tickets found."}</td></tr>}
                </tbody></table></div>
              </div>
            ) : active === "Settings" ? (
  <div className="settings-page">
    <div className="settings-section">
      <div className="settings-title">
        <div><h3>Profile Settings</h3><p>Manage your account information.</p></div>
        <Users />
      </div>
      <div className="settings-fields">
        <label>Full Name
          <input value={settings.name} onChange={(e) => updateSetting("name", e.target.value)} />
        </label>
        <label>Email Address
          <input type="email" value={settings.email} onChange={(e) => updateSetting("email", e.target.value)} />
        </label>
      </div>
    </div>

    <div className="settings-section">
      <div className="settings-title">
        <div><h3>Notifications</h3><p>Choose which notifications you receive.</p></div>
        <Bell />
      </div>
      <div className="setting-option">
        <div><strong>Push Notifications</strong><p>Receive updates about support activity.</p></div>
        <input type="checkbox" checked={settings.notifications} onChange={(e) => updateSetting("notifications", e.target.checked)} />
      </div>
      <div className="setting-option">
        <div><strong>Email Alerts</strong><p>Get important ticket updates through email.</p></div>
        <input type="checkbox" checked={settings.emailAlerts} onChange={(e) => updateSetting("emailAlerts", e.target.checked)} />
      </div>
    </div>

    <div className="settings-section">
      <div className="settings-title">
        <div><h3>AI Preferences</h3><p>Configure your intelligent support system.</p></div>
        <Bot />
      </div>
      <div className="setting-option">
        <div><strong>AI Response Review</strong><p>Enable review of AI-generated responses.</p></div>
        <input type="checkbox" checked={settings.aiReview} onChange={(e) => updateSetting("aiReview", e.target.checked)} />
      </div>
    </div>

    <div className="settings-section">
      <div className="settings-title">
        <div><h3>Appearance & Language</h3><p>Customize your workspace experience.</p></div>
        <Settings />
      </div>
      <div className="setting-option">
        <div><strong>Dark Mode</strong><p>Use the dark dashboard appearance.</p></div>
        <input type="checkbox" checked={settings.darkMode} onChange={(e) => updateSetting("darkMode", e.target.checked)} />
      </div>
      <label className="language-setting">Dashboard Language
        <select value={settings.language} onChange={(e) => updateSetting("language", e.target.value)}>
          <option>English</option>
          <option>Hindi</option>
        </select>
      </label>
    </div>

    <div className="settings-save">
      <span>{settingsSaved ? "✓ Settings saved for this session" : "Changes are ready to save."}</span>
      <button className="primary-button" onClick={() => setSettingsSaved(true)}>Save Changes</button>
    </div>
  </div>
) : <div className="panel empty-panel"><Settings size={30} /><h3>Settings</h3></div>}
            {active === "Overview" && <div className="panel tickets-panel recent-panel"><div className="panel-header"><div><h3>Recent Support Tickets</h3><p>Keep track of your latest customer requests</p></div><button className="text-button" onClick={() => setActive("Tickets")}>View all <ArrowUpRight size={15} /></button></div>
              <div className="table-scroll"><table><thead><tr><th>Ticket ID</th><th>Customer</th><th>Issue</th><th>Status</th><th>Priority</th></tr></thead><tbody>
                {tickets.slice(0, 3).map((t) => {
                  const id = t.id ?? t.ticket_id;
                  const status = String(t.status || "pending_review").replaceAll("_", " ");
                  return <tr key={id}><td className="ticket-id">#{id}</td><td>{t.customer_id || "Customer"}</td><td>{t.issue || t.description || "Support request"}</td><td><span className={`status status-${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span></td><td><span className="priority priority-medium">{t.priority || "Medium"}</span></td></tr>;
                })}
              </tbody></table></div>
            </div>}
          </section>
        )}
      </main>
    </div>
  );
}