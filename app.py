import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json

from utils.analytics import (
    load_data, station_stats, peak_hour_analysis, weather_impact,
    hourly_pattern, top_routes, overall_summary, monthly_trend
)
from utils.simulation import RailSimulator
from model.predictor import DelayPredictor

st.set_page_config(
    page_title="RailPulse - Railway Intelligence",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def get_data():
    return load_data()

@st.cache_resource
def get_predictor():
    return DelayPredictor()

@st.cache_resource
def get_simulator():
    return RailSimulator()

df = get_data()
predictor = get_predictor()
simulator = get_simulator()
summary = overall_summary(df)

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
        --sidebar-bg: linear-gradient(180deg, #0a0f1a 0%, #0f172a 100%);
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
        --sidebar-bg: linear-gradient(180deg, #f1f5f9 0%, #ffffff 100%);
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

    .stat-glow {
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        background: var(--bg-card);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: var(--bg-canvas);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        color: var(--text-muted);
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        color: #60a5fa !important;
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

    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg);
        border-right: 1px solid var(--border-color);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🚆 RailPulse</h1>
    <p>Real-Time Railway Performance Intelligence &bull; Delay Prediction &bull; Analytics</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="text-align:center; padding: 0.5rem 0;">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/null/train.png", width=70)
    st.markdown("<h2 style='color:var(--text-primary); font-weight:700; margin:0;'>RailPulse</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 📊 System Overview")
    st.markdown(f"""
    <div style="background:var(--bg-card); border-radius:10px; padding:12px; margin-bottom:12px;">
        <div style="display:flex; justify-content:space-between; color:var(--text-secondary); font-size:0.85rem;">
            <span>Total Records</span><span style="color:var(--text-primary);font-weight:600;">{len(df):,}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:var(--text-secondary); font-size:0.85rem;">
            <span>Stations</span><span style="color:var(--text-primary);font-weight:600;">{df['from_station'].nunique()}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:var(--text-secondary); font-size:0.85rem;">
            <span>Routes</span><span style="color:var(--text-primary);font-weight:600;">{df.groupby(['from_station','to_station']).ngroups}</span>
        </div>
        <div style="display:flex; justify-content:space-between; color:var(--text-secondary); font-size:0.85rem;">
            <span>Period</span><span style="color:var(--text-primary);font-weight:600;">{df['scheduled_departure'].min().strftime('%b %Y')} - {df['scheduled_departure'].max().strftime('%Y')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🎯 Network Health")
    cola, colb, colc = st.columns(3)
    cola.markdown(f"<div style='text-align:center;background:var(--badge-bg-green);border-radius:8px;padding:8px;'><span style='color:var(--badge-text-green);font-size:1.3rem;font-weight:700;'>{summary['on_time_pct']}%</span><br><span style='color:var(--text-secondary);font-size:0.7rem;'>On-Time</span></div>", unsafe_allow_html=True)
    colb.markdown(f"<div style='text-align:center;background:var(--badge-bg-yellow);border-radius:8px;padding:8px;'><span style='color:var(--badge-text-yellow);font-size:1.3rem;font-weight:700;'>{summary['delayed_pct']}%</span><br><span style='color:var(--text-secondary);font-size:0.7rem;'>Delayed</span></div>", unsafe_allow_html=True)
    colc.markdown(f"<div style='text-align:center;background:var(--badge-bg-red);border-radius:8px;padding:8px;'><span style='color:var(--badge-text-red);font-size:1.3rem;font-weight:700;'>{summary['cancelled_pct']}%</span><br><span style='color:var(--text-secondary);font-size:0.7rem;'>Cancelled</span></div>", unsafe_allow_html=True)

    if "avg_delay" in summary:
        st.markdown(f"""
        <div style="margin-top:12px;background:var(--bg-card);border-radius:10px;padding:12px;text-align:center;">
            <span style="color:var(--text-secondary);font-size:0.8rem;">Average Delay</span><br>
            <span style="color:#f59e0b;font-size:1.8rem;font-weight:700;">{summary['avg_delay']}</span><span style="color:var(--text-muted);"> min</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:var(--text-muted); font-size:0.75rem; text-align:center;">
        Built with ❤️ for Railways Hackathon<br>
        v1.0 &bull; RailPulse
    </div>
    """, unsafe_allow_html=True)

tabs = st.tabs([
    "🚦 Live Dashboard",
    "🔮 Delay Prediction",
    "📈 Analytics",
    "🗺️ Route Network",
    "ℹ️ About"
])

with tabs[0]:
    st.markdown('<div class="section-title">🚦 Live Train Status Dashboard</div>', unsafe_allow_html=True)

    sim_stats = simulator.current_stats()
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🚄 Active Trains</div><div style="font-size:1.8rem;font-weight:700;color:var(--text-primary);">{sim_stats["active_trains"]}</div></div>', unsafe_allow_html=True)
    mc2.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🟢 On-Time Rate</div><div style="font-size:1.8rem;font-weight:700;color:#4ade80;">{sim_stats["on_time_pct"]}%</div></div>', unsafe_allow_html=True)
    mc3.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">⏱ Avg Delay</div><div style="font-size:1.8rem;font-weight:700;color:#f59e0b;">{sim_stats["avg_delay"]}<span style="font-size:1rem;color:var(--text-muted);"> min</span></div></div>', unsafe_allow_html=True)
    mc4.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.85rem;">🔴 Delayed %</div><div style="font-size:1.8rem;font-weight:700;color:#f87171;">{sim_stats["delayed_pct"]}%</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 1])
    with c2:
        filter_status = st.selectbox("Filter by status", ["All", "on_time", "delayed", "cancelled"])
        search_query = st.text_input("🔍 Search train name or ID", placeholder="e.g. Rajdhani")
    with c1:
        pass

    live_trains = simulator.get_live_trains(20)
    live_df = pd.DataFrame(live_trains)

    if filter_status != "All":
        live_df = live_df[live_df["status"] == filter_status]
    if search_query:
        mask = live_df["train_name"].str.contains(search_query, case=False) | live_df["train_id"].str.contains(search_query)
        live_df = live_df[mask]

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
                    <span>{row['distance_km']} km</span>
                </div>
                <div style="display:flex; gap:16px; margin-top:6px; font-size:0.8rem; color:var(--text-muted);">
                    <span>🕐 {t.strftime('%H:%M')}</span>
                    <span>🌤 {row['weather']}</span>
                    <span>⏱ <strong style="color:{'#4ade80' if delay_val <= 3 else '#f59e0b' if delay_val <= 15 else '#ef4444'};">{delay_display}</strong></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Refresh Feed", width='stretch', type="secondary"):
            st.rerun()

    with lc2:
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

with tabs[1]:
    st.markdown('<div class="section-title">🔮 Train Delay Predictor</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:var(--text-secondary); margin-bottom:1.5rem;">Predict delays using ML — trained on historical patterns, weather, and congestion data.</p>', unsafe_allow_html=True)

    stations = sorted(df["from_station"].unique().tolist())
    train_names = sorted(df["train_name"].unique().tolist())

    pc1, pc2 = st.columns(2)
    with pc1:
        from_st = st.selectbox("🚉 From Station", stations, index=stations.index("New Delhi") if "New Delhi" in stations else 0, key="pred_from")
        dep_date = st.date_input("📅 Departure Date", datetime.now(), key="pred_date")
        dep_hour = st.slider("🕐 Departure Hour", 0, 23, 8, key="pred_hour")
        weather = st.selectbox("🌤 Weather Condition", ["clear", "rain", "fog", "storm"], key="pred_weather")

    with pc2:
        to_st = st.selectbox("🚉 To Station", stations, index=stations.index("Mumbai Central") if "Mumbai Central" in stations else 1, key="pred_to")
        train_name = st.selectbox("🚄 Train Name", train_names, index=0, key="pred_train")
        congestion = st.slider("🚦 Congestion Index", 0.5, 2.0, 1.0, 0.1, key="pred_cong")

    route_match = df[(df["from_station"] == from_st) & (df["to_station"] == to_st)]
    if len(route_match) > 0:
        dist = int(route_match["distance_km"].iloc[0])
    else:
        dist = st.number_input("📏 Distance (km)", 100, 3000, 500, key="pred_dist")

    is_peak = 1 if (7 <= dep_hour <= 10) or (16 <= dep_hour <= 20) else 0
    dow = dep_date.weekday()
    month = dep_date.month

    if st.button("🔮 Predict Delay", type="primary", width='stretch'):
        result = predictor.predict(
            from_station=from_st, to_station=to_st, distance_km=dist,
            hour=dep_hour, day_of_week=dow, month=month,
            is_peak_hour=is_peak, weather=weather,
            train_name=train_name, congestion_index=congestion
        )

        delay = result["predicted_delay_minutes"]
        will_delay = result["will_be_delayed"]

        res1, res2, res3 = st.columns(3)
        with res1:
            if will_delay:
                st.markdown(f"""
                <div style="background:var(--badge-bg-red);border:1px solid var(--badge-bg-red);border-radius:12px;padding:20px;text-align:center;">
                    <div style="font-size:2.5rem;">⚠️</div>
                    <div style="color:var(--badge-text-red);font-size:1.3rem;font-weight:700;">Delayed</div>
                    <div style="color:var(--badge-text-red);font-size:1.1rem;opacity:0.8;">~{delay} minutes</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:var(--badge-bg-green);border:1px solid var(--badge-bg-green);border-radius:12px;padding:20px;text-align:center;">
                    <div style="font-size:2.5rem;">✅</div>
                    <div style="color:var(--badge-text-green);font-size:1.3rem;font-weight:700;">On Time</div>
                    <div style="color:var(--badge-text-green);font-size:1.1rem;opacity:0.8;">~{delay} min delay expected</div>
                </div>
                """, unsafe_allow_html=True)

        with res2:
            risk = "Low" if delay <= 8 else ("Moderate" if delay <= 20 else "High")
            risk_color = {"Low": "#4ade80", "Moderate": "#f59e0b", "High": "#ef4444"}
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border-color);border-radius:12px;padding:20px;text-align:center;">
                <div style="color:var(--text-secondary);font-size:0.85rem;">Delay Risk</div>
                <div style="color:{risk_color[risk]};font-size:2rem;font-weight:700;">{risk}</div>
                <div style="color:var(--text-muted);font-size:0.85rem;">{delay} min predicted</div>
            </div>
            """, unsafe_allow_html=True)

        with res3:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border-color);border-radius:12px;padding:20px;text-align:center;">
                <div style="color:var(--text-secondary);font-size:0.85rem;">Route Info</div>
                <div style="color:var(--text-primary);font-size:1.1rem;font-weight:600;">{dist} km</div>
                <div style="color:var(--text-muted);font-size:0.85rem;">{'Peak Hour' if is_peak else 'Off-Peak'} &bull; {weather}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📊 Historical Context")
        hour_delays = df.groupby("hour")["delay_minutes"].mean().reset_index()
        fig_hour = px.bar(
            hour_delays, x="hour", y="delay_minutes",
            title="Avg Delay by Hour (your departure marked)",
            labels={"hour": "Hour", "delay_minutes": "Avg Delay (min)"},
            color="delay_minutes", color_continuous_scale="RdYlGn_r"
        )
        fig_hour.add_vline(x=dep_hour, line_dash="dash", line_color="white",
                           annotation_text="Your departure", annotation_position="top",
                           annotation_font_color="white")
        fig_hour.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        weather_ctx = df.groupby("weather")["delay_minutes"].mean().reset_index()
        fig_weather = px.bar(
            weather_ctx, x="weather", y="delay_minutes",
            title="Avg Delay by Weather",
            color="delay_minutes", color_continuous_scale="RdYlGn_r",
            text_auto=".1f"
        )
        fig_weather.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        c1, c2 = st.columns(2)
        c1.plotly_chart(fig_hour, width='stretch', config={'displayModeBar': False})
        c2.plotly_chart(fig_weather, width='stretch', config={'displayModeBar': False})
    else:
        st.info("👆 Select parameters above and click **Predict Delay**")

with tabs[2]:
    st.markdown('<div class="section-title">📈 Railway Analytics</div>', unsafe_allow_html=True)

    view = st.radio(
        "Select View",
        ["📊 Overview", "🏢 Stations", "🌤 Weather", "🕐 Peak Hours", "🛤 Routes", "📅 Monthly Trend"],
        horizontal=True, label_visibility="collapsed"
    )

    if view == "📊 Overview":
        r1, r2, r3, r4 = st.columns(4)
        r1.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.8rem;">Total Trains</div><div style="font-size:2rem;font-weight:700;color:var(--text-primary);">{summary["total_trains"]:,}</div></div>', unsafe_allow_html=True)
        r2.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.8rem;">On-Time Rate</div><div style="font-size:2rem;font-weight:700;color:#4ade80;">{summary["on_time_pct"]}%</div></div>', unsafe_allow_html=True)
        r3.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.8rem;">Avg Delay</div><div style="font-size:2rem;font-weight:700;color:#f59e0b;">{summary["avg_delay"]}<span style="font-size:1rem;color:var(--text-muted);"> min</span></div></div>', unsafe_allow_html=True)
        r4.markdown(f'<div class="stat-glow"><div style="color:var(--text-secondary);font-size:0.8rem;">Max Delay</div><div style="font-size:2rem;font-weight:700;color:#ef4444;">{summary["max_delay"]}<span style="font-size:1rem;color:var(--text-muted);"> min</span></div></div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        sd = df["status"].value_counts().reset_index()
        sd.columns = ["status", "count"]
        fig1 = px.bar(
            sd, x="status", y="count", title="Status Distribution",
            color="status",
            color_discrete_map={"on_time": "#22c55e", "delayed": "#f59e0b", "cancelled": "#ef4444"},
            text_auto=True
        )
        fig1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c1.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})

        dh = px.histogram(df, x="delay_minutes", nbins=40, title="Delay Distribution (all trains)",
                          color_discrete_sequence=["#3b82f6"])
        dh.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c2.plotly_chart(dh, width='stretch', config={'displayModeBar': False})

    elif view == "🏢 Stations":
        ss = station_stats(df).reset_index()
        ss.columns = ["Station", "Avg Delay", "Max Delay", "Train Count"]
        fig = px.bar(
            ss.head(15), x="Station", y="Avg Delay",
            title="Top 15 Stations by Avg Delay",
            color="Avg Delay", color_continuous_scale="RdYlGn_r",
            text_auto=".1f"
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-30)
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        st.dataframe(
            ss.style.format({"Avg Delay": "{:.1f}", "Max Delay": "{:.1f}"}),
            width='stretch', hide_index=True
        )

        csv = ss.to_csv(index=False).encode()
        st.download_button("📥 Download CSV", csv, "station_delays.csv", "text/csv")

    elif view == "🌤 Weather":
        wi = weather_impact(df).reset_index()
        c1, c2 = st.columns(2)
        fig = px.bar(
            wi, x="weather", y="avg_delay", title="Avg Delay by Weather",
            color="avg_delay", color_continuous_scale="RdYlGn_r",
            text_auto=".1f"
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c1.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        fig2 = px.scatter(
            wi, x="count", y="delay_rate", size="avg_delay",
            color="weather", text="weather",
            title="Frequency vs Delay Rate",
            labels={"count": "Trains", "delay_rate": "Delay Rate"},
            size_max=60
        )
        fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c2.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})

    elif view == "🕐 Peak Hours":
        hp = hourly_pattern(df).reset_index()
        fig = px.line(
            hp, x="hour", y="avg_delay", title="Avg Delay Throughout the Day",
            markers=True, labels={"hour": "Hour", "avg_delay": "Avg Delay (min)"}
        )
        fig.add_vrect(x0=7, x1=10, fillcolor="red", opacity=0.08, annotation_text="Morning Peak", annotation_position="top left")
        fig.add_vrect(x0=16, x1=20, fillcolor="red", opacity=0.08, annotation_text="Evening Peak", annotation_position="top left")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

        c1, c2 = st.columns(2)
        pa = peak_hour_analysis(df).reset_index()
        pa["is_peak_hour"] = pa["is_peak_hour"].map({0: "Off-Peak", 1: "Peak Hours"})
        fig2 = px.bar(
            pa, x="is_peak_hour", y="avg_delay", title="Peak vs Off-Peak",
            color="is_peak_hour", text_auto=".1f",
            color_discrete_map={"Peak Hours": "#ef4444", "Off-Peak": "#22c55e"}
        )
        fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        c1.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=pa["is_peak_hour"], y=pa["delay_rate"],
            text=pa["delay_rate"].apply(lambda x: f"{x:.0%}"),
            textposition="outside",
            marker_color=["#22c55e", "#ef4444"]
        ))
        fig3.update_layout(title="Delay Rate", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", yaxis_tickformat=".0%")
        c2.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})

    elif view == "🛤 Routes":
        tr = top_routes(df).reset_index()
        tr["route"] = tr["from_station"] + " → " + tr["to_station"]
        fig = px.bar(
            tr, x="route", y="avg_delay", title="Top 10 Most Delayed Routes",
            color="avg_delay", color_continuous_scale="RdYlGn_r",
            text_auto=".1f"
        )
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=-30)
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
        st.dataframe(tr[["route", "avg_delay", "total_trains"]], width='stretch', hide_index=True)

    elif view == "📅 Monthly Trend":
        mt = monthly_trend(df).reset_index()
        mt["month_name"] = mt["month"].apply(lambda m: datetime(2025, m, 1).strftime("%b"))
        c1, c2 = st.columns(2)
        fig1 = px.line(
            mt, x="month_name", y="avg_delay", title="Avg Delay by Month",
            markers=True, text="avg_delay",
            labels={"month_name": "", "avg_delay": "Avg Delay (min)"}
        )
        fig1.update_traces(textposition="top center", line_color="#f59e0b")
        fig1.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c1.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})

        fig2 = px.bar(
            mt, x="month_name", y="delay_rate", title="Delay Rate by Month",
            color="delay_rate", color_continuous_scale="RdYlGn_r",
            text_auto=".0%",
            labels={"month_name": "", "delay_rate": "Delay Rate"}
        )
        fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        c2.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})

with tabs[3]:
    st.markdown('<div class="section-title">🗺️ Railway Network Map</div>', unsafe_allow_html=True)

    city_coords = {
        "New Delhi": (28.6139, 77.2090),
        "Mumbai Central": (19.0760, 72.8777),
        "Howrah": (22.5958, 88.2636),
        "Chennai Central": (13.0827, 80.2707),
        "Bengaluru City": (12.9716, 77.5946),
        "Secunderabad": (17.3850, 78.4867),
        "Ahmedabad": (23.0225, 72.5714),
        "Jaipur": (26.9124, 75.7873),
        "Lucknow": (26.8467, 80.9462),
        "Patna": (25.5941, 85.1376),
        "Bhopal": (23.2599, 77.4126),
        "Chandigarh": (30.7333, 76.7794),
        "Pune": (18.5204, 73.8567),
        "Kolkata": (22.5726, 88.3639),
        "Thiruvananthapuram": (8.5241, 76.9366),
        "Guwahati": (26.1445, 91.7362),
        "Bhubaneswar": (20.2961, 85.8245),
        "Jodhpur": (26.2389, 73.0243),
        "Varanasi": (25.3176, 82.9739),
        "Nagpur": (21.1458, 79.0882),
    }

    try:
        import folium
        from streamlit_folium import st_folium

        station_delays = df.groupby("from_station")["delay_minutes"].mean().to_dict()

        m = folium.Map(location=[22.5, 80.0], zoom_start=5, tiles="cartodb dark_matter")

        for city, (lat, lon) in city_coords.items():
            delay = station_delays.get(city, 0)
            if delay > 20:
                color, icon = "red", "exclamation-triangle"
            elif delay > 10:
                color, icon = "orange", "train"
            else:
                color, icon = "green", "check-circle"

            folium.Marker(
                [lat, lon],
                popup=folium.Popup(f"<b>{city}</b><br>Avg Delay: {delay:.1f} min", max_width=200),
                tooltip=city,
                icon=folium.Icon(color=color, icon=icon, prefix="fa"),
            ).add_to(m)

        route_delays = df.groupby(["from_station", "to_station"])["delay_minutes"].mean().reset_index()
        for _, route in route_delays.iterrows():
            frm, to = route["from_station"], route["to_station"]
            if frm in city_coords and to in city_coords:
                d = route["delay_minutes"]
                if d > 15:
                    dash, w, col = "2, 4", 2, "#ef4444"
                elif d > 8:
                    dash, w, col = "5, 5", 1.5, "#f59e0b"
                else:
                    dash, w, col = "0", 1, "#22c55e"
                folium.PolyLine(
                    [city_coords[frm], city_coords[to]],
                    color=col, weight=w, dash_array=dash, opacity=0.6,
                    popup=f"{frm} ↔ {to}<br>Avg Delay: {d:.1f}min",
                ).add_to(m)

        st_folium(m, width=None, height=600)
    except ImportError:
        st.info("Install folium and streamlit-folium: `pip install folium streamlit-folium`")

with tabs[4]:
    st.markdown('<div class="section-title">ℹ️ About RailPulse</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("""
        **RailPulse** is an AI-powered Railway Intelligence System built for the Railways Hackathon.

        It combines **machine learning**, **real-time simulation**, and **interactive analytics**
        to help railway operators monitor performance and predict delays.

        ### 🚀 Key Features
        - **Real-Time Monitoring** — Simulated live train feed with search &amp; filters
        - **ML Delay Prediction** — Random Forest model (73% accuracy, ~8 min MAE)
        - **Analytics Suite** — Station, weather, peak hour, route, and monthly trends
        - **Interactive Route Map** — Folium network with delay heat markers
        - **Smart Filters** — Search, filter, and export capabilities
        """)

    with c2:
        st.markdown("""
        ### 🛠 Tech Stack
        | Component | Technology |
        |---|---|
        | Frontend | Streamlit |
        | ML | Scikit-learn |
        | Data | Pandas, NumPy |
        | Viz | Plotly, Folium |
        | Storage | Apache Parquet |

        ### 📦 Dataset
        5,000+ train records across 20 major Indian stations,
        20+ train types, 4 weather conditions.

        ### 🚀 Run It
        ```
        streamlit run app.py
        ```
        """)

    st.markdown("""
    <div class="footer-text">
        RailPulse v1.0 &bull; Built for Railways Hackathon
    </div>
    """, unsafe_allow_html=True)
