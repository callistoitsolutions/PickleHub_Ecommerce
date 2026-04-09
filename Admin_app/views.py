import json
from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET


from django.db import transaction
from Admin_app.models import *
from django.views.decorators.csrf import csrf_exempt

import traceback

from Admin_app.models import *
from products.models import *

from django.shortcuts import render, get_object_or_404


from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from django.core.serializers.json import DjangoJSONEncoder


from products.product_utils  import _product_page_data

from django.utils.dateparse import parse_datetime
from django.utils import timezone





def dashboard(request):

    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        """
        Admin dashboard page.
        Passes hero_json and features_json as JS-injectable strings.
        """
        hero     = HeroSection.get_or_create_default()
        features = FeaturesSection.get_or_create_default()
        category = CategorySection.get_or_create_default() 

        hero_data = {
            'badge_text':        hero.badge_text,
            'title_line1':       hero.title_line1,
            'title_highlight':   hero.title_highlight,
            'title_line2':       hero.title_line2,
            'subtitle':          hero.subtitle,
            'jar_emoji':         hero.jar_emoji,
            'hero_image_url':    hero.hero_image_url,
            'buttons_json':      hero.buttons_json,
            'stats_json':        hero.stats_json,
            'float_badges_json': hero.float_badges_json,
            'is_visible':        hero.is_visible,
        }

        features_data = {
            'items_json': features.items_json,
            'is_visible': features.is_visible,
        }

        return render(request, 'Admin_pages/dashboard.html', {
        'hero_json':     json.dumps(_hero_data(hero)),
        'features_json': json.dumps(_features_data(features)),
        'category_json': json.dumps(_category_data(category)),
        'admin_obj':admin_obj,  # ← NEW
        })
    else:
        return render(request,'Admin_pages/admin_login.html')

    

# ──────────────────────────────────────────────
# 2. ADMIN HOME PAGE
# ──────────────────────────────────────────────


############## Views start for admin login #####################

@csrf_exempt
def Admin_Login(request):
    session_id = request.session.get('Admin_id')
    user_type = request.session.get('user_type')
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            admin_email = data['admin_email']
            admin_password = data['admin_password']

            if AdminDetails.objects.filter(admin_email=admin_email, admin_password=admin_password):

                obj = AdminDetails.objects.get(admin_email=admin_email, admin_password=admin_password)
                
                request.session['Admin_id'] = str(obj.id)
                request.session['user_type'] = str('Admin')

                send_data = {'status':1,'msg':'Login Successful...'}
            else:
                send_data = {'status':0,'msg':'Invalid Credentials'}
        except:
            print(traceback.format_exc())
            send_data = {'status':0 , 'msg':'Something went wrong','error':traceback.format_exc()}
        return JsonResponse(send_data)
    else:
        if session_id and user_type == "Admin":
            return redirect('dashboard')
        else:
            return render(request,'Admin_pages/admin_login.html')

########## Views end for admin login ########################


######### Views start for admin logout #############################

@csrf_exempt
def Admin_Logout(request):
    try:
        del request.session['Admin_id']
        del request.session['user_type']
        return JsonResponse({"status":"1",'msg': 'Logout Successfully '})
    except:
        print(traceback.format_exc())

########## Views end for admin logout ###############################


############ Views start for update admin profile ######################

def Admin_Profile(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        context = {'admin_obj':admin_obj}
        return render(request,'Admin_pages/Profile/admin_profile.html',context)
    else:
        return render(request,'Admin_pages/admin_login.html')
    

############## Views end for update admin profile ############################


########## Views start for ajax for update admin profile ########################

@csrf_exempt
def Admin_Profile_Ajax(request):
    data=request.POST.dict()
    try:
        AdminDetails.objects.get(id=data['id'])
        AdminDetails.objects.filter(id=data['id']).update(**data)
        return JsonResponse({"status":"1", "msg" : f"Admin Profile updated successfully"})
    except:
        traceback.print_exc()
        return JsonResponse({"status":"0", "msg" : "Something went wrong..."})

############## Views end for ajax for update admin profile #######################



############### Views start for offer banner section ######################

def Offer_Banner_Section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        active_banners = OfferBanner.objects.filter(is_active=True).order_by('order', '-created_at')

        # 1. Create the standard Python list
        banners_list = [banner.to_dict() for banner in active_banners]

        # 2. DO NOT use json.dumps(banners_list) here! 
        # Just pass the raw Python list directly into the context.
        context = {
            'offers_list': banners_list,
            'admin_obj':admin_obj,
        }

        return render(request,'Admin_pages/Offer_Banner/offer_banner.html',context)
    else:
        return render(request,'Admin_pages/admin_login.html')

######### Views end for offer banner section ##################################


############ Views start for ajax for save offer banner ########################

@csrf_exempt
def Save_Offer_Ajax(request):
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            
            # 1. Get the IDs of the banners that are STILL on the screen
            incoming_ids = [offer.get('id') for offer in data if offer.get('id')]
            
            # 2. TARGETED DELETE: Delete ONLY the rows in the database that are missing from the screen
            OfferBanner.objects.exclude(id__in=incoming_ids).delete()
            
            # 3. Update existing banners or create brand new ones
            for index, offer in enumerate(data):
                offer_id = offer.get('id')
                
                # Set up the base fields every banner shares
                defaults = {
                    'name': offer.get('name', ''),
                    'price': offer.get('price', 0) or 0,
                    'old_price': offer.get('oldPrice') or None,
                    'url': offer.get('url', ''),
                    'order': index, # Saves the exact sequence
                    'is_active': True
                }
                
                # Add the specific fields depending on the banner type
                if offer.get('type') == 'main':
                    defaults.update({
                        'offer_type': 'main',
                        'badge': offer.get('badge', ''),
                        'description': offer.get('desc', ''),
                        'discount_label': offer.get('discount', ''),
                    })
                else:
                    defaults.update({
                        'offer_type': 'potw',
                        'emoji': offer.get('emoji', '🧄'),
                        'weight_type': offer.get('weight', ''),
                    })
                
                # If the banner has an ID, it already exists -> UPDATE IT
                if offer_id:
                    OfferBanner.objects.filter(id=offer_id).update(**defaults)
                
                # If it doesn't have an ID, it was just added -> CREATE IT
                else:
                    OfferBanner.objects.create(**defaults)
            
        return JsonResponse({"status": "success", "message": "Banners synced perfectly!"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

########### Views end for ajax for save offer banner ############################


########### Views start for brand section ############################

def Brand_Section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        active_brands = Brand.objects.filter(is_active=True).order_by('order')
        brands_list = [brand.to_dict() for brand in active_brands]

        # 2. DO NOT use json.dumps(banners_list) here! 
        # Just pass the raw Python list directly into the context.
        context = {
            'brands_list': brands_list, 
            'admin_obj':admin_obj
        }

        return render(request,'Admin_pages/Brand/brand.html',context)
    else:
        return render(request,'Admin_pages/admin_login.html')


############# Views end for brand section ##############################


########### Views start for ajax for save brands ########################

@csrf_exempt
def Save_Brand_Ajax(request):
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            # 1. Get IDs of kept brands
            incoming_ids = [brand.get('id') for brand in data if brand.get('id')]
            
            # 2. Delete removed brands
            Brand.objects.exclude(id__in=incoming_ids).delete()
            
            # 3. Update or Create
            for index, brand in enumerate(data):
                brand_id = brand.get('id')
                defaults = {
                    'emoji': brand.get('emoji', ''),
                    'name': brand.get('name', ''),
                    'url': brand.get('url', ''),
                    'order': index,
                    'is_active': True
                }
                
                if brand_id:
                    Brand.objects.filter(id=brand_id).update(**defaults)
                else:
                    Brand.objects.create(**defaults)
            
        return JsonResponse({"status": "success", "message": "Brands synced!"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

############# Views end for ajax for save brands ########################


############## Views start for review section #######################

def Review_Section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        active_reviews = Review.objects.filter(is_active=True).order_by('order')
        reviews_list = [review.to_dict() for review in active_reviews]

        # # 2. DO NOT use json.dumps(banners_list) here! 
        # # Just pass the raw Python list directly into the context.
        context = {
            'reviews_list': reviews_list, 
            'admin_obj':admin_obj,
        }

        return render(request,'Admin_pages/Review/review.html',context)
    else:
        return render(request,'Admin_pages/admin_login.html')

########### Views end for review section ###########################


############## Views start for ajax for save reviews #######################

@csrf_exempt
def Save_Review_Ajax(request):
    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # 1. Get IDs of kept reviews
            incoming_ids = [review.get('id') for review in data if review.get('id')]
            
            # 2. Delete removed reviews (Targeted Delete)
            Review.objects.exclude(id__in=incoming_ids).delete()
            
            # 3. Update or Create existing reviews
            for index, review in enumerate(data):
                review_id = review.get('id')
                defaults = {
                    'avatar': review.get('avatar', '👤'),
                    'name': review.get('name', ''),
                    'city': review.get('city', ''),
                    'rating': int(review.get('rating', 5)), # Ensure this is an integer!
                    'text': review.get('text', ''),
                    'order': index,
                    'is_active': True
                }
                
                if review_id:
                    Review.objects.filter(id=review_id).update(**defaults)
                else:
                    Review.objects.create(**defaults)
                    
        return JsonResponse({"status": "success", "message": "Reviews synced!"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

############# Views end for ajax for save reviews #########################


############# Views start for newsletter section ############################

def Newsletter_Section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        admin_obj = AdminDetails.objects.get(id=session_id)

        newsletter = NewsletterSetting.objects.first()

        context={
            'newsletter':newsletter,
            'admin_obj':admin_obj,
        }

        return render(request,'Admin_pages/Newsletter/newsletter.html',context)
    else:
        return render(request,'Admin_pages/admin_login.html')

############### Views end for newsletter section #############################


########### Views start for ajax for save newsletter #######################

@csrf_exempt
def Save_Newsletter_Ajax(request):
    try:
        data = json.loads(request.body)
        
        # Grab the one row, update it, and save it
        settings, created = NewsletterSetting.objects.get_or_create(id=1)
        
        settings.heading = data.get('heading', '')
        settings.description = data.get('desc', '')
        settings.placeholder = data.get('placeholder', '')
        settings.btn_text = data.get('btnText', '')
        settings.privacy_note = data.get('privacy', '')
        settings.url = data.get('url', '')
        settings.save()
        
        # 👇 THIS is what JavaScript is looking for!
        return JsonResponse({"status": "success", "message": "Newsletter saved!"})
        
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

########### Views end for ajax for save newsletter ############################


#################################### Website Page Sections Views Start Here ###############################################

def hero_section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        """
        Dedicated admin builder page for the Hero Section.
        """
        admin_obj = AdminDetails.objects.get(id=session_id)

        hero     = HeroSection.get_or_create_default()
        features = FeaturesSection.get_or_create_default()
        category = CategorySection.get_or_create_default()          # ← NEW
    
        return render(request, 'Admin_pages/hero_section.html', {
            'hero_json':     json.dumps(_hero_data(hero)),
            'features_json': json.dumps(_features_data(features)),
            'category_json': json.dumps(_category_data(category)),
            'admin_obj':admin_obj,  # ← NEW
        })
    else:
        return render(request,'Admin_pages/admin_login.html')



def feature_section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        """
        Dedicated admin builder page for the Features Strip.
        """
        admin_obj = AdminDetails.objects.get(id=session_id)

        hero     = HeroSection.get_or_create_default()
        features = FeaturesSection.get_or_create_default()
        category = CategorySection.get_or_create_default()          # ← NEW
    
        return render(request, 'Admin_pages/feature_section.html', {
            'hero_json':     json.dumps(_hero_data(hero)),
            'features_json': json.dumps(_features_data(features)),
            'category_json': json.dumps(_category_data(category)),
            'admin_obj':admin_obj  # ← NEW
        })
    else:
        return render(request,'Admin_pages/admin_login.html')
    
    
def category_section(request):
    session_id = request.session.get('Admin_id')
    if session_id:
        """
        Dedicated admin builder page for the Category Section.
        Only passes category_json — this page only edits categories.
        """

        admin_obj = AdminDetails.objects.get(id=session_id)

        category = CategorySection.get_or_create_default()
    
        return render(request, 'Admin_pages/category_section.html', {
            'category_json': json.dumps(_category_data(category)),
            'admin_obj':admin_obj
        })
    else:
        return render(request,'Admin_pages/admin_login.html')



def _hero_data(hero):
    return {
        'badge_text':        hero.badge_text,
        'title_line1':       hero.title_line1,
        'title_highlight':   hero.title_highlight,
        'title_line2':       hero.title_line2,
        'subtitle':          hero.subtitle,
        'jar_emoji':         hero.jar_emoji,
        'hero_image_url':    hero.hero_image_url,
        'buttons_json':      hero.buttons_json,
        'stats_json':        hero.stats_json,
        'float_badges_json': hero.float_badges_json,
        'is_visible':        hero.is_visible,
    }
 
def _features_data(features):
    return {
        'items_json': features.items_json,
        'is_visible': features.is_visible,
    }
 
def _category_data(category):                        # ← NEW helper
    return {
        'section_title':    category.section_title,
        'section_subtitle': category.section_subtitle,
        'items_json':       category.items_json,
        'is_visible':       category.is_visible,
    }
 
 
 
 #################################### Website Page Sections Views Ends Here ###############################################

#################################### Products Views Start Here ###############################################


def product_builder(request):
    products   = Product.objects.all().select_related('brand', 'category').order_by('sort_order', '-created_at')
    brands     = Brand.objects.filter(is_active=True).order_by('order', 'name')
    categories = CategorySection.get_or_create_default()
    coupons    = Coupon.objects.filter(is_active=True)

    # ✅ PRODUCTS
    products_data = [
        {
            'id':               p.id,
            'emoji':            p.emoji,
            'image_url':        p.image.url if p.image else '',
            'name':             p.name,
            'slug':             p.slug,
            'brand_id':         p.brand_id,
            'brand_name':       p.brand.name if p.brand else '',
            'category_id':      p.category_id,
            'weight':           p.weight,
            'oil_type':         p.oil_type,
            'region':           p.region,
            'badge':            p.badge,
            'badge_color':      p.badge_color,
            'card_bg':          p.card_bg,
            'price':            p.price,
            'old_price':        p.old_price,
            'discount':         p.discount,
            'stock':            p.stock,
            'low_stock_label':  p.low_stock_label,
            'rating':           str(p.rating),
            'review_count':     p.review_count,
            'whatsapp_number':  p.whatsapp_number,
            'is_active':        p.is_active,
            'is_featured':      p.is_featured,
            'sort_order':       p.sort_order,

            # extra fields
            'short_description': p.short_description,
            'long_description':  p.long_description,
            'highlights':        p.highlights,
            'sku':               p.sku,
            'hsn_code':          p.hsn_code,
            'unit_type':         p.unit_type,
            'cost_price':        p.cost_price,
            'gst_rate':          p.gst_rate,
            'gst_inclusive':     p.gst_inclusive,
            'free_delivery':     p.free_delivery,
            'shelf_life':        p.shelf_life,
            'storage_info':      p.storage_info,
            'min_order_qty':     p.min_order_qty,
            'max_order_qty':     p.max_order_qty,
            'seo_title':         p.seo_title,
            'seo_description':   p.seo_description,
            'seo_keywords':      p.seo_keywords,
            'tags':              p.tags,

            'assigned_coupon_ids': list(
                p.assigned_coupons.values_list('id', flat=True)
            ),
        }
        for p in products
    ]

    # ✅ BRANDS
    brands_data = [
        {'id': b.id, 'name': b.name, 'emoji': b.emoji}
        for b in brands
    ]

    # ✅ CATEGORIES
    categories_data = categories.items_json

    # ✅ COUPONS (💯 ERROR-FREE VERSION)
    coupons_data = []
    for c in coupons:
        # safe discount display
        discount_text = ''

        if hasattr(c, 'discount_value'):
            discount_text = f"{c.discount_value} OFF"
        elif hasattr(c, 'amount'):
            discount_text = f"₹{c.amount} OFF"
        elif hasattr(c, 'value'):
            discount_text = f"{c.value} OFF"
        else:
            discount_text = 'Offer'

        coupons_data.append({
            'id': c.id,
            'code': getattr(c, 'code', ''),
            'type': discount_text,
            'expiry': c.expiry_date.strftime('%d/%m/%Y') if getattr(c, 'expiry_date', None) else '—',
        })

    return render(request, 'products_panel/product_builder.html', {
        'products_json':   json.dumps(products_data),
        'brands_json':     json.dumps(brands_data),
        'categories_json': json.dumps(categories_data),
        'coupons_json':    json.dumps(coupons_data),
    })


def brand_builder(request):
    """
    Admin page to add / edit / delete brands.
    Brands are used in: filter sidebar + home page brand strip.
    """
    brands = Brand.objects.all().order_by('sort_order', 'name')
    brands_data = [
        {
            'id':            b.id,
            'emoji':         b.emoji,
            'name':          b.name,
            'slug':          b.slug,
            'url':           b.url,
            'product_count': b.product_count,
            'is_active':     b.is_active,
            'sort_order':    b.sort_order,
        }
        for b in brands
    ]
    return render(request, 'products_panel/brand_builder.html', {
        'brands_json': json.dumps(brands_data),
    })
    
    
    
def product_filter_builder(request):
    """
    Admin page to configure the filter sidebar on the public products page.
    Controls which filters show, price range, region list, weight list.
    """
    settings   = ProductPageSettings.get_or_create_default()
    categories = CategorySection.get_or_create_default()
    brands = Brand.objects.filter(is_active=True).order_by('order', 'name')

    return render(request, 'products_panel/product_filter_builder.html', {
        'settings_json':   json.dumps(_product_page_data(settings)),
        'categories_json': json.dumps({
            'section_title':    categories.section_title,
            'section_subtitle': categories.section_subtitle,
            'items_json':       categories.items_json,
            'is_visible':       categories.is_visible,
        }),
        'brands_json': json.dumps([
            {'id': b.id, 'emoji': b.emoji, 'name': b.name, 'product_count': b.product_count}
            for b in brands
        ]),
    })
    
    
    
    #################################### Prouducts Views Ends Here ###############################################


#################################### Stock  Views Start Here ###############################################


def stock_manager(request):
    """
    Main stock management dashboard — shows all products with stock controls.
    """
    search   = request.GET.get('q', '').strip()
    brand_id = request.GET.get('brand', '')
    cat_id   = request.GET.get('cat', '')
    status   = request.GET.get('status', '')   # in_stock | low_stock | out_of_stock

    qs = Product.objects.select_related('brand', 'category').filter()

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(brand__name__icontains=search))
    if brand_id:
        qs = qs.filter(brand__id=brand_id)
    if cat_id:
        qs = qs.filter(category__id=cat_id)
    if status == 'out_of_stock':
        qs = qs.filter(Q(stock=0) | Q(is_out_of_stock_manual=True))
    elif status == 'low_stock':
        qs = qs.filter(stock__gt=0, stock__lte=20, is_out_of_stock_manual=False)
    elif status == 'in_stock':
        qs = qs.filter(stock__gt=20, is_out_of_stock_manual=False)

    # summary counts
    all_products = Product.objects.all()
    summary = {
        'total':         all_products.count(),
        'in_stock':      all_products.filter(stock__gt=20, is_out_of_stock_manual=False).count(),
        'low_stock':     all_products.filter(stock__gt=0, stock__lte=20, is_out_of_stock_manual=False).count(),
        'out_of_stock':  all_products.filter(Q(stock=0) | Q(is_out_of_stock_manual=True)).count(),
    }

    return render(request, 'Admin_pages/Stock/stock_manager.html', {
        'products':   qs.order_by('name'),
        'brands':     Brand.objects.filter(is_active=True),
        'categories': CategorySection.objects.all(),
        'summary':    summary,
        'search':     search,
        'sel_brand':  brand_id,
        'sel_cat':    cat_id,
        'sel_status': status,
    })



@require_POST
def stock_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    changed = []

    if 'stock' in data:
        new_stock = int(data['stock'])
        if new_stock < 0:
            return JsonResponse({'ok': False, 'error': 'Stock cannot be negative'}, status=400)
        product.stock = new_stock
        changed.append('stock')

    if 'is_out_of_stock_manual' in data:
        product.is_out_of_stock_manual = bool(data['is_out_of_stock_manual'])
        changed.append('is_out_of_stock_manual')

    if changed:
        product.save(update_fields=changed)   # ← fixed, no 'updated_at'

    return JsonResponse({
        'ok':                     True,
        'stock':                  product.stock,
        'is_out_of_stock_manual': product.is_out_of_stock_manual,
        'is_out_of_stock':        product.is_out_of_stock,
        'stock_status':           product.stock_status,
        'low_stock_text':         product.low_stock_text,
    })


@require_POST
def stock_bulk_update(request):
    """
    Bulk update — mark multiple products OOS or restock.
    Body JSON: { "ids": [1,2,3], "action": "mark_oos" | "mark_available" | "restock" , "qty": 100 }
    """
    try:
        data    = json.loads(request.body)
        ids     = data.get('ids', [])
        action  = data.get('action', '')
        qty     = int(data.get('qty', 100))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid data'}, status=400)

    products = Product.objects.filter(id__in=ids)

    if action == 'mark_oos':
        products.update(is_out_of_stock_manual=True)
    elif action == 'mark_available':
        products.update(is_out_of_stock_manual=False)
    elif action == 'restock':
        products.update(stock=qty, is_out_of_stock_manual=False)
    else:
        return JsonResponse({'ok': False, 'error': 'Unknown action'}, status=400)

    return JsonResponse({'ok': True, 'updated': products.count()})


####################################  Stock Views Ends Here ###############################################



##############Start View Section of Deals and offers ########################################################



def admin_ticker_view(request):
    tickers = TickerMessage.objects.all().order_by('order')
    ticker_list = [{'text': t.text, 'is_active': t.is_active} for t in tickers]
    
    return render(request, 'Admin_pages/Deal_Offer/ticker.html', {
        'ticker_json': json.dumps(ticker_list, cls=DjangoJSONEncoder)
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json


@require_POST
def save_ticker_api(request):
    try:
        data = json.loads(request.body)
        messages = data.get('messages', [])
        
        TickerMessage.objects.all().delete()
        for index, msg in enumerate(messages):
            if msg.get('text', '').strip():
                TickerMessage.objects.create(
                    text=msg.get('text').strip(),
                    is_active=msg.get('is_active', True),
                    order=index
                )
        return JsonResponse({'status': 'success', 'message': 'Ticker messages updated!'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    






def todays_offer_admin(request):
    offers = TodaysOffer.objects.select_related('product').all()
    products = Product.objects.filter(is_active=True)

    return render(request, 'Admin_pages/Deal_Offer/todays_offers.html', {
        'offers': offers,
        'products': products,   # ✅ ADD THIS
        'badge_choices': TodaysOffer.BADGE_CHOICES,
    })


@require_POST
def todays_offer_add(request):
    try:
        data = json.loads(request.body)

        product = Product.objects.get(id=data.get('product_id'))

        offer = TodaysOffer.objects.create(
            product      = product,
            badge        = data.get('badge', 'deal'),
            badge_label  = data.get('badge_label', 'DEAL').strip(),
            is_visible   = data.get('is_visible', True),
            order        = TodaysOffer.objects.count(),
        )

        return JsonResponse({
            'ok': True,
            'id': offer.id,
            'message': f'"{product.name}" offer added!'
        })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    
    

@require_POST
def todays_offer_edit(request, offer_id):
    try:
        offer = get_object_or_404(TodaysOffer, id=offer_id)
        data  = json.loads(request.body)

        product = Product.objects.get(id=data.get('product_id'))

        offer.product      = product
        offer.badge        = data.get('badge', offer.badge)
        offer.badge_label  = data.get('badge_label', offer.badge_label).strip()
        offer.is_visible   = data.get('is_visible', offer.is_visible)
        offer.save()

        return JsonResponse({'ok': True, 'message': f'"{product.name}" updated!'})

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
def todays_offer_delete(request, offer_id):
    try:
        offer = get_object_or_404(TodaysOffer, id=offer_id)
        name  = offer.product.name   # ✅ CHANGE
        offer.delete()
        return JsonResponse({'ok': True, 'message': f'"{name}" deleted!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@require_POST
def todays_offer_toggle(request, offer_id):
    try:
        offer = get_object_or_404(TodaysOffer, id=offer_id)
        offer.is_visible = not offer.is_visible
        offer.save()

        return JsonResponse({
            'ok': True,
            'is_visible': offer.is_visible,
            'message': f'"{offer.product.name}" is now {"visible" if offer.is_visible else "hidden"}!'
        })

    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

@require_POST
def todays_offer_reorder(request):
    try:
        data     = json.loads(request.body)
        id_order = data.get('order', [])  # list of IDs in new order
        for index, offer_id in enumerate(id_order):
            TodaysOffer.objects.filter(id=offer_id).update(order=index)
        return JsonResponse({'ok': True, 'message': 'Order saved!'})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)
    
    
    #################################### Deals & Offers Views Ends Here ###############################################
    
    
#####################Start Coupen Views Section #######################################################




def coupon_wall_admin(request):
    coupons = Coupon.objects.filter(show_on_wall=True).order_by('order', '-id')
    return render(request, 'Admin_pages/Deal_Offer/coupon_wall.html', {'coupon_wall': coupons})


def coupon_add_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    try:
        d = json.loads(request.body)

        coupon = Coupon.objects.create(
            code            = d['code'],
            name            = d['name'],
            description     = d.get('description', ''),
            coupon_type     = d.get('coupon_type', 'percent'),
            discount_value  = d.get('discount_value') or None,
            max_discount    = d.get('max_discount') or None,
            min_order_value = d.get('min_order_value') or 0,
            max_uses        = d.get('max_uses') or None,
            start_date      = d.get('start_date') or None,
            end_date        = d.get('end_date') or None,
            discount_val    = d.get('discount_val', ''),
            expiry_note     = d.get('expiry_note', ''),
            icon            = d.get('icon', '🎁'),
            color_bg        = d.get('color_bg', '#e4eeff'),
            order           = d.get('order', 0),
            is_active       = d.get('is_active', True),
            show_on_wall    = d.get('show_on_wall', True),
            show_on_strip   = d.get('show_on_strip', False),
            first_order_only= d.get('first_order_only', False),
            is_public       = d.get('is_public', True),
        )

        return JsonResponse({'success': True, 'coupon': {
            'code':         coupon.code,
            'discount_val': coupon.discount_val,
            'description':  coupon.description,
            'expiry_note':  coupon.expiry_note,
            'icon':         coupon.icon,
            'color_bg':     coupon.color_bg,
            'is_active':    coupon.is_active,
        }})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

#####################End Coupen Views Section #######################################################




def deal_of_the_day_admin(request):
    dotd     = DealOfTheDay.objects.select_related('product').first()
    products = Product.objects.filter(is_active=True).order_by('name')
    return render(request, 'Admin_pages/Deal_Offer/deal_of_day_admin.html', {
        'dotd':     dotd,
        'products': products,
    })


def dotd_save_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST only'})
    try:
        d          = json.loads(request.body)
        product    = Product.objects.get(id=d['product_id'])

        # Always update the single DOTD record (id=1), create if not exists
        dotd, _    = DealOfTheDay.objects.get_or_create(id=1)
        dotd.product      = product
        dotd.badge_text   = d.get('badge_text', '🔥 Deal of the Day')
        dotd.float_badge1 = d.get('float_badge1', '')
        dotd.float_badge2 = d.get('float_badge2', '')
        dotd.is_visible   = d.get('is_visible', True)

        if d.get('end_time'):
            dt = parse_datetime(d['end_time'])
            if dt and timezone.is_naive(dt):
                dt = timezone.make_aware(dt)
            dotd.end_time = dt

        dotd.save()
        return JsonResponse({'success': True})

    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Product not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
    
    

#####################Start Pincode Manager  Views Section #######################################################






def _get_admin(request):
    """Return the admin object stored in session (adapt as needed)."""
  # adjust import to your actual Admin model
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return None
    try:
        return AdminDetails.objects.get(id=admin_id)
    except Exception:
        return None



def pincode_manager(request):
    """
    Main page — lists all pincodes.
    GET  → render page
    """
    admin_obj = _get_admin(request)

    pincodes  = DeliveryPincode.objects.all()

    # live filter via query string
    q = request.GET.get('q', '').strip()
    if q:
        pincodes = pincodes.filter(
            Q(pincode__icontains=q) |
            Q(area_name__icontains=q) |
            Q(city__icontains=q)
        )

    status_filter = request.GET.get('status', '')   # 'active' | 'inactive'
    if status_filter == 'active':
        pincodes = pincodes.filter(is_active=True)
    elif status_filter == 'inactive':
        pincodes = pincodes.filter(is_active=False)

    stats = {
        'total':    DeliveryPincode.objects.count(),
        'active':   DeliveryPincode.objects.filter(is_active=True).count(),
        'inactive': DeliveryPincode.objects.filter(is_active=False).count(),
        'cod':      DeliveryPincode.objects.filter(cod_allowed=True).count(),
    }

    ctx = {
        'admin_obj': admin_obj,
        'pincodes':  pincodes,
        'stats':     stats,
        'q':         q,
        'status_filter': status_filter,
    }
    return render(request, 'Admin_Pages/Pincode/pincode_manager.html', ctx)


def pincode_add(request):
    """AJAX POST — add a new pincode."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    pincode      = request.POST.get('pincode', '').strip()
    area_name    = request.POST.get('area_name', '').strip()
    city         = request.POST.get('city', 'Nagpur').strip()
    state        = request.POST.get('state', 'Maharashtra').strip()
    cod_allowed  = request.POST.get('cod_allowed', 'true') == 'true'
    delivery_days = int(request.POST.get('delivery_days', 2))

    if not pincode or not area_name:
        return JsonResponse({'status': '0', 'msg': 'Pincode and Area Name are required.'})

    if DeliveryPincode.objects.filter(pincode=pincode).exists():
        return JsonResponse({'status': '0', 'msg': f'Pincode {pincode} already exists.'})

    obj = DeliveryPincode.objects.create(
        pincode=pincode,
        area_name=area_name,
        city=city,
        state=state,
        cod_allowed=cod_allowed,
        delivery_days=delivery_days,
        is_active=True,
    )
    return JsonResponse({'status': '1', 'msg': f'Pincode {pincode} added successfully!', 'id': obj.id})


def pincode_toggle(request, pk):
    """AJAX POST — toggle active/inactive."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    obj = get_object_or_404(DeliveryPincode, pk=pk)
    obj.is_active = not obj.is_active
    obj.save()
    state = 'Active' if obj.is_active else 'Inactive'
    return JsonResponse({'status': '1', 'msg': f'Pincode marked as {state}.', 'is_active': obj.is_active})


def pincode_delete(request, pk):
    """AJAX POST — soft delete (just marks inactive) or hard delete."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    obj = get_object_or_404(DeliveryPincode, pk=pk)
    pincode_val = obj.pincode
    obj.delete()
    return JsonResponse({'status': '1', 'msg': f'Pincode {pincode_val} deleted.'})


def pincode_edit(request, pk):
    """AJAX POST — edit an existing pincode."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    obj = get_object_or_404(DeliveryPincode, pk=pk)
    obj.area_name     = request.POST.get('area_name',    obj.area_name).strip()
    obj.city          = request.POST.get('city',         obj.city).strip()
    obj.state         = request.POST.get('state',        obj.state).strip()
    obj.cod_allowed   = request.POST.get('cod_allowed', 'true') == 'true'
    obj.delivery_days = int(request.POST.get('delivery_days', obj.delivery_days))
    obj.save()
    return JsonResponse({'status': '1', 'msg': 'Pincode updated successfully!'})



def demand_report(request):
    """
    Admin demand report page.
    GET → render with stats + list
    """
    admin_obj = _get_admin(request)

    demands = DemandReport.objects.all()

    # Filters
    dtype   = request.GET.get('type', '')
    dstatus = request.GET.get('status', '')
    q       = request.GET.get('q', '').strip()

    if dtype:
        demands = demands.filter(demand_type=dtype)
    if dstatus:
        demands = demands.filter(status=dstatus)
    if q:
        demands = demands.filter(
            Q(product_name__icontains=q) |
            Q(requested_pincode__icontains=q) |
            Q(category_name__icontains=q) |
            Q(customer_name__icontains=q)
        )

    stats = {
        'total':       DemandReport.objects.count(),
        'new':         DemandReport.objects.filter(status='new').count(),
        'in_progress': DemandReport.objects.filter(status='in_progress').count(),
        'fulfilled':   DemandReport.objects.filter(status='fulfilled').count(),
        'product_demand':  DemandReport.objects.filter(demand_type='product').count(),
        'pincode_demand':  DemandReport.objects.filter(demand_type='pincode').count(),
        'category_demand': DemandReport.objects.filter(demand_type='category').count(),
    }

    ctx = {
        'admin_obj': admin_obj,
        'demands':   demands,
        'stats':     stats,
        'dtype':     dtype,
        'dstatus':   dstatus,
        'q':         q,
        'type_choices':   DemandReport.TYPE_CHOICES,
        'status_choices': DemandReport.STATUS_CHOICES,
    }
    return render(request, 'Admin_Pages/Pincode/demand_report.html', ctx)


def demand_update_status(request, pk):
    """AJAX POST — update status + admin remarks."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    obj = get_object_or_404(DemandReport, pk=pk)
    new_status     = request.POST.get('status', obj.status)
    admin_remarks  = request.POST.get('admin_remarks', '').strip()

    obj.status        = new_status
    obj.admin_remarks = admin_remarks
    obj.save()
    return JsonResponse({'status': '1', 'msg': 'Demand status updated!'})


def demand_delete(request, pk):
    """AJAX POST — delete a demand entry."""
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    obj = get_object_or_404(DemandReport, pk=pk)
    obj.delete()
    return JsonResponse({'status': '1', 'msg': 'Demand entry deleted.'})


def demand_add(request):
    """
    AJAX POST — manually add a demand (admin can log offline requests).
    Also used by the public-facing 'Request a Product' form if you add one.
    """
    if request.method != 'POST':
        return JsonResponse({'status': '0', 'msg': 'Invalid method'})

    demand_type       = request.POST.get('demand_type', 'product')
    customer_name     = request.POST.get('customer_name', '').strip()
    customer_phone    = request.POST.get('customer_phone', '').strip()
    customer_email    = request.POST.get('customer_email', '').strip()
    product_name      = request.POST.get('product_name', '').strip()
    requested_pincode = request.POST.get('requested_pincode', '').strip()
    category_name     = request.POST.get('category_name', '').strip()
    notes             = request.POST.get('notes', '').strip()

    # If same item already exists, increment vote count
    lookup = {}
    if demand_type == 'product' and product_name:
        lookup = {'demand_type': 'product', 'product_name__iexact': product_name}
    elif demand_type == 'pincode' and requested_pincode:
        lookup = {'demand_type': 'pincode', 'requested_pincode': requested_pincode}
    elif demand_type == 'category' and category_name:
        lookup = {'demand_type': 'category', 'category_name__iexact': category_name}

    if lookup:
        existing = DemandReport.objects.filter(**lookup).first()
        if existing:
            existing.vote_count += 1
            existing.save()
            return JsonResponse({'status': '1', 'msg': 'Vote added to existing demand!', 'id': existing.id})

    obj = DemandReport.objects.create(
        demand_type=demand_type,
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_email=customer_email,
        product_name=product_name,
        requested_pincode=requested_pincode,
        category_name=category_name,
        notes=notes,
    )
    return JsonResponse({'status': '1', 'msg': 'Demand logged successfully!', 'id': obj.id})



#####################End Pincode Manager  Views Section #######################################################

