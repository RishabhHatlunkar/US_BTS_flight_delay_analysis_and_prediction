"use client";

import React from "react";
import { Kpis } from "@/lib/types";
import { 
  Plane, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  XCircle, 
  Flame
} from "lucide-react";

interface KpiBannerProps {
  kpis: Kpis;
}

export const KpiBanner: React.FC<KpiBannerProps> = ({ kpis }) => {
  const onTimeRate = (100 - kpis.arr_delay_rate).toFixed(1);
  const totalBurdensMillions = (kpis.total_delay_burden_minutes / 1_000_000).toFixed(0);

  return (
    <div className="grid grid-cols-2 lg:grid-cols-6 gap-4 my-6">
      {/* 1. Total Flights */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-blue-800">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total US Flights</span>
          <div className="p-2 rounded-lg bg-blue-50 text-blue-700">
            <Plane className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-blue-950 tracking-tight">
            {(kpis.total_flights / 1_000_000).toFixed(1)}M
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-1 block">
            {kpis.total_flights.toLocaleString()} flights analyzed
          </span>
        </div>
      </div>

      {/* 2. On-Time Arrival Rate */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-emerald-600">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">On-Time Flights</span>
          <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
            <CheckCircle className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-emerald-700 tracking-tight">
            {onTimeRate}%
          </div>
          <span className="text-[11px] font-medium text-emerald-600 mt-1 block">
            Arrived on or ahead of time
          </span>
        </div>
      </div>

      {/* 3. Delayed Arrivals Rate */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-amber-500">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Late Flights</span>
          <div className="p-2 rounded-lg bg-amber-50 text-amber-600">
            <AlertTriangle className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-amber-600 tracking-tight">
            {kpis.arr_delay_rate}%
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-1 block">
            About 1 in every 5 flights
          </span>
        </div>
      </div>

      {/* 4. Average Arrival Delay */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-blue-600">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Average Delay</span>
          <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
            <Clock className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-blue-900 tracking-tight">
            {kpis.avg_arrival_delay_positive} min
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-1 block">
            Average wait when a flight is late
          </span>
        </div>
      </div>

      {/* 5. Cancellation Rate */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-rose-500">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Cancelled Flights</span>
          <div className="p-2 rounded-lg bg-rose-50 text-rose-600">
            <XCircle className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-rose-600 tracking-tight">
            {kpis.cancel_rate}%
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-1 block">
            {kpis.cancelled_flights.toLocaleString()} trips cancelled
          </span>
        </div>
      </div>

      {/* 6. Total Delay Burden */}
      <div className="card-royal p-4 flex flex-col justify-between border-t-4 border-t-indigo-600">
        <div className="flex items-center justify-between text-slate-400 mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Total Time Lost</span>
          <div className="p-2 rounded-lg bg-indigo-50 text-indigo-600">
            <Flame className="w-4 h-4" />
          </div>
        </div>
        <div>
          <div className="text-2xl font-black text-indigo-900 tracking-tight">
            {totalBurdensMillions}M min
          </div>
          <span className="text-[11px] font-medium text-slate-500 mt-1 block">
            Total passenger minutes delayed
          </span>
        </div>
      </div>
    </div>
  );
};

export default KpiBanner;
