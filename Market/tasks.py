from django.core import management
from django.conf import settings
from celery import shared_task
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    From,
)


@shared_task(ignore_result=True)
def crawl_market_products():
    management.call_command('crawl')
    
    
@shared_task(ignore_result=True)
def send_daily_prices_mail():
    print(settings.FROM_MAIL)
    print(settings.SENDGRID_API_KEY)
    message = Mail(to_emails=["sddrijver@gmail.com"])
    message.from_email = From(email=settings.FROM_MAIL, name=settings.FROM_NAME)
    message.template_id = settings.SENDGRID_TEMPLATES['daily_prices']

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
    except Exception as e:
        print(e.message)
