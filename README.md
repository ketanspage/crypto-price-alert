# Cryptocurrency Price Alert Application

This is a Django application that allows users to set price alerts for various cryptocurrencies. When the target price for a cryptocurrency is reached or exceeded, the application sends an email notification to the user.

## Features

- User authentication
- Create, view, and delete price alerts
- Email notifications when the target price is reached
- Caching for alert listings

## Prerequisites

- Python 3.x
- Django 3.x or higher
- Celery
- Redis (for Celery broker)
- An email service (configured in Django settings)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/ketanspage/crypto-price-alert.git
    cd crypto-price-alert
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up your Django settings:
    - Configure your database in `settings.py`
    - Configure your email backend in `settings.py`
    - Add your Celery configuration in `settings.py`

4. Run the migrations:
    ```bash
    python manage.py migrate
    ```

5. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

6. Build and start the services with Docker Compose:
    ```bash
    docker compose --build
    docker compose up

    ```
    
## Usage

### API Endpoints

#### Alerts

- **Create a new alert**: 
    ```http
    POST /alerts/
    ```
    Request body:
    ```json
    {
        "cryptocurrency": "btc",
        "target_price": 30000.00
    }
    ```
    Headers:
    ```http
    Authorization: Token your-auth-token
    ```

- **List all alerts for the authenticated user**: 
    ```http
    GET /alerts/
    ```
    Headers:
    ```http
    Authorization: Token your-auth-token
    ```

- **Filter alerts by status**: 
    ```http
    GET /alerts/?status=created
    ```
    Headers:
    ```http
    Authorization: Token your-auth-token
    ```

- **Delete an alert**: 
    ```http
    DELETE /alerts/{alert_id}/delete_alert/
    ```
    Headers:
    ```http
    Authorization: Token your-auth-token
    ```
- **Get token**: 
    ```http
    POST /api/token/
    ```
    Headers:
    ```http
    Username: your_created_username
    Password: your_created_password
    ```


## Celery Task

The Celery task `check_cryptocurrency_prices` periodically fetches the latest prices of cryptocurrencies and checks them against the created alerts. If the target price is met or exceeded, it sends an email notification to the user and updates the alert status.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Django REST framework](https://www.django-rest-framework.org/)
- [Celery](https://docs.celeryproject.org/en/stable/)
- [CoinGecko API](https://www.coingecko.com/en/api)

## Contact

For any issues or questions, please contact [gandhi.ketan55555@gmail.com](mailto:gandhi.ketan55555@gmail.com).
