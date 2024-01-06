from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('create-listing/', views.create_listing, name='create-listing'),
    path('<str:parent_category_slug>/<str:child_category_slug>/<int:listing_id>',views.single_listing, name="single-listing"),
    path('add-to-watchlist/<int:listing_id>/', views.add_to_watchlist, name='add-to-watchlist'),
    path('remove-from-watchlist/<int:listing_id>/', views.remove_from_watchlist, name='remove-from-watchlist'),
    path('watchlist/', views.watchlist, name='watchlist'),
    path('close-auction/<str:parent_category_slug>/<str:child_category_slug>/<int:listing_id>/', views.close_auction, name='close-auction'),
    path('search/', views.search_listings, name='search'),
    path('search/<str:query>/', views.search_listings, name='search-results'),
    path('categories/', views.category_list, name='category-list'),
    path('<str:category_slug>/', views.category_detail, name='category-detail'),

]
