from django.shortcuts import render
from django.http import HttpResponse
from .database.data import *

# Create your views here.

def index(request):
    return render(request, "webPages/FrontEnd_ClientView/index.html")





def about(request, complain = ''):
    if complain != '':
        result = custom_sql_select(f'''
                                   
            SELECT * FROM Complaint
        
        ''')
        return HttpResponse(str(result))
    else:
        return render(request, "webPages/FrontEnd_ClientView/about.html")





def shop(request, current_page = 1, category = '', subcategory = ''):
    
    limit_on_single_page = 10
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



    total_pages = (len(result)//limit_on_single_page)+1
    pages = [i+1 for i in range(total_pages)]

    return render(request, "webPages/FrontEnd_ClientView/shopExtension/product.html", {
        "products": result,
        "pages": pages,
        "current_page": current_page
    })