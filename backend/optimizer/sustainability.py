def calculate_sustainability_score(avg_carbon_grams, threshold=500.0):
    if threshold <= 0:
        return 100.0
    score = 100.0 - ((avg_carbon_grams / threshold) * 100.0)
    return round(min(max(score, 0.0), 100.0), 2)
