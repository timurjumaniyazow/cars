from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Advertisement, AdvertisementAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Сommunication, СommunicationAdmin)