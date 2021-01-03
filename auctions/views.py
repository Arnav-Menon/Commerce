from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages

from .models import *

class NewBidForm(forms.Form):
    bid = forms.IntegerField()

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listing": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def item_info(request, item_id):
    listing = Listing.objects.get(id=item_id)
    num_bids = listing.listed_item.all().count()

    # TODO: get user who listed the item
    # probably gonna have to mess with the Listing model

    return render(request, "auctions/item.html", {
        "listing": listing,
        "bid_count": num_bids,
        "form": NewBidForm()
    })

# TODO: finish this method
# form is not rendering prperly
def place_bid(request, item_id):

    listing = Listing.objects.get(id=item_id)
    num_bids = listing.listed_item.all().count()

    form = NewBidForm(request.POST)
    if form.is_valid():
        potential_bid = form.cleaned_data["bid"]
        if potential_bid <= listing.current_price:
            messages.add_message(request, messages.INFO, "New bid must be greater than current bid. Please try again.")
        else:    
            listing.current_price = potential_bid
            listing.save()
            # creates and saves object all in one line
            new_bid = Bid.objects.create(new_price=potential_bid, bid_item=listing)
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/item.html", {
        "listing": listing,
        "bid_count": num_bids,
        "form": NewBidForm()
    })

def create_listing(request):
    if request.method == "POST":

        form = ListingForm(request.POST)
        if form.errors:
            messages.add_message(request, messages.INFO, form.errors)
            return render(request, "auctions/create.html", {
                "form": form
            })

        if form.is_valid():
            fcd = form.cleaned_data
            title = fcd["item"]
            des = fcd["description"]
            cp = fcd["current_price"]
            pu = None
            cat = None
            if fcd["picture_url"]:
                pu = fcd["picture_url"]
            if fcd["category"]:
                cat = fcd["category"]
            
            messages.add_message(request, messages.INFO, "Listing created successfully")
            new_obj = Listing.objects.create(
                item=title,
                description=des,
                current_price=cp,
                picture_url=None or pu,
                category=None or cat
            )
            return index(request)

    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })