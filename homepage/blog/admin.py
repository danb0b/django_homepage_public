from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.conf import settings

from .models import Post
from .models import Tag
from .models import Folder
from .management.commands.import_markdown import import_markdown

class FolderAdmin(admin.ModelAdmin):
    list_display = ['name'] 
admin.site.register(Folder,FolderAdmin)

class TagAdmin(admin.ModelAdmin):
    list_display = ['name'] 
admin.site.register(Tag,TagAdmin)

class PostAdmin(admin.ModelAdmin):
    change_list_template = 'admin/blog/post/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-post/', self.admin_site.admin_view(self.update_post_view), name='update-post'),
        ]
        return custom_urls + urls

    def update_post_view(self, request):
        context = {
            'title': 'Import Markdown Data',
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
        }
        import_markdown(settings.MARKDOWN_SOURCE_PATH)
        return HttpResponseRedirect("../")

admin.site.register(Post, PostAdmin)


