# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from Market.models import DailyPrice,TrackedProduct


class DailyPriceItem(DjangoItem):
    django_model = DailyPrice


class TrackedProductItem(DjangoItem):
    django_model = TrackedProduct
