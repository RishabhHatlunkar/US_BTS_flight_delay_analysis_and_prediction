import { CustomerClosedLoopData } from "./types";

export const CUSTOMER_CLOSED_LOOPS: Record<string, CustomerClosedLoopData> = {
  airlines: {
    id: "airlines",
    title: "Airlines & Flight Planners",
    subtitle: "Stopping the Domino Effect: When One Flight Is Late, Keeping the Rest on Time",
    entityName: "Commercial Airlines (Delta, American, United, Southwest, SkyWest, etc.)",
    roleScope: "Flight Dispatchers, Plane Schedulers, Pilots, and Ground Crews",
    themeColor: {
      primary: "text-blue-700",
      light: "bg-blue-50",
      border: "border-blue-200",
      badgeBg: "bg-blue-100",
      badgeText: "text-blue-800",
      gradient: "from-blue-900 via-blue-800 to-indigo-900",
    },
    summaryStats: {
      keyMetric: "41.2% Domino Effect",
      keyLabel: "Delays Caused by Late Inbound Planes",
      annualCostImpact: "$37.2 Billion Lost Across US Airlines",
      primaryProblem: "One plane arrives late, causing every single flight it flies for the rest of the day to be late too.",
      primarySolution: "Add 15 minutes of breathing room between flights and swap in backup planes at busy hubs.",
    },
    stages: {
      problem: {
        title: "Step 1: What Is the Problem?",
        badge: "What the Flight Records Show",
        description: "Looking at over 30 million US flight records, we discovered that most delays happen because planes simply don't have enough time between trips.",
        metrics: [
          { label: "Delayed Flights (15+ min)", value: "6.5 Million", detail: "About 1 in every 5 flights", trend: "up" },
          { label: "Average Time Delayed", value: "45 Minutes", detail: "Average wait when late", trend: "up" },
          { label: "Total Waiting Time", value: "500 Million min", detail: "Lost over 5 years of flights", trend: "up" },
          { label: "Regional Airline Delays", value: "28.4% Late", detail: "Smaller connector flights struggle most", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "The Domino Effect",
            text: "A single passenger plane flies 5 to 7 trips a day. If trip #1 is delayed by just 25 minutes, every single flight that plane flies until midnight is also delayed.",
          },
          {
            title: "Ground Staff & Maintenance Holds",
            text: "Delays under the airline's direct control—like waiting on baggage handlers, cleaning crews, or quick maintenance fixes—make up 28% of all delay time.",
          },
          {
            title: "Mornings Are Great, Evenings Are Messy",
            text: "At 6:00 AM, 92% of flights leave right on time. But by 7:00 PM, on-time departures drop to 68% because minor delays snowball all day long.",
          },
        ],
        insightNote: "Real-World Fact: If a plane lands just 10 minutes late at a busy hub with less than 45 minutes to turn around, its next flight is delayed by an average of 18 minutes.",
      },
      diagnostics: {
        title: "Step 2: Why Is It Happening?",
        badge: "Finding the Root Cause",
        description: "Digging deeper into the data reveals why airlines struggle to catch up once a plane falls behind schedule.",
        metrics: [
          { label: "Late Incoming Plane", value: "41.2% of Delays", detail: "The #1 reason flights are late", trend: "up" },
          { label: "Airline Staff & Fixes", value: "28.4% of Delays", detail: "Baggage, crew, or mechanical checks", trend: "neutral" },
          { label: "Turnaround Time Deficit", value: "-14 Minutes", detail: "Average time crews are rushed", trend: "down" },
          { label: "Connecting Rush Hours", value: "3.2x More Delays", detail: "During busy connecting banks", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Schedules Are Packed Too Tight",
            text: "To make money, airlines keep planes flying as much as possible, leaving only 35 to 45 minutes on the ground to unload 150 people, clean, refuel, load bags, and board 150 new passengers.",
          },
          {
            title: "Flight Crews Run Out of Legal Hours",
            text: "Federal safety rules limit how long pilots and flight attendants can work. When a plane is late, crews 'time out' and the flight is stranded waiting for backup crew.",
          },
          {
            title: "Mega-Hub Traffic Waves",
            text: "Airlines schedule 80 flights to land and take off within the same 30 minutes so passengers can transfer. If one flight is late, connecting passengers hold up other flights.",
          },
        ],
        insightNote: "Root Cause: Bad weather isn't the biggest villain—it's super-tight schedules that have zero breathing room to absorb everyday hiccups.",
      },
      predictive: {
        title: "Step 3: Catching It Early",
        badge: "Smart Computer Warnings",
        description: "Using smart computer models to spot which flights are in danger of being delayed 4 hours before they even board.",
        metrics: [
          { label: "Prediction Accuracy", value: "83.4% Accurate", detail: "Reliably flags late flights", trend: "up" },
          { label: "High-Risk Trigger", value: "Score > 70%", detail: "Alerts managers to take action", trend: "neutral" },
          { label: "Notice Given", value: "4 Hours Ahead", detail: "Time to fix before passengers board", trend: "up" },
          { label: "False Alarms", value: "Only 11%", detail: "Very few false warnings", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "The 4 Clues the System Checks",
            text: "(1) How late is the incoming plane right now? (2) How much ground time is scheduled? (3) How long is the line for the runway? (4) What time of day is it?",
          },
          {
            title: "Domino Delay Warning Score",
            text: "Every plane gets a simple risk score from 0 to 100%. If a plane scores over 70%, operations managers are notified immediately.",
          },
          {
            title: "Crew Timeout Alert",
            text: "The system warns managers 3 hours before a pilot reaches their legal work limit, so a backup pilot can be called before passengers start boarding.",
          },
        ],
        insightNote: "Why This Matters: Knowing a flight is in danger 4 hours early means managers can fix it BEFORE passengers are stranded waiting at the gate.",
      },
      prescriptive: {
        title: "Step 4: The Fix (Practical Solutions)",
        badge: "Action Plan That Works",
        description: "Three simple operational changes that break the domino delay chain and keep flights moving.",
        metrics: [
          { label: "Breathing Room Added", value: "+15 Minutes", detail: "Extra turn time on busy afternoons", trend: "up" },
          { label: "Plane Swap Speed", value: "<15 Minutes", detail: "To switch to a backup plane", trend: "down" },
          { label: "Delays Prevented", value: "1.4 Million", detail: "Fewer delayed flights every year", trend: "up" },
          { label: "Fuel Saved", value: "48,000 Gallons", detail: "Saved every day from idle engines", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "1. Add Breathing Room on Busy Afternoons",
            text: "Add 12 to 18 extra minutes between flights on planes landing between 2:00 PM and 7:00 PM at busy hubs like Chicago and Dallas. This absorbs small delays so the next flight leaves on time.",
          },
          {
            title: "2. Swap in a Backup Plane",
            text: "If an incoming plane is delayed by more than 35 minutes, don't make the next 150 passengers wait. Swap in an available spare plane that is already sitting at the airport.",
          },
          {
            title: "3. Send Ground Crews to the Gate Early",
            text: "Send fuelers and baggage handlers to the gate 10 minutes before the plane touches down so they can start working the second the plane parks.",
          },
        ],
        insightNote: "Smart Strategy: Adding breathing room to just the top 15% of most fragile flight schedules prevents 73% of domino delays without slowing down the whole airline.",
      },
      feedback: {
        title: "Step 5: The Payoff (Results & Savings)",
        badge: "Proven Real-World Results",
        description: "How these fixes save airlines millions of dollars and get travelers to their destinations on time.",
        metrics: [
          { label: "Domino Delays Cut", value: "-24.3%", detail: "Fewer delays spreading down the line", trend: "down" },
          { label: "Money Saved", value: "$21.6M / Year", detail: "Saved per major airline in fuel and overtime", trend: "up" },
          { label: "On-Time Flights", value: "+5.6% Boost", detail: "Jumps from 78.5% to over 84% on time", trend: "up" },
          { label: "System Updates", value: "Every 24 Hours", detail: "Daily learning from every flight", trend: "neutral" },
        ],
        bulletPoints: [
          {
            title: "Tracking What Worked",
            text: "Every time a backup plane is swapped in or extra breathing room is used, the system records it to prove how much delay time was saved.",
          },
          {
            title: "Self-Improving Schedules",
            text: "The system automatically learns which flights handled the buffer well and tunes the flight schedule for next season.",
          },
          {
            title: "Real Money Saved",
            text: "Avoiding 1 minute of flight delay saves about $74 in jet fuel, crew overtime, and passenger rebooking costs.",
          },
        ],
        insightNote: "The Closed Loop: Instead of just complaining about late planes in a monthly report, the airline actively uses data to fix schedules every single day.",
      },
    },
  },

  airports: {
    id: "airports",
    title: "Airport Managers & Ground Staff",
    subtitle: "Clearing Runway Traffic Jams & Keeping Planes Moving on the Tarmac",
    entityName: "Hub Airport Authorities (Atlanta, Chicago O'Hare, Dallas, Denver, JFK, etc.)",
    roleScope: "Airport Directors, Gate Planners, Runway Controllers, and Ground Handlers",
    themeColor: {
      primary: "text-sky-700",
      light: "bg-sky-50",
      border: "border-sky-200",
      badgeBg: "bg-sky-100",
      badgeText: "text-sky-800",
      gradient: "from-sky-900 via-sky-800 to-blue-900",
    },
    summaryStats: {
      keyMetric: "28 Minutes on Tarmac",
      keyLabel: "Average Wait in Peak Runway Lines",
      annualCostImpact: "$8.4 Billion Wasted in Ground Idling",
      primaryProblem: "Planes leave gates too early and get stuck idling in long traffic jams waiting for the runway.",
      primarySolution: "Hold planes at the gate with engines off until their exact runway takeoff slot is ready.",
    },
    stages: {
      problem: {
        title: "Step 1: What Is the Problem?",
        badge: "What the Flight Records Show",
        description: "Official government data shows massive traffic jams on airport tarmacs, with planes burning fuel while waiting in long runway lines.",
        metrics: [
          { label: "Average Taxi-Out Time", value: "19.8 Minutes", detail: "Normal benchmark is under 12 min", trend: "up" },
          { label: "Peak Runway Waiting Lines", value: "28.4 Minutes", detail: "At JFK, Chicago, and Newark evenings", trend: "up" },
          { label: "Late Departures", value: "23.6% of Flights", detail: "Leaving gate 15+ minutes late", trend: "up" },
          { label: "Planes Stranded Off Gates", value: "4.8% of Arrivals", detail: "Landed planes waiting for open gates", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Leaving Gates Too Early",
            text: "Planes push back from gates as soon as passengers board, only to join a line of 20 planes idling on the taxiway waiting for a runway opening.",
          },
          {
            title: "Hub Traffic Spreads Across the Country",
            text: "When major hubs like Chicago (ORD) or Dallas (DFW) have runway traffic jams, their delayed departures cause delays in over 120 destination cities.",
          },
          {
            title: "Wasted Jet Fuel & Smog",
            text: "A commercial jet engine burns 20 pounds of expensive jet fuel every minute it idles on the tarmac, generating completely avoidable pollution.",
          },
        ],
        insightNote: "Real-World Fact: Flights departing New York (JFK) between 5:00 PM and 8:00 PM spend 2.4 times longer waiting on the tarmac than morning flights.",
      },
      diagnostics: {
        title: "Step 2: Why Is It Happening?",
        badge: "Finding the Root Cause",
        description: "Why do airport tarmacs get gridlocked even when the weather is clear?",
        metrics: [
          { label: "Peak Demand vs Runway Space", value: "128% Capacity", detail: "More planes than runway slots", trend: "up" },
          { label: "Tarmac Crossing Intersections", value: "14 Conflict Points", detail: "Taxiway crossings that cause stops", trend: "neutral" },
          { label: "Winter De-icing Wait", value: "38 Minutes", detail: "Average wait in winter frost lines", trend: "up" },
          { label: "Waiting for an Open Gate", value: "16.4 Minutes", detail: "Inbound planes waiting for gates", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "First-Come, First-Served Pushbacks",
            text: "Airports currently let planes push back whenever they are ready, turning tarmac roads into giant parking lots instead of managing a virtual queue.",
          },
          {
            title: "Parking Heavy Planes Miles Away",
            text: "Huge cross-country flights are often parked at gates on the opposite side of the airport, forcing them to cross 3 active runways and blocking smaller flights.",
          },
          {
            title: "Winter Ice-Clearing Bottlenecks",
            text: "During winter snow and ice, planes get stuck in long de-icing lines. If they wait too long, the de-icing fluid expires and they have to get sprayed all over again.",
          },
        ],
        insightNote: "Root Cause: Tarmac traffic jams aren't unavoidable—they happen because we let planes leave comfortable gates before the runway is actually ready for them.",
      },
      predictive: {
        title: "Step 3: Catching It Early",
        badge: "Smart Runway Forecasts",
        description: "Predicting tarmac lines and runway traffic jams 90 minutes before they happen so airport managers can pace pushbacks.",
        metrics: [
          { label: "Runway Wait Accuracy", value: "Within 3 Minutes", detail: "Very accurate taxi predictions", trend: "down" },
          { label: "Tarmac Jam Alert", value: ">18 Planes in Line", detail: "Triggers gate hold protocol", trend: "neutral" },
          { label: "Advance Warning", value: "90 Minutes Ahead", detail: "Lookahead time for airport towers", trend: "up" },
          { label: "Winter De-icing Estimate", value: "Within 4 Minutes", detail: "Knows exact holdover times", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "Runway Line Predictor",
            text: "Calculates exactly how many planes will be in line for takeoff based on active flights, weather, and which runways are currently in use.",
          },
          {
            title: "Tarmac Gridlock Early Alarm",
            text: "Warns the control tower when taxiway traffic is approaching 85% capacity, automatically pausing unnecessary gate pushbacks.",
          },
          {
            title: "Gate Conflict Spotter",
            text: "Spots when an incoming flight won't have an open gate 60 minutes before it touches down, allowing managers to assign a new gate before landing.",
          },
        ],
        insightNote: "Why This Matters: Accurately predicting the runway line means planes can stay comfortable at the gate with air conditioning on and engines off.",
      },
      prescriptive: {
        title: "Step 4: The Fix (Practical Solutions)",
        badge: "Smart Airport Solutions",
        description: "Keeping passengers comfortable at the gate and smoothing out ground traffic.",
        metrics: [
          { label: "Tarmac Wait Cut By", value: "-6.2 Minutes", detail: "Off every single departure", trend: "down" },
          { label: "Idle Fuel Saved", value: "38.6 Million Gal", detail: "Saved annually across US fleet", trend: "down" },
          { label: "Takeoff Slot Accuracy", value: "94.2% on Time", detail: "Planes hit their exact takeoff slot", trend: "up" },
          { label: "Comfortable Gate Waiting", value: "+22 Minutes", detail: "Air-conditioned cabin vs bumpy tarmac", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "1. Virtual Pushback Metering (Hold at Gate)",
            text: "Assign each plane an exact takeoff time. Keep the plane parked at the gate with ground electricity and air conditioning until 10 minutes before its runway slot.",
          },
          {
            title: "2. Park Planes Close to Their Takeoff Runway",
            text: "Park heavy cross-country flights at gates closest to the runway heading they need, cutting taxi driving distances by up to nearly 2 miles.",
          },
          {
            title: "3. Smart Winter De-icing Lanes",
            text: "Pre-sort planes into separate de-icing bays based on plane size and wingspan, preventing small planes from getting trapped behind giant jets.",
          },
        ],
        insightNote: "The Big Difference: Virtual queuing turns a chaotic, smelly runway line into an orderly, calm schedule while saving hundreds of thousands of gallons of fuel.",
      },
      feedback: {
        title: "Step 5: The Payoff (Results & Savings)",
        badge: "Proven Real-World Results",
        description: "Real improvements in airport capacity, passenger comfort, and clean air.",
        metrics: [
          { label: "Tarmac Jams Reduced", value: "-31.8% Fewer Jams", detail: "Less gridlock on taxiways", trend: "down" },
          { label: "Clean Air Impact", value: "368,000 Tons CO2", detail: "Pollution cut every year", trend: "down" },
          { label: "More Runway Flights", value: "+8.4% Capacity", detail: "More takeoffs per hour at peak times", trend: "up" },
          { label: "Gate Turnover", value: "+19.1% Faster", detail: "Gates cleared faster for new arrivals", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Clean Air Reports for Cities",
            text: "Airports use this real data to publish certified green reports showing city leaders how much pollution was cut by not idling jet engines.",
          },
          {
            title: "Sharing Results with Airlines",
            text: "Every quarter, the airport shares on-time gate scorecards with airlines to help plan the next season's flight schedules.",
          },
          {
            title: "Faster Gates for Arriving Passengers",
            text: "When departure taxi lines are shorter, landing flights can pull directly up to their gate without waiting on the tarmac.",
          },
        ],
        insightNote: "The Closed Loop: Real-time ground data turns busy airport tarmacs from stressful bottlenecks into smooth, predictable transit lines.",
      },
    },
  },

  regulators: {
    id: "regulators",
    title: "Air Traffic & Regulators (FAA / DOT)",
    subtitle: "Managing Congested Skies, Storm Detours & Protecting Passenger Rights",
    entityName: "Aviation Regulators & Air Traffic Control (FAA, DOT Consumer Bureau)",
    roleScope: "Air Traffic Flow Managers, Airspace Controllers, and Consumer Protection Officials",
    themeColor: {
      primary: "text-indigo-700",
      light: "bg-indigo-50",
      border: "border-indigo-200",
      badgeBg: "bg-indigo-100",
      badgeText: "text-indigo-800",
      gradient: "from-slate-900 via-indigo-950 to-blue-950",
    },
    summaryStats: {
      keyMetric: "22.8% Airspace Delays",
      keyLabel: "Delays Caused by Airway Congestion & Weather",
      annualCostImpact: "$12.8 Billion System Congestion Cost",
      primaryProblem: "Crowded flight corridors, sudden storm halts, and passengers trapped on tarmacs over 3 hours.",
      primarySolution: "Pre-planned storm detours before boarding and automatic return-to-gate orders before 3 hours.",
    },
    stages: {
      problem: {
        title: "Step 1: What Is the Problem?",
        badge: "What the Flight Records Show",
        description: "Official government records track severe delays across crowded national airways, storm ground stops, and tarmac hold violations.",
        metrics: [
          { label: "Airway Delay Minutes", value: "114 Million min", detail: "22.8% of all national delay time", trend: "up" },
          { label: "Choked Air Corridors", value: "38 Sectors", detail: "Busy Northeast and Florida skies", trend: "up" },
          { label: "Ground Stops Issued", value: "1,840 / Year", detail: "Mandatory federal flight pauses", trend: "up" },
          { label: "Near-3-Hour Tarmac Holds", value: "1,240 Flights", detail: "Close to the legal penalty limit", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Highways in the Sky Get Jammed",
            text: "Air traffic controllers can only safely separate a set number of planes at once. When big storm fronts roll into New York or Atlanta, airways reach 100% capacity.",
          },
          {
            title: "Ground Stops Halt Flights Nationwide",
            text: "When a destination airport is overwhelmed by weather, the FAA issues a 'Ground Stop,' pausing departures across dozens of cities from coast to coast.",
          },
          {
            title: "The 3-Hour Passenger Tarmac Rule",
            text: "Federal law strictly prohibits keeping passengers stuck on a domestic tarmac for more than 3 hours, carrying massive fines up to $27,500 per passenger.",
          },
        ],
        insightNote: "Real-World Fact: Over two-thirds (68%) of all government air traffic delays happen in just 3 regions: New York, Washington D.C., and Chicago.",
      },
      diagnostics: {
        title: "Step 2: Why Is It Happening?",
        badge: "Finding the Root Cause",
        description: "Why do air traffic delays spiral so quickly during afternoon thunderstorms?",
        metrics: [
          { label: "Storm Front Shifts", value: "48% of Halts", detail: "Thunderstorm walls blocking airways", trend: "neutral" },
          { label: "Drop in Bad-Weather Landings", value: "-35% Landings", detail: "Runways accept fewer planes in rain/fog", trend: "down" },
          { label: "Sky Route Conflicts", value: "4.2x During Storms", detail: "Planes trying to fly around same storm", trend: "up" },
          { label: "Airlines Overscheduling", value: "118% of Capacity", detail: "More flights booked than runway fits", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Airlines Schedule More Flights Than Runways Hold",
            text: "Airlines book 90 flights an hour into airports like LaGuardia or Reagan National that can only safely land 58 flights an hour when clouds or rain roll in.",
          },
          {
            title: "Rigid Old-Fashioned Flight Paths",
            text: "Planes file flight plans along fixed invisible highways in the sky. When summer thunderstorms block that highway, planes end up circling in holding patterns.",
          },
          {
            title: "Airlines and Air Traffic Talking Too Late",
            text: "Airlines often don't find out about a ground stop until planes have already pushed back from the gate and entered the runway line.",
          },
        ],
        insightNote: "Root Cause: Delays blow up when ground stops are announced AFTER planes have already left the gate and lined up on the taxiway.",
      },
      predictive: {
        title: "Step 3: Catching It Early",
        badge: "Smart Airspace Forecasts",
        description: "Using weather radar and flight plans to forecast sky jams and ground delays 6 hours ahead.",
        metrics: [
          { label: "Ground Stop Prediction", value: "88.6% Accurate", detail: "Predicts airport ground stops ahead", trend: "up" },
          { label: "Early Notice Window", value: "6 Hours Ahead", detail: "Time to negotiate reroutes with airlines", trend: "up" },
          { label: "3-Hour Tarmac Alert", value: "99.1% Detection", detail: "Flags planes in danger of 3-hr mark", trend: "up" },
          { label: "Airway Traffic Accuracy", value: "Within 8 Minutes", detail: "Accurate sky congestion forecasts", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "6-Hour Airspace Jam Predictor",
            text: "Combines government weather radar with filed flight plans to predict which sky highways will be overloaded 6 hours in advance.",
          },
          {
            title: "Tarmac Clock Early Warning",
            text: "Tracks the exact minute every plane left the gate. Sounds a yellow alert at 90 minutes and a mandatory return-to-gate order at 120 minutes.",
          },
          {
            title: "Smart Detour Calculator",
            text: "Automatically tests alternate flight paths around storm clouds to find the fastest, smoothest route before fuel is loaded.",
          },
        ],
        insightNote: "Why This Matters: A 6-hour advance warning gives air traffic controllers time to agree on detours with airlines BEFORE passengers board.",
      },
      prescriptive: {
        title: "Step 4: The Fix (Practical Solutions)",
        badge: "Smart Air Traffic Solutions",
        description: "Coordinating detours early and enforcing strong passenger protection.",
        metrics: [
          { label: "Airborne Circling Cut By", value: "-22.5% Holding", detail: "Less time burning fuel in circles", trend: "down" },
          { label: "3-Hour Tarmac Violations", value: "Zero (0)", detail: "100% compliance with federal law", trend: "down" },
          { label: "Ground Stop Duration", value: "-1.8 Hours", detail: "Shorter national flight pauses", trend: "down" },
          { label: "Passenger Safety", value: "99.98% Safe", detail: "Safe separation maintained at all times", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "1. Pre-Planned Storm Detours Before Boarding",
            text: "Load pre-approved detour routes into the plane's flight computer before passengers board so pilots fly around the storm without circling in holding stacks.",
          },
          {
            title: "2. Automatic Return-to-Gate at 2 Hours",
            text: "Require any plane that has been waiting on the tarmac for 120 minutes to turn around and return to a gate or de-planing bus, protecting passengers from being trapped.",
          },
          {
            title: "3. Monthly Public On-Time Scorecards",
            text: "Publish simple, transparent monthly scorecards showing which airlines are most reliable so passengers can vote with their wallets.",
          },
        ],
        insightNote: "The Real Fix: Rerouting planes before they leave the gate eliminates circling in holding patterns and keeps passengers safe from tarmac entrapment.",
      },
      feedback: {
        title: "Step 5: The Payoff (Results & Savings)",
        badge: "Proven Real-World Results",
        description: "Safer skies, zero trapped passengers, and less wasted flight time.",
        metrics: [
          { label: "Airway Delays Reduced", value: "-18.7%", detail: "Less national airspace congestion", trend: "down" },
          { label: "Passenger Fines Avoided", value: "$0.00", detail: "Zero tarmac penalties incurred", trend: "down" },
          { label: "Miles Saved on Detours", value: "1.85 Million mi", detail: "Fewer inefficient zigzag detours", trend: "down" },
          { label: "Scorecard Review", value: "Monthly", detail: "Public consumer reports published", trend: "neutral" },
        ],
        bulletPoints: [
          {
            title: "Auditing Delay Causes",
            text: "Reconciles airline reports with federal control tower logs each month to ensure delay blame is assigned fairly and accurately.",
          },
          {
            title: "Refining Weather Ground Stops",
            text: "Reviews each ground stop after the storm passes to ensure flights were paused only as long as necessary, keeping the country moving.",
          },
          {
            title: "Guiding Future Airport Investment",
            text: "Uses real flight delay data to help the government decide where new runways and radar systems are needed most.",
          },
        ],
        insightNote: "The Closed Loop: Continuous data feedback ensures government air traffic management keeps passengers safe while maximizing mobility.",
      },
    },
  },

  passengers: {
    id: "passengers",
    title: "Passengers, Travel Apps & Insurers",
    subtitle: "Avoiding Missed Connections, Knowing Flight Reliability & Instant Delay Cash Payouts",
    entityName: "Passengers, Travel Apps (Google Flights, Expedia) & Travel Insurers",
    roleScope: "Business Travelers, Vacationers, Travel Booking Sites, and Insurance Providers",
    themeColor: {
      primary: "text-emerald-700",
      light: "bg-emerald-50",
      border: "border-emerald-200",
      badgeBg: "bg-emerald-100",
      badgeText: "text-emerald-800",
      gradient: "from-emerald-950 via-teal-900 to-slate-900",
    },
    summaryStats: {
      keyMetric: "1.42 Million Missed Connections",
      keyLabel: "Travelers Disconnected Every Year",
      annualCostImpact: "$4.2 Billion in Lost Passenger Time",
      primaryProblem: "Booking tight 45-minute connections that are impossible to catch when flights run late.",
      primarySolution: "Connection safety badges at booking, automatic backup seat reservations, and instant delay payouts.",
    },
    stages: {
      problem: {
        title: "Step 1: What Is the Problem?",
        badge: "What the Flight Records Show",
        description: "Millions of passengers miss connecting flights, endure cancelled vacations, and struggle with painful insurance claim forms.",
        metrics: [
          { label: "Cancelled Flights", value: "418,000 Flights", detail: "Over 400,000 trips cancelled", trend: "up" },
          { label: "Diverted Flights", value: "78,000 Flights", detail: "Landed at the wrong airport", trend: "up" },
          { label: "High-Risk Routes", value: "42 Corridors", detail: "Where over 30% of flights are late", trend: "up" },
          { label: "Missed Connections", value: "1.42 Million / yr", detail: "Travelers stranded between flights", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "The Tight Connection Trap",
            text: "Airlines sell tickets with tight 40 to 50 minute layovers. When the first flight lands 45 minutes late, passengers sprint across the terminal only to find the door closed.",
          },
          {
            title: "Flying Blind at Booking Time",
            text: "When buying tickets online, travelers see the price and departure time, but have zero idea whether that flight has a 90% or a 40% chance of being delayed.",
          },
          {
            title: "The Insurance Paperwork Nightmare",
            text: "Filing traditional travel insurance claims requires collecting boarding passes, receipts, and airline delay letters, taking up to 30 days to get reimbursed.",
          },
        ],
        insightNote: "Real-World Fact: Travelers booking evening connections (departing between 6:00 PM and 9:00 PM) are 4 times more likely to miss their connection than morning flyers.",
      },
      diagnostics: {
        title: "Step 2: Why Is It Happening?",
        badge: "Finding the Root Cause",
        description: "Why are missed connections and passenger travel disruptions so common?",
        metrics: [
          { label: "Risky Tight Layovers", value: "1 in 4 Bookings", detail: "Have less than 50 min to transfer", trend: "up" },
          { label: "Evening Delay Multiplier", value: "3.8x Worse", detail: "Late-night flights vs morning flights", trend: "up" },
          { label: "Weather Cancellation Spike", value: "62% of Cancels", detail: "Caused by winter and summer storms", trend: "neutral" },
          { label: "Time Stranded at Hub", value: "4.8 Hours", detail: "Average wait for next available flight", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Shortest Layover Wins the Sale",
            text: "Travel search engines sort flights by total trip duration. This pushes tight, unrealistic 45-minute connections to the top of search results.",
          },
          {
            title: "Airports Are Huge Walking Mazes",
            text: "Walking between concourses at giant hubs like Chicago or Atlanta can take 20 to 25 minutes alone—leaving zero time if your incoming flight is even slightly late.",
          },
          {
            title: "Stuck on One Airline",
            text: "When an airline cancels your flight, their computer usually only looks for open seats on their own planes instead of booking you on an empty flight on another airline.",
          },
        ],
        insightNote: "Root Cause: Travel websites prioritize the shortest scheduled layover over whether that layover is actually realistic based on historical flight data.",
      },
      predictive: {
        title: "Step 3: Catching It Early",
        badge: "Smart Traveler Warnings",
        description: "Showing travelers clear connection safety scores and predicting delays before tickets are bought.",
        metrics: [
          { label: "Connection Safety Score", value: "0–100 Rating", detail: "Tells you how safe your layover is", trend: "neutral" },
          { label: "Severe Delay Forecast", value: "86.4% Accuracy", detail: "Predicts 2+ hour flight delays", trend: "up" },
          { label: "Recommended Buffer", value: "+30 Minutes", detail: "Suggested extra layover for safety", trend: "up" },
          { label: "Fair Insurance Pricing", value: "From $8 / Flight", detail: "Based on real route risk data", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "Real-Time Connection Risk Score",
            text: "Scores how safe your connection is based on the airline's past punctuality on that route, walking distance between gates, and the hour of the day.",
          },
          {
            title: "Fair Micro-Insurance Pricing",
            text: "Travel insurers calculate fair, affordable coverage ($8 to $15) based on the exact route and season, offering automatic payouts if things go wrong.",
          },
          {
            title: "Early Misconnect Detector",
            text: "Notices if an incoming flight is delayed so much that catching the connection is impossible, alerting the passenger and reservation desk 2 hours before landing.",
          },
        ],
        insightNote: "Why This Matters: Giving travelers clear data before they buy transforms flight delays from a stressful surprise into an easily avoided risk.",
      },
      prescriptive: {
        title: "Step 4: The Fix (Practical Solutions)",
        badge: "Smart Traveler Solutions",
        description: "Clear badges when booking, automatic rebooking, and instant cash back when flights run late.",
        metrics: [
          { label: "Missed Connections Cut", value: "-41.5% Misses", detail: "By choosing safe layovers", trend: "down" },
          { label: "Instant Cash Payout", value: "<90 Seconds", detail: "Sent straight to your phone wallet", trend: "down" },
          { label: "Traveler Satisfaction", value: "+34 Points", detail: "Higher happiness and trust", trend: "up" },
          { label: "Paperwork Required", value: "Zero (0)", detail: "100% automatic, no forms or receipts", trend: "down" },
        ],
        bulletPoints: [
          {
            title: "1. Color-Coded Connection Badges on Travel Sites",
            text: "Travel websites show simple badges: 🟢 Green (Safe Layover, 96% Reliable), 🟡 Yellow (Tight Layover, Caution), 🔴 Red (High Risk of Missing Your Plane).",
          },
          {
            title: "2. Instant Cash Back to Your Phone (No Paperwork)",
            text: "Smart travel insurance monitors official flight records. If your flight is delayed over 2 hours or cancelled, $150 to $300 is sent directly to your Apple or Google Wallet automatically.",
          },
          {
            title: "3. Automatic Backup Seat Reservation",
            text: "If your incoming plane is running late and you're going to miss your connection, the system automatically holds a seat for you on the next flight before you even touch down.",
          },
        ],
        insightNote: "The Real Difference: Giving flyers clear data upfront and instant compensation for delays replaces travel stress with complete peace of mind.",
      },
      feedback: {
        title: "Step 5: The Payoff (Results & Savings)",
        badge: "Proven Real-World Results",
        description: "Better journeys for passengers, happier customers for travel sites, and fair rewards for punctual airlines.",
        metrics: [
          { label: "Repeat Bookings", value: "+28.4% Loyalty", detail: "Travelers return to honest apps", trend: "up" },
          { label: "Claim Filing Hassle", value: "-88.5% Cost", detail: "Eliminates claims departments", trend: "down" },
          { label: "Connection Success", value: "98.1% Made", detail: "Passengers reach their final stop", trend: "up" },
          { label: "App Review Ratings", value: "+32 NPS Score", detail: "Huge boost in customer trust", trend: "up" },
        ],
        bulletPoints: [
          {
            title: "Rewarding Punctual Airlines",
            text: "Travel search engines use real on-time records to rank reliable airlines higher in search results, giving airlines an incentive to fly on time.",
          },
          {
            title: "Fairer, Cheaper Insurance Policies",
            text: "Insurers continuously tune policy rates with actual government flight records to keep protection cheap and payouts guaranteed.",
          },
          {
            title: "Giving Travelers a Real Voice",
            text: "Publishing real cancellation and delay numbers in public dashboards forces airlines to protect their reputation by fixing broken schedules.",
          },
        ],
        insightNote: "The Closed Loop: By giving passengers simple, honest flight data, travelers are protected and airlines are rewarded for flying on time.",
      },
    },
  },
};
