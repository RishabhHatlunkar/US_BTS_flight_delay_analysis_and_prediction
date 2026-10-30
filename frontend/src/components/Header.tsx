"use client";

import React, { useState } from "react";
import { Plane, Database, RefreshCw } from "lucide-react";
import { refreshDatabricksCache } from "@/lib/api";

interface HeaderProps {
  totalFlights: number;
  catalog: string;
  schema: string;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  totalFlights,
  catalog,
  schema,
  onRefresh,
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refreshDatabricksCache();
    onRefresh();
    setTimeout(() => setIsRefreshing(false), 800);
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-blue-100 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Logo & Platform Info */}
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl gradient-royal flex items-center justify-center shadow-md shadow-blue-500/20 text-white">
              <Plane className="w-6 h-6 transform -rotate-45" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-black tracking-tight text-blue-900">
                  SkyAnalytics<span className="text-blue-600">.</span>
                </h1>
                <span className="px-2.5 py-0.5 text-xs font-bold rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                  Flight Delay Problem Solver
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium flex items-center space-x-1.5 mt-0.5">
                <Database className="w-3.5 h-3.5 text-blue-600 inline" />
                <span>Source: US Bureau of Transportation Statistics Database</span>
              </p>
            </div>
          </div>

          {/* Right Controls: Volume Counter, Status Badge, Refresh Button */}
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex flex-col text-right">
              <span className="text-xs text-slate-500 font-medium">Flights Analyzed</span>
              <span className="text-sm font-extrabold text-blue-900 tracking-tight">
                {totalFlights.toLocaleString()} Flights
              </span>
            </div>

            <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Live Flight Data</span>
            </div>

            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl gradient-royal text-white text-xs font-semibold hover:opacity-95 shadow-md shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? "animate-spin" : ""}`} />
              <span className="hidden sm:inline">Refresh Data</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
