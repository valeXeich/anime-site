from django.contrib import admin

from .models import *

@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):

    prepopulated_fields = {'url': ('title',)}


admin.site.register(Genre)
admin.site.register(Directors)
admin.site.register(Studio)
admin.site.register(Profile)
admin.site.register(AnimeList)
admin.site.register(WatchingNow)
admin.site.register(WillWatch)
admin.site.register(Viewed)
admin.site.register(Throw)
admin.site.register(Favorite)
admin.site.register(Comment)