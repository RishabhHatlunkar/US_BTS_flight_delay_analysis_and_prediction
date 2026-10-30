"use client";

import React from "react";
import { Plane, Building, ShieldAlert, Users, TrendingUp, CheckCircle2, ArrowRight } from "lucide-react";
import { TargetCustomerId } from "@/lib/types";

interface StakeholderTabProps {
  onSelectCustomer?: (customerId: TargetCustomerId) => void;
}

export const StakeholderTab: React.FC<StakeholderTabProps> = ({ onSelectCustomer }) => {
  return (
    <div className="space-y-6">
      <div className="card-royal p-6 bg-white border border-blue-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-blue-950 flex items-center space-x-2">
            <Users className="w-6 h-6 text-blue-700" />
            <span>Solutions Tailored for Every Role</span>
          </h3>
          <p className="text-xs text-slate-500 mt-1">
            Practical, real-world fixes based on 30.7 million US flights for airlines, airport managers, air traffic controllers, and passengers.
          </p>
        </div>

        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 text-blue-800 border border-blue-200 self-start sm:self-auto">
          4 Roles Covered
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Stakeholder 1: Commercial Airlines */}
        <div className="card-royal p-6 border-t-4 border-t-blue-700 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 rounded-xl bg-blue-50 text-blue-800">
                <Plane className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-blue-950">Airlines &amp; Flight Planners</h4>
                <span className="text-xs text-blue-600 font-semibold">Flight Dispatchers, Plane Schedulers &amp; Ground Crews</span>
              </div>
            </div>

            <ul className="space-y-3 text-xs text-slate-600 mb-6">
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Stop Domino Delays:</strong> Incoming plane delays cause 41% of all delay time. Adding 15 minutes of breathing room between afternoon flights stops the domino effect.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Send Ground Crews Early:</strong> Send baggage handlers and fuelers to the gate 10 minutes before touchdown so they start the second the plane parks.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Swap in Backup Planes:</strong> If an incoming flight is delayed over 35 minutes, swap in a spare plane sitting at the hub so the next 150 passengers leave on time.</span>
              </li>
            </ul>
          </div>

          {onSelectCustomer && (
            <button
              onClick={() => onSelectCustomer("airlines")}
              className="w-full py-2 px-3 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors border border-blue-200"
            >
              <span>See Complete 5-Step Solution Loop</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Stakeholder 2: Airport Authorities */}
        <div className="card-royal p-6 border-t-4 border-t-sky-600 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 rounded-xl bg-sky-50 text-sky-800">
                <Building className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-blue-950">Airport Managers &amp; Towers</h4>
                <span className="text-xs text-sky-600 font-semibold">Airport Directors, Gate Planners &amp; Runway Controllers</span>
              </div>
            </div>

            <ul className="space-y-3 text-xs text-slate-600 mb-6">
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Hold at Gate, Not on the Runway:</strong> Keep planes waiting at comfortable gates with air conditioning and engines off until the runway is actually clear.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Smart Gate Parking:</strong> Park heavy cross-country flights near their departure runway heading to cut taxi driving across the airport by nearly 2 miles.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Faster Winter De-Icing Lines:</strong> Pre-sort planes into separate de-icing bays by size so smaller planes aren't trapped waiting behind jumbo jets.</span>
              </li>
            </ul>
          </div>

          {onSelectCustomer && (
            <button
              onClick={() => onSelectCustomer("airports")}
              className="w-full py-2 px-3 rounded-lg bg-sky-50 hover:bg-sky-100 text-sky-700 text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors border border-sky-200"
            >
              <span>See Complete 5-Step Solution Loop</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Stakeholder 3: Aviation Regulators (FAA/DOT) */}
        <div className="card-royal p-6 border-t-4 border-t-indigo-600 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 rounded-xl bg-indigo-50 text-indigo-800">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-blue-950">Air Traffic &amp; Regulators (FAA / DOT)</h4>
                <span className="text-xs text-indigo-600 font-semibold">Sky Flow Controllers &amp; Passenger Protection Officials</span>
              </div>
            </div>

            <ul className="space-y-3 text-xs text-slate-600 mb-6">
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Storm Detours Before Boarding:</strong> Give pilots pre-approved detours around storms before pushback so planes don't waste fuel circling in clouds.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>The 3-Hour Passenger Protection Rule:</strong> Order planes back to the gate at 120 minutes so no traveler is trapped on the tarmac past the 3-hour limit.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Public On-Time Scorecards:</strong> Publish honest monthly scorecards comparing true airline arrival performance so travelers know who is reliable.</span>
              </li>
            </ul>
          </div>

          {onSelectCustomer && (
            <button
              onClick={() => onSelectCustomer("regulators")}
              className="w-full py-2 px-3 rounded-lg bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors border border-indigo-200"
            >
              <span>See Complete 5-Step Solution Loop</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Stakeholder 4: Travel Aggregators & Insurers */}
        <div className="card-royal p-6 border-t-4 border-t-emerald-600 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-3 rounded-xl bg-emerald-50 text-emerald-800">
                <TrendingUp className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-base font-bold text-blue-950">Passengers, Travel Apps &amp; Insurers</h4>
                <span className="text-xs text-emerald-600 font-semibold">Travelers, Booking Apps (Google Flights, Expedia) &amp; Insurers</span>
              </div>
            </div>

            <ul className="space-y-3 text-xs text-slate-600 mb-6">
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Color-Coded Layover Badges:</strong> Show green, yellow, or red badges when booking so travelers know if a 45-minute layover is safe or risky.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Automatic Backup Seat Reservation:</strong> Hold a seat on the next flight before you even land if an incoming delay makes missing your connection certain.</span>
              </li>
              <li className="flex items-start space-x-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                <span><strong>Instant Cash Back for Delays:</strong> If your flight is delayed over 2 hours, get $150–$300 sent straight to your phone wallet automatically with zero paperwork.</span>
              </li>
            </ul>
          </div>

          {onSelectCustomer && (
            <button
              onClick={() => onSelectCustomer("passengers")}
              className="w-full py-2 px-3 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold flex items-center justify-center space-x-1.5 transition-colors border border-emerald-200"
            >
              <span>See Complete 5-Step Solution Loop</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default StakeholderTab;
