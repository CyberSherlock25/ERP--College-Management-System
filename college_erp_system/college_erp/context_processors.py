"""
Context processors to make certain data available to all templates
"""
from academics.models import Department

def global_context(request):
    """
    Add global context data available to all templates
    """
    context = {
        'all_departments': Department.objects.all().order_by('name'),
    }
    return context
