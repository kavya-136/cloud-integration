def simulate_cost(current_cost, current_cpu, current_memory, cpu, memory):
    if current_cost <= 0:
        return 0.0

    safe_cpu = max(current_cpu, 1.0)
    safe_memory = max(current_memory, 1.0)
    cpu_factor = cpu / safe_cpu
    memory_factor = memory / safe_memory
    weighted_factor = (0.6 * cpu_factor) + (0.4 * memory_factor)
    return round(max(current_cost * weighted_factor, 0.0), 2)
