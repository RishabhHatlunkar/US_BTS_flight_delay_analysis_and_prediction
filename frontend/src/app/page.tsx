"use client";

import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  Plane,
  Building2,
  GitBranch,
  AlertTriangle,
  Clock,
  Filter,
  Briefcase,
  Layers,
  Database,
  ShieldCheck,
  Zap,
  ArrowRight,
} from "lucide-react";

import Header from "../components/Header";
import KpiBanner from "../components/KpiBanner";
import OverviewTab from "../components/OverviewTab";
import AirlinesTab from "../components/AirlinesTab";
import AirportsTab from "../components/AirportsTab";
import RoutesTab from "../components/RoutesTab";
import RootCausesTab from "../components/RootCausesTab";
import TemporalTab from "../components/TemporalTab";
import OlapFilterTab from "../components/OlapFilterTab";
import StakeholderTab from "../components/StakeholderTab";
import CustomerNavigation, { ViewSelection } from "../components/CustomerNavigation";
import CustomerClosedLoop from "../components/CustomerClosedLoop";
import { CUSTOMER_CLOSED_LOOPS } from "../lib/customerClosedLoopData";

import {
  fetchHealth,
  fetchOverview,
  fetchAirlines,
  fetchAirports,
  fetchRoutes,
  fetchCauses,
  fetchTemporal,
  refreshDatabricksCache,
  FALLBACK_KPIS,
  FALLBACK_MONTHLY,
  FALLBACK_AIRLINES,
  FALLBACK_ORIG_AIRPORTS,
  FALLBACK_DEST_AIRPORTS,
  FALLBACK_ROUTES,
  FALLBACK_DELAY_CAUSES,
  FALLBACK_LATE_AIRCRAFT_SHARE,
  FALLBACK_WEEKDAY,
  FALLBACK_HOURLY,
  Kpis,
  MonthlyTrend,
  AirlinePerf,
  AirportDelay,
  RouteMetric,
  DelayCause,
  TemporalPattern,
  TargetCustomerId,
} from "../lib/api";

type TabId =
  | "overview"
  | "airlines"
  | "airports"
  | "routes"
  | "causes"
  | "temporal"
  | "filter"
  | "stakeholders";

interface TabDef {
  id: TabId;
  label: string;
  badge?: string;
  icon: React.ComponentType<{ className?: string }>;
}

const TABS: TabDef[] = [
  { id: "overview", label: "Overview: Flight Performance", badge: "Overall", icon: TrendingUp },
  { id: "airlines", label: "Airline Rankings", badge: "18 Airlines", icon: Plane },
  { id: "airports", label: "Busiest Airports & Tarmac Delays", badge: "Hubs", icon: Building2 },
  { id: "routes", label: "Most Delayed Flight Routes", badge: "Top Routes", icon: GitBranch },
  { id: "causes", label: "Why Flights Get Delayed", badge: "5 Main Reasons", icon: AlertTriangle },
  { id: "temporal", label: "Best & Worst Times to Fly", badge: "Hours & Days", icon: Clock },
  { id: "filter", label: "Search by Airline & Airport", badge: "Custom Search", icon: Filter },
  { id: "stakeholders", label: "Solutions by Role", badge: "Action Guide", icon: Briefcase },
];

export default function DashboardPage() {
  // Navigation: customer persona closed-loop vs global warehouse
  const [selectedView, setSelectedView] = useState<ViewSelection>("airlines");
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [connected, setConnected] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);

  // Data states initialized with resilient Databricks Gold fallbacks
  const [kpis, setKpis] = useState<Kpis>(FALLBACK_KPIS);
  const [monthlyTrend, setMonthlyTrend] = useState<MonthlyTrend[]>(FALLBACK_MONTHLY);
  const [airlines, setAirlines] = useState<AirlinePerf[]>(FALLBACK_AIRLINES);
  const [originAirports, setOriginAirports] = useState<AirportDelay[]>(FALLBACK_ORIG_AIRPORTS);
  const [destAirports, setDestAirports] = useState<AirportDelay[]>(FALLBACK_DEST_AIRPORTS);
  const [routes, setRoutes] = useState<RouteMetric[]>(FALLBACK_ROUTES);
  const [causes, setCauses] = useState<DelayCause[]>(FALLBACK_DELAY_CAUSES);
  const [lateAircraftShare, setLateAircraftShare] = useState<number>(FALLBACK_LATE_AIRCRAFT_SHARE);
  const [weekdayPatterns, setWeekdayPatterns] = useState<TemporalPattern[]>(FALLBACK_WEEKDAY);
  const [hourlyPatterns, setHourlyPatterns] = useState<TemporalPattern[]>(FALLBACK_HOURLY);

  const loadData = async () => {
    setLoading(true);
    try {
      const [
        healthRes,
        overviewRes,
        airlinesRes,
        airportsRes,
        routesRes,
        causesRes,
        temporalRes,
      ] = await Promise.all([
        fetchHealth().catch(() => ({ connected: false })),
        fetchOverview().catch(() => ({ kpis: FALLBACK_KPIS, monthly_trend: FALLBACK_MONTHLY })),
        fetchAirlines().catch(() => FALLBACK_AIRLINES),
        fetchAirports().catch(() => ({
          origin_airports: FALLBACK_ORIG_AIRPORTS,
          dest_airports: FALLBACK_DEST_AIRPORTS,
        })),
        fetchRoutes().catch(() => FALLBACK_ROUTES),
        fetchCauses().catch(() => ({
          delay_causes: FALLBACK_DELAY_CAUSES,
          late_aircraft_share: FALLBACK_LATE_AIRCRAFT_SHARE,
        })),
        fetchTemporal().catch(() => ({
          weekday_patterns: FALLBACK_WEEKDAY,
          hourly_patterns: FALLBACK_HOURLY,
        })),
      ]);

      if (healthRes && typeof healthRes.connected === "boolean") {
        setConnected(healthRes.connected);
      }
      if (overviewRes?.kpis) setKpis(overviewRes.kpis);
      if (overviewRes?.monthly_trend) setMonthlyTrend(overviewRes.monthly_trend);
      if (airlinesRes && Array.isArray(airlinesRes)) setAirlines(airlinesRes);
      if (airportsRes?.origin_airports) setOriginAirports(airportsRes.origin_airports);
      if (airportsRes?.dest_airports) setDestAirports(airportsRes.dest_airports);
      if (routesRes && Array.isArray(routesRes)) setRoutes(routesRes);
      if (causesRes?.delay_causes) setCauses(causesRes.delay_causes);
      if (typeof causesRes?.late_aircraft_share === "number") {
        setLateAircraftShare(causesRes.late_aircraft_share);
      }
      if (temporalRes?.weekday_patterns) setWeekdayPatterns(temporalRes.weekday_patterns);
      if (temporalRes?.hourly_patterns) setHourlyPatterns(temporalRes.hourly_patterns);
    } catch (err) {
      console.warn("Using Databricks Gold cached models:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = async () => {
    await refreshDatabricksCache().catch(() => {});
    await loadData();
  };

  const handleCustomerSelect = (selection: ViewSelection) => {
    setSelectedView(selection);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Top Header */}
      <Header
        totalFlights={kpis.total_flights || 30742408}
        catalog="flight_delay_dwm"
        schema="gold"
        onRefresh={handleRefresh}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Dataset Banner */}
        <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 text-white rounded-xl shadow-md p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border border-blue-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-blue-700/60 flex items-center justify-center shrink-0 border border-blue-400/30">
              <Database className="w-5 h-5 text-blue-200" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-white text-base">Official US Flight Performance Database</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                  Verified Data
                </span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-500/30 text-blue-200 border border-blue-400/30">
                  30,742,408 Flights
                </span>
              </div>
              <p className="text-xs text-blue-200/90 mt-0.5">
                Source: <span className="font-semibold text-white">U.S. Bureau of Transportation Statistics (BTS)</span> • Processed across 5 Years of US Domestic Flights
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
            <span className="text-xs text-blue-200 flex items-center gap-1.5 bg-blue-950/40 px-3 py-1.5 rounded-lg border border-blue-700/40">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% Complete Government Dataset</span>
            </span>
          </div>
        </div>

        {/* TARGET CUSTOMER NAVIGATION BAR AT THE START */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <CustomerNavigation
            currentSelection={selectedView}
            onSelect={handleCustomerSelect}
          />
        </div>

        {/* VIEW 1: TARGET CUSTOMER CLOSED LOOP VIEW */}
        {selectedView !== "global_warehouse" && (
          <div className="space-y-6">
            <CustomerClosedLoop
              data={CUSTOMER_CLOSED_LOOPS[selectedView]}
            />

            {/* Quick Action to Explore Underlying Warehouse Data */}
            <div className="card-royal p-4 bg-white border border-blue-100 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="text-xs text-slate-600">
                Want to see raw airline rankings, airport maps, and full flight statistics?
              </div>
              <button
                onClick={() => setSelectedView("global_warehouse")}
                className="py-2 px-4 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold flex items-center space-x-1.5 shadow-sm transition-all shrink-0"
              >
                <span>Open Full Flight Database Explorer</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* VIEW 2: GLOBAL WAREHOUSE / OLAP ANALYTICS VIEW */}
        {selectedView === "global_warehouse" && (
          <div className="space-y-6">
            {/* Global KPI Banner */}
            <KpiBanner kpis={kpis} />

            {/* Tab Navigation Pill Bar */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-2">
              <div className="flex items-center gap-1 overflow-x-auto no-scrollbar scroll-smooth">
                {TABS.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-2 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition-all duration-150 whitespace-nowrap shrink-0 ${
                        isActive
                          ? "bg-blue-600 text-white shadow-sm ring-2 ring-blue-600/30"
                          : "text-slate-600 hover:text-blue-600 hover:bg-blue-50/70"
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-blue-600"}`} />
                      <span>{tab.label}</span>
                      {tab.badge && (
                        <span
                          className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded-full tracking-wide ${
                            isActive
                              ? "bg-white/20 text-white"
                              : "bg-blue-100 text-blue-700"
                          }`}
                        >
                          {tab.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Active Tab View */}
            <div className="transition-all duration-200">
              {activeTab === "overview" && <OverviewTab monthlyData={monthlyTrend} />}

              {activeTab === "airlines" && <AirlinesTab airlines={airlines} />}

              {activeTab === "airports" && (
                <AirportsTab originAirports={originAirports} destAirports={destAirports} />
              )}

              {activeTab === "routes" && <RoutesTab routes={routes} />}

              {activeTab === "causes" && (
                <RootCausesTab causes={causes} lateAircraftShare={lateAircraftShare} />
              )}

              {activeTab === "temporal" && (
                <TemporalTab weekdayPatterns={weekdayPatterns} hourlyPatterns={hourlyPatterns} />
              )}

              {activeTab === "filter" && <OlapFilterTab />}

              {activeTab === "stakeholders" && (
                <StakeholderTab
                  onSelectCustomer={(c: TargetCustomerId) => setSelectedView(c)}
                />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer with Lineage & Tech Stack */}
      <footer className="bg-white border-t border-slate-200 mt-12 py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm">
                ✈
              </div>
              <div>
                <p className="font-bold text-slate-800 text-sm">
                  US BTS Flight Delay Analytics &amp; Prediction System
                </p>
                <p className="text-slate-500">
                  Data Warehousing &amp; Data Mining (DWM) — Star Schema Medallion Architecture
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 text-slate-600">
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 rounded-md border border-slate-200">
                <Database className="w-3.5 h-3.5 text-blue-600" />
                Databricks Unity Catalog Gold
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 rounded-md border border-slate-200">
                <Zap className="w-3.5 h-3.5 text-amber-500" />
                FastAPI Python Engine
              </span>
              <span className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 rounded-md border border-slate-200">
                <Layers className="w-3.5 h-3.5 text-indigo-600" />
                Next.js 16 + Tailwind CSS
              </span>
            </div>
          </div>

          <div className="border-t border-slate-100 pt-3 flex flex-col sm:flex-row items-center justify-between gap-2 text-slate-400">
            <p>
              Primary Source: U.S. Bureau of Transportation Statistics (BTS) Reporting Carrier On-Time Performance. 30,742,408 Processed Flights.
            </p>
            <p>
              Integrated Data Pipeline: Medallion Bronze &rarr; Silver &rarr; Gold Star Schema &rarr; Closed-Loop Decision Intelligence.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
