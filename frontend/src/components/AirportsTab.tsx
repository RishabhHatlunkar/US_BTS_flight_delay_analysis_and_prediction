"use client";

import React, { useState } from "react";
import { AirportDelay } from "@/lib/types";
import { Building2, Navigation, Clock, AlertTriangle } from "lucide-react";

interface AirportsTabProps {
  originAirports: AirportDelay[];
  destAirports: AirportDelay[];
}

export const AirportsTab: React.FC<AirportsTabProps> = ({
  originAirports,
  destAirports,
}) => {
  const [viewMode, setViewMode] = useState<"origin" | "dest">("origin");

  return (
    <div className="space-y-6">
      {/* Header and Toggle */}
      <div className="card-royal p-6 bg-white border border-blue-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
            <Building2 className="w-6 h-6 text-blue-700" />
            <span>Hub Airport Operations & Tarmac Bottleneck Analytics</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Analyzing origin departure pushback delays, runway queue congestion, and destination gate holding times
          </p>
        </div>
        <div className="flex rounded-xl bg-slate-100 p-1 border border-slate-200">
          <button
            onClick={() => setViewMode("origin")}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === "origin"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-600 hover:text-blue-900"
            }`}
          >
            Origin Departures
          </button>
          <button
            onClick={() => setViewMode("dest")}
            className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${
              viewMode === "dest"
                ? "bg-blue-600 text-white shadow-sm"
                : "text-slate-600 hover:text-blue-900"
            }`}
          >
            Destination Arrivals
          </button>
        </div>
      </div>

      {/* Grid of Airport Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(viewMode === "origin" ? originAirports : destAirports).slice(0, 15).map((apt, idx) => {
          const code = apt.origin_airport_code || apt.dest_airport_code;
          const city = apt.origin_city_name || apt.dest_city_name;
          const state = apt.origin_state || apt.dest_state;
          const count = apt.eligible_departures || apt.eligible_arrivals || 0;
          const delayRate = apt.dep_delay_rate ?? apt.arr_delay_rate ?? 0;
          const avgDelay = apt.avg_dep_delay ?? apt.avg_arr_delay ?? 0;

          return (
            <div key={idx} className="card-royal p-5 flex flex-col justify-between hover:border-blue-300">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl font-black text-blue-900 tracking-wider">
                      {code}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">
                      {state}
                    </span>
                  </div>
                  <span className="text-xs font-medium text-slate-400">Rank #{idx + 1}</span>
                </div>
                <p className="text-xs font-semibold text-slate-600 truncate mb-4">
                  {city}
                </p>
              </div>

              <div className="space-y-3 pt-3 border-t border-slate-100">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 font-medium">Scheduled Flights:</span>
                  <span className="font-bold text-slate-800">{count.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 font-medium">Delay Rate (≥15m):</span>
                  <span className={`font-bold ${delayRate > 22 ? "text-amber-600" : "text-blue-700"}`}>
                    {delayRate}%
                  </span>
                </div>
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-500 font-medium">Average Delay:</span>
                  <span className="font-bold text-slate-800">+{avgDelay} min</span>
                </div>

                {/* Delay Meter */}
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      delayRate > 22 ? "bg-amber-500" : "bg-blue-600"
                    }`}
                    style={{ width: `${Math.min(delayRate * 3, 100)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};


export default AirportsTab;
