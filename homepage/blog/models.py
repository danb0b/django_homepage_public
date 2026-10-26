from django.db import models
from django.urls import reverse 
from django.conf import settings
from django.contrib.auth.models import User
import markdown
import os
import json
import re
import markdown_extensions.find_replace_pre
import markdown_extensions.glightboxify

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

    def get_image(self):
        try:
            my_json = json.loads(self.json)
            image = self.replace_static(my_json['image'])
        except KeyError:
            image=None
        except TypeError:
            image=None
        return image

    def get_summary(self):
        try:
            my_json = json.loads(self.json)
            summary=my_json['summary']
        except KeyError:
            summary=None
        except TypeError:
            summary=None
        return summary

    def gen_preview_text(self):
        return utils.render_markdown(' '.join(self.content[:200].split(' ')[:-1][:15])+' ...',extra_extensions=self.get_extra_extensions())['html']


    def summary_or_short_generated_preview(self):
        summary = self.get_summary()
        if not summary:
            summary=self.gen_preview_text()
        return summary

    def get_preview_text(self):
        if self.can_be_split():
            return self.render_split_markdown()['html']     
        else:
            return self.gen_preview_text()


    @staticmethod
    def split_content(markdown):
        kernel = re.compile('<!-- *split *-->')
        results = kernel.search(markdown)
    
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

        if results is not None:
            return markdown[:results.start()]
        else:
            return markdown

    def can_be_split(self):
        markdown = self.content
        kernel = re.compile('<!-- *split *-->')
        results = kernel.search(markdown)
        if results is not None:
            return True
        else:
            return False

    def replace_static(self,text):
        text = re.sub(regex_templates.RELFIND_CORE,regex_templates.RELREPLACE1_CORE+self.get_relpath()+'/'+regex_templates.RELREPLACE2_CORE,text)
        text = re.sub(regex_templates.ABSFIND_CORE,regex_templates.ABSREPLACE_CORE,text)
        print(text)
        return text

    def render_full_markdown(self):
        return utils.render_markdown(self.content,extra_extensions=self.get_extra_extensions())        

    def render_split_markdown(self):
        return utils.render_markdown(self.split_content(self.content),extra_extensions=self.get_extra_extensions())        
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
