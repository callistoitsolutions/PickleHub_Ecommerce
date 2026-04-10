from datetime import date
from core.models import *
from datetime import datetime


def notifications(request):

    cart_obj_count_today = CartItem.objects.filter(cart_date=datetime.today()).count()

    return {
        'cart_obj_count_today': cart_obj_count_today
    }


