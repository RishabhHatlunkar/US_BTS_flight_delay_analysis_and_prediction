"""
OLAP Analytics Engine
Calculates dimensional aggregations, OLAP cubes, KPI metrics,
and answers business questions Q1 to Q31.
"""

import pandas as pd
import numpy as np


class OLAPAnalytics:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._preprocess()

    def _preprocess(self):
        # Eligible arrivals: not cancelled, not diverted, with valid arrival delay
        self.df["is_eligible_arr"] = (self.df["cancelled"] == 0) & (self.df["arr_delay"].notna())
        self.df["is_eligible_dep"] = self.df["dep_delay"].notna()
        # Positive-only arrival delay minutes
        self.df["pos_arr_delay_minutes"] = np.maximum(0, self.df["arr_delay"].fillna(0))

    def apply_filters(
        self,
        years=None,
        quarters=None,
        months=None,
        airlines=None,
        origins=None,
        destinations=None,
        routes=None,
        weekdays=None,
        departure_hours=None,
    ) -> "OLAPAnalytics":
        filtered = self.df
        if years:
            filtered = filtered[filtered["year"].isin(years)]
        if quarters:
            filtered = filtered[filtered["quarter"].isin(quarters)]
        if months:
            filtered = filtered[filtered["month"].isin(months)]
        if airlines:
            filtered = filtered[filtered["reporting_airline"].isin(airlines)]
        if origins:
            filtered = filtered[filtered["origin_airport_code"].isin(origins)]
        if destinations:
            filtered = filtered[filtered["dest_airport_code"].isin(destinations)]
        if routes:
            filtered = filtered[filtered["route_code"].isin(routes)]
        if weekdays:
            filtered = filtered[filtered["day_of_week"].isin(weekdays)]
        if departure_hours:
            filtered = filtered[filtered["departure_hour"].isin(departure_hours)]

        return OLAPAnalytics(filtered)

    # -------------------------------------------------------------------------
    # Page 1 — Executive Overview (Q1–Q4)
    # -------------------------------------------------------------------------
    def get_kpis(self) -> dict:
        total_flights = len(self.df)
        eligible_arr = self.df["is_eligible_arr"].sum()
        delayed_arr = ((self.df["is_eligible_arr"]) & (self.df["arr_del15"] == 1)).sum()
        arr_delay_rate = (delayed_arr / eligible_arr * 100) if eligible_arr > 0 else 0.0

        cancelled = self.df["cancelled"].sum()
        cancel_rate = (cancelled / total_flights * 100) if total_flights > 0 else 0.0

        diverted = self.df["diverted"].sum()
        divert_rate = (diverted / total_flights * 100) if total_flights > 0 else 0.0

        avg_arr_delay = self.df.loc[self.df["is_eligible_arr"], "arr_delay"].mean() if eligible_arr > 0 else 0.0
        avg_pos_delay = self.df.loc[self.df["is_eligible_arr"] & (self.df["arr_delay"] > 0), "arr_delay"].mean() if eligible_arr > 0 else 0.0
        total_delay_minutes = self.df.loc[self.df["is_eligible_arr"], "pos_arr_delay_minutes"].sum()

        return {
            "total_flights": int(total_flights),
            "eligible_arrivals": int(eligible_arr),
            "delayed_arrivals": int(delayed_arr),
            "arr_delay_rate": round(float(arr_delay_rate), 2),
            "cancelled_flights": int(cancelled),
            "cancel_rate": round(float(cancel_rate), 2),
            "diverted_flights": int(diverted),
            "divert_rate": round(float(divert_rate), 2),
            "avg_arrival_delay_signed": round(float(avg_arr_delay), 2),
            "avg_arrival_delay_positive": round(float(avg_pos_delay), 2),
            "total_delay_burden_minutes": int(total_delay_minutes),
        }

    def q2_delays_over_time(self) -> pd.DataFrame:
        """Monthly trend for delay rate, avg arrival delay, cancellation rate, diversion rate."""
        grouped = self.df.groupby(["year", "month", "month_name"], as_index=False).apply(
            lambda g: pd.Series({
                "total_flights": len(g),
                "eligible_arrivals": g["is_eligible_arr"].sum(),
                "delayed_arrivals": ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum(),
                "delay_rate": (
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100
                    if g["is_eligible_arr"].sum() > 0 else 0
                ),
                "avg_arrival_delay": g.loc[g["is_eligible_arr"], "arr_delay"].mean(),
                "cancel_rate": g["cancelled"].sum() / len(g) * 100 if len(g) > 0 else 0,
                "divert_rate": g["diverted"].sum() / len(g) * 100 if len(g) > 0 else 0,
            }),
            include_groups=False
        ).sort_values(["year", "month"])
        return grouped

    def q3_flight_outcomes(self) -> pd.DataFrame:
        """Flight-outcome breakdown: On-Time / Early, Delayed (15+ min), Cancelled, Diverted."""
        total = len(self.df)
        if total == 0:
            return pd.DataFrame()

        cancelled = self.df["cancelled"].sum()
        diverted = self.df["diverted"].sum()
        delayed_15 = ((self.df["is_eligible_arr"]) & (self.df["arr_del15"] == 1)).sum()
        ontime_early = ((self.df["is_eligible_arr"]) & (self.df["arr_del15"] == 0)).sum()

        data = [
            {"Outcome": "On-Time / Early (<15 min delay)", "Count": ontime_early, "Percentage": round(ontime_early / total * 100, 2)},
            {"Outcome": "Delayed (>=15 min delay)", "Count": delayed_15, "Percentage": round(delayed_15 / total * 100, 2)},
            {"Outcome": "Cancelled", "Count": cancelled, "Percentage": round(cancelled / total * 100, 2)},
            {"Outcome": "Diverted", "Count": diverted, "Percentage": round(diverted / total * 100, 2)},
        ]
        return pd.DataFrame(data)

    def q4_top_delay_burden(self, entity="reporting_airline", top_n=10) -> pd.DataFrame:
        """Ranks airlines or routes by total delay minutes, volume, and delay rate."""
        grouped = self.df.groupby(entity).apply(
            lambda g: pd.Series({
                "Total Flights": len(g),
                "Eligible Arrivals": g["is_eligible_arr"].sum(),
                "Total Delay Minutes (Positive)": int(g.loc[g["is_eligible_arr"], "pos_arr_delay_minutes"].sum()),
                "Total Delay Minutes (Signed)": int(g.loc[g["is_eligible_arr"], "arr_delay"].sum()),
                "Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0,
                "Avg Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
            }),
            include_groups=False
        ).reset_index()
        return grouped.sort_values("Total Delay Minutes (Positive)", ascending=False).head(top_n)

    # -------------------------------------------------------------------------
    # Page 2 — Airline Performance (Q5–Q9)
    # -------------------------------------------------------------------------
    def q5_airline_delay_rates(self) -> pd.DataFrame:
        """Compares delay percentages and eligible flight counts by airline."""
        res = self.df.groupby("reporting_airline").apply(
            lambda g: pd.Series({
                "Eligible Flights": int(g["is_eligible_arr"].sum()),
                "Delayed Flights": int(((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum()),
                "Arrival Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
            }),
            include_groups=False
        ).reset_index().sort_values("Arrival Delay Rate (%)", ascending=False)
        return res

    def q6_q7_airline_delay_metrics(self) -> pd.DataFrame:
        """Airline average delay (signed vs positive-only) and total delay burden."""
        res = self.df.groupby("reporting_airline").apply(
            lambda g: pd.Series({
                "Eligible Flights": int(g["is_eligible_arr"].sum()),
                "Avg Arrival Delay Signed (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2),
                "Avg Arrival Delay Positive Only (min)": round(g.loc[g["is_eligible_arr"] & (g["arr_delay"] > 0), "arr_delay"].mean(), 2),
                "Total Delay Minutes (Positive)": int(g.loc[g["is_eligible_arr"], "pos_arr_delay_minutes"].sum()),
                "Total Delay Minutes (Signed)": int(g.loc[g["is_eligible_arr"], "arr_delay"].sum()),
            }),
            include_groups=False
        ).reset_index().sort_values("Total Delay Minutes (Positive)", ascending=False)
        return res

    def q8_airline_cancellation_diversion(self) -> pd.DataFrame:
        """Airlines ranked by cancellation and diversion rates (denominator: total flights)."""
        res = self.df.groupby("reporting_airline").apply(
            lambda g: pd.Series({
                "Total Scheduled Flights": len(g),
                "Cancelled Flights": int(g["cancelled"].sum()),
                "Cancellation Rate (%)": round(g["cancelled"].sum() / len(g) * 100, 2),
                "Diverted Flights": int(g["diverted"].sum()),
                "Diversion Rate (%)": round(g["diverted"].sum() / len(g) * 100, 2),
            }),
            include_groups=False
        ).reset_index().sort_values("Cancellation Rate (%)", ascending=False)
        return res

    def q9_airline_drilldown(self, airline: str, dimension="month_name") -> pd.DataFrame:
        """Drill down into an airline by month, weekday, or scheduled departure hour."""
        sub = self.df[self.df["reporting_airline"] == airline]
        res = sub.groupby(dimension).apply(
            lambda g: pd.Series({
                "Eligible Flights": int(g["is_eligible_arr"].sum()),
                "Delayed Flights": int(((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum()),
                "Arrival Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
            }),
            include_groups=False
        ).reset_index()
        return res

    # -------------------------------------------------------------------------
    # Page 3 — Airport & Route Analysis (Q10–Q14)
    # -------------------------------------------------------------------------
    def q10_origin_departure_delays(self, min_flights=20, top_n=15) -> pd.DataFrame:
        """Origin airports with highest departure delay rates (dep_del15 / eligible_dep)."""
        res = self.df.groupby("origin_airport_code").apply(
            lambda g: pd.Series({
                "Eligible Departures": int(g["is_eligible_dep"].sum()),
                "Delayed Departures (>=15m)": int(((g["is_eligible_dep"]) & (g["dep_del15"] == 1)).sum()),
                "Departure Delay Rate (%)": round(
                    ((g["is_eligible_dep"]) & (g["dep_del15"] == 1)).sum() / g["is_eligible_dep"].sum() * 100, 2
                ) if g["is_eligible_dep"].sum() > 0 else 0.0,
                "Avg Dep Delay (min)": round(g.loc[g["is_eligible_dep"], "dep_delay"].mean(), 2),
            }),
            include_groups=False
        ).reset_index()
        res = res[res["Eligible Departures"] >= min_flights]
        return res.sort_values("Departure Delay Rate (%)", ascending=False).head(top_n)

    def q11_dest_arrival_delays(self, min_flights=20, top_n=15) -> pd.DataFrame:
        """Destination airports with highest arrival delay rates (arr_del15 / eligible_arr)."""
        res = self.df.groupby("dest_airport_code").apply(
            lambda g: pd.Series({
                "Eligible Arrivals": int(g["is_eligible_arr"].sum()),
                "Delayed Arrivals (>=15m)": int(((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum()),
                "Arrival Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arr Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2),
            }),
            include_groups=False
        ).reset_index()
        res = res[res["Eligible Arrivals"] >= min_flights]
        return res.sort_values("Arrival Delay Rate (%)", ascending=False).head(top_n)

    def q12_q13_route_analysis(self, min_flights=15, top_n=15) -> pd.DataFrame:
        """Routes ranked by arrival delay rate, average delay, and total delay minutes."""
        res = self.df.groupby("route_code").apply(
            lambda g: pd.Series({
                "Flight Volume": len(g),
                "Eligible Arrivals": int(g["is_eligible_arr"].sum()),
                "Arrival Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
                "Total Delay Burden (min)": int(g.loc[g["is_eligible_arr"], "pos_arr_delay_minutes"].sum()),
            }),
            include_groups=False
        ).reset_index()
        res = res[res["Flight Volume"] >= min_flights]
        return res

    def q14_route_by_airline(self, route: str) -> pd.DataFrame:
        """Comparison of different airlines operating the same route."""
        sub = self.df[self.df["route_code"] == route]
        res = sub.groupby("reporting_airline").apply(
            lambda g: pd.Series({
                "Flights": len(g),
                "Eligible Arrivals": int(g["is_eligible_arr"].sum()),
                "Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
                "Cancel Rate (%)": round(g["cancelled"].sum() / len(g) * 100, 2),
            }),
            include_groups=False
        ).reset_index().sort_values("Delay Rate (%)", ascending=False)
        return res

    # -------------------------------------------------------------------------
    # Page 4 — Time and Operational Patterns (Q15–Q19)
    # -------------------------------------------------------------------------
    def q15_seasonal_patterns(self) -> pd.DataFrame:
        """Arrival delay rates by Month and Quarter."""
        res = self.df.groupby(["quarter", "month", "month_name"]).apply(
            lambda g: pd.Series({
                "Eligible Flights": int(g["is_eligible_arr"].sum()),
                "Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
            }),
            include_groups=False
        ).reset_index().sort_values(["quarter", "month"])
        return res

    def q16_day_of_week_patterns(self) -> pd.DataFrame:
        """Performance comparison across Monday through Sunday."""
        res = self.df.groupby(["day_of_week", "day_name"]).apply(
            lambda g: pd.Series({
                "Eligible Flights": int(g["is_eligible_arr"].sum()),
                "Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
                "Total Delay Minutes": int(g.loc[g["is_eligible_arr"], "pos_arr_delay_minutes"].sum()),
            }),
            include_groups=False
        ).reset_index().sort_values("day_of_week")
        return res

    def q17_hourly_patterns(self) -> pd.DataFrame:
        """Hourly scheduled departure block analysis."""
        res = self.df.groupby(["departure_hour", "dep_time_blk"]).apply(
            lambda g: pd.Series({
                "Eligible Departures": int(g["is_eligible_dep"].sum()),
                "Departure Delay Rate (%)": round(
                    ((g["is_eligible_dep"]) & (g["dep_del15"] == 1)).sum() / g["is_eligible_dep"].sum() * 100, 2
                ) if g["is_eligible_dep"].sum() > 0 else 0.0,
                "Arrival Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Departure Delay (min)": round(g.loc[g["is_eligible_dep"], "dep_delay"].mean(), 2),
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2),
            }),
            include_groups=False
        ).reset_index().sort_values("departure_hour")
        return res

    def q18_delay_association(self, sample_n=1000) -> pd.DataFrame:
        """Departure vs Arrival Delay scatter sample and correlation."""
        valid = self.df[self.df["is_eligible_arr"] & self.df["is_eligible_dep"] & (self.df["dep_delay"] > -30) & (self.df["arr_delay"] > -40)]
        sample = valid.sample(min(sample_n, len(valid)), random_state=42) if len(valid) > 0 else valid
        corr = valid["dep_delay"].corr(valid["arr_delay"]) if len(valid) > 1 else 0.0
        return sample[["dep_delay", "arr_delay", "reporting_airline", "route_code"]], round(corr, 3)

    def q19_disruptions_by_time(self, dimension="month_name") -> pd.DataFrame:
        """Cancellation and diversion rates across time periods."""
        res = self.df.groupby(dimension).apply(
            lambda g: pd.Series({
                "Total Flights": len(g),
                "Cancellation Rate (%)": round(g["cancelled"].sum() / len(g) * 100, 2),
                "Diversion Rate (%)": round(g["diverted"].sum() / len(g) * 100, 2),
            }),
            include_groups=False
        ).reset_index()
        return res

    # -------------------------------------------------------------------------
    # Page 5 — Delay Causes & Disruptions (Q20–Q23)
    # -------------------------------------------------------------------------
    def q20_q23_delay_causes_breakdown(self) -> tuple[pd.DataFrame, float]:
        """Breakdown of recorded delay causes and share of late-arriving aircraft."""
        delayed = self.df[self.df["arr_del15"] == 1]
        carrier = delayed["carrier_delay"].sum()
        weather = delayed["weather_delay"].sum()
        nas = delayed["nas_delay"].sum()
        security = delayed["security_delay"].sum()
        late_aircraft = delayed["late_aircraft_delay"].sum()

        total_cause_minutes = carrier + weather + nas + security + late_aircraft
        if total_cause_minutes == 0:
            total_cause_minutes = 1.0

        data = [
            {"Cause": "Carrier Delay", "Minutes": int(carrier), "Share (%)": round(carrier / total_cause_minutes * 100, 2)},
            {"Cause": "Late Aircraft Delay", "Minutes": int(late_aircraft), "Share (%)": round(late_aircraft / total_cause_minutes * 100, 2)},
            {"Cause": "National Airspace System (NAS)", "Minutes": int(nas), "Share (%)": round(nas / total_cause_minutes * 100, 2)},
            {"Cause": "Weather Delay", "Minutes": int(weather), "Share (%)": round(weather / total_cause_minutes * 100, 2)},
            {"Cause": "Security Delay", "Minutes": int(security), "Share (%)": round(security / total_cause_minutes * 100, 2)},
        ]
        df_causes = pd.DataFrame(data).sort_values("Minutes", ascending=False)
        late_aircraft_share = round(late_aircraft / total_cause_minutes * 100, 2)
        return df_causes, late_aircraft_share

    def q21_causes_over_time(self) -> pd.DataFrame:
        """Delay cause distributions over months."""
        delayed = self.df[self.df["arr_del15"] == 1]
        res = delayed.groupby(["month", "month_name"]).agg({
            "carrier_delay": "sum",
            "late_aircraft_delay": "sum",
            "nas_delay": "sum",
            "weather_delay": "sum",
            "security_delay": "sum",
        }).reset_index().sort_values("month")
        return res

    def q22_airline_cause_totals(self) -> pd.DataFrame:
        """Airlines compared across each recorded delay cause."""
        delayed = self.df[self.df["arr_del15"] == 1]
        res = delayed.groupby("reporting_airline").agg({
            "carrier_delay": "sum",
            "late_aircraft_delay": "sum",
            "nas_delay": "sum",
            "weather_delay": "sum",
            "security_delay": "sum",
        }).reset_index()
        return res

    # -------------------------------------------------------------------------
    # Page 6 — Historical Delay Risk (Q24–Q27)
    # -------------------------------------------------------------------------
    def q24_q27_airline_route_risk(self, min_flights=25, top_n=20) -> pd.DataFrame:
        """Estimates historical delay risk for airline-route pairs with sample size & confidence."""
        res = self.df.groupby(["reporting_airline", "route_code"]).apply(
            lambda g: pd.Series({
                "Sample Size (Eligible Flights)": int(g["is_eligible_arr"].sum()),
                "Historical Delay Probability (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
            }),
            include_groups=False
        ).reset_index()

        res = res[res["Sample Size (Eligible Flights)"] >= min_flights]

        def get_confidence(n):
            if n >= 100:
                return "High Confidence (N >= 100)"
            elif n >= 50:
                return "Moderate Confidence (50-99)"
            return "Low Confidence (<50)"

        res["Confidence Level"] = res["Sample Size (Eligible Flights)"].apply(get_confidence)
        return res.sort_values("Historical Delay Probability (%)", ascending=False).head(top_n)

    def q26_multi_factor_risk(self, airline=None, route=None, weekday=None, hour=None) -> dict:
        """Evaluates historical risk for specific attribute combination with sample size."""
        sub = self.df
        if airline:
            sub = sub[sub["reporting_airline"] == airline]
        if route:
            sub = sub[sub["route_code"] == route]
        if weekday:
            sub = sub[sub["day_of_week"] == weekday]
        if hour is not None:
            sub = sub[sub["departure_hour"] == hour]

        n = sub["is_eligible_arr"].sum()
        if n == 0:
            return {"sample_size": 0, "delay_probability": 0.0, "avg_delay": 0.0, "confidence": "Insufficient Data"}

        delays = ((sub["is_eligible_arr"]) & (sub["arr_del15"] == 1)).sum()
        prob = round(delays / n * 100, 2)
        avg_d = round(sub.loc[sub["is_eligible_arr"], "arr_delay"].mean(), 2)
        
        conf = "High Confidence" if n >= 50 else ("Moderate Confidence" if n >= 20 else "Low Sample (Caution)")
        return {
            "sample_size": int(n),
            "delay_probability": float(prob),
            "avg_delay": float(avg_d),
            "confidence": conf
        }

    # -------------------------------------------------------------------------
    # Page 7 — OLAP Explorer (Q28–Q31)
    # -------------------------------------------------------------------------
    def olap_rollup_drilldown(self, level="month") -> pd.DataFrame:
        """Demonstrates Roll-up and Drill-down: Year -> Quarter -> Month -> Day."""
        group_cols = {
            "year": ["year"],
            "quarter": ["year", "quarter"],
            "month": ["year", "quarter", "month", "month_name"],
            "day": ["year", "quarter", "month", "day_of_month", "day_name"],
        }.get(level, ["month_name"])

        res = self.df.groupby(group_cols).apply(
            lambda g: pd.Series({
                "Total Flights": len(g),
                "Eligible Arrivals": int(g["is_eligible_arr"].sum()),
                "Delay Rate (%)": round(
                    ((g["is_eligible_arr"]) & (g["arr_del15"] == 1)).sum() / g["is_eligible_arr"].sum() * 100, 2
                ) if g["is_eligible_arr"].sum() > 0 else 0.0,
                "Avg Arrival Delay (min)": round(g.loc[g["is_eligible_arr"], "arr_delay"].mean(), 2) if g["is_eligible_arr"].sum() > 0 else 0,
                "Total Delay Minutes": int(g.loc[g["is_eligible_arr"], "pos_arr_delay_minutes"].sum()),
            }),
            include_groups=False
        ).reset_index()
        return res

    def olap_pivot_table(self, row_dim="reporting_airline", col_dim="month_name") -> pd.DataFrame:
        """Demonstrates Pivot: 2D matrix comparing Arrival Delay Rate %."""
        pivot = self.df.pivot_table(
            index=row_dim,
            columns=col_dim,
            values="arr_del15",
            aggfunc=lambda x: round(np.nanmean(x) * 100, 2)
        ).fillna(0.0)
        return pivot

    def olap_drillthrough(self, airline=None, route=None, limit=50) -> pd.DataFrame:
        """Demonstrates Drill-through: Inspects underlying granular flight records."""
        sub = self.df
        if airline:
            sub = sub[sub["reporting_airline"] == airline]
        if route:
            sub = sub[sub["route_code"] == route]

        cols = [
            "flight_date", "reporting_airline", "flight_number", "tail_number",
            "origin_airport_code", "dest_airport_code", "crs_dep_time", "dep_time",
            "dep_delay", "crs_arr_time", "arr_time", "arr_delay", "arr_del15",
            "cancelled", "diverted", "carrier_delay", "weather_delay", "nas_delay", "late_aircraft_delay"
        ]
        available_cols = [c for c in cols if c in sub.columns]
        return sub[available_cols].head(limit)
