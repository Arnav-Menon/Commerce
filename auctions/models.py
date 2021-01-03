from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    item = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    current_price = models.IntegerField()
    picture_url = models.URLField(default="", blank=True)
    category = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f"{self.id}: {self.item}"

class Bid(models.Model):
    new_price = models.IntegerField()
    bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listed_item")

    def __str__(self):
        return f"${self.new_price} on {self.bid_item}"

class Comment(models.Model):
    item_commented = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="og_item")
    comment = models.CharField(max_length=128)