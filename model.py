"""
=============================================================
  FRESH WATER RECOVERY & REUSE SYSTEM — Python Simulation
  Project: Integrated Water Management for Tirunelveli Region
=============================================================
"""

# ── Imports ─────────────────────────────────────────────────
import math
import random
import sys

# ── Configuration ───────────────────────────────────────────
CONFIG = {
    "catchment_area_m2"       : 500,      # Roof/surface catchment area
    "rainfall_mm_per_day"     : 80,       # Average daily rainfall
    "runoff_coefficient"      : 0.85,     # Fraction of rain captured
    "household_size"          : 5,        # Number of people
    "daily_water_use_L"       : 135,      # Litres per person per day (IS standard)
    "greywater_fraction"      : 0.65,     # Fraction of used water = greywater
    "greywater_recovery_rate" : 0.75,     # How much greywater we recover
    "treatment_efficiency"    : 0.92,     # RO+UV treatment efficiency
    "storage_capacity_L"      : 40000,    # Total tank capacity
    "cost_per_litre_INR"      : 0.09,     # Municipal water cost
    "simulation_days"         : 365,      # Days to simulate
}

# Tirunelveli monthly rainfall pattern (mm/day average)
MONTHLY_RAINFALL = {
    1: 1.2, 2: 0.8, 3: 1.0, 4: 2.1, 5: 3.5, 6: 4.2,
    7: 5.8, 8: 6.1, 9: 7.3, 10: 8.5, 11: 9.2, 12: 4.1
}

# ── Helper Functions ─────────────────────────────────────────

def get_monthly_rainfall(day_of_year: int, base: float) -> float:
    month = min(12, max(1, (day_of_year // 30) + 1))
    factor = MONTHLY_RAINFALL[month] / 5.0  # normalize around base
    noise = random.gauss(1.0, 0.15)
    return max(0, base * factor * noise)


def calculate_rainwater(rainfall_mm: float, area_m2: float, rc: float) -> float:
    """Litres of rainwater harvested"""
    return rainfall_mm * area_m2 * rc  # mm × m² = litres


def calculate_greywater(hh: int, daily_use_L: float, gw_frac: float, gw_rec: float) -> float:
    """Litres of greywater recovered"""
    greywater_generated = hh * daily_use_L * gw_frac
    return greywater_generated * gw_rec


def apply_treatment(raw_litres: float, efficiency: float) -> float:
    """Litres after treatment (loss from RO brine, evaporation etc.)"""
    return raw_litres * efficiency


def simulate(config: dict, verbose: bool = False) -> dict:
    random.seed(42)
    c = config

    # Accumulators
    total_rainwater      = 0.0
    total_greywater      = 0.0
    total_treated        = 0.0
    total_demand         = 0.0
    total_deficit        = 0.0
    total_overflow       = 0.0
    storage              = c["storage_capacity_L"] * 0.30   # start at 30%
    daily_log            = []

    for day in range(1, c["simulation_days"] + 1):
        rf      = get_monthly_rainfall(day, c["rainfall_mm_per_day"])
        rain_L  = calculate_rainwater(rf, c["catchment_area_m2"], c["runoff_coefficient"])
        grey_L  = calculate_greywater(c["household_size"], c["daily_water_use_L"],
                                      c["greywater_fraction"], c["greywater_recovery_rate"])
        raw_in  = rain_L + grey_L
        treated = apply_treatment(raw_in, c["treatment_efficiency"])
        demand  = c["household_size"] * c["daily_water_use_L"]

        # Storage dynamics
        storage += treated
        if storage > c["storage_capacity_L"]:
            total_overflow += storage - c["storage_capacity_L"]
            storage = c["storage_capacity_L"]

        supply  = min(storage, demand)
        deficit = max(0, demand - supply)
        storage -= supply

        total_rainwater += rain_L
        total_greywater += grey_L
        total_treated   += treated
        total_demand    += demand
        total_deficit   += deficit

        if verbose and day % 30 == 0:
            month_name = ["Jan","Feb","Mar","Apr","May","Jun",
                          "Jul","Aug","Sep","Oct","Nov","Dec"][(day-1)//30 % 12]
            print(f"  Day {day:>3} ({month_name}): Rain={rain_L:>7.0f}L  "
                  f"Grey={grey_L:>6.0f}L  Treated={treated:>7.0f}L  "
                  f"Storage={storage:>8.0f}L  Deficit={deficit:>6.0f}L")

        daily_log.append({
            "day": day, "rainfall_L": rain_L, "greywater_L": grey_L,
            "treated_L": treated, "storage_L": storage, "deficit_L": deficit
        })

    # Summary metrics
    total_supply         = total_treated
    supply_rate          = total_supply / total_demand * 100
    annual_cost_saved    = total_treated * c["cost_per_litre_INR"]
    co2_offset_kg        = total_treated * 0.001 * 0.5   # 0.5 kg CO2 per kL pumping energy
    avg_daily_recovery   = total_treated / c["simulation_days"]
    self_sufficiency_pct = min(100, supply_rate)

    return {
        "total_rainwater_L"    : round(total_rainwater, 0),
        "total_greywater_L"    : round(total_greywater, 0),
        "total_treated_L"      : round(total_treated, 0),
        "total_demand_L"       : round(total_demand, 0),
        "total_deficit_L"      : round(total_deficit, 0),
        "total_overflow_L"     : round(total_overflow, 0),
        "supply_rate_pct"      : round(supply_rate, 1),
        "annual_cost_saved_INR": round(annual_cost_saved, 2),
        "co2_offset_kg"        : round(co2_offset_kg, 1),
        "avg_daily_recovery_L" : round(avg_daily_recovery, 0),
        "self_sufficiency_pct" : round(self_sufficiency_pct, 1),
        "daily_log"            : daily_log,
    }


def water_quality_report() -> None:
    """Print a simulated water quality analysis."""
    params = [
        ("pH",             6.8,  8.5,  7.2,   ""),
        ("TDS (ppm)",      0,    500,  382,   ""),
        ("Turbidity (NTU)",0,    1,    0.31,  ""),
        ("Hardness (mg/L)",0,    300,  145,   ""),
        ("Chloride (mg/L)",0,    250,  88,    ""),
        ("Nitrate (mg/L)", 0,    45,   12.4,  ""),
        ("Coliform (MPN)", 0,    0,    0,     "Absent"),
        ("DO (mg/L)",      5,    8,    6.8,   ""),
    ]
    print("\n┌─────────────────────────────────────────────────────┐")
    print("│         WATER QUALITY ANALYSIS REPORT (IS 10500)   │")
    print("├───────────────────┬────────┬────────┬───────────────┤")
    print("│ Parameter         │ Limit  │ Result │ Status        │")
    print("├───────────────────┼────────┼────────┼───────────────┤")
    for name, lo, hi, val, note in params:
        result = note if note else f"{val}"
        within = (note == "Absent") or (lo <= val <= hi)
        status = "✅ PASS" if within else "❌ FAIL"
        limit = f"{hi}" if lo == 0 else f"{lo}–{hi}"
        print(f"│ {name:<17} │ {limit:<6} │ {result:<6} │ {status:<13} │")
    print("└───────────────────┴────────┴────────┴───────────────┘")


def print_summary(results: dict) -> None:
    kL = 1000
    print("\n" + "═"*60)
    print("   FRESH WATER RECOVERY & REUSE — ANNUAL SIMULATION")
    print("═"*60)
    print(f"\n  📥  Total Water Input:")
    print(f"       Rainwater Harvested  : {results['total_rainwater_L']/kL:>8.1f} kL")
    print(f"       Greywater Recovered  : {results['total_greywater_L']/kL:>8.1f} kL")
    print(f"       After Treatment      : {results['total_treated_L']/kL:>8.1f} kL")

    print(f"\n  📊  Demand & Supply:")
    print(f"       Total Demand         : {results['total_demand_L']/kL:>8.1f} kL")
    print(f"       Supply Met           : {results['supply_rate_pct']:>7.1f} %")
    print(f"       Self-Sufficiency     : {results['self_sufficiency_pct']:>7.1f} %")
    print(f"       Remaining Deficit    : {results['total_deficit_L']/kL:>8.1f} kL")

    print(f"\n  💰  Economic & Environmental:")
    print(f"       Annual Cost Saved    : ₹{results['annual_cost_saved_INR']:>9,.2f}")
    print(f"       CO₂ Offset           : {results['co2_offset_kg']:>7.1f} kg/year")
    print(f"       Avg Daily Recovery   : {results['avg_daily_recovery_L']:>8.0f} L/day")

    print(f"\n  ♻️  Reuse Breakdown (Estimated):")
    t = results['total_treated_L']
    print(f"       Irrigation           : {t*0.38/kL:>8.1f} kL  (38%)")
    print(f"       Toilet Flushing      : {t*0.22/kL:>8.1f} kL  (22%)")
    print(f"       Drinking/Cooking     : {t*0.18/kL:>8.1f} kL  (18%)")
    print(f"       Industrial Use       : {t*0.12/kL:>8.1f} kL  (12%)")
    print(f"       Laundry              : {t*0.10/kL:>8.1f} kL  (10%)")

    print("\n" + "═"*60)


def treatment_stages() -> None:
    print("\n┌─────────────────────────────────────────────────────┐")
    print("│           TREATMENT PROCESS EFFICIENCY              │")
    print("├──────────────────────┬────────────┬─────────────────┤")
    print("│ Stage                │ Flow (L/h) │ Efficiency      │")
    print("├──────────────────────┼────────────┼─────────────────┤")
    stages = [
        ("1. Screen/Mesh Filter", 1000, "Removes debris 100%"),
        ("2. Sediment Filter",     950, "95% particulate removal"),
        ("3. Activated Carbon",    920, "88% organic removal"),
        ("4. Reverse Osmosis",     830, "92% TDS removal"),
        ("5. UV Disinfection",     820, "99.9% pathogen kill"),
        ("6. pH Correction",       820, "Adjusts to 7.0–7.5"),
        ("7. Distribution",        800, "Output to storage"),
    ]
    for name, flow, eff in stages:
        print(f"│ {name:<20} │ {flow:<10} │ {eff:<15} │")
    print("└──────────────────────┴────────────┴─────────────────┘")


def print_monthly_breakdown(daily_log: list) -> None:
    months = ["Jan","Feb","Mar","Apr","May","Jun",
              "Jul","Aug","Sep","Oct","Nov","Dec"]
    print("\n┌──────────────────────────────────────────────────────────────┐")
    print("│                  MONTHLY RECOVERY REPORT                    │")
    print("├─────────┬─────────────┬─────────────┬──────────┬────────────┤")
    print("│ Month   │ Rainwater L │ Greywater L │ Total kL │ Cost Saved │")
    print("├─────────┼─────────────┼─────────────┼──────────┼────────────┤")
    for m in range(12):
        days_in_month = [d for d in daily_log if m*30 < d["day"] <= (m+1)*30]
        if not days_in_month:
            continue
        rain = sum(d["rainfall_L"] for d in days_in_month)
        grey = sum(d["greywater_L"] for d in days_in_month)
        total = sum(d["treated_L"] for d in days_in_month)
        cost = total * 0.09
        print(f"│ {months[m]:<7} │ {rain:>11,.0f} │ {grey:>11,.0f} │ {total/1000:>8.1f} │ ₹{cost:>9,.0f} │")
    print("└─────────┴─────────────┴─────────────┴──────────┴────────────┘")


# ── Main ─────────────────────────────────────────────────────

def main():
    print("\n" + "╔"+"═"*58+"╗")
    print("║  💧 FRESH WATER RECOVERY & REUSE SYSTEM SIMULATION  ║")
    print("║     Project for Tirunelveli, Tamil Nadu, India       ║")
    print("╚"+"═"*58+"╝")

    print("\n🔧 Configuration:")
    for k, v in CONFIG.items():
        print(f"   {k:<30}: {v}")

    print("\n⏳ Running 365-day simulation...")
    print("   (Monthly snapshots below)\n")
    results = simulate(CONFIG, verbose=True)

    print_summary(results)
    treatment_stages()
    water_quality_report()
    print_monthly_breakdown(results["daily_log"])

    print("\n✅ Simulation completed successfully!")
    print("   Open freshwater_recovery_project.html for the interactive dashboard.\n")
    return results


if __name__ == "__main__":
    main()