from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import (
    HttpResponseNotFound,
    HttpResponseForbidden,
    HttpResponseBadRequest,
)
from django.shortcuts import render, redirect
from django import forms

from .models import *


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


class BidForm(forms.Form):
    price = forms.FloatField(
        label="Bid Price",
        min_value=0.01,
        widget=forms.NumberInput(attrs={"step": 0.01}),
    )


class newForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        categories = [("", "")] + [
            (category.id, category.name) for category in categories
        ]
        self.fields["category"].choices = categories

    title = forms.CharField(label="Title", max_length=64)
    description = forms.CharField(
        label="Description", widget=forms.Textarea, max_length=256
    )
    image_link = forms.CharField(label="Image Link", required=False, max_length=128)
    category = forms.ChoiceField(label="Category", required=False)
    starting_bid = forms.FloatField(
        label="Starting Bid",
        min_value=0.01,
        widget=forms.NumberInput(attrs={"step": 0.01}),
    )


class CategoryForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        categories = [(category.id, category.name) for category in categories]
        categories.insert(0, ("", "Select an option"))
        self.fields["category"].choices = categories

    category = forms.ChoiceField(label="Category")


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return redirect("index")
    else:
        return render(request, "auctions/register.html")


@login_required
def new(request):
    if request.method == "POST":
        form = newForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            newList = Listing()
            if form.cleaned_data["image_link"]:
                newList.image_link = form.cleaned_data["image_link"]
            category = form.cleaned_data["category"]
            if category:
                category = Category.objects.get(id=category)
                if category:
                    newList.category = category
            newList.title = form.cleaned_data["title"]
            newList.description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            if (starting_bid % 0.01) != 0:
                return HttpResponseForbidden(
                    "starting bid can't be preciser than 0.01$"
                )
            newList.starting_bid = starting_bid
            newList.current = newList.starting_bid
            newList.submitter = request.user
            newList.save()
            return redirect("index")
        else:
            return render(
                request,
                "auctions/new.html",
                {"form": form, "message": "Invalid inputs."},
            )
    form = newForm()
    return render(request, "auctions/new.html", {"form": form})


def listing_view(request, id):
    try:
        listing = Listing.objects.get(id=id)
    except:
        return HttpResponseNotFound()

    if not listing.active:
        isWinner = listing.winner == request.user
        return render(
            request,
            "auctions/listing.html",
            {"listing": listing, "isWinner": isWinner},
        )

    bid_form = BidForm()
    comment_form = CommentForm()
    return render(
        request,
        "auctions/listing.html",
        {"listing": listing, "bid_form": bid_form, "comment_form": comment_form},
    )


@login_required
def add_watch_list(request, id):
    listing = Listing.objects.get(id=id)
    if listing:
        request.user.watchList.add(listing)
        request.user.save()
    else:
        return HttpResponseNotFound()
    return redirect("watchList")


@login_required
def delete_watch_list(request, id):
    listing = Listing.objects.get(id=id)
    if listing:
        request.user.watchList.remove(listing)
        request.user.save()
    else:
        return HttpResponseNotFound()
    return redirect("watchList")


@login_required
def watch_list_view(request):
    return render(request, "auctions/watch_list.html")


@login_required
def inactivate_view(request, id):
    listing = Listing.objects.get(id=id)
    if listing:
        if request.user == listing.submitter:
            listing.active = False
            current_price = listing.current
            winner = Bid.objects.get(listing=listing, price=current_price).user
            listing.winner = winner
            listing.save()
            bids = listing.bids.all()
            for bid in bids:
                bid.delete()
            return redirect("index")
        else:
            return HttpResponseForbidden()
    else:
        return HttpResponseNotFound()


def categories_view(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data["category"]
            if not category:
                return render(
                    request,
                    "auctions/categories.html",
                    {"form": CategoryForm(), "message": "Forgot the category."},
                )
            category = Category.objects.get(id=category)
            listings = Listing.objects.filter(category=category)
            return render(
                request,
                "auctions/categories.html",
                {"form": form, "listings": listings},
            )
        return render(
            request,
            "auctions/categories.html",
            {"form": CategoryForm(), "message": "Invalid input."},
        )
    form = CategoryForm()
    return render(request, "auctions/categories.html", {"form": form})


@login_required
def bid_view(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest()
    form = BidForm(request.POST)
    if form.is_valid():
        bid_price = form.cleaned_data["price"]
        if (bid_price % 0.01) != 0:
            return HttpResponseForbidden("bid price can't be preciser than 0.01$")
        try:
            listing = Listing.objects.get(id=id)
        except:
            return HttpResponseNotFound()
        if bid_price <= listing.current:
            return render(
                request,
                "auctions/new.html",
                {
                    "form": form,
                    "message": "Your bidding should be higher than the current price.",
                },
            )
        listing.current = bid_price
        listing.save()
        bid = Bid()
        bid.listing = listing
        bid.user = request.user
        bid.price = bid_price
        bid.save()
        return redirect("listing", id=listing.id)


@login_required
def comment_view(request, id):
    if request.method != "POST":
        return HttpResponseBadRequest()
    form = CommentForm(request.POST)
    if form.is_valid():
        content = form.cleaned_data["content"]
        try:
            listing = Listing.objects.get(id=id)
        except:
            return HttpResponseNotFound()
        comment = Comment()
        comment.listing = listing
        comment.user = request.user
        comment.content = content
        comment.save()
        return redirect("listing", id=listing.id)
