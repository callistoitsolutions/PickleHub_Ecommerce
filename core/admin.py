from django.contrib import admin
from core.models import *

# Register your models here.


############# Register Cart Modal Here #########################

admin.site.register(Cart)

############# Register Cart Item Modal Here #####################

admin.site.register(CartItem)