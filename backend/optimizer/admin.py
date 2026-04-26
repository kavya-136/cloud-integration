from django.contrib import admin

from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('resource_name', 'current_cost', 'optimized_cost', 'savings_percent', 'created_at')
