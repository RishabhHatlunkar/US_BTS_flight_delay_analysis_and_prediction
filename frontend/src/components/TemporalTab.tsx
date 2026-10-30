"use client";

import React from "react";
import { TemporalPattern } from "@/lib/types";
import { Clock, CalendarDays, Activity } from "lucide-react";

interface TemporalTabProps {
  weekdayPatterns: TemporalPattern[];
  hourlyPatterns: TemporalPattern[];
}

export const TemporalTab: React.FC<TemporalTabProps> = ({
  weekdayPatterns,
  hourlyPatterns,
}) => {
  const maxHourDelay = Math.max(
    ...hourlyPatterns.map((h) => h.delay_rate ?? h.arr_delay_rate ?? 0),
    1
  );

  return (
    <div className="space-y-6">
      <div className="card-royal p-6 bg-white border border-blue-100 shadow-sm rounded-xl">
        <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
          <CalendarDays className="w-6 h-6 text-blue-700" />
          <span>Day of Week Delay Distribution (OLAP Slice)</span>
        </h3>
        <p className="text-sm text-slate-500 mt-1">
          Evaluation of structural congestion patterns across calendar weekdays
        </p>

        <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {weekdayPatterns.map((w, idx) => {
            const totalFl = w.total_flights ?? w.flight_count ?? 0;
            const delayRt = w.delay_rate ?? w.arr_delay_rate ?? 0;
            const avgDel = w.avg_arrival_delay ?? w.avg_delay ?? 0;

            return (
              <div
                key={idx}
                className="bg-gradient-to-b from-white to-blue-50/50 p-4 rounded-xl border border-blue-100 flex flex-col justify-between hover:shadow-md transition-shadow"
              >
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-blue-600">
                    {w.day_name || `Day ${w.day_of_week}`}
                  </span>
                  <div className="text-2xl font-black text-blue-950 mt-1">
                    {delayRt.toFixed(1)}%
                  </div>
                  <div className="text-xs text-slate-500">Delay Rate</div>
                </div>

                <div className="mt-4 pt-3 border-t border-blue-100/60 text-xs text-slate-600 space-y-1">
                  <div className="flex justify-between">
                    <span>Flights:</span>
                    <span className="font-semibold">{totalFl.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Delay:</span>
                    <span className="font-semibold font-mono">{avgDel.toFixed(1)}m</span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="card-royal p-6 bg-white border border-blue-100 shadow-sm rounded-xl">
        <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
          <Clock className="w-6 h-6 text-blue-700" />
          <span>Hourly Departure Congestion Profile (24-Hour Diurnal Cycle)</span>
        </h3>
        <p className="text-sm text-slate-500 mt-1">
          Morning clear air vs. afternoon reactionary cascade propagation
        </p>

        <div className="mt-6">
          <div className="space-y-2">
            {hourlyPatterns.map((h, idx) => {
              const hr = h.departure_hour ?? h.hour ?? idx;
              const delayRt = h.delay_rate ?? h.arr_delay_rate ?? 0;
              const depRt = h.dep_delay_rate ?? 0;
              const widthPct = Math.min(100, Math.max(5, (delayRt / maxHourDelay) * 100));

              return (
                <div key={idx} className="flex items-center space-x-3 text-xs">
                  <span className="w-14 font-mono font-semibold text-slate-600">
                    {hr.toString().padStart(2, "0")}:00
                  </span>
                  <div className="flex-1 bg-slate-100 rounded-full h-4 overflow-hidden relative">
                    <div
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-300"
                      style={{ width: `${widthPct}%` }}
                    />
                  </div>
                  <span className="w-16 text-right font-mono font-bold text-blue-900">
                    {delayRt.toFixed(1)}%
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemporalTab;
