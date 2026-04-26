def estimate_region_cost(cpu, memory, hours, multiplier):
    base_hourly = (cpu * 0.045) + (memory * 0.01)
    return round(base_hourly * hours * multiplier, 4)


def recommend_region(costs_by_region, current_region):
    if not costs_by_region:
        return current_region, 0.0, 0.0
    recommended = min(costs_by_region, key=costs_by_region.get)
    current_cost = costs_by_region.get(current_region, costs_by_region[recommended])
    recommended_cost = costs_by_region[recommended]
    difference = round(current_cost - recommended_cost, 4)
    if current_cost <= 0:
        savings_percent = 0.0
    else:
        savings_percent = round((difference / current_cost * 100.0), 2)
    return recommended, difference, max(savings_percent, 0.0)
