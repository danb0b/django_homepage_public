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

FILE_SEARCH=r"""(?P<group2>[a-zA-Z0-9./\-_ ]+(png|jpg|mp4|json|csv|xlsx|yml|trz))"""

ABSFIND_CORE=r"""^/"""+FILE_SEARCH
ABSREPLACE_CORE=settings.STATIC_URL+r'''\g<group2>'''

RELFIND_CORE="""^(?!/)"""+FILE_SEARCH
RELREPLACE1_CORE=r"""/"""
RELREPLACE2_CORE=r"""\g<group2>"""

ABSFIND=r"""(?P<group1>\]\(|src=")/"""+FILE_SEARCH+r"""(?P<group4>\)|"| *\n)"""
ABSREPLACE=r"""\g<group1>"""+settings.STATIC_URL+r"""\g<group2>\g<group4>"""

RELFIND=r"""(?P<group1>\]\(|src=")(?!/)"""+FILE_SEARCH+r"""(?P<group4>\)|"| *\n)"""
RELREPLACE1 = r'''\g<group1>/'''
RELREPLACE2 = r'''\g<group2>\g<group4>'''


class Tag(models.Model):

    name  = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)

class Folder(models.Model):
    name = models.CharField(max_length=200, unique=True,blank=True)

    def __str__(self):
        return str(self.name)

class Post(models.Model):
    # title = models.CharField(max_length=200,unique=True)
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
                
    def _render_markdown(self,input):
        md_ex = settings.MARKDOWN_EXTENSIONS
        md_ex.extend([
            markdown_extensions.find_replace_pre.FindReplaceExtension(
                find=RELFIND,
                replace=RELREPLACE1+self.get_relpath()+'/'+RELREPLACE2,
                priority=202,
                name='rel-find-replace'),
            markdown_extensions.find_replace_pre.FindReplaceExtension(
                find=ABSFIND,
                replace=ABSREPLACE,priority=201,
                name='abs-find-replace'),
            markdown_extensions.glightboxify.GlightboxExtension(),
            ])
        md = markdown.Markdown(extensions=md_ex)
        html_pass_1=md.convert(input)
        toc_tokens=md.toc_tokens
        my_dict = dict(html=html_pass_1,toc_tokens=toc_tokens)
        return my_dict

    def render_full_markdown(self):
        return self._render_markdown(self.content)          

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
        return self._render_markdown(' '.join(self.content[:200].split(' ')[:-1][:15])+' ...')['html']


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
        text = re.sub(RELFIND_CORE,RELREPLACE1_CORE+self.get_relpath()+'/'+RELREPLACE2_CORE,text)
        text = re.sub(ABSFIND_CORE,ABSREPLACE_CORE,text)
        print(text)
        return text

    def render_split_markdown(self):
        return self._render_markdown(self.split_content(self.content))             