from django.contrib import admin
from django.urls import path, include

from core.views.logout import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__reload__/', include('django_browser_reload.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include('dashboard.urls', namespace='dashboard')),
]

# Custom error handlers
handler403 = 'core.views.error_handlers.permission_denied_view'
