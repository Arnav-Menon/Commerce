from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    item = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    start_price = models.FloatField()

    def __str__(self):
        return f"{self.item}"

class Bid(models.Model):
    bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listed_item")
    new_price = models.FloatField()

    def __str__(self):
        return f"${self.new_price} on {self.bid_item}"

class Comment(models.Model):
    item_commented = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="og_item")
    comment = models.CharField(max_length=128)