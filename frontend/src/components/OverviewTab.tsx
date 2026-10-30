"use client";

import React from "react";
import { MonthlyTrend } from "@/lib/types";
import { Calendar, TrendingUp, BarChart3, AlertCircle } from "lucide-react";

interface OverviewTabProps {
  monthlyData: MonthlyTrend[];
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ monthlyData }) => {
  // Compute max total flights for bar scaling
  const maxVolume = Math.max(...monthlyData.map((m) => m.total_flights), 1);
  const maxDelay = Math.max(...monthlyData.map((m) => m.delay_rate), 1);

  return (
    <div className="space-y-6">
      {/* Executive Summary Card */}
      <div className="card-royal p-6 bg-gradient-to-r from-blue-900 via-blue-800 to-blue-700 text-white">
        <div className="max-w-3xl">
          <span className="px-3 py-1 text-xs font-bold rounded-full bg-blue-500/30 text-blue-100 border border-blue-400/30 uppercase tracking-wider">
            Databricks Star Schema Executive Summary
          </span>
          <h2 className="text-2xl font-bold mt-3 mb-2">
            Macro Flight Performance & Seasonal Delay Exposure
          </h2>
          <p className="text-sm text-blue-100 leading-relaxed">
            Historical analysis across 30,742,408 commercial flights reveals an overall on-time arrival rate of 
            <strong className="text-white"> 78.55%</strong>. Significant seasonal volatility occurs during peak summer travel windows (June–July) and severe winter storm periods (December–January), where arrival delay rates surge above 
            <strong className="text-amber-300"> 25.4%</strong>.
          </p>
        </div>
      </div>

      {/* Monthly Trend Chart */}
      <div className="card-royal p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 border-b border-slate-100 gap-2">
          <div>
            <h3 className="text-lg font-bold text-blue-950 flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              <span>Monthly Flight Volume vs. Arrival Delay Rate</span>
            </h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Dual-axis performance trajectory from 2020 through 2025 in Databricks Gold Fact
            </p>
          </div>
          <div className="flex items-center space-x-4 text-xs font-semibold">
            <span className="flex items-center space-x-1.5 text-blue-800">
              <span className="w-3 h-3 rounded bg-blue-700"></span>
              <span>Flight Volume</span>
            </span>
            <span className="flex items-center space-x-1.5 text-amber-600">
              <span className="w-3 h-3 rounded bg-amber-500"></span>
              <span>Delay Rate (%)</span>
            </span>
          </div>
        </div>

        {/* Visual Monthly Grid */}
        <div className="mt-6 overflow-x-auto">
          <div className="min-w-[700px] space-y-3">
            {monthlyData.slice(-18).map((m, idx) => {
              const volPct = (m.total_flights / maxVolume) * 100;
              const delayPct = (m.delay_rate / 35) * 100; // normalized to 35% scale
              return (
                <div key={idx} className="flex items-center space-x-4 text-xs">
                  <div className="w-20 font-bold text-slate-700">
                    {m.month_name.slice(0, 3)} {m.year}
                  </div>
                  <div className="flex-1 space-y-1">
                    {/* Volume Bar */}
                    <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex">
                      <div
                        className="bg-blue-600 h-full rounded-full transition-all duration-500 hover:bg-blue-700"
                        style={{ width: `${volPct}%` }}
                        title={`${m.total_flights.toLocaleString()} flights`}
                      ></div>
                    </div>
                  </div>
                  <div className="w-24 text-right font-medium text-slate-600">
                    {(m.total_flights / 1000).toFixed(0)}k flights
                  </div>
                  {/* Delay Rate Badge */}
                  <div className="w-20 text-right">
                    <span
                      className={`px-2 py-0.5 rounded-md font-bold text-xs ${
                        m.delay_rate > 22
                          ? "bg-amber-100 text-amber-800 border border-amber-300"
                          : "bg-blue-50 text-blue-700 border border-blue-200"
                      }`}
                    >
                      {m.delay_rate}%
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};


export default OverviewTab;
