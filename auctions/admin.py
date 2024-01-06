from django.contrib import admin
from .models import User, UserRole, Category, AuctionListing, Watchlist, Bid, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(Category)
admin.site.register(AuctionListing)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)
