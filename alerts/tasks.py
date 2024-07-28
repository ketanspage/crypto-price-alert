import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import Alert
from celery import shared_task

@shared_task
def check_cryptocurrency_prices():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {'vs_currency': 'USD', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1, 'sparkline': False}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        alerts = Alert.objects.filter(status='created')
        for alert in alerts:
            # Find the current price of the cryptocurrency
            symbol = alert.cryptocurrency.upper()
            for coin in data:
                if coin['symbol'].upper() == symbol:
                    current_price = coin['current_price']
                    if current_price >= alert.target_price:
                        # Send email to the user
                        send_mail(
                            subject=f'{alert.cryptocurrency} Price Alert',
                            message=f'The price of {alert.cryptocurrency} has reached {current_price}, which is above your target of {alert.target_price}.',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[alert.user.email],
                            fail_silently=False,
                        )
                        # Update alert status
                        alert.status = 'triggered'
                        alert.save()
                    break
    except requests.exceptions.RequestException as e:
        # Log the error
        print(f"Error fetching cryptocurrency prices: {e}")
