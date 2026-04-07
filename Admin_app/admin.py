from django.contrib import admin
from Admin_app.models import *

# Register your models here.

############ Register Admin Details Table/Modal #################

admin.site.register(AdminDetails)

############## Register User Details Table/Modal ##################

admin.site.register(UserDetails)

############ Register Offer Banner Table ####################

admin.site.register(OfferBanner)


############ Regsiter Brand Details Table ####################\

admin.site.register(Brand)

########### Register Review Details Table/Modal ##################

admin.site.register(Review)

############## Register Newsletter Details Table/Modal #################

admin.site.register(NewsletterSetting)



