from django.contrib.staticfiles.apps import StaticFilesConfig

class StaticFilesConfig(StaticFilesConfig):
    name = 'staticfiles'
    ignore_patterns = [
        "CVS", ".*", "*~",
        "*.md",
        ]