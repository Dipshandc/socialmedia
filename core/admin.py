from django.contrib import admin
from. models import *
# Register your models here.

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Followercount)



admin.site.site_header = "Social Media"
admin.site.index_title= "Social Media Administration"