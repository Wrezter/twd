from django.contrib import admin
from rango.models import Category, Page, UserProfile


class PageInline(admin.TabularInline):
    model = Page
    extra = 3


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'number_of_pages', 'likes', 'views']
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Likes and views', {'fields': ['likes', 'views'], 'classes': ['collapse']})
    ]
    inlines = [PageInline]


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url', 'views')
    list_filter = ['category']
    search_fields = ['title']
    fields = ['title', 'url', 'category', 'views']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'website', 'get_picture_url')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
