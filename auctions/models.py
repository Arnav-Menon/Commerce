from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ModelForm
from django import forms


class User(AbstractUser):
    pass

class Listing(models.Model):
    item = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    current_price = models.IntegerField()
    picture_url = models.URLField(default="", null=True, blank=True)
    category = models.CharField(max_length=32, null=True, blank=True)
    user = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"{self.item}"

class ListingForm(ModelForm):
    picture_url = forms.URLField(
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "Optional", "rows": 1}
        ),
    )
    category = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={"placeholder": "Optional", "rows": 1}
        ),
    )
    user = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    class Meta:
        model = Listing
        fields = "__all__"

class Bid(models.Model):
    new_price = models.IntegerField()
    bid_item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listed_item")
    latest_bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")

    def __str__(self):
        return f"{self.latest_bidder} bid ${self.new_price} on {self.bid_item}"

class Comment(models.Model):
    item_commented = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="og_item")
    comment = models.CharField(max_length=128)