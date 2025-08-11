from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('administration/', views.admin_panel, name='admin'),
    
    # Trading URLs
    path('trades/', views.trades_list, name='trades'),
    path('trades/create/', views.trade_create, name='trade_create'),
    path('trades/<int:trade_id>/', views.trade_detail, name='trade_detail'),
    path('trades/<int:trade_id>/confirm/', views.trade_confirm, name='trade_confirm'),
    path('trades/<int:trade_id>/approve/', views.trade_approve, name='trade_approve'),
]
