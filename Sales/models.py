from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    unit_cost = models.DecimalField(max_digits=9, decimal_places=2)
    content = models.CharField(max_length=255)
    content_cost = models.DecimalField(max_digits=9, decimal_places=2)
    transport = models.DecimalField(max_digits=9, decimal_places=2)

    def packaging_cost(self):
        return self.unit_cost + self.content_cost

    def total_cost(self):
        return self.unit_cost + self.content_cost + self.transport

    def __str__(self):
        return f"{self.title} - {self.unit}"


class Market(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class DeliveryNote(models.Model):
    delivery_note_reference = models.CharField(max_length=255)
    send_date = models.DateField(auto_now=True)
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name="market_sold_at")
    delivery_date = models.DateField()

    def __str__(self):
        return f"{self.delivery_note_reference}"


class DailySale(models.Model):
    sale_date = models.DateField()
    # Null Delivery note = Cash Sale
    delivery_note = models.ForeignKey(DeliveryNote, on_delete=models.SET_NULL,related_name="delivery_sales", null=True)

    def daily_payment(self):
        total = 0
        for item in self.sold_items.objects.all():
            total += item.payment

    def __str__(self):
        return f"DN:{self.delivery_note} - {self.sale_date}"


class ItemSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    payment = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    sale = models.ForeignKey(DailySale, on_delete=models.CASCADE, related_name="sold_items")


class DeliveredProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    delivery_note = models.ForeignKey(DeliveryNote, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.delivery_note} - {self.product} x {self.quantity}"

    @property
    def unsold_amount(self):
        if not self.quantity:
            return

        quantity_sold = 0
        for sale in self.delivery_note.delivery_sales.all():
            for sold_product in sale.sold_items.filter(product=self.product):
                quantity_sold += sold_product.quantity

        return self.quantity - quantity_sold

