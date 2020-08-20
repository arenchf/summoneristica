from django.contrib import admin
from .models import Summoner,Matchlist
from .models import Programmer
from .models import Company
from .models import Deneme
# Register your models here.


admin.site.register(Summoner)
admin.site.register(Programmer)
admin.site.register(Company)
admin.site.register(Deneme)
admin.site.register(Matchlist)