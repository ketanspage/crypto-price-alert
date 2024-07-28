from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Alert
from .serializers import AlertSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import requests

class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status', None)
        queryset = Alert.objects.filter(user=user)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        cache_key = f'alerts_{request.user.id}'
        if cache.get(cache_key):
            return Response(cache.get(cache_key))
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*60)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        alert = serializer.save(user=self.request.user)
        # Send email notification about alert creation
        send_mail(
            'New Alert Created',
            f'You have created a new alert for {alert.cryptocurrency} with a target price of {alert.target_price}.',
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
            fail_silently=False,
        )
        # Check if the alert should be triggered immediately
        self.check_and_notify(alert)

    def check_and_notify(self, alert):
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        params = {'vs_currency': 'USD', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1, 'sparkline': False}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

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

    @action(detail=True, methods=['delete'])
    def delete_alert(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'deleted'
        alert.save()
        
        # Invalidate cache
        cache_key = f'alerts_{request.user.id}'
        cache.delete(cache_key)
        
        # Send email notification
        send_mail(
            'Alert Deleted',
            f'Your alert for {alert.cryptocurrency} with a target price of {alert.target_price} has been deleted.',
            settings.DEFAULT_FROM_EMAIL,
            [self.request.user.email],
            fail_silently=False,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
