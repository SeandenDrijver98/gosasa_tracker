from django.core import management
from django.conf import settings
from datetime import datetime
from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    From,
)
from .models import DailyPrice


@shared_task(ignore_result=True)
def crawl_market_products():
    management.call_command('crawl')
    
    
@shared_task(ignore_result=True)
def send_daily_prices_mail():
    today = datetime.today()
    daily_prices_for_products = DailyPrice.objects.filter(date_created=today)
    message = Mail(to_emails=["sddrijver@gmail.com"])
    message.from_email = From(email=settings.FROM_MAIL, name=settings.FROM_NAME)
    message.template_id = settings.SENDGRID_TEMPLATES['daily_prices']
    message.dynamic_template_data = {
        "date": today.strftime("%d %B %Y"),
        "tracked_products": [
            {"product": str(product.product), "price": product.price} for product in daily_prices_for_products
        ]
    }

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(e.message)
