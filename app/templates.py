import os
import json
from pathlib import PurePath
details = '<details open="true">{}</details>'
sumary = '<summary>{}</summary>'
ul = '<ul>{}</ul>'
li = '<li><a href={url}>{title}</a></li>'
p = '<div class="detail"><p >{}</p></div>'

def generate_sidebar():
    with open(PurePath(os.getcwd(),'constants','sidebar.json'), encoding='utf-8') as json_file:
        headers = json.load(json_file)
    sidebar_html = ""
    for header in headers.keys():
        list_items = ""
        for sub_header in headers[header]:
            [url] = sub_header.values()
            [title] = sub_header.keys()
            list_items = list_items + li.format(url=url,title=title) 
        sidebar_html = sidebar_html + details.format(sumary.format(header) + ul.format(list_items))
    return sidebar_html
