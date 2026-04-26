def generate_rightsizing_recommendations(cpu, memory, current_cost):
    recommendations = []

    if cpu >= 80:
        recommendations.append(
            {
                'type': 'cpu_scale_up',
                'description': 'CPU usage is high. Scale up or move to a larger instance class.',
                'potential_savings': 0.0,
            }
        )
    elif cpu <= 30:
        recommendations.append(
            {
                'type': 'cpu_rightsize',
                'description': 'CPU usage is low. Downsize the instance to reduce waste.',
                'potential_savings': round(current_cost * 0.15, 2),
            }
        )

    if memory >= 80:
        recommendations.append(
            {
                'type': 'memory_scale_up',
                'description': 'Memory pressure is high. Consider increasing memory capacity.',
                'potential_savings': 0.0,
            }
        )
    elif memory <= 30:
        recommendations.append(
            {
                'type': 'memory_rightsize',
                'description': 'Memory usage is low. Reduce allocated memory to save cost.',
                'potential_savings': round(current_cost * 0.12, 2),
            }
        )

    if not recommendations:
        recommendations.append(
            {
                'type': 'monitoring',
                'description': 'Resource usage looks healthy. Continue monitoring for drift.',
                'potential_savings': 0.0,
            }
        )

    return recommendations
