from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="admin_dashboard"),
    path(
        "orders/update-status/",
        views.admin_update_order_status,
        name="admin_update_order_status",
    ),
    path(
        "products/save/",
        views.admin_save_product,
        name="admin_save_product",
    ),
    path(
        "products/<int:item_id>/delete/",
        views.admin_delete_product,
        name="admin_delete_product",
    ),
    path(
        "users/save/",
        views.admin_save_user,
        name="admin_save_user",
    ),
    path(
        "users/<int:user_id>/details/",
        views.get_user_details,
        name="admin_get_user_details",
    ),
    path(
        "orders/<int:order_id>/invoice/",
        views.admin_order_invoice,
        name="admin_order_invoice",
    ),
    path(
        "products/<int:item_id>/image/",
        views.get_product_image_view,
        name="admin_product_image",
    ),
]