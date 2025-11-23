from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    
    path("about/<str:complain>/", views.about, name="about"),
    path("about/", views.about, name="about"),
    

    path("shop/<int:current_page>/<str:category>/<str:subcategory>/", views.shop, name="shop"),
    path("shop/<int:current_page>/<str:category>/", views.shop, name="shop"),
    path("shop/<int:current_page>/", views.shop, name="shop"),
    path("shop/", views.shop, name="shop")
]