from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model

from dashboard.models.djangouser import DjangoUser

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    STATUSES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Basic trade information
    symbol = models.CharField(max_length=10, help_text="Trading symbol (e.g., AAPL, MSFT)")
    trade_type = models.CharField(max_length=4, choices=TRADE_TYPES)
    quantity = models.PositiveIntegerField(help_text="Number of shares")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per share")
    
    # Status and workflow
    status = models.CharField(max_length=10, choices=STATUSES, default='PENDING')
    

    created_by = models.ForeignKey(DjangoUser, on_delete=models.CASCADE, related_name='created_trades')
    confirmed_by = models.ForeignKey(DjangoUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='confirmed_trades')
    approved_by = models.ForeignKey(DjangoUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_trades')

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional fields
    notes = models.TextField(blank=True, help_text="Additional notes about the trade")
    
    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('confirm_trade', 'Can confirm trades'),
            ('approve_trade', 'Can approve trades'),
            ('reject_trade', 'Can reject trades'),
            ('unconfirm_trade', 'Can move confirmed trades back to pending'),
        ]
        
    def __str__(self):
        return f"{self.trade_type} {self.quantity} {self.symbol} @ ${self.price}"
    
    @property
    def total_value(self):
        """Calculate total trade value"""
        return self.quantity * self.price
    
    @property
    def can_be_confirmed(self):
        """Check if trade can be confirmed"""
        return self.status == 'PENDING'
    
    @property
    def can_be_approved(self):
        """Check if trade can be approved"""
        return self.status == 'CONFIRMED'
    
    @property
    def status_color(self):
        """Return CSS color class for status"""
        colors = {
            'PENDING': 'yellow',
            'CONFIRMED': 'blue',
            'APPROVED': 'green',
            'REJECTED': 'red',
        }
        return colors.get(self.status, 'gray')
