"use client";

import React from "react";
import { DelayCause } from "@/lib/types";
import { AlertCircle, Wrench, CloudRain, Shield, RefreshCw } from "lucide-react";

interface RootCausesTabProps {
  causes: DelayCause[];
  lateAircraftShare: number;
}

export const RootCausesTab: React.FC<RootCausesTabProps> = ({
  causes,
  lateAircraftShare,
}) => {
  const getCauseIcon = (name: string) => {
    const n = name.toLowerCase();
    if (n.includes("carrier")) return <Wrench className="w-5 h-5 text-blue-600" />;
    if (n.includes("weather")) return <CloudRain className="w-5 h-5 text-amber-500" />;
    if (n.includes("security")) return <Shield className="w-5 h-5 text-red-500" />;
    if (n.includes("late") || n.includes("aircraft")) return <RefreshCw className="w-5 h-5 text-purple-600" />;
    return <AlertCircle className="w-5 h-5 text-emerald-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Late Aircraft Cascade Highlight */}
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 rounded-xl p-6 text-white shadow-md border border-blue-700/50">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 border border-purple-400/30 flex items-center justify-center shrink-0">
              <RefreshCw className="w-6 h-6 text-purple-300" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h4 className="text-lg font-bold">Reactionary Cascade Effect (Late Aircraft Inbound)</h4>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-purple-400/20 text-purple-200 border border-purple-300/30">
                  Primary Culprit
                </span>
              </div>
              <p className="text-xs text-blue-200 mt-1 max-w-2xl">
                Delay propagation across multi-leg turnarounds accounts for the single largest share of US airline operational disruption.
              </p>
            </div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm border border-white/15 px-6 py-3 rounded-xl text-center self-stretch md:self-auto shrink-0">
            <div className="text-3xl font-black text-purple-300">
              {lateAircraftShare.toFixed(1)}%
            </div>
            <div className="text-xs uppercase tracking-wider text-blue-200 font-semibold">
              Share of All Delays
            </div>
          </div>
        </div>
      </div>

      {/* Cause breakdown cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {causes.map((c, idx) => {
          const name = c.Cause || c.cause || "Other Delay";
          const mins = c.Minutes ?? c.minutes ?? 0;
          const share = c["Share (%)"] ?? c.share ?? 0;

          return (
            <div
              key={idx}
              className="card-royal p-5 bg-white border border-blue-100 shadow-sm rounded-xl flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getCauseIcon(name)}
                    <span className="font-bold text-slate-800 text-sm">{name}</span>
                  </div>
                  <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                    {share.toFixed(1)}%
                  </span>
                </div>

                <div className="mt-4">
                  <div className="text-2xl font-black text-blue-950 font-mono">
                    {(mins / 1000000).toFixed(1)}M
                  </div>
                  <div className="text-xs text-slate-500">Delay Minutes Incurred</div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100">
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-blue-600 rounded-full"
                    style={{ width: `${Math.min(100, share)}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RootCausesTab;
