from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from functools import wraps
from django.db import connection
import base64

from .database import data as admin_data


def admin_staff_required(view_func):
    """
    Decorator to ensure user is logged in and has admin or staff role.
    Blocks customers and non-authenticated users.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user is logged in
        if not request.session.get("login_status", False):
            return redirect("/login/")  # Redirect to login page
        
        role = request.session.get("role", "").lower()
        
        # Block customers
        if role == "customer":
            return redirect("/")  # Redirect to home
        
        # Allow admin and staff
        if role in ["admin", "staff"]:
            return view_func(request, *args, **kwargs)
        
        # Default: redirect to login
        return redirect("/login/")
    
    return wrapper


@admin_staff_required
def dashboard(request):
    """
    Admin / staff dashboard.

    Provides inventory, orders, products, users, and dashboard statistics
    to the unified `admin_ui.html` template.
    """
    user_role = request.session.get("role", "").lower()
    user_id = request.session.get("user_id")
    
    inventory = admin_data.get_inventory_snapshot()
    orders = admin_data.get_all_orders()
    products = admin_data.list_products()

    for product in products:
        if product.get("image"):
            product["image_base64"] = base64.b64encode(product["image"]).decode("utf-8")
        else:
            product["image_base64"] = None
    


    users = admin_data.list_users()
    categories = admin_data.list_categories()
    
    # Dashboard statistics
    pending_count = admin_data.get_pending_orders_count()
    low_stock_count = admin_data.get_low_stock_count(threshold=10)
    custom_count = admin_data.get_custom_requests_count()
    todays_sales = admin_data.get_todays_sales()
    
    # Reports data
    sales_summary = admin_data.get_sales_summary()
    inventory_value = admin_data.get_inventory_value()

    context = {
        "inventory": inventory,
        "orders": orders,
        "products": products,
        "users": users,
        "categories": categories,
        "pending_count": pending_count,
        "low_stock_count": low_stock_count,
        "custom_count": custom_count,
        "todays_sales": todays_sales,
        "sales_summary": sales_summary,
        "inventory_value": inventory_value,
        "user_role": user_role,
        "user_id": user_id,
        "username": request.session.get("username", ""),
    }
    return render(request, "iffat/admin_ui.html", context)


@admin_staff_required
@require_POST
def admin_update_order_status(request):
    """
    Update order status from the Orders tab.
    """
    order_id = request.POST.get("order_id")
    status = request.POST.get("status")
    staff_id = request.session.get("user_id")
    
    if order_id and status:
        admin_data.update_order_status(order_id, status)
        # Optionally assign staff to order
        if staff_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE Orders SET staff_id = %s WHERE order_id = %s",
                    [staff_id, order_id]
                )
                connection.commit()
    
    return redirect("admin_dashboard")


@admin_staff_required
@require_POST
def admin_save_product(request):
    """
    Create or update a product from the Products modal.
    Only admin can create/update products.
    """
    user_role = request.session.get("role", "").lower()
    if user_role != "admin":
        return redirect("admin_dashboard")
    
    item_id = request.POST.get("item_id") or None
    if item_id:
        try:
            item_id = int(item_id)
        except ValueError:
            item_id = None

    name = request.POST.get("name") or ""
    price = request.POST.get("price") or "0"
    stock = request.POST.get("stock") or "0"
    short_desc = request.POST.get("short_desc") or ""
    full_desc = request.POST.get("full_desc") or ""
    image_url = request.POST.get("image") or ""
    category = request.POST.get("category") or ""

    try:
        price_val = float(price)
    except ValueError:
        price_val = 0.0
    try:
        stock_val = int(stock)
    except ValueError:
        stock_val = 0

    item_id = admin_data.save_product(
        item_id=item_id,
        name=name,
        price=price_val,
        stock=stock_val,
        short_desc=short_desc,
        full_desc=full_desc,
        image_url=image_url,
    )
    
    # Assign to category if provided
    if category and item_id:
        admin_data.assign_product_to_category(item_id, category)
    
    return redirect("admin_dashboard")


@admin_staff_required
@require_POST
def admin_delete_product(request, item_id):
    """
    Delete a product from the Products table.
    Only admin can delete products.
    """
    user_role = request.session.get("role", "").lower()
    if user_role != "admin":
        return redirect("admin_dashboard")
    
    admin_data.delete_product(item_id)
    return redirect("admin_dashboard")


@admin_staff_required
@require_POST
def admin_save_user(request):
    """
    Update basic user details (name, email, role, phone) from the
    Users modal form. Only admin can change roles.
    """
    user_role = request.session.get("role", "").lower()
    user_id = request.POST.get("user_id")
    name = request.POST.get("name") or ""
    email = request.POST.get("email") or ""
    role = request.POST.get("role") or "customer"
    phone = request.POST.get("phone") or None

    # Only admin can change roles
    if user_role != "admin":
        role = None  # Don't update role if not admin

    if user_id:
        try:
            user_id_int = int(user_id)
        except ValueError:
            user_id_int = None
        if user_id_int is not None:
            if role:
                admin_data.update_user(
                    user_id=user_id_int,
                    name=name,
                    email=email,
                    role=role,
                    phone=phone,
                )
            else:
                # Update without role change
                admin_data.update_profile_sql(
                    user_id=user_id_int,
                    name=name,
                    email=email,
                    phone=phone,
                )

    return redirect("admin_dashboard")


@admin_staff_required
def get_user_details(request, user_id):
    """
    AJAX endpoint to get user details including order history.
    """
    user = admin_data.get_user_by_id(user_id)
    if not user:
        return JsonResponse({"error": "User not found"}, status=404)
    
    order_history = admin_data.get_user_order_history(user_id)
    order_stats = admin_data.get_user_order_stats(user_id)
    
    return JsonResponse({
        "user": user,
        "order_history": order_history,
        "order_stats": order_stats,
    })


@admin_staff_required
def admin_order_invoice(request, order_id):
    """
    Simple invoice view for an order.
    Shows order header and line items in a printable layout.
    """
    details = admin_data.get_order_details(order_id)
    if not details:
        return redirect("admin_dashboard")

    # All rows share the same order header fields
    order = details[0]

    # Line items are the full list
    items = details

    return render(
        request,
        "iffat/order_invoice.html",
        {
            "order": order,
            "items": items,
        },
    )


@admin_staff_required
def get_product_image_view(request, item_id):
    """
    Serve product image as HTTP response.
    Reads BLOB from database and returns it with appropriate content-type.
    """
    image_blob = admin_data.get_product_image(item_id)
    
    if not image_blob:
        # Return a placeholder or 404
        return HttpResponse(status=404)
    
    # Try to detect image type from BLOB header
    content_type = 'image/jpeg'  # default
    if image_blob.startswith(b'\x89PNG'):
        content_type = 'image/png'
    elif image_blob.startswith(b'GIF'):
        content_type = 'image/gif'
    elif image_blob.startswith(b'\xff\xd8'):
        content_type = 'image/jpeg'
    elif image_blob.startswith(b'RIFF') and b'WEBP' in image_blob[:12]:
        content_type = 'image/webp'
    
    response = HttpResponse(image_blob, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=3600'
    return response

