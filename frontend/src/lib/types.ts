export interface Kpis {
  total_flights: number;
  eligible_arrivals: number;
  delayed_arrivals: number;
  ontime_early_arrivals: number;
  cancelled_flights: number;
  diverted_flights: number;
  arr_delay_rate: number;
  avg_arrival_delay_signed: number;
  avg_arrival_delay_positive: number;
  cancel_rate: number;
  divert_rate: number;
  total_delay_burden_minutes: number;
}

export interface MonthlyTrend {
  year: number;
  month: number;
  month_name: string;
  total_flights: number;
  eligible_arrivals: number;
  delayed_arrivals: number;
  delay_rate: number;
  avg_arrival_delay: number;
  cancel_rate: number;
  divert_rate: number;
}

export interface AirlinePerf {
  reporting_airline: string;
  total_flights: number;
  eligible_arrivals: number;
  delayed_arrivals: number;
  delay_rate: number;
  avg_arr_delay_signed: number;
  avg_arr_delay_pos: number;
  total_delay_minutes_positive: number;
  total_delay_minutes_signed?: number;
  cancel_rate: number;
  divert_rate: number;
}

export interface AirportDelay {
  origin_airport_code?: string;
  origin_city_name?: string;
  origin_state?: string;
  dest_airport_code?: string;
  dest_city_name?: string;
  dest_state?: string;
  eligible_departures?: number;
  delayed_departures?: number;
  dep_delay_rate?: number;
  avg_dep_delay?: number;
  eligible_arrivals?: number;
  delayed_arrivals?: number;
  arr_delay_rate?: number;
  avg_arr_delay?: number;
}

export interface RouteMetric {
  route_code: string;
  origin_code?: string;
  origin_airport_code?: string;
  dest_code?: string;
  destination_airport_code?: string;
  dest_airport_code?: string;
  flight_count?: number;
  total_flights?: number;
  eligible_arrivals?: number;
  delayed_flights?: number;
  delayed_arrivals?: number;
  delay_rate?: number;
  arr_delay_rate?: number;
  avg_arr_delay_pos?: number;
  avg_arr_delay?: number;
  avg_delay?: number;
  total_delay_burden_minutes?: number;
}

export interface DelayCause {
  Cause?: string;
  cause?: string;
  reporting_airline?: string;
  Minutes?: number;
  minutes?: number;
  "Share (%)"?: number;
  share?: number;
  total_delayed_flights?: number;
  carrier_delay_minutes?: number;
  weather_delay_minutes?: number;
  nas_delay_minutes?: number;
  security_delay_minutes?: number;
  late_aircraft_delay_minutes?: number;
}

export interface TemporalPattern {
  day_of_week?: number;
  day_name?: string;
  hour?: number;
  departure_hour?: number;
  flight_count?: number;
  total_flights?: number;
  eligible_arrivals?: number;
  delay_rate?: number;
  dep_delay_rate?: number;
  arr_delay_rate?: number;
  avg_delay?: number;
  avg_arrival_delay?: number;
  total_delay_minutes?: number;
}

export type TargetCustomerId = "airlines" | "airports" | "regulators" | "passengers";

export interface ClosedLoopStageData {
  title: string;
  badge: string;
  description: string;
  metrics: { label: string; value: string; detail?: string; trend?: "up" | "down" | "neutral" }[];
  bulletPoints: { title: string; text: string; iconType?: string }[];
  insightNote?: string;
}

export interface CustomerClosedLoopData {
  id: TargetCustomerId;
  title: string;
  subtitle: string;
  entityName: string;
  roleScope: string;
  themeColor: {
    primary: string;
    light: string;
    border: string;
    badgeBg: string;
    badgeText: string;
    gradient: string;
  };
  summaryStats: {
    keyMetric: string;
    keyLabel: string;
    annualCostImpact: string;
    primaryProblem: string;
    primarySolution: string;
  };
  stages: {
    problem: ClosedLoopStageData;
    diagnostics: ClosedLoopStageData;
    predictive: ClosedLoopStageData;
    prescriptive: ClosedLoopStageData;
    feedback: ClosedLoopStageData;
  };
}

export interface OlapFilterParams {
  years?: number[];
  airlines?: string[];
  origins?: string[];
  destinations?: string[];
}

export interface OlapFilterResult {
  filtered_flights?: number;
  total_flights?: number;
  eligible_arrivals?: number;
  delayed_arrivals?: number;
  delay_rate?: number;
  arr_delay_rate?: number;
  avg_arr_delay?: number;
  avg_delay?: number;
  cancel_rate?: number;
  divert_rate?: number;
  total_delay_burden_minutes?: number;
  records?: Array<Record<string, unknown>>;
  message?: string;
}
