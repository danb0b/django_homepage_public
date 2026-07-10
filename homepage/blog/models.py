from django.db import models
from django.urls import reverse 
from django.conf import settings
from django.contrib.auth.models import User
import markdown

class Tag(models.Model):

    name  = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return str(self.name)

class Post(models.Model):
    title = models.CharField(max_length=200,unique=True)
    author = models.ForeignKey(User, null=True, on_delete= models.SET_NULL)
    tags = models.ManyToManyField(Tag,blank=True)
    content = models.TextField(blank=True,null=True)

    class Meta:
        ordering = ["title"]
        
    def __str__(self):
        return str(self.title)

    def get_absolute_url(self):
        return reverse('post', args=[str(self.pk)])
        
    @staticmethod
    def _render_markdown(input):
        md = markdown.Markdown(extensions=settings.MARKDOWN_EXTENSIONS)
        html_pass_1=md.convert(input)
        toc_tokens=md.toc_tokens
        my_dict = dict(html=html_pass_1,toc_tokens=toc_tokens)
        return my_dict

    def render_full_markdown(self):
        return self._render_markdown(self.content)          