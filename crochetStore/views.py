from django.shortcuts import render
from django.http import HttpResponse
from .database.data import *
import base64
from django.shortcuts import redirect
from django.contrib import messages

# Create your views here.


class User:
    def __init__(self):
        self.is_authenticated = False
        self.username = ""
        self.userID = 0
        self.email = ""
        self.phone = ""
        self.role = ""
        self.createdat = ""

user = User()

def defualtSettings(request):
    if 'login_status' not in request.session:
            request.session['login_status'] = False
            request.session['user_id'] = 0
            request.session['username'] = ""
            request.session['email'] = ""
            request.session['phone'] = ""
            request.session['role'] = ""
            request.session['createdat'] = ""
    
    user.is_authenticated = request.session['login_status'] 
    user.userID = request.session['user_id']
    user.username = request.session['username']
    user.email = request.session['email']
    user.phone = request.session['phone']
    user.role = request.session['role']
    user.createdat = request.session['createdat']


def index(request):

    defualtSettings(request)

    return render(request, "webPages/FrontEnd_ClientView/index.html", {
        "user": user
    })





def about(request, complain = ''):


    defualtSettings(request)


    if complain != '':
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Complaint
        
        ''')
        return HttpResponse(str(result))
    else:
        return render(request, "webPages/FrontEnd_ClientView/about.html", {
            "user": user
        })





def shop(request, current_page = 1, category = '', subcategory = ''):


    defualtSettings(request)
    
    limit_on_single_page = 12
    result = []

    
    if category != '' and subcategory != '':
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Items 
            WHERE item_id IN (
                SELECT item_id FROM SubCategory
                WHERE cat_id IN (
                    SELECT cat_id FROM Category
                    WHERE categoryName = '{category}'
                ) AND subCatName = '{subcategory}'
            )
        
        ''')
    elif category != '':
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Items 
            WHERE item_id IN (
                SELECT item_id FROM SubCategory
                WHERE cat_id IN (
                    SELECT cat_id FROM Category
                    WHERE categoryName = '{category}'
                ) 
            )
        
        ''')
    elif subcategory != '':
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Items 
            WHERE item_id IN (
                SELECT item_id FROM SubCategory
                WHERE subCatName = '{subcategory}'
            )
        
        ''')
    else:
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Items 
                                   
        ''')


    for item in result:
        if item.get("image"):
            item["image_base64"] = base64.b64encode(item["image"]).decode("utf-8")
        else:
            item["image_base64"] = None

    total_pages = (len(result)//limit_on_single_page)+1
    pages = [i+1 for i in range(total_pages)]

    resultSected = result[(current_page-1)*limit_on_single_page : current_page*limit_on_single_page]

    return render(request, "webPages/FrontEnd_ClientView/shopExtension/product.html", {
        "products": resultSected,
        "pages": pages,
        "user": user,
        "current_page": current_page
    })


def login(request):

    defualtSettings(request)

    return render(request, "webPages/FrontEnd_ClientView/login-register.html", {
        "user": user
    })

def myaccount(request):


   
    if request.method == "POST":
        if "login_submit" in request.POST:
            print("Login form submitted")
            print(request.POST.dict())

            email = request.POST.get("login_email")
            password = request.POST.get("login_password")

            login_data = login_sql_select(email, password)

            if login_data and isinstance(login_data, dict):
                request.session['login_status'] = True  # always set this if login_data exists

                if "user_id" in login_data:
                    request.session['user_id'] = login_data["user_id"]

                if "name" in login_data:
                    request.session['username'] = login_data["name"]

                if "email" in login_data:
                    request.session['email'] = login_data["email"]

                if "phone" in login_data:
                    request.session['phone'] = login_data["phone"]

                if "role" in login_data:
                    request.session['role'] = login_data["role"]

                if "createdat" in login_data:
                    request.session['createdat'] = str(login_data["createdat"])

            else:
                return HttpResponse("Not found in DATABASE")

        elif "register_submit" in request.POST:
            print("Register form submitted")
            print(request.POST.dict())

            name = request.POST.get("reg_name")
            email = request.POST.get("reg_email")
            password = request.POST.get("reg_password")
            confirm_password = request.POST.get("reg_confirm_password")

            if password != confirm_password:
                return HttpResponse("Password and Confirm Password do not match.")

            register_sql_insert(name, email, password)

            login_data = login_sql_select(email, password)

            if login_data and isinstance(login_data, dict):
                request.session['login_status'] = True  # always set this if login_data exists

                if "user_id" in login_data:
                    request.session['user_id'] = login_data["user_id"]

                if "name" in login_data:
                    request.session['username'] = login_data["name"]

                if "email" in login_data:
                    request.session['email'] = login_data["email"]

                if "phone" in login_data:
                    request.session['phone'] = login_data["phone"]

                if "role" in login_data:
                    request.session['role'] = login_data["role"]

                if "createdat" in login_data:
                    request.session['createdat'] = str(login_data["createdat"])

            else:
                return HttpResponse("Not found in DATABASE")

    

    defualtSettings(request)
    context = {
        "user": user
    }

    return render(request, "webPages/FrontEnd_ClientView/my-account.html", context)


def logout_view(request):
    request.session.flush()  # clears all session data
    return redirect('index')  # redirect to home or login page

def update_profile(request):
    if request.method == "POST":
        user_id = request.session.get("user_id")
        if not user_id:
            messages.error(request, "You must be logged in to update your profile.")
            return redirect("myaccount")

        name = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        updated = update_profile_sql(user_id, name=name, email=email, phone=phone)

        if updated:
            # Update session data to reflect new profile
            if name: request.session["username"] = name
            if email: request.session["email"] = email
            if phone: request.session["phone"] = phone

            messages.success(request, "Profile updated successfully.")
        else:
            messages.info(request, "No changes were made to your profile.")

        return redirect("myaccount")

    # If GET request, just redirect to account page
    return redirect("myaccount")