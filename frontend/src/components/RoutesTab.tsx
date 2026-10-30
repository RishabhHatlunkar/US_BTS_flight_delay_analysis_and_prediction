"use client";

import React from "react";
import { RouteMetric } from "@/lib/types";
import { Navigation2, ArrowRight, Compass } from "lucide-react";

interface RoutesTabProps {
  routes: RouteMetric[];
}

export const RoutesTab: React.FC<RoutesTabProps> = ({ routes }) => {
  return (
    <div className="space-y-6">
      <div className="card-royal p-6 bg-white border border-blue-100 shadow-sm rounded-xl">
        <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
          <Navigation2 className="w-6 h-6 text-blue-700" />
          <span>Top Directional Routes by Delay Exposure</span>
        </h3>
        <p className="text-sm text-slate-500 mt-1">
          Analysis of highest delay rates across high-traffic city-pair corridors (minimum threshold: &ge; 5,000 flights)
        </p>

        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="border-b border-blue-100 bg-blue-50/50 text-blue-900 font-semibold">
                <th className="py-3 px-4">Route</th>
                <th className="py-3 px-4">Origin &rarr; Dest</th>
                <th className="py-3 px-4 text-right">Total Flights</th>
                <th className="py-3 px-4 text-right">Delayed Flights</th>
                <th className="py-3 px-4 text-right">Delay Rate (%)</th>
                <th className="py-3 px-4 text-right">Avg Delay (min)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {routes.map((r, i) => {
                const totalFl = r.total_flights ?? r.flight_count ?? 0;
                const delayedFl = r.delayed_flights ?? r.delayed_arrivals ?? 0;
                const delayRt = r.arr_delay_rate ?? r.delay_rate ?? 0;
                const avgDel = r.avg_arr_delay ?? r.avg_arr_delay_pos ?? r.avg_delay ?? 0;
                const orig = r.origin_airport_code ?? r.origin_code ?? "";
                const dest = r.destination_airport_code ?? r.dest_airport_code ?? r.dest_code ?? "";

                return (
                  <tr key={i} className="hover:bg-blue-50/30 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-blue-900">
                      {r.route_code}
                    </td>
                    <td className="py-3 px-4 flex items-center space-x-2 text-slate-700">
                      <span className="font-semibold text-blue-800">{orig}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                      <span className="font-semibold text-blue-800">{dest}</span>
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-slate-600">
                      {totalFl.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-amber-700">
                      {delayedFl.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        delayRt > 30 ? "bg-red-100 text-red-700" :
                        delayRt > 25 ? "bg-amber-100 text-amber-800" :
                        "bg-blue-100 text-blue-800"
                      }`}>
                        {delayRt.toFixed(2)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-bold text-slate-800">
                      {avgDel.toFixed(1)}m
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

export default RoutesTab;
