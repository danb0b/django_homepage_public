from django.conf import settings

FILE_SEARCH=r"""(?P<group2>[a-zA-Z0-9./\-_ ]+(png|jpg|mp4|json|csv|xlsx|yml|trz|svg))"""

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

ALERT_TEXT_SEARCH = "<!-- *alert-text '(?P<alert_text>[a-zA-Z0-9-_:/,. \"<>#\\[\\]\\(\\)\\n]*)' *-->"
ALERT_MODEL_SEARCH = "<!-- *alert '(?P<alert>[a-zA-Z0-9-_]*)' *-->"
