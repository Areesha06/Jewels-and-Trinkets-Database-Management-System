from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("about/<str:complain>/", views.about, name="about"),
    path("about/", views.about, name="about"),
    

    path("shop/<int:current_page>/<str:category>/<str:subcategory>/", views.shop, name="shop"),
    path("shop/<int:current_page>/<str:category>/", views.shop, name="shop"),
    path("shop/<int:current_page>/", views.shop, name="shop"),
    path("shop/", views.shop, name="shop"),

    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),

    path("login/", views.login, name="login"),

    path("myaccount/", views.myaccount, name="myaccount"),
    path("myaccount/addresses/", views.manage_addresses, name="manage_addresses"),
    path("myaccount/payment/", views.manage_payment_method, name="manage_payment_method"),

    path('logout/', views.logout_view, name='logout'),

    path('update_profile/', views.update_profile, name='update_profile'),

    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("checkout/", views.checkout, name="checkout"),
    path("under-construction/", views.under_construction, name="under_construction"),
]