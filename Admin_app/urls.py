from django.urls import path
from Admin_app import views

urlpatterns = [
    
    path('hero_section', views.hero_section, name='hero_section'),
    path('feature_section', views.feature_section, name='feature_section'),
    path('dashboard', views.dashboard, name='dashboard'),

    ############ urls for admin login #############################

    path('', views.Admin_Login, name='Admin_Login'),

    ############# urls for admin logout #########################

    path('Admin_Logout', views.Admin_Logout, name='Admin_Logout'),

    ############# urls for update admin profile #####################

    path('Admin_Profile', views.Admin_Profile, name='Admin_Profile'),

    ############## urls for ajax for update admin profile #####################

    path('Admin_Profile_Ajax', views.Admin_Profile_Ajax, name='Admin_Profile_Ajax'),

    ############### urls for offer banner section #####################

    path('Offer_Banner_Section', views.Offer_Banner_Section, name='Offer_Banner_Section'),

    ####### urls for ajax for save offer banner ########################

    path('Save_Offer_Ajax', views.Save_Offer_Ajax, name='Save_Offer_Ajax'),

    ########## urls for brands section ##############################

    path('Brand_Section', views.Brand_Section, name='Brand_Section'),

    ############# urls for ajax for save brands ########################

    path('Save_Brand_Ajax', views.Save_Brand_Ajax, name='Save_Brand_Ajax'),

    ########### urls for reviews section #########################

    path('Review_Section', views.Review_Section, name='Review_Section'),

    ######### urls for ajax for save reviews #########################

    path('Save_Review_Ajax', views.Save_Review_Ajax, name='Save_Review_Ajax'),

    ############# urls for newsletter section #########################

    path('Newsletter_Section', views.Newsletter_Section, name='Newsletter_Section'),

    ############ urls for ajax for save newsletter #####################

    path('Save_Newsletter_Ajax', views.Save_Newsletter_Ajax, name='Save_Newsletter_Ajax'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('category_section',   views.category_section, name='category_section'),
    
    ########################## ProductsURLS Section Starts Here ###############################################
    path('product_builder', views.product_builder, name='product_builder'), # ← NEW
    
    path('brand-builder/',          views.brand_builder,                name='brand_builder'),         # NEW
    #path('product_builder/', views.product_builder, name='product_builder'),      # NEW
    path('product-filter/',         views.product_filter_builder,       name='product_filter_builder'),# NEW
    
    
########################## Products URLS Section Ends Here ###############################################
        
#################################### Stocks URLS Section Starts Here ###############################################
    
    path('stock_manager/',                    views.stock_manager,     name='stock_manager'),
    path('stock/update/<int:product_id>/', views.stock_update, name='stock_update'),
    path('stock/bulk-update/',         views.stock_bulk_update, name='stock_bulk_update'),
    
#################################### Stocks URLS Section Ends Here ###############################################
    
   
#################################### Deals & Offers URLS Section Start Here ###############################################

    path('admin/deals/ticker/', views.admin_ticker_view, name='ticker'),
    path('admin/api/deals/ticker/save/', views.save_ticker_api, name='save_ticker_api'),
# ↑ This must NOT be caught by django's built-in admin before reaching your view
    
   

  
  

    # ── admin builder ──
    path('admin/deals/todays-offers/',
         views.todays_offer_admin,
         name='todays_offer_admin'),

    # ── admin APIs ──
    path('admin/api/todays-offers/add/',
         views.todays_offer_add,
         name='todays_offer_add'),

    path('admin/api/todays-offers/edit/<int:offer_id>/',
         views.todays_offer_edit,
         name='todays_offer_edit'),

    path('admin/api/todays-offers/delete/<int:offer_id>/',
         views.todays_offer_delete,
         name='todays_offer_delete'),

    path('admin/api/todays-offers/toggle/<int:offer_id>/',
         views.todays_offer_toggle,
         name='todays_offer_toggle'),

    path('admin/api/todays-offers/reorder/',
         views.todays_offer_reorder,
         name='todays_offer_reorder'),
    
    
    path('admin/coupon-wall/', views.coupon_wall_admin, name='coupon_wall'),
    path('admin/coupon-wall/add/', views.coupon_add_ajax, name='coupon_add_ajax'),
  
    path('admin/deal-of-the-day/',       views.deal_of_the_day_admin, name='deal_of_the_day_admin'),
    path('admin/deal-of-the-day/save/',  views.dotd_save_ajax,        name='dotd_save_ajax'),
    
    
#################################### Deals & Offers URLS Section End Here ###############################################
]




   
