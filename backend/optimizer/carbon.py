def calculate_carbon_emission(cpu, memory, hours, cpu_factor, memory_factor, region_factor):
    return round((cpu * cpu_factor + memory * memory_factor) * hours * region_factor, 4)
