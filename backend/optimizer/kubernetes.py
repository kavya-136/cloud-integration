def simulate_kubernetes_cost(cpu, memory, replicas, hours, region_multiplier):
    total_cpu = max(cpu, 0.0) * max(replicas, 0)
    total_memory = max(memory, 0.0) * max(replicas, 0)
    base_hourly = (total_cpu * 0.04) + (total_memory * 0.008)
    total_cost = base_hourly * max(hours, 0.0) * region_multiplier
    return round(total_cost, 4), total_cpu, total_memory
