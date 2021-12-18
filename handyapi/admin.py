from django.contrib import admin
from handyapi.models import *

#register all models from handyapi.models
admin.site.register(User)
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(Provider)
admin.site.register(Comment)
admin.site.register(Category)