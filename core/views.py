from django.shortcuts import render,HttpResponse
from Admin_app.models import *
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from Admin_app.models import *

from Admin_app.utils import _hero_data, _features_data, _category_data
from products.models import *
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
import traceback
from django.db.models import Q
from datetime import datetime








############################## Website Index Page Views Section Starts Here ###############################################


def index(request):

    # 🔹 Banner logic (unchanged)
    active_banners = OfferBanner.objects.filter(is_active=True).order_by('order')
    banner_pairs = []
    for i in range(0, len(active_banners), 2):
        pair = {'main': None, 'potw': None}
        if i < len(active_banners):
            banner1 = active_banners[i]
            if banner1.offer_type == 'main': pair['main'] = banner1
            else: pair['potw'] = banner1

        if i + 1 < len(active_banners):
            banner2 = active_banners[i + 1]
            if banner2.offer_type == 'main': pair['main'] = banner2
            else: pair['potw'] = banner2

        if pair['main'] or pair['potw']:
            banner_pairs.append(pair)

    # 🔹 Sections (unchanged)
    hero        = HeroSection.get_or_create_default()
    features    = FeaturesSection.get_or_create_default()
    category    = CategorySection.get_or_create_default()

    # 🔹 Data (unchanged)
    brands     = Brand.objects.filter(is_active=True).order_by('order')
    reviews    = Review.objects.filter(is_active=True).order_by('order')
    newsletter = NewsletterSetting.objects.last()

    #  Products (unchanged)
    #  Products — show all active products, not just featured
    products = Product.objects.filter(
    is_active=True,
    # is_featured=True  ← REMOVED — this was hiding your products
    ).select_related('brand', 'category').order_by('sort_order')[:12]

    #  Category names for filter buttons (unchanged)
    categories = [
        item.get('name')
        for item in category.items_json
    ]

    # ── Deals & Offers ──────────────────────────────────────────

    # Scrolling ticker messages
    ticker_messages = TickerMessage.objects.filter(is_active=True).order_by('order')

    # Deal of the Day
    dotd = DealOfTheDay.objects.filter(
        is_visible=True,
        end_time__gt=timezone.now()
    ).first()

    # Offer Strip
    offer_strip = Coupon.objects.filter(
        is_active=True,
        show_on_strip=True
    ).order_by('order')[:3]

    # Coupon Wall
    coupon_wall = Coupon.objects.filter(
        is_active=True,
        show_on_wall=True
    ).order_by('order')

    # ✅ Today's Offers
    todays_offers = TodaysOffer.objects.filter(
    is_visible=True,
    product__isnull=False        # ← add this line
    ).select_related('product').order_by('order')

    #  Build a dict {product_id: TodaysOffer}
    offer_product_ids = {o.product_id: o for o in todays_offers}

    #  Attach active_offer directly to each product object
    # Template usage: {% if p.active_offer %} — no custom filter needed
    for p in products:
        p.active_offer = offer_product_ids.get(p.id)  # None if no offer exists

    # ────────────────────────────────────────────────────────────

    context = {
        # Existing (unchanged)
        'banner_pairs':    banner_pairs,
        'hero':            hero,
        'features':        features,
        'brands':          brands,
        'reviews':         reviews,
        'newsletter':      newsletter,
        'category':        category,
        'products':        products,
        'categories':      categories,

        # Deals (unchanged)
        'ticker_messages': ticker_messages,
        'dotd':            dotd,
        'offer_strip':     offer_strip,
        'coupon_wall':     coupon_wall,
        'todays_offers':   todays_offers,
        'user_obj': None,
        # offer_map removed — not needed anymore
    }

     # 🔹 3. Handle the logged-in user logic safely
    session_id = request.session.get('User_id')
    if session_id:
        
        user_obj = UserDetails.objects.filter(id=session_id).first()
        if user_obj:
            context['user_obj'] = user_obj

    # 🔹 4. Return the render (Works safely for both scenarios now!)
    return render(request, 'home/index.html', context)


############################## Website Index Page Views Section Ends Here ###############################################




############################## Website Index Page Sections Views Section Starts Here ###############################################

@require_POST
def save_hero(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
 
    hero = HeroSection.get_or_create_default()
    hero.badge_text        = data.get('badge_text',        hero.badge_text)
    hero.title_line1       = data.get('title_line1',       hero.title_line1)
    hero.title_highlight   = data.get('title_highlight',   hero.title_highlight)
    hero.title_line2       = data.get('title_line2',       hero.title_line2)
    hero.subtitle          = data.get('subtitle',          hero.subtitle)
    hero.jar_emoji         = data.get('jar_emoji',         hero.jar_emoji)
    hero.hero_image_url    = data.get('hero_image_url',    hero.hero_image_url)
    hero.buttons_json      = data.get('buttons_json',      hero.buttons_json)
    hero.stats_json        = data.get('stats_json',        hero.stats_json)
    hero.float_badges_json = data.get('float_badges_json', hero.float_badges_json)
    hero.is_visible        = data.get('is_visible',        hero.is_visible)
    hero.save()
 
    return JsonResponse({'ok': True, 'message': '✅ Hero section saved!'})
 
# ──────────────────────────────────────────────
# 4. SAVE FEATURES  (AJAX POST)  ← NEW
# ──────────────────────────────────────────────
@require_POST
def save_features(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
 
    features = FeaturesSection.get_or_create_default()
    features.items_json = data.get('items_json', features.items_json)
    features.is_visible = data.get('is_visible', features.is_visible)
    features.save()
 
    return JsonResponse({'ok': True, 'message': '✅ Features section saved!'})
 


@require_POST
def save_category(request):
    """
    Receives JSON from the category builder.
 
    Expected body:
    {
        "section_title":    "Shop by Category",
        "section_subtitle": "Browse our wide range...",
        "items_json": [
            {
                "emoji":       "🥭",
                "name":        "Mango Pickle",
                "count":       "32 products",
                "url":         "/category/mango/",
                "bg_gradient": "linear-gradient(135deg,#fff3e0,#ffcc80)"
            },
            ...
        ],
        "is_visible": true
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
 
    category = CategorySection.get_or_create_default()
    category.section_title    = data.get('section_title',    category.section_title)
    category.section_subtitle = data.get('section_subtitle', category.section_subtitle)
    category.items_json       = data.get('items_json',       category.items_json)
    category.is_visible       = data.get('is_visible',       category.is_visible)
    category.save()
 
    return JsonResponse({'ok': True, 'message': '✅ Category section saved!'})
 
 
# ──────────────────────────────────────────────
# 5. LOAD HERO  (AJAX GET – optional)
# ──────────────────────────────────────────────
def load_hero(request):
    hero = HeroSection.get_or_create_default()
    return JsonResponse({'ok': True, 'hero': _hero_data(hero)})
 
 
# ──────────────────────────────────────────────
# 10. LOAD CATEGORY  (AJAX GET)  ← NEW
# ──────────────────────────────────────────────
 
def load_category(request):
    category = CategorySection.get_or_create_default()
    return JsonResponse({'ok': True, 'category': _category_data(category)})


############## Views start for complete profile ##########################


@csrf_exempt
def complete_profile(request):
    if request.method == "POST":
        try:
            data        = json.loads(request.body.decode('utf-8'))
            phone       = data.get('user_phone', '').strip()
            city        = data.get('user_city', '').strip()
            # pincode     = data.get('user_pincode', '').strip()

            if not phone:
                return JsonResponse({'status': '0', 'msg': 'Phone number is required'})

            user_id = request.session.get('User_id')
            user    = UserDetails.objects.get(id=user_id)

            # Check phone not already taken by another user
            if UserDetails.objects.filter(user_phone=phone).exclude(id=user_id).exists():
                return JsonResponse({'status': '0', 'msg': 'Phone number already registered'})

            user.user_phone   = phone
            user.user_city    = city
            # user.user_pincode = pincode   # add this field to your model if not exists
            user.save()

            # Clear the flag
            request.session.pop('show_complete_profile', None)

            return JsonResponse({'status': '1', 'msg': 'Profile completed successfully'})

        except Exception as e:
            return JsonResponse({'status': '0', 'msg': str(e)})
        

############## Views end for complete profile #################################


############## Views start for update user profile ######################

def User_Profile(request):
    session_id = request.session.get('User_id')
    if session_id:
        user_obj = UserDetails.objects.filter(id=session_id).first()
        context = {'user_obj':user_obj}
        return render(request,'home/User_Profile/user_profile.html',context)
    else:
        return render(request,'account/login.html')

########### Views end for update user profile #############################




@csrf_exempt
def login(request):
    session_id = request.session.get('User_id')
    user_type  = request.session.get('user_type')

    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            login_placement = data.get('login_placement')
            login_password  = data.get('login_password')

            login_user = UserDetails.objects.filter(
                Q(user_email=login_placement) | Q(user_phone=login_placement),
                user_password=login_password
            ).first()

            if login_user:
                # ── Normal login session ─────────────────────────────────
                request.session['User_id']   = str(login_user.id)
                request.session['user_type'] = 'User'
                request.session.modified     = True
                send_data = {'status': '1', 'msg': 'Login Successful...'}
            else:
                send_data = {'status': '0', 'msg': 'Invalid Credentials'}

        except Exception as e:
            print(traceback.format_exc())
            send_data = {'status': '0', 'msg': 'Something went wrong', 'error': str(e)}

        return JsonResponse(send_data)

    else:
        # ── Already logged in via normal login ───────────────────────────
        if session_id and user_type == 'User':
            return redirect('index')

      

        return render(request, 'account/login.html')


@csrf_exempt
def User_Logout(request):
    try:
        # It's safer to use .pop() to avoid KeyError if the key is already gone
        request.session.pop('User_id', None)
        request.session.pop('user_type', None)
        return JsonResponse({"status":"1", "msg": "Logout Successfully"})
    except Exception:
        print(traceback.format_exc())
        return JsonResponse({"status":"0", "msg": "Error during logout"})


@csrf_exempt
def Users_Ajax(request):
    data = request.POST.dict()

    if data.get('id') == "":
        data.pop("id", None)         
        data['user_register_date'] = datetime.today()
        data['user_register_time'] = datetime.now()
        if UserDetails.objects.filter(user_phone=data['user_phone']).exists():
            return JsonResponse({"status":"0", "msg" : f"User already exists .."})
        else:
            UserDetails.objects.create(**data)
            return JsonResponse({"status":"1", "msg" : f"User account has been created successfully"})

    # UPDATE MODE
    else:
        try:
            user = UserDetails.objects.get(id=data['id'])
        except UserDetails.DoesNotExist:
            return JsonResponse({'status': '0', 'msg': 'User Details not found'})
        

        # Update withdraw fields (unchanged)
        for key, value in data.items():
                setattr(user, key, value)

        user.save()
        return JsonResponse({"status":"1", "msg" : f"User account has been updated successfully"})



############################## Products Views Section Starts Here ###############################################



def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    related = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).select_related('brand')[:4]

    also_bought = Product.objects.filter(
        is_active=True
    ).exclude(id=product.id).exclude(
        id__in=related.values_list('id', flat=True)
    ).order_by('-review_count')[:4]

    # =========================
    # ✅ OFFERS
    # =========================
    all_ids = [product.id] + \
              list(related.values_list('id', flat=True)) + \
              list(also_bought.values_list('id', flat=True))

    offers = TodaysOffer.objects.filter(
        is_visible=True,
        product_id__in=all_ids
    ).select_related('product')

    offer_map = {o.product_id: o for o in offers}

    # =========================
    # ✅ COUPONS (OPTIMIZED)
    # =========================
    coupons = Coupon.objects.filter(
        is_active=True,
        products__id__in=all_ids
    ).prefetch_related('products')

    coupon_map = {}
    for c in coupons:
        for p in c.products.all():
            coupon_map.setdefault(p.id, []).append(c)

    # =========================
    # ASSIGN DATA
    # =========================

    # MAIN PRODUCT
    product.active_offer = offer_map.get(product.id)
    product.assigned_coupons_list = coupon_map.get(product.id, [])

    # RELATED
    for p in related:
        p.active_offer = offer_map.get(p.id)
        p.assigned_coupons_list = coupon_map.get(p.id, [])

    # ALSO BOUGHT
    for p in also_bought:
        p.active_offer = offer_map.get(p.id)
        p.assigned_coupons_list = coupon_map.get(p.id, [])

    context ={
        'product': product,
        'related': related,
        'also_bought': also_bought,
        'user_obj':None
    }

    # 🔹 3. Handle the logged-in user logic safely
    session_id = request.session.get('User_id')
    if session_id:
        
        user_obj = UserDetails.objects.filter(id=session_id).first()
        if user_obj:
            context['user_obj'] = user_obj

    return render(request, 'products_panel/product_details.html',context)


def checkout(request):
    session_id = request.session.get('User_id')
    if session_id:

        user_obj = UserDetails.objects.filter(id=session_id).first()
        context = {'user_obj':user_obj}
        return render(request, 'payments/checkout.html',context)

    else:
        return render(request, 'payments/checkout.html',context)




def cart(request):
    session_id = request.session.get('User_id')
    if session_id:
        user_obj = UserDetails.objects.filter(id=session_id).first()
        context = {'user_obj':user_obj}
        return render(request, 'cart/cart.html',context)
    else:
        return render(request, 'account/login.html')
    








# ── Wishlist page ──────────────────────────────────────────────
def product_wishlist(request):
    session_id = request.session.get('User_id')

    # 🔐 Check login
    if not session_id:
        return redirect('login')

    user_obj = UserDetails.objects.filter(id=session_id).first()
    if not user_obj:
        return redirect('login')

    # ✅ Clean queryset (NO invalid prefetch)
    wish_qs = (
        Wishlist.objects
        .filter(user=user_obj)
        .select_related('product', 'product__brand')
    )

    # 🔄 Build data for frontend
    items = []
    for w in wish_qs:
        p = w.product

        items.append({
            'id'          : p.id,
            'name'        : p.name,
            'brand'       : p.brand.name if p.brand else '',
            'size'        : p.weight or '',
            'price'       : float(p.price),
            'mrp'         : float(p.old_price) if p.old_price else float(p.price),
            'badge'       : p.badge or '',
            'img'         : p.image.url if p.image else '',
            'emoji'       : p.emoji or '🥒',
            'added'       : w.added_on.strftime('%d %b %Y'),
            'inStock'     : not p.is_out_of_stock,
            'slug'        : p.slug,
            'discount_pct': p.discount_pct,
        })

    # 📊 Summary
    context = {
        'user_obj'       : user_obj,
        'wish_items_json': json.dumps(items),
        'total'          : len(items),
        'in_stock_count' : sum(1 for i in items if i['inStock']),
        'oos_count'      : sum(1 for i in items if not i['inStock']),
    }

    return render(request, 'products_panel/product_wishlist.html', context)

# ── Toggle wishlist (AJAX) ─────────────────────────────────────
@require_POST
def toggle_wishlist(request):
    session_id = request.session.get('User_id')
    if not session_id:
        return JsonResponse({'status': '0', 'msg': 'Login required'})

    try:
        data       = json.loads(request.body)
        product_id = data.get('product_id')
    except Exception:
        return JsonResponse({'status': '0', 'msg': 'Invalid data'})

    user_obj = UserDetails.objects.filter(id=session_id).first()
    product  = Product.objects.filter(id=product_id).first()

    if not user_obj or not product:
        return JsonResponse({'status': '0', 'msg': 'Not found'})

    obj, created = Wishlist.objects.get_or_create(user=user_obj, product=product)
    if not created:
        obj.delete()
        return JsonResponse({'status': '1', 'action': 'removed', 'msg': 'Removed from wishlist'})

    return JsonResponse({'status': '1', 'action': 'added', 'msg': 'Added to wishlist'})


# ── Remove single item (AJAX) ──────────────────────────────────
@require_POST
def remove_wishlist_item(request):
    session_id = request.session.get('User_id')
    if not session_id:
        return JsonResponse({'status': '0', 'msg': 'Login required'})

    try:
        data       = json.loads(request.body)
        product_id = data.get('product_id')
    except Exception:
        return JsonResponse({'status': '0', 'msg': 'Invalid data'})

    user_obj = UserDetails.objects.filter(id=session_id).first()
    Wishlist.objects.filter(user=user_obj, product_id=product_id).delete()
    return JsonResponse({'status': '1', 'msg': 'Removed'})



def All_products(request):
    settings   = ProductPageSettings.get_or_create_default()
    categories = CategorySection.get_or_create_default()
    brands     = Brand.objects.filter(is_active=True)
    products_qs = Product.objects.filter(is_active=True).select_related('brand', 'category')

    # ── apply filters ──
    cat_ids    = request.GET.getlist('cat')
    brand_ids  = request.GET.getlist('brand')
    regions    = request.GET.getlist('region')
    price_max  = request.GET.get('price_max', settings.price_max)
    min_rating = request.GET.get('rating', '')
    weights    = request.GET.getlist('weight')
    sort       = request.GET.get('sort', 'popular')

    if cat_ids:
        products_qs = products_qs.filter(category__id__in=cat_ids)
    if brand_ids:
        products_qs = products_qs.filter(brand__id__in=brand_ids)
    if regions:
        products_qs = products_qs.filter(region__in=regions)
    if price_max:
        products_qs = products_qs.filter(price__lte=price_max)
    if min_rating:
        products_qs = products_qs.filter(rating__gte=min_rating)

    sort_map = {
        'popular':    '-review_count',
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-created_at',
        'rating':     '-rating',
    }
    products_qs = products_qs.order_by(sort_map.get(sort, '-review_count'))

    paginator = Paginator(products_qs, 12)
    page_num  = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page_num)

    # ── Today's Offers ──
    todays_offers = TodaysOffer.objects.filter(
        is_visible=True, product__isnull=False
    ).select_related('product')
    offer_map = {o.product_id: o for o in todays_offers}

    # ── Coupons ──
    page_product_ids = [p.id for p in page_obj]
    coupon_qs = Coupon.objects.filter(
        is_active=True,
        products__id__in=page_product_ids
    ).prefetch_related('products')

    coupon_map = {}
    for coupon in coupon_qs:
        for pid in coupon.products.values_list('id', flat=True):
            if pid in page_product_ids:
                coupon_map.setdefault(pid, []).append(coupon)

    for p in page_obj:
        p.active_offer          = offer_map.get(p.id)
        p.assigned_coupons_list = coupon_map.get(p.id, [])

    context = {
        'products':          page_obj,
        'paginator':         paginator,
        'page_obj':          page_obj,
        'categories':        categories,
        'brands':            brands,
        'settings':          settings,
        'total_count':       products_qs.count(),
        'selected_cats':     [int(x) for x in cat_ids   if x.isdigit()],
        'selected_brands':   [int(x) for x in brand_ids if x.isdigit()],
        'selected_regions':  regions,
        'current_price_max': int(price_max),
        'current_sort':      sort,
        'current_rating':    min_rating,
        'user_obj':          None,
        'user_wishlist_ids': set(),   # default — empty set for guests
    }

    # ── Logged-in user ──
    session_id = request.session.get('User_id')
    if session_id:
        user_obj = UserDetails.objects.filter(id=session_id).first()
        if user_obj:
            context['user_obj'] = user_obj

            # ✅ fetch this user's wishlisted product IDs in one DB query
            context['user_wishlist_ids'] = set(
                Wishlist.objects.filter(user=user_obj)
                .values_list('product_id', flat=True)
            )

    return render(request, 'products_panel/All_products.html', context)



############################## Products Views Section Ends Here ###############################################



def contact(request):
    session_id = request.session.get('User_id')
    if session_id:
        user_obj = UserDetails.objects.filter(id=session_id).first()
        context = {'user_obj':user_obj}
        return render(request, 'home/contact.html',context)
    else:
        return render(request, 'home/contact.html')