from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages

from .models import *

import datetime

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
    watch_items = Watchlist.objects.filter(who=request.user)
    is_common = False
    for i in watch_items:
        if i.what == listing:
            is_common = True
    if num_bids != 0:
        bid = Bid.objects.filter(bid_item=listing).last()
        bidder = bid.latest_bidder
    else:
        bidder = None
    return render(request, "auctions/item.html", {
        "listing": listing,
        "bid_count": num_bids,
        "form": NewBidForm(),
        "latest_bidder": bidder,
        "current_user": str(request.user),
        "watch_items": watch_items,
        "is_common": is_common
    })

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
            new_bid = Bid.objects.create(
                new_price=potential_bid, 
                bid_item=listing,
                latest_bidder=request.user
            )
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
            
            new_obj = Listing.objects.create(
                item=title,
                description=des,
                current_price=cp,
                picture_url=None or pu,
                category=None or cat,
                user=request.user
            )
            messages.add_message(request, messages.INFO, f"'{new_obj.item}' created successfully")
            return index(request)

    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })

def add_watchlist(request, item_id):
    in_watchlist = False
    listing = Listing.objects.get(id=item_id)
    watch = Watchlist.objects.all()
    for i in watch:
        if i.what == listing and i.who == request.user:
            in_watchlist = True

    if in_watchlist:
        messages.add_message(request, messages.INFO, f"'{listing.item}' removed from watchlist.")
        Watchlist.objects.filter(who=request.user, what=listing).delete()
    else:
        messages.add_message(request, messages.INFO, f"'{listing.item}' added to watchlist.")
        watch_item = Watchlist.objects.create(
            who=request.user,
            what=listing
        )
    
    return HttpResponseRedirect(reverse("index"))

def watchlist(request):
    user_items = [i.what for i in Watchlist.objects.filter(who=request.user)]
    items = Listing.objects.all()
    user = User.objects.get(username=request.user)
    user_specific_items = []
    items_list = []
    for i in items:
        if i in user_items:
            user_specific_items.append(i)
        items_list.append(i.item)
    return render(request, "auctions/watchlist.html", {
        "user": user,
        "user_items": user_items
    })

def list_categories(request):
    listings = Listing.objects.all()
    categories = []
    for l in listings:
        if l.category not in categories:
            categories.append(l.category)
    return render(request, "auctions/list_categories.html", {
        "categories": categories
    })

def categorical_items(request, category):
    listings = Listing.objects.filter(category=category)
    return render(request, "auctions/item_categories.html", {
        "category": category,
        "listings": listings
    })

def close_listing(request, item_id):
    listing = Listing.objects.get(id=item_id)
    listing.delete()
    messages.add_message(request, messages.INFO, f"'{listing.item}' successfully closed.")
    return HttpResponseRedirect(reverse("index"))