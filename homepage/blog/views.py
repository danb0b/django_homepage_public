from django.views import generic
from .models import Post
from django.template.response import TemplateResponse


def index(request, *args, **kwargs):
    context = {}
    return TemplateResponse(request, "index.html", context)


class PostListView(generic.ListView):
    model = Post
    # ordering = ["title"]
    # template_name = "blog/post_list.html"
    
class PostDetailView(generic.DetailView):
    model = Post
    # template_name = "blog/post_detail.html"