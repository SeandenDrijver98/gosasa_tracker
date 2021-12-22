from django.core import management
from celery import shared_task


@shared_task(ignore_result=True)
def crawl_market_products():
    management.call_command('crawl')