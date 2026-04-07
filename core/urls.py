from django.urls import path
from core import views

urlpatterns = [
    path('', views.index, name='index'),
    
   # path('products', views.products, name='products'),
   
 
    
    path('login/', views.login, name='login'),

    ############# urls for complete profile ####################

    path('complete-profile/', views.complete_profile, name='complete_profile'),

    ################ urls for update user profile #############################

    path('User_Profile', views.User_Profile, name='User_Profile'),


    ############# urls for user logout ###########################

    path('User_Logout', views.User_Logout, name='User_Logout'),

    ############ urls for ajax for register user #############################

    path('Users_Ajax', views.Users_Ajax, name='Users_Ajax'),
    
 
    path('contact', views.contact, name='contact'),
    
    ########################## Products URLS Section Starts Here ###############################################

    #path('product_details', views.product_details, name='product_details'),
    path('products/<slug:slug>/', views.product_details, name='product_details'),
    
    path('payments', views.checkout, name='checkout'),
    

    
    path('All_products', views.All_products, name='All_products'),
    

    
    path('cart', views.cart, name='cart'),
    
      ##########################  Products Urls Section Ends Here ###############################################

########################## Wesbite Page Sections URLS Section Starts Here ###############################################
    
    path('api/hero/load/',                  views.load_hero,        name='load_hero'),
    path('api/category/load/',              views.load_category,    name='load_category'), 
    
    path('api/hero/save/',                  views.save_hero,        name='save_hero'),
    path('api/features/save/',              views.save_features,    name='save_features'),
    path('api/category/save/',              views.save_category,    name='save_category'),  
    
    
    ########################## Wesbite Page Sections URLS Section ENDS Here ###############################################
]