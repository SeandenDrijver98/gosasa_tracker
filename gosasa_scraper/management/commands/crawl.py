from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gosasa_scraper.gosasa_scraper import settings as scraper_settings
from gosasa_scraper.gosasa_scraper.spiders.product_spider import ProductSpider


class Command(BaseCommand):
    help = 'Release spider'

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(scraper_settings)

        process = CrawlerProcess(settings=crawler_settings)

        process.crawl(ProductSpider)
        process.start()