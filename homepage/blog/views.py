from django.views import generic
from .models import Post
from django.template.response import TemplateResponse
from .models import Folder
from django.http import Http404
import os

def index(request, *args, **kwargs):
    context = {}
    return TemplateResponse(request, "index.html", context)

def add_parents(context, top_dir, subpath):
    if subpath == "":
        path = top_dir
    else:
        path = os.path.join(top_dir, subpath)
    path_items = path.split("/")
    parents = []
    previous = ""
    for item in path_items:
        previous = "/".join([previous, item])
        parents.append((item, previous))
    context["parents"] = parents
    context["current_folder"] = path_items[-1]

def add_children(context, topdir, subpath):
    if subpath == "":
        path = topdir
    else:
        path = os.path.join(topdir, subpath)
    blocked = Folder.objects.filter(name=path)
    query = (
        Folder.objects.filter(name__startswith=path)
        .exclude(id__in=blocked)
        .order_by("name")
    )
    children = []
    for child in query:
        query2 = Post.objects.filter(folder__exact=child)
        if len(query2) == 1:
            if query2[0].get_filename() != "index.md":
                children.append(child)
        else:
            children.append(child)
    context["children"] = children

class PostListView(generic.ListView):
    model = Post
    # ordering = ["title"]
    # template_name = "blog/post_list.html"
    
class PostDetailView(generic.DetailView):
    model = Post

    def get_object(self, queryset=None):
        if ("subpath" in self.kwargs) and ("top_dir" in self.kwargs):
            fullpath = (
                os.path.join(self.kwargs["top_dir"], self.kwargs["subpath"]) + ".md"
            )
            return Post.objects.get(path=fullpath)
        elif "pk" in self.kwargs:
            pk = self.kwargs["pk"]
            return Post.objects.get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topdir = self.kwargs["top_dir"]
        subpath = self.kwargs["subpath"]
        add_parents(context, topdir, subpath)
        post = self.get_object()
        return context

class FolderView(generic.DetailView):
    model = Folder
    template_name = "blog/post_list.html"
    ordering = [
        "-date",
        "path",
    ]

    def get_object(self):
        if ("top_dir" in self.kwargs) and ("subpath" in self.kwargs):
            if self.kwargs["subpath"] != "":
                path = "/".join([self.kwargs["top_dir"], self.kwargs["subpath"]])
                results = Folder.objects.get(name=path)
            else:
                results = Folder.objects.get(name=self.kwargs["top_dir"])
            return results
        else:
            raise Http404("Path does not exist")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if ("top_dir" in self.kwargs) and ("subpath" in self.kwargs):
            topdir = self.kwargs["top_dir"]
            subpath = self.kwargs["subpath"]
            post_list = Post.objects.filter(folder__exact=context["folder"]).order_by(
                *self.ordering
            )
            context["post_list"] = post_list
            add_parents(context, topdir, subpath)
            add_children(context, topdir, subpath)
        return context

class FolderListView(generic.ListView):
    model = Folder


def find_post_or_folder(request, *args, **kwargs):
    subpath = kwargs["subpath"]
    if subpath.endswith("/"):
        subpath = subpath[:-1]
    try:
        return PostDetailView.as_view()(
            request, top_dir=kwargs["top_dir"], subpath=subpath
        )
    except Post.DoesNotExist:
        try:
            return PostDetailView.as_view()(
                request,
                top_dir=kwargs["top_dir"],
                subpath=os.path.join(subpath, "index"),
            )
        except:
            try:
                return FolderView.as_view()(
                    request, top_dir=kwargs["top_dir"], subpath=subpath
                )
            except:
                raise Http404("Path does not exist")