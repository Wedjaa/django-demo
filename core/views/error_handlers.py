from django.shortcuts import render
from django.http import HttpResponseForbidden

def permission_denied_view(request, exception=None):
    """
    Custom 403 Forbidden view with cute cat theme.
    """
    return HttpResponseForbidden(
        render(request, '403.html', {
            'user': request.user,
        }).content
    )
