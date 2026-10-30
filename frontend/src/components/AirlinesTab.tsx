"use client";

import React, { useState } from "react";
import { AirlinePerf } from "@/lib/types";
import { Award, ArrowUpDown, ShieldCheck, AlertTriangle } from "lucide-react";

interface AirlinesTabProps {
  airlines: AirlinePerf[];
}

export const AirlinesTab: React.FC<AirlinesTabProps> = ({ airlines }) => {
  const [sortBy, setSortBy] = useState<"delay_rate" | "total_flights" | "avg_arr_delay_pos">("delay_rate");
  const [ascending, setAscending] = useState(true);

  const sorted = [...airlines].sort((a, b) => {
    let diff = (a[sortBy] as number) - (b[sortBy] as number);
    return ascending ? diff : -diff;
  });

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="card-royal p-6 bg-white border border-blue-100">
        <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
          <Award className="w-6 h-6 text-blue-700" />
          <span>Major US Airline Performance & Reliability Scorecard</span>
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Benchmarking arrival punctuality (ArrDel15 &lt; 15 mins), average positive delay minutes, and cancellation frequencies
        </p>
      </div>

      {/* Airlines Table */}
      <div className="card-royal overflow-hidden">
        <div className="p-4 bg-slate-50/80 border-b border-slate-200 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
            Carrier Reliability Rankings ({airlines.length} Operating Airlines)
          </span>
          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-500 font-medium">Sort by:</span>
            <button
              onClick={() => {
                if (sortBy === "delay_rate") setAscending(!ascending);
                else { setSortBy("delay_rate"); setAscending(true); }
              }}
              className={`px-3 py-1 rounded-lg border font-semibold flex items-center space-x-1 ${
                sortBy === "delay_rate" ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-700 border-slate-200"
              }`}
            >
              <span>Delay Rate</span>
              <ArrowUpDown className="w-3 h-3 ml-1" />
            </button>
            <button
              onClick={() => {
                if (sortBy === "total_flights") setAscending(!ascending);
                else { setSortBy("total_flights"); setAscending(false); }
              }}
              className={`px-3 py-1 rounded-lg border font-semibold flex items-center space-x-1 ${
                sortBy === "total_flights" ? "bg-blue-600 text-white border-blue-600" : "bg-white text-slate-700 border-slate-200"
              }`}
            >
              <span>Flight Volume</span>
              <ArrowUpDown className="w-3 h-3 ml-1" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-600 text-xs uppercase font-bold border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Rank / Carrier</th>
                <th className="py-3 px-4">Flight Volume</th>
                <th className="py-3 px-4">On-Time Rate</th>
                <th className="py-3 px-4">Delay Rate (≥15m)</th>
                <th className="py-3 px-4">Avg Delay (Delayed Only)</th>
                <th className="py-3 px-4">Cancel Rate</th>
                <th className="py-3 px-4">Reliability Rating</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sorted.map((airline, idx) => {
                const onTime = (100 - airline.delay_rate).toFixed(1);
                const isTopTier = airline.delay_rate < 18;
                const isHighRisk = airline.delay_rate > 23;
                return (
                  <tr key={airline.reporting_airline} className="hover:bg-blue-50/40 transition-colors">
                    <td className="py-3.5 px-4 font-bold text-blue-950 flex items-center space-x-3">
                      <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-xs flex items-center justify-center font-bold">
                        {idx + 1}
                      </span>
                      <span className="text-base tracking-wide font-black text-blue-900">
                        {airline.reporting_airline}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-700">
                      {airline.total_flights.toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-emerald-500 h-full rounded-full"
                            style={{ width: `${onTime}%` }}
                          ></div>
                        </div>
                        <span className="font-bold text-emerald-700">{onTime}%</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-amber-700">
                      {airline.delay_rate}%
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-700">
                      +{airline.avg_arr_delay_pos} min
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-rose-600">
                      {airline.cancel_rate}%
                    </td>
                    <td className="py-3.5 px-4">
                      {isTopTier ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300 flex items-center w-fit space-x-1">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          <span>Industry Leader</span>
                        </span>
                      ) : isHighRisk ? (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-800 border border-rose-300 flex items-center w-fit space-x-1">
                          <AlertTriangle className="w-3.5 h-3.5" />
                          <span>High Delay Risk</span>
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">
                          Average
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};


export default AirlinesTab;
