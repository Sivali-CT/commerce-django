from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from .models import User, AuctionListing, Category, Watchlist, Bid, Comment
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

class ListingForm(forms.ModelForm):
    parent_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent_category__isnull=True),
        empty_label="Parent category",
        required=False,
        widget=forms.Select(attrs={'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6'})  

    )
    child_category = forms.ModelChoiceField(
        queryset=Category.objects.filter(parent_category__isnull=False),
        empty_label="Child category",
        required=False,
        widget=forms.Select(attrs={'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6'}) 
    )
    class Meta:
        model = AuctionListing
        fields = ['title', 'description', 'start_price', 'current_price', 'start_time', 'end_time', 'status', 'shipping', 'image_url', 'parent_category', 'child_category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'description': forms.Textarea(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'start_price': forms.NumberInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'current_price': forms.NumberInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'start_time': forms.DateTimeInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'end_time': forms.DateTimeInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'status': forms.Select(attrs={'class': 'block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6'}),

            'shipping': forms.TextInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),

            'image_url': forms.TextInput(attrs={'class': 'block w-full border-0 py-2 px-4 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields =['amount']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets= {
            'content': forms.Textarea(attrs={'class': 'px-0 w-full text-sm text-gray-900 border-0 focus:ring-0 focus:outline-none'}),
        }
        labels = {
            'content': '',
        }

# Home and Auth
def index(request):
    active_listings = AuctionListing.objects.filter(status='Active').order_by('-start_time')
    return render(request, "auctions/index.html", {'active_listings': active_listings})

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

# Listings
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.seller = request.user
            parent_category = form.cleaned_data.get('parent_category')
            child_category = form.cleaned_data.get('child_category')

            if child_category:
                listing.category = child_category
            elif parent_category:
                listing.category = parent_category

            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create-listing.html", {'form': ListingForm()})
    

# Single listing and bid
def single_listing(request, parent_category_slug, child_category_slug, listing_id):
    # Get slug
    parent_category = get_object_or_404(Category, slug=parent_category_slug, parent_category=None)

    try:
        category = Category.objects.get(slug=child_category_slug, parent_category=parent_category)
    except Category.DoesNotExist:
        category = parent_category

    listing = get_object_or_404(AuctionListing, listing_id=listing_id, category=category)

    # Comment
    comments = Comment.objects.filter(listing=listing).order_by('-comment_time')

    if request.method == "POST":
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.listing = listing
            comment.comment_time = timezone.now()
            comment.save()
            return HttpResponseRedirect(reverse("single-listing", args=(parent_category_slug, child_category_slug, listing_id)))
    else:
        comment_form = CommentForm()

    # Bid
    if request.method == "POST":
        bid_form = BidForm(request.POST)

        if bid_form.is_valid():
            bid_amount = bid_form.cleaned_data["amount"]

            if bid_amount >= listing.start_price and bid_amount >= listing.current_price:
                bid = Bid(bidder=request.user, listing=listing, amount=bid_amount)
                bid.bid_time = timezone.now()
                bid.save()

                listing.current_price += bid_amount
                listing.save()
                
                return HttpResponseRedirect(reverse("single-listing", args=(parent_category_slug, child_category_slug, listing_id)))
            else:
                messages.error(request, "Invalid bid amount.")
        else:
            messages.error(request, "Invalid form data.")
    else:
        bid_form = BidForm()

    # Check winner
    is_winner = False
    if listing.status == "Closed" and listing.winner == request.user:
        is_winner = True

    # Get messages from the session
    error_messages = messages.get_messages(request)

    return render(request, "auctions/listing-detail.html", {"listing": listing, "is_winner": is_winner, "error_messages": error_messages, "comments": comments, "comment_form": comment_form})

@login_required
def close_auction(request, parent_category_slug, child_category_slug, listing_id):
    listing = get_object_or_404(AuctionListing, listing_id=listing_id)

    if request.user != listing.seller:
        messages.error(request, "You are not authorized to close this auction.")

        return HttpResponseRedirect(reverse("single-listing", args=(parent_category_slug, child_category_slug, listing_id)))

    if listing.status == "Closed":
        messages.error(request, "The auction is already closed.")

        return HttpResponseRedirect(reverse("single-listing", args=(parent_category_slug, child_category_slug, listing_id)))
    
    # Who is the highest bidding?
    highest_bid = Bid.objects.filter(listing=listing).order_by('-amount').first()

    if highest_bid:
        listing.winner = highest_bid.bidder

    else:
        messages.error(request, "No bids have been placed on this listing.")

    listing.status = "Closed"
    listing.save()

    messages.success(request, "Auction closed successfully.")
    return HttpResponseRedirect(reverse("single-listing", args=(parent_category_slug, child_category_slug, listing_id)))

# Watchlist
@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)
    watchlist.listings.add(listing)
    return HttpResponseRedirect(reverse('watchlist'))


@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    # Check if the listing is in the user's watchlist
    if watchlist.listings.filter(pk=listing_id).exists():
        watchlist.listings.remove(listing)

    return HttpResponseRedirect(reverse("watchlist"))

@login_required
def watchlist(request):
    watchlist, created = Watchlist.objects.get_or_create(user=request.user)

    watchlist_items = watchlist.listings.all()
    print(watchlist_items)
    return render(request, "auctions/watchlist.html", {"watchlist_items": watchlist_items})


# Categories

def category_list(request):
    categories = Category.objects.filter(parent_category__isnull=True)
    return render(request, "auctions/categories.html", {"categories":categories})

def category_detail(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    
    # Get listings in both parent and child categories
    listings = AuctionListing.objects.filter(
        Q(category=category) | Q(category__parent_category=category),
        status="Active"
    )

    return render(request, "auctions/category-detail.html", {"category": category, "listings": listings})

# Search
def search_listings(request, query=None):
    query = request.GET.get("q")

    if query:
        listings = AuctionListing.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query))

    else:
        listings = AuctionListing.objects.all()

    return render(request, "auctions/search.html", {"listings": listings, "query": query})
