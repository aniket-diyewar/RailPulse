import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from realtime import RailwayFetcher

st.set_page_config(
    page_title="RailPulse - Nagpur Live",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SKELETON_CARD = """
<div class="skeleton-card" style="background:linear-gradient(135deg,var(--bg-card) 0%,var(--bg-elevated) 100%);border:1px solid var(--border-color);border-radius:12px;padding:16px 18px;margin-bottom:10px;border-left:4px solid var(--border-color);">
    <div style="display:flex;justify-content:space-between;align-items:center;">
        <div class="skeleton-line" style="height:20px;width:55%;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
        <div class="skeleton-line" style="height:20px;width:70px;background:var(--border-color);border-radius:20px;animation:pulse 1.5s ease-in-out infinite;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:8px;">
        <div class="skeleton-line" style="height:14px;width:45%;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
        <div class="skeleton-line" style="height:14px;width:50px;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
    </div>
    <div style="display:flex;gap:16px;margin-top:8px;">
        <div class="skeleton-line" style="height:14px;width:60px;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
        <div class="skeleton-line" style="height:14px;width:80px;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
        <div class="skeleton-line" style="height:14px;width:100px;background:var(--border-color);border-radius:4px;animation:pulse 1.5s ease-in-out infinite;"></div>
    </div>
</div>
"""

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    :root {
        --bg-canvas: #0a0f1a;
        --bg-card: #1e293b;
        --bg-elevated: #0f172a;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --text-heading: #e2e8f0;
        --border-color: #334155;
        --border-hover: #475569;
        --shadow: rgba(0,0,0,0.3);
        --badge-bg-green: #052e16;
        --badge-text-green: #4ade80;
        --badge-bg-yellow: #451a03;
        --badge-text-yellow: #fbbf24;
        --badge-bg-red: #450a0a;
        --badge-text-red: #f87171;
    }
    [data-theme="light"] {
        --bg-canvas: #f1f5f9;
        --bg-card: #ffffff;
        --bg-elevated: #f8fafc;
        --text-primary: #0f172a;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --text-heading: #1e293b;
        --border-color: #e2e8f0;
        --border-hover: #cbd5e1;
        --shadow: rgba(0,0,0,0.06);
        --badge-bg-green: #dcfce7;
        --badge-text-green: #166534;
        --badge-bg-yellow: #fef3c7;
        --badge-text-yellow: #92400e;
        --badge-bg-red: #fee2e2;
        --badge-text-red: #991b1b;
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.25; }
        50% { opacity: 0.6; }
    }
    .main-header {
        background: linear-gradient(135deg, var(--bg-elevated) 0%, var(--bg-card) 50%, var(--bg-elevated) 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 24px var(--shadow);
    }
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-header p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0.3rem 0 0 0;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }
    .train-card {
        background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-elevated) 100%);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
        border-left: 4px solid var(--border-color);
    }
    .train-card:hover {
        border-color: var(--border-hover);
        transform: translateX(4px);
        box-shadow: 0 4px 16px var(--shadow);
    }
    .train-card.on-time  { border-left-color: #22c55e; }
    .train-card.delayed  { border-left-color: #f59e0b; }
    .train-card.cancelled { border-left-color: #ef4444; }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-ontime  { background: var(--badge-bg-green); color: var(--badge-text-green); }
    .badge-delayed { background: var(--badge-bg-yellow); color: var(--badge-text-yellow); }
    .badge-cancelled { background: var(--badge-bg-red); color: var(--badge-text-red); }
    .stat-glow {
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem;
        color: var(--text-secondary);
    }
    .footer-text {
        color: var(--text-muted);
        font-size: 0.75rem;
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
    }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        border: none;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(59,130,246,0.4);
    }
    .stDeployButton { display: none !important; }
    #tabs-bui3-tab-0, #tabs-bui3-tab-1, #tabs-bui3-tab-2, #tabs-bui3-tab-3 { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stToolbarActions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🚆 RailPulse — Nagpur</h1>
    <p>Live train departures from Nagpur Junction (NGP) via NTES</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">🚦 Live Departures</div>', unsafe_allow_html=True)

fetcher = RailwayFetcher()

skeleton_holder = st.empty()
with skeleton_holder.container():
    for _ in range(6):
        st.markdown(SKELETON_CARD, unsafe_allow_html=True)
    st.markdown('<div class="skeleton-line" style="height:40px;width:200px;background:var(--border-color);border-radius:8px;margin:12px auto;animation:pulse 1.5s ease-in-out infinite;"></div>', unsafe_allow_html=True)

live_trains = fetcher.get_live_trains(20)
live_df = pd.DataFrame(live_trains)

skeleton_holder.empty()

src_badge = fetcher.status_text()
src_time = fetcher.last_updated
src_err = fetcher.last_error
src_info = f"{src_badge}"
if src_time:
    src_info += f" &nbsp;|&nbsp; Updated {src_time.strftime('%H:%M:%S')}"
if src_err and not fetcher.is_live:
    src_info += f" &nbsp;|&nbsp; <span style='color:#f87171;'>{src_err}</span>"
st.markdown(f'<div style="text-align:right;color:var(--text-muted);font-size:0.8rem;margin-bottom:0.5rem;">{src_info}</div>', unsafe_allow_html=True)

fetcher_stats = fetcher.current_stats()
mc1, mc2, mc3, mc4 = st.columns(4)
mc1.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🚄 Active Trains</div><div style="font-size:1.8rem;font-weight:700;color:var(--text-primary);">{fetcher_stats["active_trains"]}</div></div>', unsafe_allow_html=True)
mc2.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🟢 On-Time Rate</div><div style="font-size:1.8rem;font-weight:700;color:#4ade80;">{fetcher_stats["on_time_pct"]}%</div></div>', unsafe_allow_html=True)
mc3.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">⏱ Avg Delay</div><div style="font-size:1.8rem;font-weight:700;color:#f59e0b;">{fetcher_stats["avg_delay"]}<span style="font-size:1rem;color:var(--text-muted);"> min</span></div></div>', unsafe_allow_html=True)
mc4.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🔴 Delayed %</div><div style="font-size:1.8rem;font-weight:700;color:#f87171;">{fetcher_stats["delayed_pct"]}%</div></div>', unsafe_allow_html=True)

lc1, lc2 = st.columns([7, 3])

with lc1:
    st.markdown(f"#### Showing {len(live_df)} trains")
    for _, row in live_df.iterrows():
        status_class = row["status"]
        t = pd.Timestamp(row["scheduled_departure"])
        delay_val = int(row.get("simulated_delay", row["delay_minutes"]))

        if status_class == "on_time":
            delay_display = "On Time"
        elif status_class == "delayed":
            delay_display = f"Delayed {delay_val} min"
        else:
            delay_display = "Cancelled"

        badge_class = {"on_time": "badge-ontime", "delayed": "badge-delayed", "cancelled": "badge-cancelled"}[status_class]
        badge_label = {"on_time": "ON TIME", "delayed": "DELAYED", "cancelled": "CANCELLED"}[status_class]

        dist_display = f"{row['distance_km']} km" if row['distance_km'] else "—"

        st.markdown(f"""
        <div class="train-card {status_class}">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="color:var(--text-primary); font-size:1.05rem;">{row['train_name']}</strong>
                    <span style="color:var(--text-muted); font-size:0.8rem;"> #{row['train_id']}</span>
                </div>
                <div><span class="badge {badge_class}">{badge_label}</span></div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:6px; color:var(--text-secondary); font-size:0.85rem;">
                <span>{row['from_station']} → {row['to_station']}</span>
                <span>{dist_display}</span>
            </div>
            <div style="display:flex; gap:16px; margin-top:6px; font-size:0.8rem; color:var(--text-muted);">
                <span>🕐 {t.strftime('%H:%M')}</span>
                <span>🚉 Pltf {row['platform']}</span>
                <span>⏱ <strong style="color:{'#4ade80' if delay_val <= 3 else '#f59e0b' if delay_val <= 15 else '#ef4444'};">{delay_display}</strong></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Refresh Feed", width='stretch', type="secondary"):
        st.rerun()

with lc2:
    if len(live_df) > 0:
        status_counts = live_df["status"].value_counts()
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Status Distribution",
            color_discrete_map={"on_time": "#22c55e", "delayed": "#f59e0b", "cancelled": "#ef4444"},
            hole=0.5
        )
        fig_pie.update_layout(
            template="plotly_dark",
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            showlegend=True,
            legend=dict(orientation="h", y=1.1, font=dict(size=10))
        )
        st.plotly_chart(fig_pie, width='stretch', config={'displayModeBar': False})

        delay_hist = px.histogram(
            live_df, x="delay_minutes", nbins=12,
            title="Delay Distribution",
            color_discrete_sequence=["#3b82f6"],
            labels={"delay_minutes": "Minutes"}
        )
        delay_hist.update_layout(
            template="plotly_dark",
            margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            showlegend=False
        )
        st.plotly_chart(delay_hist, width='stretch', config={'displayModeBar': False})

st.markdown("""
<div class="footer-text">
    RailPulse &bull; Live NTES data from Nagpur Junction (NGP) &bull; v2.0
</div>
""", unsafe_allow_html=True)
