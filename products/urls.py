
# ──────────────────────────────────────────────────────────────────────────────

from django.urls import path
from products import views

 

urlpatterns = [
 
############################## Products  Urls Section Starts Here ###############################################
   
    path('api/brand/save/',                     views.save_brand,                   name='save_brand'),            # NEW
    path('api/brand/delete/<int:brand_id>/',    views.delete_brand,                 name='delete_brand'),          # NEW
    path('api/product/save/',                   views.save_product,                 name='save_product'),          # NEW
    path('api/product/delete/<int:product_id>/',views.delete_product,               name='delete_product'),        # NEW
    path('api/product-filter/save/',            views.save_product_filter_settings, name='save_product_filter'),   # NEW

 
    path('api/brands/load/',                    views.load_brands,                  name='load_brands'),           # NEW
    
    
############################## Products  Urls Section Ends Here ###############################################
    
]
