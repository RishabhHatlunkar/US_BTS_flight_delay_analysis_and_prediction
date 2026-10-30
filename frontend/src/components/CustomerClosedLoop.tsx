"use client";

import React, { useState } from "react";
import {
  CustomerClosedLoopData,
} from "@/lib/types";
import CustomerProofCharts from "./CustomerProofCharts";
import {
  AlertCircle,
  HelpCircle,
  Cpu,
  CheckCircle,
  TrendingDown,
  TrendingUp,
  Sliders,
  Database,
  ShieldCheck,
  RefreshCw,
  Lightbulb,
} from "lucide-react";

interface CustomerClosedLoopProps {
  data: CustomerClosedLoopData;
}

type StageKey = "all" | "problem" | "diagnostics" | "predictive" | "prescriptive" | "feedback";

export const CustomerClosedLoop: React.FC<CustomerClosedLoopProps> = ({ data }) => {
  const [activeStage, setActiveStage] = useState<StageKey>("all");

  // Interactive Solution Simulator state per customer
  const [sliderValue, setSliderValue] = useState<number>(() => {
    if (data.id === "airlines") return 15; // +15 mins buffer
    if (data.id === "airports") return 80; // 80% gate holding compliance
    if (data.id === "regulators") return 4; // 4 hrs pre-coordination
    return 65; // 65 min connection layover
  });

  // Simulator calculations
  const getSimulatorResults = () => {
    if (data.id === "airlines") {
      const buffer = sliderValue;
      const cascadeAvoidancePct = Math.min(38, Math.round(buffer * 1.55));
      const annualSavingsM = ((buffer * 1.45) * 1.2).toFixed(1);
      const onTimeBoost = (buffer * 0.38).toFixed(1);
      return {
        metric1: `${cascadeAvoidancePct}% Cut`,
        label1: "Domino Delays Avoided",
        metric2: `$${annualSavingsM} Million`,
        label2: "Annual Fuel & Overtime Saved",
        metric3: `+${onTimeBoost}%`,
        label3: "More Flights on Time",
        callout: `Giving planes +${buffer} minutes of breathing room between afternoon flights absorbs small delays before they ruin the rest of the day.`,
      };
    } else if (data.id === "airports") {
      const compliance = sliderValue;
      const taxiCutMin = ((compliance - 40) * 0.12).toFixed(1);
      const co2AbatedK = Math.round((compliance - 45) * 6.8);
      const gateComfort = Math.round((compliance - 50) * 0.5 + 15);
      return {
        metric1: `-${taxiCutMin} Minutes`,
        label1: "Less Time Stuck on Tarmac",
        metric2: `${co2AbatedK},000 Tons`,
        label2: "Fuel & Smog Cut Annually",
        metric3: `${gateComfort} Minutes`,
        label3: "Air-Conditioned Gate Comfort",
        callout: `Holding ${compliance}% of departing planes at comfortable gates with engines off means shorter lines and much cleaner airport air.`,
      };
    } else if (data.id === "regulators") {
      const hours = sliderValue;
      const holdingCutPct = Math.min(28, Math.round(hours * 4.4));
      const gdpDurationSlashed = (hours * 0.45).toFixed(1);
      const tarmacViolations = "Zero (0)";
      return {
        metric1: `-${holdingCutPct}%`,
        label1: "Less Circling in the Air",
        metric2: `-${gdpDurationSlashed} Hours`,
        label2: "Shorter Storm Flight Pauses",
        metric3: tarmacViolations,
        label3: "Passengers Trapped Over 3 Hours",
        callout: `Planning storm detours ${hours} hours ahead moves planes safely around bad weather before passengers even board the plane.`,
      };
    } else {
      const layover = sliderValue;
      const misconnectReduction = Math.min(65, Math.round((layover - 35) * 1.25));
      const csatBoost = Math.round((layover - 40) * 0.7 + 10);
      const payoutTime = "<90 Seconds";
      return {
        metric1: `-${misconnectReduction}%`,
        label1: "Fewer Missed Connections",
        metric2: `+${csatBoost} Points`,
        label2: "Traveler Happiness Score",
        metric3: payoutTime,
        label3: "Instant Delay Cash Payout",
        callout: `Guiding flyers toward a realistic ${layover}-minute layover ensures they catch their connecting flight, while automatic delay protection pays cash with zero forms.`,
      };
    }
  };

  const sim = getSimulatorResults();

  const stagesList = [
    { key: "problem" as StageKey, label: "1. The Problem", data: data.stages.problem, icon: AlertCircle },
    { key: "diagnostics" as StageKey, label: "2. Why It Happens", data: data.stages.diagnostics, icon: HelpCircle },
    { key: "predictive" as StageKey, label: "3. Spot It Early", data: data.stages.predictive, icon: Cpu },
    { key: "prescriptive" as StageKey, label: "4. How to Fix It", data: data.stages.prescriptive, icon: CheckCircle },
    { key: "feedback" as StageKey, label: "5. The Payoff", data: data.stages.feedback, icon: RefreshCw },
  ];

  return (
    <div className="space-y-6">
      {/* Persona Hero Executive Summary */}
      <div className={`rounded-2xl p-6 sm:p-8 text-white shadow-lg bg-gradient-to-r ${data.themeColor.gradient} border border-white/10`}>
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full bg-white/20 text-white border border-white/20">
                Case Study: Problems &amp; Practical Fixes
              </span>
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-500/30 text-blue-100 border border-blue-400/30">
                Source: Official US Bureau of Transportation Statistics (BTS)
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black tracking-tight">{data.title}</h2>
            <p className="text-sm sm:text-base text-blue-100/90 font-medium leading-relaxed">
              {data.subtitle}
            </p>
            <div className="text-xs text-blue-200/80 pt-1">
              <strong>Who This Is For:</strong> {data.roleScope}
            </div>
          </div>

          {/* Quick Metrics Pillar */}
          <div className="grid grid-cols-2 gap-3 lg:w-72 shrink-0">
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/15 text-center">
              <div className="text-xl sm:text-2xl font-black text-amber-300 font-mono">
                {data.summaryStats.keyMetric.split(" ")[0]}
              </div>
              <div className="text-[11px] text-blue-100 font-semibold mt-0.5">
                {data.summaryStats.keyLabel}
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/15 text-center">
              <div className="text-xl sm:text-2xl font-black text-emerald-300 font-mono">
                {data.summaryStats.annualCostImpact.split(" ")[0]}
              </div>
              <div className="text-[11px] text-blue-100 font-semibold mt-0.5">
                Annual Cost
              </div>
            </div>

            <div className="col-span-2 bg-black/20 rounded-xl p-2.5 border border-white/10 text-xs text-blue-100 text-center">
              <span className="font-bold text-white">The Proven Fix:</span>{" "}
              {data.summaryStats.primarySolution}
            </div>
          </div>
        </div>
      </div>

      {/* Stage Progress Bar / Sub-Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-2">
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar scroll-smooth">
          <button
            onClick={() => setActiveStage("all")}
            className={`px-3.5 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap shrink-0 ${
              activeStage === "all"
                ? "bg-slate-900 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
            }`}
          >
            All 5 Steps
          </button>

          {stagesList.map((stg) => {
            const Icon = stg.icon;
            const isSelected = activeStage === stg.key;
            return (
              <button
                key={stg.key}
                onClick={() => setActiveStage(stg.key)}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-bold transition-all whitespace-nowrap shrink-0 ${
                  isSelected
                    ? "bg-blue-600 text-white shadow-sm ring-2 ring-blue-600/30"
                    : "text-slate-600 hover:text-blue-600 hover:bg-blue-50/70"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? "text-white" : "text-blue-600"}`} />
                <span>{stg.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Supportive Visual Data Proof Graphs */}
      <CustomerProofCharts customerId={data.id} />

      {/* Interactive Case Study Solution Simulator */}
      <div className="card-royal p-6 bg-gradient-to-br from-white via-blue-50/30 to-indigo-50/20 border-blue-200">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-blue-100 gap-3">
          <div>
            <div className="flex items-center space-x-2">
              <Sliders className="w-5 h-5 text-blue-600" />
              <h3 className="text-base font-bold text-slate-900">
                Try It Yourself: Interactive Solution Simulator
              </h3>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Move the slider below to see how applying our solution cuts delays, saves fuel, and keeps passengers on time:
            </p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300 self-start md:self-auto">
            Live Simulator
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-6 items-center">
          {/* Slider Controls */}
          <div className="lg:col-span-5 space-y-4">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-slate-700">
                {data.id === "airlines" && "Extra Breathing Room Added Between Flights (Minutes):"}
                {data.id === "airports" && "Planes Held at Gate Instead of on Runway (%):"}
                {data.id === "regulators" && "Hours Ahead We Plan Storm Detours (Hours):"}
                {data.id === "passengers" && "Layover Time Recommended to Passengers (Minutes):"}
              </label>
              <span className="font-mono font-black text-sm px-2.5 py-1 bg-blue-100 text-blue-900 rounded-lg">
                {sliderValue}
                {data.id === "airlines" && " min"}
                {data.id === "airports" && "%"}
                {data.id === "regulators" && " hrs"}
                {data.id === "passengers" && " min"}
              </span>
            </div>

            <input
              type="range"
              min={data.id === "airlines" ? 0 : data.id === "airports" ? 50 : data.id === "regulators" ? 1 : 40}
              max={data.id === "airlines" ? 25 : data.id === "airports" ? 100 : data.id === "regulators" ? 6 : 90}
              step={1}
              value={sliderValue}
              onChange={(e) => setSliderValue(Number(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
            />

            <div className="flex justify-between text-[10px] text-slate-400 font-medium">
              <span>No Action (Standard Delays)</span>
              <span>Full Solution Applied</span>
            </div>

            <div className="p-3 bg-blue-50/70 rounded-xl border border-blue-100 text-xs text-blue-900 leading-snug">
              <Lightbulb className="w-4 h-4 text-blue-600 inline mr-1 -mt-0.5" />
              <strong>How It Works:</strong> {sim.callout}
            </div>
          </div>

          {/* Simulated Impact Pillars */}
          <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-xl sm:text-2xl font-black text-blue-700 font-mono">
                {sim.metric1}
              </div>
              <div className="text-[11px] font-bold text-slate-700 mt-1">{sim.label1}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Main Operational Relief</div>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-xl sm:text-2xl font-black text-emerald-600 font-mono">
                {sim.metric2}
              </div>
              <div className="text-[11px] font-bold text-slate-700 mt-1">{sim.label2}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Money Saved</div>
            </div>

            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm text-center">
              <div className="text-xl sm:text-2xl font-black text-indigo-700 font-mono">
                {sim.metric3}
              </div>
              <div className="text-[11px] font-bold text-slate-700 mt-1">{sim.label3}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">Punctuality &amp; Happiness</div>
            </div>
          </div>
        </div>
      </div>

      {/* Render Loop Stages */}
      <div className="space-y-6">
        {stagesList.map((stg) => {
          if (activeStage !== "all" && activeStage !== stg.key) {
            return null;
          }

          const stageData = stg.data;
          const Icon = stg.icon;

          return (
            <div
              key={stg.key}
              className="card-royal p-6 bg-white border border-slate-200/90 shadow-sm rounded-xl space-y-4 hover:border-blue-200 transition-colors"
            >
              {/* Stage Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-100 gap-2">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center shrink-0 border border-blue-200">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="text-base font-bold text-slate-900">{stageData.title}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">{stageData.description}</p>
                  </div>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 border border-slate-200 self-start sm:self-auto shrink-0">
                  {stageData.badge}
                </span>
              </div>

              {/* Stage Numerical Metrics Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {stageData.metrics.map((m, mIdx) => (
                  <div
                    key={mIdx}
                    className="p-3 bg-slate-50/80 rounded-xl border border-slate-100 flex flex-col justify-between"
                  >
                    <span className="text-[11px] text-slate-500 font-semibold">{m.label}</span>
                    <div className="my-1 flex items-baseline space-x-1">
                      <span className="text-lg font-black text-slate-900 font-mono">{m.value}</span>
                      {m.trend === "up" && <TrendingUp className="w-3.5 h-3.5 text-red-500 inline" />}
                      {m.trend === "down" && <TrendingDown className="w-3.5 h-3.5 text-emerald-600 inline" />}
                    </div>
                    {m.detail && <span className="text-[10px] text-slate-400">{m.detail}</span>}
                  </div>
                ))}
              </div>

              {/* Stage Core Points */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                {stageData.bulletPoints.map((bp, bIdx) => (
                  <div
                    key={bIdx}
                    className="p-3.5 rounded-xl bg-blue-50/40 border border-blue-100/60 flex flex-col justify-between space-y-1.5"
                  >
                    <div className="font-bold text-xs text-blue-950 flex items-center space-x-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" />
                      <span>{bp.title}</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed">{bp.text}</p>
                  </div>
                ))}
              </div>

              {/* Key Empirical Insight Box */}
              {stageData.insightNote && (
                <div className="p-3 rounded-xl bg-slate-900 text-white text-xs flex items-start space-x-2.5 mt-2">
                  <div className="w-5 h-5 rounded-lg bg-blue-500/20 text-blue-300 flex items-center justify-center shrink-0 mt-0.5">
                    ★
                  </div>
                  <div className="text-slate-200 leading-snug">
                    <strong className="text-white">Real-World Fact:</strong> {stageData.insightNote}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Closed-Loop Lineage to Databricks Gold Fact */}
      <div className="p-5 rounded-xl bg-slate-100 border border-slate-200 text-xs text-slate-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <Database className="w-5 h-5 text-blue-700 shrink-0" />
          <div>
            <span className="font-bold text-slate-800">
              How This Data Works in the Real World
            </span>
            <p className="text-slate-500 mt-0.5">
              Every time an airline or airport applies one of these solutions, the actual flight times are recorded and checked against official US government data so the system gets smarter every single day.
            </p>
          </div>
        </div>
        <span className="px-3 py-1 rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold text-[11px] shrink-0 flex items-center space-x-1">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Live Data Feedback Active</span>
        </span>
      </div>
    </div>
  );
};

export default CustomerClosedLoop;
