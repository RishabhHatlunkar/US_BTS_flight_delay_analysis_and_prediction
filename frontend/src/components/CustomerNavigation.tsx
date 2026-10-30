"use client";

import React from "react";
import { Plane, Building2, ShieldAlert, Users, Layers, ArrowRight } from "lucide-react";
import { TargetCustomerId } from "@/lib/types";

export type ViewSelection = TargetCustomerId | "global_warehouse";

interface CustomerNavigationProps {
  currentSelection: ViewSelection;
  onSelect: (selection: ViewSelection) => void;
}

interface CustomerItem {
  id: ViewSelection;
  title: string;
  badge: string;
  subtitle: string;
  keyMetric: string;
  icon: React.ComponentType<{ className?: string }>;
  colorStyle: {
    bg: string;
    border: string;
    activeBorder: string;
    activeRing: string;
    iconBg: string;
    iconText: string;
    badgeBg: string;
    badgeText: string;
  };
}

const CUSTOMER_ITEMS: CustomerItem[] = [
  {
    id: "airlines",
    title: "Airlines & Flight Planners",
    badge: "For Airlines",
    subtitle: "Stopping domino delays when an incoming plane lands late",
    keyMetric: "41% Domino Delays",
    icon: Plane,
    colorStyle: {
      bg: "bg-blue-50/60",
      border: "border-blue-200/80",
      activeBorder: "border-blue-600",
      activeRing: "ring-2 ring-blue-500/20",
      iconBg: "bg-blue-600",
      iconText: "text-white",
      badgeBg: "bg-blue-100",
      badgeText: "text-blue-800",
    },
  },
  {
    id: "airports",
    title: "Airport Managers & Towers",
    badge: "For Airports",
    subtitle: "Clearing runway traffic jams & keeping planes moving",
    keyMetric: "28m Peak Taxi Line",
    icon: Building2,
    colorStyle: {
      bg: "bg-sky-50/60",
      border: "border-sky-200/80",
      activeBorder: "border-sky-600",
      activeRing: "ring-2 ring-sky-500/20",
      iconBg: "bg-sky-600",
      iconText: "text-white",
      badgeBg: "bg-sky-100",
      badgeText: "text-sky-800",
    },
  },
  {
    id: "regulators",
    title: "Air Traffic & Regulators",
    badge: "For Regulators (FAA)",
    subtitle: "Managing crowded skies & protecting passenger rights",
    keyMetric: "23% Airway Jams",
    icon: ShieldAlert,
    colorStyle: {
      bg: "bg-indigo-50/60",
      border: "border-indigo-200/80",
      activeBorder: "border-indigo-600",
      activeRing: "ring-2 ring-indigo-500/20",
      iconBg: "bg-indigo-600",
      iconText: "text-white",
      badgeBg: "bg-indigo-100",
      badgeText: "text-indigo-800",
    },
  },
  {
    id: "passengers",
    title: "Passengers & Travel Apps",
    badge: "For Travelers & OTAs",
    subtitle: "Avoiding missed connections & instant cash delay payouts",
    keyMetric: "1.4M Missed Turns",
    icon: Users,
    colorStyle: {
      bg: "bg-emerald-50/60",
      border: "border-emerald-200/80",
      activeBorder: "border-emerald-600",
      activeRing: "ring-2 ring-emerald-500/20",
      iconBg: "bg-emerald-600",
      iconText: "text-white",
      badgeBg: "bg-emerald-100",
      badgeText: "text-emerald-800",
    },
  },
  {
    id: "global_warehouse",
    title: "All Flight Data Explorer",
    badge: "Full Database",
    subtitle: "Explore all 30.7 million raw flight records and charts",
    keyMetric: "30.7M Flights",
    icon: Layers,
    colorStyle: {
      bg: "bg-slate-50/60",
      border: "border-slate-200/80",
      activeBorder: "border-slate-800",
      activeRing: "ring-2 ring-slate-500/20",
      iconBg: "bg-slate-800",
      iconText: "text-white",
      badgeBg: "bg-slate-200",
      badgeText: "text-slate-800",
    },
  },
];

export const CustomerNavigation: React.FC<CustomerNavigationProps> = ({
  currentSelection,
  onSelect,
}) => {
  return (
    <div className="space-y-3">
      {/* Bar Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-blue-900 bg-blue-100/70 px-2.5 py-0.5 rounded-md">
              Choose Who You Are
            </span>
            <span className="text-xs text-slate-500 font-medium hidden md:inline">
              Select your role to see your specific delays, why they happen, and tested fixes
            </span>
          </div>
          <h2 className="text-base font-bold text-slate-900 mt-1">
            Flight Problem Solver: Pick Your Role
          </h2>
        </div>

        <div className="text-xs text-slate-500">
          Source: <strong className="text-slate-700">Official US Bureau of Transportation Statistics (BTS)</strong>
        </div>
      </div>

      {/* Grid of Customer Selectable Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {CUSTOMER_ITEMS.map((item) => {
          const Icon = item.icon;
          const isSelected = currentSelection === item.id;
          const { colorStyle } = item;

          return (
            <button
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={`p-3.5 rounded-xl border text-left transition-all duration-200 flex flex-col justify-between relative group ${
                isSelected
                  ? `bg-white shadow-md ${colorStyle.activeBorder} ${colorStyle.activeRing} scale-[1.01]`
                  : `bg-white/80 hover:bg-white border-slate-200 hover:border-slate-300 shadow-sm hover:shadow`
              }`}
            >
              {isSelected && (
                <div className="absolute top-0 right-0 left-0 h-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-xl" />
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <div
                    className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      isSelected
                        ? colorStyle.iconBg
                        : "bg-slate-100 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-600"
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isSelected
                        ? `${colorStyle.badgeBg} ${colorStyle.badgeText}`
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {item.badge}
                  </span>
                </div>

                <div className="font-bold text-xs text-slate-900 line-clamp-1">{item.title}</div>
                <p className="text-[11px] text-slate-500 line-clamp-2 mt-0.5 leading-snug">
                  {item.subtitle}
                </p>
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[11px]">
                <span className="font-mono font-bold text-blue-900">{item.keyMetric}</span>
                <span
                  className={`flex items-center font-semibold text-[10px] ${
                    isSelected ? "text-blue-600 font-bold" : "text-slate-400 group-hover:text-blue-600"
                  }`}
                >
                  <span>{isSelected ? "Active View" : "Open View"}</span>
                  <ArrowRight className="w-3 h-3 ml-0.5" />
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default CustomerNavigation;
