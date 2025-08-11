from django.core.management.base import BaseCommand
from dashboard.models import Trade, DjangoUser
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Create sample trades for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of trades to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Create or get a default user
        user, created = DjangoUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: admin/admin123'))

        # Sample data
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC']
        trade_types = ['BUY', 'SELL']
        statuses = ['PENDING', 'CONFIRMED', 'APPROVED']
        notes_options = [
            'Regular market order',
            'Limit order execution',
            'Stop loss trigger',
            'Quarterly rebalancing',
            'Portfolio diversification',
            'Market timing strategy',
            '',  # Some trades without notes
        ]

        created_trades = 0
        for i in range(count):
            symbol = random.choice(symbols)
            trade_type = random.choice(trade_types)
            quantity = random.randint(10, 1000)
            price = Decimal(str(round(random.uniform(50.0, 500.0), 2)))
            status = random.choice(statuses)
            notes = random.choice(notes_options)
            
            trade = Trade.objects.create(
                symbol=symbol,
                trade_type=trade_type,
                quantity=quantity,
                price=price,
                status=status,
                notes=notes,
                created_by=user,
            )
            
            # If confirmed or approved, set the appropriate fields
            if status in ['CONFIRMED', 'APPROVED']:
                trade.confirmed_by = user
                trade.confirmed_at = trade.created_at
                
            if status == 'APPROVED':
                trade.approved_by = user
                trade.approved_at = trade.created_at
                
            trade.save()
            created_trades += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_trades} sample trades'
            )
        )
        
        # Display summary
        total_trades = Trade.objects.count()
        pending = Trade.objects.filter(status='PENDING').count()
        confirmed = Trade.objects.filter(status='CONFIRMED').count()
        approved = Trade.objects.filter(status='APPROVED').count()

        self.stdout.write(f'Trade Summary:')
        self.stdout.write(f'  Total: {total_trades}')
        self.stdout.write(f'  Pending: {pending}')
        self.stdout.write(f'  Confirmed: {confirmed}')
        self.stdout.write(f'  Approved: {approved}')
