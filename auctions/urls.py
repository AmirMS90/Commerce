from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:id>", views.listing_view, name="listing"),
    path("inactivate/<int:id>", views.inactivate_view, name="inactivate"),
    path("addToWatchList/<int:id>", views.add_watch_list, name="add_watch_list"),
    path("deleteFromWatchList/<int:id>", views.delete_watch_list, name="delete_watch_list"),
	path("watchList", views.watch_list_view, name="watchList"),
	path("categories", views.categories_view, name="categories"),
	path("bid/<int:id>", views.bid_view, name="bid"),
	path("comment/<int:id>", views.comment_view, name="comment"),
	path("new", views.new, name="new")
]
