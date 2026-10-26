from django.db import models
from django.urls import reverse 
from django.conf import settings
from django.contrib.auth.models import User
import markdown
import os
import json
import re
import markdown_extensions.find_replace_pre

from blog import regex_templates
from blog import utils

class Tag(models.Model):

    name  = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)

class Folder(models.Model):
    name = models.CharField(max_length=200, unique=True,blank=True)

    def __str__(self):
        return str(self.name)

class Post(models.Model):
    path = models.CharField(max_length=200,unique=True)
    author = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    tags = models.ManyToManyField(Tag,blank=True)
    json = models.TextField(null=True)
    folder = models.ForeignKey(Folder, null=True, on_delete= models.SET_NULL)
    date =  models.DateTimeField(blank=True,null= True)
    content = models.TextField(blank=True,null=True)

    class Meta:
        ordering = ["-date", "path"]

    def __str__(self):
        return str(self.path)


    def get_relpath(self):
        return os.path.split(self.path)[0]
    
    def get_absolute_url(self):
        return reverse('post', args=[str(self.pk)])
        
    def get_filename(self):
        return os.path.split(self.path)[1]

    def get_markdown_url(self):
        path_elements = self.path.split('/')
        if len(path_elements)>1:
            header = path_elements[0]
            dirs = self.path.split('/')[1:]
            dirs[-1] = os.path.splitext(dirs[-1])[0]
            dirs_string = '/'.join(dirs)
            return reverse('find_post_or_folder', kwargs={'top_dir':header,'subpath':dirs_string})
        if len(path_elements)==1:
            header = path_elements[0]
            return reverse('find_top_folder', kwargs={'top_dir':header})

    def get_title(self):
        try:
            my_json = json.loads(self.json)
            title=my_json['title']
        except KeyError:
            title=os.path.split(self.path)[1]
        except TypeError:
            title=os.path.split(self.path)[1]
        return title

    def render_full_markdown(self):
        return utils.render_markdown(self.content,extra_extensions=self.get_extra_extensions())        

    def get_extra_extensions(self):
        extra_extensions = [
                markdown_extensions.find_replace_pre.FindReplaceExtension(
                    find=regex_templates.RELFIND,
                    replace=regex_templates.RELREPLACE1
                    + self.get_relpath()
                    + "/"
                    + regex_templates.RELREPLACE2,
                    priority=202,
                    name="rel-find-replace",
                ),
                markdown_extensions.find_replace_pre.FindReplaceExtension(
                    find=regex_templates.ABSFIND,
                    replace=regex_templates.ABSREPLACE,
                    priority=201,
                    name="abs-find-replace",
                ),
                markdown_extensions.glightboxify.GlightboxExtension(),
            ]
        return extra_extensions