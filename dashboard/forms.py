from django import forms
from .models.trade import Trade

class TradeForm(forms.ModelForm):
    class Meta:
        model = Trade
        fields = ['symbol', 'trade_type', 'quantity', 'price', 'notes']
        widgets = {
            'symbol': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400/40',
                'placeholder': 'e.g., AAPL, MSFT'
            }),
            'trade_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:ring-2 focus:ring-cyan-400/40'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400/40',
                'placeholder': 'Number of shares'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400/40',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-400/40',
                'placeholder': 'Additional notes (optional)',
                'rows': 3
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make symbol uppercase
        if 'symbol' in self.data:
            self.data = self.data.copy()
            self.data['symbol'] = self.data['symbol'].upper()
    
    def clean_symbol(self):
        symbol = self.cleaned_data.get('symbol')
        if symbol:
            return symbol.upper().strip()
        return symbol
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than 0")
        return price
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError("Quantity must be greater than 0")
        return quantity
