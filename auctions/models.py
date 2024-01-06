from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class User(AbstractUser):
    pass

# Did not show this model for CS50 view. But I made this for template for the future client.
class UserRole(models.Model):
    role_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=255, default='Subscriber', choices=[('Admin', 'Admin'), ('User', 'User'), ('Subscriber', 'Subscriber')])

    def __str__(self):
        return self.user.username

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    slug = models.SlugField(default='', blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name.lower())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class AuctionListing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_listings')
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=255, default='Active', choices=[('Active', 'Active'), ('Closed', 'Closed'), ('Cancelled', 'Cancelled')])
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shipping = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    watchers = models.ManyToManyField(User, related_name='watchlist_listings', blank=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='winner_listings')


    def __str__(self):
        return self.title

class Bid(models.Model):
    bid_id = models.AutoField(primary_key=True)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField()

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.listing.title}"

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    content = models.TextField()
    comment_time = models.DateTimeField()

class Watchlist(models.Model):
    watchlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(AuctionListing, related_name='watchlist_users', blank=True)

    def __str__(self):
        return f"Watchlist of {self.user.username}"

# Did not show this model for CS50 view. But I made this for template for the future client.
class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders')
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_time = models.DateTimeField()
    status = models.CharField(max_length=255, default='Pending', choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')])