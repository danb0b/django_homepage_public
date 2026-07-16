from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.conf import settings

from .models import Post
from .models import Tag
from .models import Folder

class FolderAdmin(admin.ModelAdmin):
    list_display = ['name'] 
admin.site.register(Folder,FolderAdmin)

class TagAdmin(admin.ModelAdmin):
    pass
    list_display = ['name'] 
admin.site.register(Tag,TagAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ['path','author'] 
    pass

admin.site.register(Post, PostAdmin)