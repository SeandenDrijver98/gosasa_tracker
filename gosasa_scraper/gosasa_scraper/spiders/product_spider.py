import logging

from scrapy.http import HtmlResponse
from selenium import webdriver

from Market.models import TrackedProduct, DailyPrice

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

scrapy_logger = logging.getLogger('scrapy')

class ProductSpider(scrapy.Spider):
    name = 'product_spider'
    allowed_domains = ['joburgmarket.co.za']
    start_urls = [
        "https://www.joburgmarket.co.za/jhbmarket/daily-price-list/"
    ]

    def start_requests(self):
        # Use SeleniumRequest instead of scrapy.Request to enable Selenium
        scrapy_logger.info("Starting the spider")
        yield SeleniumRequest(
            url=self.start_urls[0],
            callback=self.parse,
            wait_time=50,  # Time to wait for JavaScript to load
            wait_until=EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="commodity"]'))
        )


    def parse(self, response):
        # Extract items (values from <option> elements)
        if '<select' in response.text:
            print("Select element found in the response")
        else:
            print("Select element not found in the response")

        options = response.css('select[name="commodity"] option::attr(value)').getall()
        print(options)
        # Remove the empty option
        options = [option for option in options if option]
        scrapy_logger.info(f"Found {len(options)} items")

        # Iterate over each item and interact with the dropdown
        for item in options:
            yield SeleniumRequest(
                url=self.start_urls[0],
                callback=self.handle_dropdown,
                meta={'item': item}
            )

    def handle_dropdown(self, response):
        item_value = response.meta['item']

        # Get the WebDriver instance from the response
        driver = response.meta['driver']
        wait = WebDriverWait(driver, 10)  # 10 seconds timeout

        # Wait for the dropdown to be present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'select[name="commodity"]')))

        # Locate the dropdown and select the option by value
        select_element = driver.find_element(By.CSS_SELECTOR, 'select[name="commodity"]')
        select = Select(select_element)
        select.select_by_value(item_value)

        # Optionally wait for form submission and page update
        time.sleep(1)  # Adjust the sleep time if needed for your page's response time

        # Verify the selected option
        selected_option = select.first_selected_option.get_attribute('value')
        assert selected_option == item_value, f"Expected '{item_value}', but got '{selected_option}'"

        # Wait until the 'containers' div is loaded
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.containers')))

        # Extract all <a> tags within the 'containers' div
        links = driver.find_elements(By.CSS_SELECTOR, 'div.containers a')
        scrapy_logger.info(f"Found {len(links)} containers for {item_value}")

        # Iterate over each <a> tag and follow the link
        for link in links:
            name = link.text
            url = link.get_attribute('href')
            yield SeleniumRequest(
                url=url,
                callback=self.handle_container_stats,
                meta={'item': item_value, 'container_name': name}
            )

    def handle_container_stats(self,response):
        item_value = response.meta['item']
        container_value = response.meta['container_name']
        # Get the WebDriver instance from the response
        driver = response.meta['driver']
        wait = WebDriverWait(driver, 10)  # 10 seconds timeout

        # Wait until the elements are present
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.statistics')))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.Container')))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.myform select[name="commodity"]')))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'table.alltable')))

        # Extract the statistics
        statistics = driver.find_element(By.CSS_SELECTOR, 'div.statistics').text
        expected_statistics = f"Statistics for {item_value}"
        assert statistics == expected_statistics, f"Expected '{expected_statistics}', but got '{statistics}'"

        # Extract the container
        container = driver.find_element(By.CSS_SELECTOR, 'div.Container').text
        expected_container = f"Container: {container_value}"
        assert container == expected_container, f"Expected '{expected_container}', but got '{container}'"

        # Extract the selected commodity
        commodity_select = driver.find_element(By.CSS_SELECTOR, 'div.myform select[name="commodity"]')
        selected_commodity = commodity_select.find_element(By.CSS_SELECTOR, 'option[selected]').text
        expected_commodity = item_value
        assert selected_commodity == expected_commodity, f"Expected '{expected_commodity}', but got '{selected_commodity}'"

        # Extract the average price
        average_price = driver.find_element(By.CSS_SELECTOR, 'table.alltable tbody tr td:nth-child(5)').text

        scrapy_logger.info(f"Statistics for {item_value} - Container: {container_value} - Price: {average_price}")
        tracked_product, created = TrackedProduct.objects.get_or_create(commodity=item_value, container=container_value)

        DailyPrice.objects.create(product=tracked_product, price=average_price)
