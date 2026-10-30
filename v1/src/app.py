"""
Interactive Streamlit Analytics Dashboard for Databricks Gold Star Schema Data Warehouse.
Answers Business Questions Q1 to Q31 across 7 Pages with live OLAP capabilities.
"""

import sys
import os
from pathlib import Path

# Add v1 to sys.path so imports work seamlessly
V1_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(V1_DIR))

import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from src.data_loader import get_cached_cubes_and_sample, build_and_cache_olap_cubes, is_databricks_configured

# Set page config
st.set_page_config(
    page_title="US BTS Flight Delay Analytics | Databricks Gold",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1.05rem; color: #4B5563; margin-bottom: 1.2rem; }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-databricks {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
    }
    .analytical-rule {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        margin-bottom: 12px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Data Loading & Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Connecting to Databricks Gold Warehouse...")
def load_data(force_refresh=False):
    return get_cached_cubes_and_sample(force_refresh=force_refresh)


try:
    cubes, df_sample, data_source_desc = load_data()
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# Sidebar Navigation & Global Filters
# -----------------------------------------------------------------------------
st.sidebar.image("https://raw.githubusercontent.com/databricks/universe/main/databricks-logo.png", width=180) if False else None
st.sidebar.markdown(f"""
<div style="margin-bottom: 14px;">
    <span class="badge-databricks">🟢 Databricks Unity Catalog</span>
    <p style="font-size: 0.8rem; color: #6B7280; margin-top: 4px;">
        Catalog: <code>flight_delay_dwm.gold</code><br>
        Source Volume: <b>30,742,408 Flights</b>
    </p>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🔄 Sync Live from Databricks"):
    st.cache_data.clear()
    with st.spinner("Executing queries across 30.7M flights in Databricks SQL Warehouse..."):
        build_and_cache_olap_cubes()
    st.success("Successfully synced fresh cubes from Databricks!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Navigation")
page = st.sidebar.radio(
    "Select Dashboard Page:",
    [
        "Page 1 — Executive Overview",
        "Page 2 — Airline Performance",
        "Page 3 — Airport & Route Analysis",
        "Page 4 — Time & Operational Patterns",
        "Page 5 — Delay Causes & Disruptions",
        "Page 6 — Historical Delay Risk",
        "Page 7 — OLAP Explorer",
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Global Slicers & Filters")
st.sidebar.caption("Applies to interactive views and drill-throughs")

all_airlines = sorted(df_sample["reporting_airline"].dropna().unique().tolist())
selected_airlines = st.sidebar.multiselect("Reporting Airline", all_airlines, default=[])

all_years = sorted(df_sample["year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect("Year", all_years, default=all_years)

all_months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
selected_months = st.sidebar.multiselect("Month", all_months, default=[])

min_vol_threshold = st.sidebar.slider("Min Flight Volume (Rankings)", min_value=100, max_value=5000, value=1000, step=100)

# Filter df_sample according to slicers
filtered_sample = df_sample.copy()
if selected_airlines:
    filtered_sample = filtered_sample[filtered_sample["reporting_airline"].isin(selected_airlines)]
if selected_years:
    filtered_sample = filtered_sample[filtered_sample["year"].isin(selected_years)]
if selected_months:
    filtered_sample = filtered_sample[filtered_sample["month_name"].isin(selected_months)]


# =============================================================================
# PAGE 1 — EXECUTIVE OVERVIEW (Q1–Q4)
# =============================================================================
if page == "Page 1 — Executive Overview":
    st.markdown('<div class="main-header">Page 1 — Executive Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Audience: Airline executives, operations managers, and transport analysts</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="analytical-rule">
        <b>Non-Negotiable BTS Rules Applied:</b><br>
        • Cancelled flights are excluded from the arrival delay denominator (Eligible Arrivals = Completed Flights with Arrival Data).<br>
        • Delay Rate = Arrivals delayed ≥ 15 minutes ÷ Eligible Arrivals (BTS Standard).<br>
        • Signed delay includes early arrivals; Positive delay isolates minutes behind schedule.
    </div>
    """, unsafe_allow_html=True)

    kpi = cubes["kpis"]
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Arrival Delay Rate (Q1)", f"{kpi['arr_delay_rate']}%", help="Delayed ≥15m / Eligible Arrivals")
        st.caption(f"Denominator: {kpi['eligible_arrivals']:,} eligible arrivals")
    with c2:
        st.metric("Avg Arrival Delay", f"{kpi['avg_arrival_delay_signed']} min", help="Signed average (includes early flights)")
        st.caption(f"Positive-only avg: {kpi['avg_arrival_delay_positive']} min")
    with c3:
        st.metric("Cancellation Rate (Q3)", f"{kpi['cancel_rate']}%", f"{kpi['cancelled_flights']:,} flights")
        st.caption(f"Diversion rate: {kpi['divert_rate']}% ({kpi['diverted_flights']:,} flights)")
    with c4:
        st.metric("Total Flight Population", f"{kpi['total_flights']:,}", "100% Census")
        st.caption(f"Total delay burden: {int(kpi['total_delay_burden_minutes']):,} min")

    st.markdown("---")

    # Q2: Delays Over Time
    st.subheader("Q2. How Have Flight Delays Changed Over Time?")
    st.caption("Monthly and yearly trends for delay rate, average arrival delay, cancellations, and diversions (30.7M Census)")
    
    df_trend = pd.DataFrame(cubes["monthly_trend"])
    df_trend["period"] = df_trend["year"].astype(str) + " " + df_trend["month_name"].str[:3]

    tab_trend1, tab_trend2 = st.tabs(["Delay Rate (%) & Average Delay (min)", "Cancellations & Diversions (%)"])
    with tab_trend1:
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=df_trend["period"], y=df_trend["delay_rate"],
            name="Arrival Delay Rate (%)", marker_color="#2563EB", yaxis="y1"
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_trend["period"], y=df_trend["avg_arrival_delay"],
            name="Avg Delay (min)", mode="lines+markers", line=dict(color="#DC2626", width=3), yaxis="y2"
        ))
        fig_trend.update_layout(
            title="Monthly Delay Rate (%) and Average Arrival Delay (Minutes)",
            xaxis_title="Month",
            yaxis=dict(title="Arrival Delay Rate (%)", side="left"),
            yaxis2=dict(title="Average Arrival Delay (Minutes)", overlaying="y", side="right"),
            legend=dict(x=0.01, y=0.99),
            height=420
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab_trend2:
        fig_disrupt = px.line(
            df_trend, x="period", y=["cancel_rate", "divert_rate"],
            labels={"value": "Disruption Rate (%)", "period": "Month", "variable": "Disruption Type"},
            title="Monthly Cancellation Rate (%) and Diversion Rate (%)",
            color_discrete_map={"cancel_rate": "#DC2626", "divert_rate": "#F59E0B"}
        )
        st.plotly_chart(fig_disrupt, use_container_width=True)

    st.markdown("---")

    col_q3, col_q4 = st.columns(2)
    with col_q3:
        st.subheader("Q3. Flight Outcomes Breakdown")
        st.caption("Distribution across all 30,742,408 recorded operations")
        
        outcomes_data = [
            {"Outcome": "On-Time / Early (<15m)", "Count": kpi["ontime_early_arrivals"], "Color": "#10B981"},
            {"Outcome": "Delayed (>=15m)", "Count": kpi["delayed_arrivals"], "Color": "#F59E0B"},
            {"Outcome": "Cancelled", "Count": kpi["cancelled_flights"], "Color": "#EF4444"},
            {"Outcome": "Diverted", "Count": kpi["diverted_flights"], "Color": "#6B7280"},
        ]
        df_outcomes = pd.DataFrame(outcomes_data)
        fig_pie = px.pie(
            df_outcomes, values="Count", names="Outcome",
            title="Population Outcome Breakdown",
            color="Outcome",
            color_discrete_map={d["Outcome"]: d["Color"] for d in outcomes_data},
            hole=0.45
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_q4:
        st.subheader("Q4. Top Delay Burden Contributors")
        st.caption("Airlines ranked by total positive delay minutes (cumulative burden)")
        df_air = pd.DataFrame(cubes["airline_performance"]).head(8)
        fig_burden = px.bar(
            df_air, x="reporting_airline", y="total_delay_minutes_positive",
            labels={"reporting_airline": "Carrier", "total_delay_minutes_positive": "Total Delay Minutes"},
            title="Total Positive Delay Minutes by Carrier (Millions of Minutes)",
            color="total_delay_minutes_positive",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_burden, use_container_width=True)


# =============================================================================
# PAGE 2 — AIRLINE PERFORMANCE (Q5–Q9)
# =============================================================================
elif page == "Page 2 — Airline Performance":
    st.markdown('<div class="main-header">Page 2 — Airline Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comparative evaluation across reporting carriers</div>', unsafe_allow_html=True)

    df_air = pd.DataFrame(cubes["airline_performance"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Q5. Highest Arrival Delay Rates")
        st.caption("Percentage of eligible arrivals delayed ≥15 minutes (with flight counts)")
        fig_q5 = px.bar(
            df_air.sort_values("delay_rate", ascending=True),
            x="delay_rate", y="reporting_airline", orientation="h",
            text="delay_rate",
            labels={"delay_rate": "Delay Rate (%)", "reporting_airline": "Airline"},
            color="delay_rate", color_continuous_scale="Reds"
        )
        fig_q5.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_q5, use_container_width=True)

    with c2:
        st.subheader("Q6. Average Arrival Delay (Minutes)")
        st.caption("Comparison between Signed (includes early arrivals) and Positive-Only delays")
        fig_q6 = go.Figure()
        fig_q6.add_trace(go.Bar(
            x=df_air["reporting_airline"], y=df_air["avg_arr_delay_pos"],
            name="Positive-Only Avg Delay (min)", marker_color="#DC2626"
        ))
        fig_q6.add_trace(go.Bar(
            x=df_air["reporting_airline"], y=df_air["avg_arr_delay_signed"],
            name="Signed Avg Delay (min)", marker_color="#3B82F6"
        ))
        fig_q6.update_layout(barmode="group", xaxis_title="Airline", yaxis_title="Minutes", height=420)
        st.plotly_chart(fig_q6, use_container_width=True)

    st.markdown("---")

    col_q7, col_q8 = st.columns(2)
    with col_q7:
        st.subheader("Q7. Total Delay Burden by Airline")
        st.caption("Cumulative signed vs positive-only minutes generated across network")
        fig_q7 = px.bar(
            df_air, x="reporting_airline", y=["total_delay_minutes_positive", "total_delay_minutes_signed"],
            barmode="group", labels={"value": "Total Minutes", "reporting_airline": "Airline", "variable": "Metric"},
            title="Signed vs Positive Total Delay Minutes by Airline"
        )
        st.plotly_chart(fig_q7, use_container_width=True)

    with col_q8:
        st.subheader("Q8. Cancellation & Diversion Rates")
        st.caption("Disruption rates with total scheduled flights as the denominator")
        fig_q8 = px.scatter(
            df_air, x="cancel_rate", y="divert_rate", size="total_flights",
            text="reporting_airline", color="delay_rate",
            labels={"cancel_rate": "Cancellation Rate (%)", "divert_rate": "Diversion Rate (%)"},
            title="Cancellation Rate vs Diversion Rate (Bubble size = Flight Volume)"
        )
        fig_q8.update_traces(textposition="top center")
        st.plotly_chart(fig_q8, use_container_width=True)

    st.markdown("---")
    st.subheader("Q9. Airline Performance Drill-down")
    st.caption("Inspect how a specific airline's performance varies across months, weekdays, or departure hours")
    selected_carrier = st.selectbox("Select Carrier to Inspect:", sorted(df_air["reporting_airline"].unique()), index=0)

    sub_carrier = filtered_sample[filtered_sample["reporting_airline"] == selected_carrier]
    if len(sub_carrier) > 0:
        c_m1, c_m2 = st.columns(2)
        with c_m1:
            dow_perf = sub_carrier.groupby("day_name").agg(
                delay_rate=("arr_del15", lambda x: round(np.mean(x) * 100, 2)),
                flights=("flight_key", "count")
            ).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).reset_index()
            fig_dow = px.bar(dow_perf, x="day_name", y="delay_rate", title=f"{selected_carrier}: Delay Rate by Day of Week", labels={"day_name": "Weekday", "delay_rate": "Delay Rate (%)"})
            st.plotly_chart(fig_dow, use_container_width=True)
        with c_m2:
            hour_perf = sub_carrier.groupby("departure_hour").agg(
                delay_rate=("arr_del15", lambda x: round(np.mean(x) * 100, 2)),
                flights=("flight_key", "count")
            ).reset_index()
            fig_hr = px.line(hour_perf, x="departure_hour", y="delay_rate", markers=True, title=f"{selected_carrier}: Delay Rate by Scheduled Hour", labels={"departure_hour": "Departure Hour", "delay_rate": "Delay Rate (%)"})
            st.plotly_chart(fig_hr, use_container_width=True)
    else:
        st.info("No sample flights found for current filter selection.")


# =============================================================================
# PAGE 3 — AIRPORT AND ROUTE ANALYSIS (Q10–Q14)
# =============================================================================
elif page == "Page 3 — Airport & Route Analysis":
    st.markdown('<div class="main-header">Page 3 — Airport & Route Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Origin departure bottlenecks, destination arrival congestion, and route reliability</div>', unsafe_allow_html=True)

    df_orig = pd.DataFrame(cubes["origin_airports"])
    df_dest = pd.DataFrame(cubes["dest_airports"])
    df_routes = pd.DataFrame(cubes["routes"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Q10. Worst Origin Airports (Departure Delays)")
        st.caption("Airports with highest percentage of departures delayed ≥15 minutes (Min 1,000 flights)")
        fig_q10 = px.bar(
            df_orig.head(10).sort_values("dep_delay_rate", ascending=True),
            x="dep_delay_rate", y="origin_airport_code", orientation="h",
            text="dep_delay_rate", hover_data=["origin_city_name", "eligible_departures", "avg_dep_delay"],
            labels={"dep_delay_rate": "Dep Delay Rate (%)", "origin_airport_code": "Airport"},
            color="dep_delay_rate", color_continuous_scale="Oranges"
        )
        fig_q10.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_q10, use_container_width=True)

    with c2:
        st.subheader("Q11. Worst Destination Airports (Arrival Delays)")
        st.caption("Airports with highest percentage of arrivals delayed ≥15 minutes (Min 1,000 flights)")
        fig_q11 = px.bar(
            df_dest.head(10).sort_values("arr_delay_rate", ascending=True),
            x="arr_delay_rate", y="dest_airport_code", orientation="h",
            text="arr_delay_rate", hover_data=["dest_city_name", "eligible_arrivals", "avg_arr_delay"],
            labels={"arr_delay_rate": "Arr Delay Rate (%)", "dest_airport_code": "Airport"},
            color="arr_delay_rate", color_continuous_scale="Reds"
        )
        fig_q11.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_q11, use_container_width=True)

    st.markdown("---")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Q12. Worst Routes by Arrival Delay Rate")
        st.caption("Origin–Destination pairs ranked by delay rate (Min 2,000 flights)")
        top_rate_routes = df_routes.sort_values("arr_delay_rate", ascending=False).head(10)
        fig_q12 = px.bar(
            top_rate_routes.sort_values("arr_delay_rate", ascending=True),
            x="arr_delay_rate", y="route_code", orientation="h",
            text="arr_delay_rate", hover_data=["total_flights", "avg_arr_delay"],
            labels={"arr_delay_rate": "Delay Rate (%)", "route_code": "Route"},
            color="arr_delay_rate", color_continuous_scale="Purples"
        )
        fig_q12.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_q12, use_container_width=True)

    with c4:
        st.subheader("Q13. Routes Accounting for Most Total Delay Minutes")
        st.caption("High cumulative delay burden in minutes across the network")
        top_burden_routes = df_routes.sort_values("total_delay_burden_minutes", ascending=False).head(10)
        fig_q13 = px.bar(
            top_burden_routes.sort_values("total_delay_burden_minutes", ascending=True),
            x="total_delay_burden_minutes", y="route_code", orientation="h",
            labels={"total_delay_burden_minutes": "Total Delay Minutes", "route_code": "Route"},
            color="total_delay_burden_minutes", color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_q13, use_container_width=True)

    st.markdown("---")
    st.subheader("Q14. Route Comparison Across Airlines & Months")
    st.caption("Examine whether performance on the same route differs between airlines")
    sample_routes = df_sample["route_code"].value_counts().head(20).index.tolist()
    chosen_route = st.selectbox("Select Route to Compare:", sample_routes, index=0)

    route_flights = df_sample[df_sample["route_code"] == chosen_route]
    if len(route_flights) > 0:
        comp = route_flights.groupby("reporting_airline").agg(
            total_flights=("flight_key", "count"),
            delay_rate=("arr_del15", lambda x: round(np.mean(x) * 100, 2)),
            avg_delay=("arr_delay", lambda x: round(np.mean(x), 2)),
            cancel_rate=("cancelled", lambda x: round(np.mean(x) * 100, 2))
        ).reset_index()
        st.dataframe(comp, use_container_width=True)
    else:
        st.info("No sample data for this route.")


# =============================================================================
# PAGE 4 — TIME AND OPERATIONAL PATTERNS (Q15–Q19)
# =============================================================================
elif page == "Page 4 — Time & Operational Patterns":
    st.markdown('<div class="main-header">Page 4 — Time & Operational Patterns</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Temporal patterns: seasonality, day of week variations, hourly ripples, and disruption spread</div>', unsafe_allow_html=True)

    df_dow = pd.DataFrame(cubes["weekday_patterns"])
    df_hour = pd.DataFrame(cubes["hourly_patterns"])
    df_trend = pd.DataFrame(cubes["monthly_trend"])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Q15. Seasonal Patterns (Months & Quarters)")
        st.caption("Arrival delay rates across months in the multi-year census")
        fig_q15 = px.line(
            df_trend, x="month_name", y="delay_rate", color="year", markers=True,
            labels={"month_name": "Month", "delay_rate": "Arrival Delay Rate (%)", "year": "Year"},
            title="Arrival Delay Rate (%) by Month & Year"
        )
        st.plotly_chart(fig_q15, use_container_width=True)

    with c2:
        st.subheader("Q16. Day of Week Flight-Delay Performance")
        st.caption("Comparison across Monday through Sunday (30.7M Census)")
        fig_q16 = px.bar(
            df_dow, x="day_name", y="delay_rate", text="delay_rate",
            labels={"day_name": "Day of Week", "delay_rate": "Delay Rate (%)"},
            title="Arrival Delay Rate by Day of Week",
            color="delay_rate", color_continuous_scale="Teal"
        )
        fig_q16.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_q16, use_container_width=True)

    st.markdown("---")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Q17. Scheduled Departure Hour Delay Progression")
        st.caption("Ripple effect: delays accumulate progressively from morning to evening")
        fig_q17 = go.Figure()
        fig_q17.add_trace(go.Scatter(
            x=df_hour["departure_hour"], y=df_hour["dep_delay_rate"],
            mode="lines+markers", name="Departure Delay Rate (%)", line=dict(color="#F59E0B", width=3)
        ))
        fig_q17.add_trace(go.Scatter(
            x=df_hour["departure_hour"], y=df_hour["arr_delay_rate"],
            mode="lines+markers", name="Arrival Delay Rate (%)", line=dict(color="#EF4444", width=3)
        ))
        fig_q17.update_layout(
            xaxis=dict(title="Scheduled Departure Hour (00:00 to 23:00)", tickmode="linear", dtick=2),
            yaxis_title="Delay Rate (%)",
            title="Delay Probability by Hour of Day",
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(fig_q17, use_container_width=True)

    with c4:
        st.subheader("Q18. Departure vs. Arrival Delay Association")
        st.caption("Quantifying how departure delays propagate into arrival delays")
        valid_sample = filtered_sample[filtered_sample["dep_delay"].notna() & filtered_sample["arr_delay"].notna()].sample(min(800, len(filtered_sample)), random_state=42)
        corr_val = valid_sample["dep_delay"].corr(valid_sample["arr_delay"])
        
        fig_q18 = px.scatter(
            valid_sample, x="dep_delay", y="arr_delay", opacity=0.6,
            labels={"dep_delay": "Departure Delay (min)", "arr_delay": "Arrival Delay (min)"},
            title=f"Delay Persistence (Pearson Correlation: r = {corr_val:.3f})",
            trendline="ols", trendline_color_override="#DC2626"
        )
        st.plotly_chart(fig_q18, use_container_width=True)

    st.markdown("---")
    st.subheader("Q19. Disruption Rates Over Time (Cancellations & Diversions)")
    st.caption("Tracking elevated disruption periods")
    st.dataframe(df_trend[["year", "month_name", "total_flights", "cancel_rate", "divert_rate"]], use_container_width=True)


# =============================================================================
# PAGE 5 — DELAY CAUSES AND DISRUPTIONS (Q20–Q23)
# =============================================================================
elif page == "Page 5 — Delay Causes & Disruptions":
    st.markdown('<div class="main-header">Page 5 — Delay Causes & Disruptions</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Recorded delay breakdowns: Carrier, Late Aircraft, NAS, Weather, and Security</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="analytical-rule">
        <b>Important Context:</b> BTS delay cause categories are officially recorded by airlines for flights delayed ≥ 15 minutes.
        Treat these as recorded cause data rather than definitive proof of underlying systemic root cause.
    </div>
    """, unsafe_allow_html=True)

    causes_list = cubes["delay_causes"]
    df_causes = pd.DataFrame(causes_list)
    late_aircraft_share = cubes["late_aircraft_share"]

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Q20. Recorded Delay Causes Breakdown")
        st.caption("Share of total recorded delay minutes across 30.7M flights")
        fig_causes = px.pie(
            df_causes, values="Minutes", names="Cause", hole=0.45,
            title="Distribution of Delay Minutes by Cause",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_causes, use_container_width=True)

    with c2:
        st.subheader("Q23. Late-Arriving Aircraft Delay Burden")
        st.metric("Late-Arriving Aircraft Share", f"{late_aircraft_share}%", "Primary Delay Driver")
        st.caption(f"Late aircraft accounts for {int(df_causes.loc[df_causes['Cause'] == 'Late Aircraft Delay', 'Minutes'].iloc[0]):,} minutes of disruption.")
        st.markdown("""
        **Operational Takeaway:**  
        Late-arriving aircraft delay represents the single largest delay mechanism in commercial aviation.
        When an inbound flight arrives late, the delay cascades into subsequent flight legs throughout the operating day,
        compounding delay probability in afternoon and evening departures.
        """)

    st.markdown("---")
    st.subheader("Q21 & Q22. Delay Cause Distributions Across Airlines")
    st.caption("Examining how different carriers record their primary disruption sources")
    
    # Calculate airline causes from sample
    sample_delayed = filtered_sample[filtered_sample["arr_del15"] == 1]
    if len(sample_delayed) > 0:
        air_causes = sample_delayed.groupby("reporting_airline").agg(
            carrier_delay=("carrier_delay", "sum"),
            late_aircraft_delay=("late_aircraft_delay", "sum"),
            nas_delay=("nas_delay", "sum"),
            weather_delay=("weather_delay", "sum")
        ).reset_index()
        fig_air_causes = px.bar(
            air_causes, x="reporting_airline", y=["carrier_delay", "late_aircraft_delay", "nas_delay", "weather_delay"],
            title="Recorded Delay Minutes by Carrier and Category",
            labels={"value": "Total Minutes", "reporting_airline": "Carrier", "variable": "Delay Cause"},
            barmode="stack"
        )
        st.plotly_chart(fig_air_causes, use_container_width=True)


# =============================================================================
# PAGE 6 — HISTORICAL DELAY RISK (Q24–Q27)
# =============================================================================
elif page == "Page 6 — Historical Delay Risk":
    st.markdown('<div class="main-header">Page 6 — Historical Delay Risk</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Empirical probability estimates grounded in 30.7M historical flight records</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="analytical-rule">
        <b>Analytical Principle:</b> This page provides empirical delay probability estimates based on historical frequency.
        It is NOT a predictive ML model (which requires supervised train-test validation). Minimum sample thresholds are enforced to ensure reliability.
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Q26. Multi-Factor Historical Delay Risk Calculator")
    st.caption("Select flight parameters to evaluate historical delay probability and sample reliability")

    r_col1, r_col2, r_col3, r_col4 = st.columns(4)
    with r_col1:
        calc_airline = st.selectbox("Airline:", ["All"] + sorted(df_sample["reporting_airline"].dropna().unique()), index=0)
    with r_col2:
        calc_route = st.selectbox("Route:", ["All"] + sorted(df_sample["route_code"].dropna().unique()), index=0)
    with r_col3:
        calc_dow = st.selectbox("Day of Week:", ["All", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=0)
    with r_col4:
        calc_hour = st.selectbox("Departure Hour:", ["All"] + [f"{h:02d}:00" for h in range(24)], index=0)

    # Filter matching records
    calc_df = df_sample.copy()
    if calc_airline != "All":
        calc_df = calc_df[calc_df["reporting_airline"] == calc_airline]
    if calc_route != "All":
        calc_df = calc_df[calc_df["route_code"] == calc_route]
    if calc_dow != "All":
        calc_df = calc_df[calc_df["day_name"] == calc_dow]
    if calc_hour != "All":
        calc_df = calc_df[calc_df["departure_hour"] == int(calc_hour.split(":")[0])]

    n_sample = len(calc_df)
    k1, k2, k3 = st.columns(3)
    if n_sample >= 20:
        eligible_n = (calc_df["cancelled"] == 0).sum()
        del_rate = (calc_df["arr_del15"] == 1).sum() / eligible_n * 100 if eligible_n > 0 else 0
        avg_d = calc_df.loc[calc_df["cancelled"] == 0, "arr_delay"].mean()
        
        with k1:
            st.metric("Historical Delay Probability", f"{del_rate:.1f}%")
        with k2:
            st.metric("Average Arrival Delay", f"{avg_d:.1f} min")
        with k3:
            conf_label = "🟢 High Confidence (N ≥ 100)" if n_sample >= 100 else "🟡 Moderate Confidence (20–99)"
            st.metric("Sample Size", f"{n_sample} flights", conf_label)
    else:
        st.warning(f"⚠️ Insufficient sample size ({n_sample} flights). Minimum 20 flights required to compute reliable estimates.")

    st.markdown("---")
    st.subheader("Q24 & Q27. High-Risk Airline-Route Pairs with Reliability Indicators")
    st.caption("Ranked by historical delay probability (Minimum volume threshold applied)")

    route_stats = df_sample.groupby(["reporting_airline", "route_code"]).agg(
        flights=("flight_key", "count"),
        delay_rate=("arr_del15", lambda x: round(np.mean(x) * 100, 2)),
        avg_delay=("arr_delay", lambda x: round(np.mean(x), 2))
    ).reset_index()

    route_stats = route_stats[route_stats["flights"] >= 30].sort_values("delay_rate", ascending=False).head(20)
    route_stats["Reliability"] = route_stats["flights"].apply(lambda n: "High (N≥100)" if n >= 100 else "Moderate (30-99)")
    st.dataframe(route_stats, use_container_width=True)


# =============================================================================
# PAGE 7 — OLAP EXPLORER (Q28–Q31)
# =============================================================================
elif page == "Page 7 — OLAP Explorer":
    st.markdown('<div class="main-header">Page 7 — OLAP Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive demonstration of core Data Warehousing operations: Roll-up, Drill-down, Slice, Dice, Pivot, and Drill-through</div>', unsafe_allow_html=True)

    tab_rollup, tab_slicedice, tab_pivot, tab_drillthrough = st.tabs([
        "Q28: Roll-up & Drill-down",
        "Q29: Slice & Dice",
        "Q30: Multi-dimensional Pivot",
        "Q31: Drill-through to Fact Grain"
    ])

    with tab_rollup:
        st.subheader("Q28. Roll-up and Drill-down Hierarchy")
        st.caption("Demonstrating navigation across the temporal dimensional hierarchy: Year ⇄ Quarter ⇄ Month")
        
        df_rollup = pd.DataFrame(cubes["rollup_hierarchy"])
        granularity = st.radio("Select Temporal Granularity:", ["Year (Roll-up)", "Quarter", "Month (Drill-down)"], horizontal=True)
        
        if "Year" in granularity:
            res = df_rollup.groupby("year").agg(
                total_flights=("total_flights", "sum"),
                eligible_arrivals=("eligible_arrivals", "sum"),
                delay_rate=("delay_rate", "mean"),
                avg_arrival_delay=("avg_arrival_delay", "mean")
            ).reset_index()
            st.dataframe(res, use_container_width=True)
            fig = px.bar(res, x="year", y="delay_rate", title="Yearly Roll-up: Delay Rate (%)", text="delay_rate")
            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        elif "Quarter" in granularity:
            res = df_rollup.groupby(["year", "quarter"]).agg(
                total_flights=("total_flights", "sum"),
                eligible_arrivals=("eligible_arrivals", "sum"),
                delay_rate=("delay_rate", "mean"),
                avg_arrival_delay=("avg_arrival_delay", "mean")
            ).reset_index()
            res["period"] = res["year"].astype(str) + " Q" + res["quarter"].astype(str)
            st.dataframe(res, use_container_width=True)
            fig = px.bar(res, x="period", y="delay_rate", title="Quarterly Aggregation: Delay Rate (%)", text="delay_rate")
            fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        else:
            df_rollup["period"] = df_rollup["year"].astype(str) + " " + df_rollup["month_name"].str[:3]
            st.dataframe(df_rollup[["period", "total_flights", "eligible_arrivals", "delay_rate", "avg_arrival_delay"]], use_container_width=True)
            fig = px.line(df_rollup, x="period", y="delay_rate", markers=True, title="Monthly Drill-down: Delay Rate (%)")
            st.plotly_chart(fig, use_container_width=True)

    with tab_slicedice:
        st.subheader("Q29. Multi-dimensional Slice & Dice")
        st.caption("Dynamically slicing the dimensional cube across Carrier, Origin, and Day of Week")
        
        s1, s2 = st.columns(2)
        with s1:
            slice_air = st.multiselect("Slice Carrier:", sorted(df_sample["reporting_airline"].unique()), default=["AA", "DL", "UA"])
        with s2:
            slice_dow = st.multiselect("Slice Weekday:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], default=["Friday", "Sunday", "Monday"])

        sliced = df_sample.copy()
        if slice_air:
            sliced = sliced[sliced["reporting_airline"].isin(slice_air)]
        if slice_dow:
            sliced = sliced[sliced["day_name"].isin(slice_dow)]

        st.caption(f"Showing sliced cube metrics across {len(sliced)} granular flights:")
        slice_agg = sliced.groupby(["reporting_airline", "day_name"]).agg(
            flights=("flight_key", "count"),
            delay_rate=("arr_del15", lambda x: round(np.mean(x) * 100, 2)),
            avg_delay=("arr_delay", lambda x: round(np.mean(x), 2))
        ).reset_index()
        st.dataframe(slice_agg, use_container_width=True)

    with tab_pivot:
        st.subheader("Q30. Multi-dimensional Pivot Table")
        st.caption("2D Matrix comparing Arrival Delay Rate (%) across Airlines (rows) and Months (columns)")
        
        df_pivot_data = pd.DataFrame(cubes["pivot_data"])
        pivot_table = df_pivot_data.pivot(
            index="reporting_airline", columns="month_name", values="delay_rate"
        )
        # Order months chronologically
        month_order = [m for m in all_months if m in pivot_table.columns]
        pivot_table = pivot_table[month_order]
        
        st.dataframe(
            pivot_table.style.background_gradient(cmap="Reds", axis=None).format("{:.2f}%"),
            use_container_width=True
        )

    with tab_drillthrough:
        st.subheader("Q31. Drill-through to Fact Table Grain")
        st.caption("Navigate from high-level summary KPIs directly down to individual flight records in fact_flight")
        
        dt_col1, dt_col2 = st.columns(2)
        with dt_col1:
            dt_carrier = st.selectbox("Drill-through Carrier:", ["All"] + sorted(df_sample["reporting_airline"].dropna().unique()), index=0)
        with dt_col2:
            dt_only_delayed = st.checkbox("Show Only Delayed Flights (≥ 15 min)", value=True)

        dt_df = df_sample.copy()
        if dt_carrier != "All":
            dt_df = dt_df[dt_df["reporting_airline"] == dt_carrier]
        if dt_only_delayed:
            dt_df = dt_df[dt_df["arr_del15"] == 1]

        st.caption(f"Displaying top 50 underlying flight records (Grain: 1 row = 1 flight):")
        cols_to_show = [
            "flight_date", "reporting_airline", "flight_number", "tail_number",
            "origin_airport_code", "dest_airport_code", "crs_dep_time", "dep_time", "dep_delay",
            "crs_arr_time", "arr_time", "arr_delay", "carrier_delay", "late_aircraft_delay", "weather_delay"
        ]
        available_dt_cols = [c for c in cols_to_show if c in dt_df.columns]
        st.dataframe(dt_df[available_dt_cols].head(50), use_container_width=True)
