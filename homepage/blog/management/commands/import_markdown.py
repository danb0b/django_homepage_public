#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 26 14:07:29 2022

@author: danaukes
"""

import os
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.utils import timezone
from blog.models import Post
from blog.models import Folder
from blog.models import User
from blog.models import Tag
from django.conf import settings

import glob
import datetime
import pytz
import json
import frontmatter

def fix_path(path_in):
    path = path_in
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    path = os.path.normcase(path)
    path = os.path.normpath(path)
    return path

def create_tags(tag_list):
    tags = Tag.objects.all()
    tag_names = [tag.name.lower() for tag in tags]
    post_tags = []
    for tag_name in tag_list:
        if tag_name.lower() not in tag_names:
            tag = Tag(name=tag_name)
            tag.full_clean()
            tag.save()
            post_tags.append(tag)
        else:
            post_tags.extend(Tag.objects.filter(name=tag_name))
    return post_tags

def update_post(post,parent):
    path = post.path
    print(path)
    
    fullpath=os.path.join(settings.MARKDOWN_SOURCE_PATH,path)
    
    with open(fullpath) as f:
        fm = frontmatter.load(f)

    my_dict = fm.to_dict()
    try:
        tags = create_tags(my_dict['tags'])
    except KeyError:
        tags = []
    content = my_dict['content']
    del my_dict['content']
    my_json = json.dumps(my_dict,default=str)
    post.author = User.objects.get(pk=1)
    post.json = my_json
    post.content = content
    post.folder = Folder.objects.get(name=parent)

    try:
        my_tz = pytz.timezone(settings.TIME_ZONE)
        date = my_dict['date']
        dt = datetime.datetime.combine(date, datetime.datetime.min.time())
        post.date = my_tz.localize(dt)
    except KeyError:
        pass

    try:
        post.full_clean()
    except ValidationError as e:
        raise

    post.save()
    post.tags.set(tags)

def import_markdown(my_path):

    my_path = fix_path(my_path)

    markdown_file_structure = {}
    
    for d,sd,f in os.walk(my_path):
        fixed_path=fix_path(d)
        rel_dir = os.path.relpath(fixed_path,my_path)
        markdown_files = glob.glob(os.path.join(fixed_path,'*.md'))
        markdown_files = [os.path.relpath(os.path.join(fixed_path,item),my_path) for item in markdown_files]
        terminal_directory=False
        if len(markdown_files)==1:
            if os.path.split(markdown_files[0])[1]=='index.md':
                markdown_file_structure[os.path.split(rel_dir)[0]].extend(markdown_files)
                terminal_directory=True

        if not terminal_directory:
            if rel_dir=='.': rel_dir=''
            markdown_file_structure[rel_dir] = markdown_files

    for folder in Folder.objects.all():
        folder.delete()

    print(markdown_file_structure.keys())

    for item in markdown_file_structure.keys():
        folder=Folder(name=item)
        folder.full_clean()
        folder.save()

    file_structure_inv = {}
    for folder, files in markdown_file_structure.items():
        file_structure_inv |= dict([(file,folder) for file in files])

    markdown_relative_paths = []
    for key,value in markdown_file_structure.items():
        markdown_relative_paths.extend(value)

    existing_paths = [post.path for post in Post.objects.all()]

    dead_paths = sorted(list(set(existing_paths) - set(markdown_relative_paths)))
    new_paths=sorted(list(set(markdown_relative_paths) - set(existing_paths)))
    update_paths = sorted(list(set(existing_paths) & set(markdown_relative_paths)))

    for post in dead_paths:
        post=Post.objects.get(path=post)
        post.delete()

    for item in new_paths:
        folder = file_structure_inv[item]
        post = Post(path=item)
        update_post(post,folder)

    for item in update_paths:
        folder = file_structure_inv[item]
        post = Post.objects.get(path=item)
        update_post(post,folder)


    print(len(dead_paths),' dead posts deleted')
    print(len(new_paths),' new posts added')
    print(len(update_paths),' posts updated')

class Command(BaseCommand):
    help = 'Imports Markdown'

    def handle(self, *args, **kwargs):

        import_markdown(settings.MARKDOWN_SOURCE_PATH)
