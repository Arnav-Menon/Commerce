from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:item_id>", views.item_info, name="item_info"),
    path("<int:item_id>/bid", views.place_bid, name="bid"),
    path("create/", views.create_listing, name="create"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("list_categories/", views.list_categories, name="list_categories"),
    path("items_by_category/<str:category>", views.categorical_items, name="cat_items"),
    path("close/<int:item_id>", views.close_listing, name="close_list"),
    path("add_watchlist/<int:item_id>", views.add_watchlist, name="add_watchlist"),
]
