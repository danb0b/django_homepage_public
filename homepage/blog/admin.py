from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.conf import settings

from .models import Post
from .models import Tag

class TagAdmin(admin.ModelAdmin):
    list_display = ['name'] 
admin.site.register(Tag,TagAdmin)

class PostAdmin(admin.ModelAdmin):
    pass
admin.site.register(Post, PostAdmin)