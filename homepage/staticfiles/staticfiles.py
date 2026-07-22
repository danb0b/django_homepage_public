import django.contrib.staticfiles.apps

class StaticFilesConfig(django.contrib.staticfiles.apps.StaticFilesConfig):
    ignore_patterns =  ['CVS', '.*', '*~','*.md'],