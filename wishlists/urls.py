from django.urls import path
from . import views

urlpatterns = [
    path("", views.Wishlists.as_view()), 
    path("<int:id>/", views.WishlistDeatil.as_view()),
    path('<int:wishlist_id>/rooms/<int:room_id>/', views.WishlistRoom.as_view())
]