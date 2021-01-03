from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import *

class NewBidForm(forms.Form):
    bid = forms.CharField(max_length=6)

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
        "bid_count": num_bids
    })

# TODO: finish this method
# form is not rendering prperly
def place_bid(request, item_id):
    if request.method == "POST":
        print("Lets place a bid")
        form = NewBidForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            potential_bid = form.cleaned_data["bid"]
            print(potential_bid)
            return HttpResponseRedirect(reverse("index"))
        
        listings = Listing.objects.get(id=item_id)
        print(listings)
        num_bids = listings.listed_item.all().count()

    print("First Time")
    return render(request, "auctions/item.html", {
        "listing": listings,
        "bid_count": num_bids,
        "form": NewBidForm()
    })