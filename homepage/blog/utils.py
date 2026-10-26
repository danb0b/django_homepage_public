from django.conf import settings
import markdown

def render_markdown(input, extra_extensions=None):
    extra_extensions = extra_extensions or []

    md_ex = settings.MARKDOWN_EXTENSIONS
    md_ex.extend(extra_extensions)
    md = markdown.Markdown(extensions=md_ex)
    html_pass_1 = md.convert(input)
    toc_tokens = md.toc_tokens
    my_dict = dict(html=html_pass_1, toc_tokens=toc_tokens)
    return my_dict
