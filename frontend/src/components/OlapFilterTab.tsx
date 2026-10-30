"use client";

import React, { useState } from "react";
import { applyOlapFilter } from "@/lib/api";
import { OlapFilterParams, Kpis } from "@/lib/types";
import { Filter, RotateCcw, Sparkles, CheckCircle2, AlertTriangle } from "lucide-react";

interface OlapResponse {
  kpis?: Kpis;
  filtered_flights?: number;
  message?: string;
  source?: string;
}

export const OlapFilterTab: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  const [selectedAirline, setSelectedAirline] = useState<string>("");
  const [selectedAirport, setSelectedAirport] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OlapResponse | null>(null);

  const handleApply = async () => {
    setLoading(true);
    const filters: OlapFilterParams = {};
    if (selectedYear) filters.years = [selectedYear];
    if (selectedAirline) filters.airlines = [selectedAirline];
    if (selectedAirport.trim()) filters.origins = [selectedAirport.toUpperCase().trim()];

    try {
      const res = await applyOlapFilter(filters);
      setResult(res);
    } catch {
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedYear(null);
    setSelectedAirline("");
    setSelectedAirport("");
    setResult(null);
  };

  return (
    <div className="space-y-6">
      <div className="card-royal p-6 bg-white border border-blue-100">
        <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
          <Filter className="w-6 h-6 text-blue-700" />
          <span>Interactive OLAP Slice &amp; Dice Engine</span>
        </h3>
        <p className="text-xs text-slate-500 mt-1">
          Perform live dynamic multidimensional filtering on Databricks Gold Fact data by Year, Reporting Airline, and Origin Hub
        </p>

        {/* Filter Controls Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mt-6 p-4 rounded-xl bg-slate-50 border border-slate-200">
          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">Year</label>
            <select
              value={selectedYear || ""}
              onChange={(e) => setSelectedYear(e.target.value ? Number(e.target.value) : null)}
              className="w-full text-xs font-semibold px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Years (2020-2025)</option>
              <option value="2024">2024</option>
              <option value="2025">2025</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">Airline</label>
            <select
              value={selectedAirline}
              onChange={(e) => setSelectedAirline(e.target.value)}
              className="w-full text-xs font-semibold px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Operating Carriers</option>
              <option value="AA">AA - American Airlines</option>
              <option value="DL">DL - Delta Air Lines</option>
              <option value="UA">UA - United Airlines</option>
              <option value="WN">WN - Southwest Airlines</option>
              <option value="9E">9E - Endeavor Air</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-bold text-slate-600 block mb-1">Origin Airport</label>
            <input
              type="text"
              placeholder="e.g. JFK, ORD, ATL"
              value={selectedAirport}
              onChange={(e) => setSelectedAirport(e.target.value)}
              className="w-full text-xs font-semibold px-3 py-2 rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 uppercase"
            />
          </div>

          <div className="flex items-end space-x-2">
            <button
              onClick={handleApply}
              disabled={loading}
              className="flex-1 py-2 px-4 rounded-lg gradient-royal text-white text-xs font-bold shadow-md shadow-blue-500/20 hover:opacity-95 active:scale-95 transition-all disabled:opacity-50"
            >
              {loading ? "Querying..." : "Apply Slice"}
            </button>
            <button
              onClick={handleReset}
              className="p-2 rounded-lg bg-white border border-slate-300 text-slate-600 hover:bg-slate-100 transition-colors"
              title="Reset Filters"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Dynamic Results Display */}
      {result && result.kpis && (
        <div className="card-royal p-6 border-2 border-blue-200 bg-white">
          <div className="flex items-center justify-between pb-3 mb-4 border-b border-blue-100">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-blue-600" />
              <h4 className="text-base font-bold text-blue-950">Filtered OLAP Slice Performance</h4>
            </div>
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800">
              Databricks Gold Fact
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-100">
              <span className="text-xs font-semibold text-slate-500 block">Sample Filter Volume</span>
              <span className="text-2xl font-black text-blue-900 mt-1 block">
                {result.kpis.total_flights?.toLocaleString() || "0"}
              </span>
            </div>
            <div className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-100">
              <span className="text-xs font-semibold text-slate-500 block">On-Time Rate</span>
              <span className="text-2xl font-black text-emerald-700 mt-1 block">
                {(100 - (result.kpis.arr_delay_rate || 0)).toFixed(1)}%
              </span>
            </div>
            <div className="p-4 rounded-xl bg-amber-50/60 border border-amber-100">
              <span className="text-xs font-semibold text-slate-500 block">Delay Rate (≥15m)</span>
              <span className="text-2xl font-black text-amber-600 mt-1 block">
                {result.kpis.arr_delay_rate?.toFixed(1) || "0.0"}%
              </span>
            </div>
            <div className="p-4 rounded-xl bg-rose-50/60 border border-rose-100">
              <span className="text-xs font-semibold text-slate-500 block">Cancellation Rate</span>
              <span className="text-2xl font-black text-rose-600 mt-1 block">
                {result.kpis.cancel_rate?.toFixed(2) || "0.00"}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OlapFilterTab;
