from django.contrib import admin

# Register your models here.
from django.contrib import admin
from app.models import House,User,Histroy
# Register your models here.

class HouseMange(admin.ModelAdmin):
    list_display = ["id","title","type","building","city",'street','area','direct','price']
    list_per_page = 20
    search_fields = ['title','building','city','price']
    list_filter = ['city','building']
class UserManager(admin.ModelAdmin):
    list_display = ['id', 'username', 'password', 'phone', 'email', 'time', 'admin_sample']
    list_per_page = 5

class HistoryManager(admin.ModelAdmin):
    list_display = ['id','house','user','count']
    list_per_page = 5

admin.site.register(House, HouseMange)
admin.site.register(User, UserManager)
admin.site.register(Histroy, HistoryManager)
