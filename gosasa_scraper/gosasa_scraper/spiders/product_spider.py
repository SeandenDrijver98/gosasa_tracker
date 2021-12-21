from scrapy.spiders import CrawlSpider

from Market.models import TrackedProduct, DailyPrice

class ProductSpider(CrawlSpider):
    name = 'product_spider'
    allowed_domains = ['joburgmarket.co.za']
    tracked_products = TrackedProduct.objects.all()
    start_urls = [
        product.start_url for product in tracked_products
    ]

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        try:
            tracked_product = TrackedProduct.objects.get(start_url=response.url)
        except TrackedProduct.DoesNotExists():
            pass

        price = response.css('.alltable > tbody > tr > td:nth-of-type(5)::text').get()[1:]
        print(f"Price found is R{price} for {str(tracked_product)}")
        DailyPrice.objects.create(product=tracked_product, price=price)

        # property_loader = ItemLoader(item=ScraperItem(), response=response)
        # property_loader.default_output_processor = TakeFirst()
        #
        # property_loader.add_css(
        #     "code", "span#ContentPlaceHolder1_DetailsFormView_CodeLabel::text"
        # )
