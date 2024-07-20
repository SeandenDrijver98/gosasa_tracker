from django.db import models


class TrackedProduct(models.Model):
    commodity = models.CharField(max_length=255)
    container = models.CharField(max_length=255)

    def __str__(self):
        return self.commodity + " - " + self.container


class DailyPrice(models.Model):
    product = models.ForeignKey(TrackedProduct, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    date_created = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.date_created} - {self.product} - R{self.price}"