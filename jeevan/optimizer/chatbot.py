def generate_chatbot_response(query, knowledge_base, context):
    lowered = query.lower()
    if 'budget' in lowered:
        status = context.get('budget_status', 'normal')
        return f"Your current budget status is {status}. Keep monitoring your spend against threshold."
    if 'sustain' in lowered or 'carbon' in lowered:
        score = context.get('sustainability_score')
        if score is None:
            return knowledge_base.get('sustainability', 'Track carbon usage to compute sustainability score.')
        return f"Your latest sustainability score is {score}/100. Lower carbon usage can improve this score."
    if 'region' in lowered:
        recommended = context.get('recommended_region')
        if recommended:
            return f"The most cost-efficient region right now appears to be {recommended}."
        return knowledge_base.get('region', 'Use region advisor to compare cloud regions.')
    if 'recommend' in lowered or 'optimiz' in lowered:
        count = context.get('recommendation_count', 0)
        return f"You currently have {count} optimization recommendations available."
    return knowledge_base.get(
        'default',
        'I can help with budget, sustainability, region choices, and optimization recommendations.',
    )
