# query-to-pdf copy/html_components.py
import re
import os
from typing import List

class Component:
    def render(self) -> str: raise NotImplementedError
class PageBreak(Component):
    def render(self) -> str: return '<div class="page-break"></div>'
class CoverPage(Component):
    def __init__(self, title, subtitle, author, company, date):
        self.title, self.subtitle, self.author, self.company, self.date = title, subtitle, author, company, date
    def render(self) -> str:
        return f'<div class="cover-page"><h1 class="cover-title">{self.title}</h1><h2 class="cover-subtitle">{self.subtitle}</h2><div class="author-info"><p>Prepared by: <strong>{self.author}</strong></p><p>For: <strong>{self.company}</strong></p><p>Date: <strong>{self.date}</strong></p></div></div>'
class TableOfContents(Component):
    def __init__(self, sections: List[dict]): self.sections = sections
    def render(self) -> str:
        toc_html = '<div class="toc"><h1 class="toc-title">Table of Contents</h1><ol class="toc-list">'
        for sec in self.sections:
            toc_html += f'<li><a href="#{sec["id"]}">{sec["title"]}</a></li>'
        toc_html += '</ol></div>'
        return toc_html
class Header1(Component):
    def __init__(self, text: str, element_id: str): self.text, self.element_id = text, element_id
    def render(self) -> str: return f'<h1 id="{self.element_id}">{self.text}</h1>'
class Paragraph(Component):
    def __init__(self, text: str): self.text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text.replace('\n', '<br>'))
    def render(self) -> str: return f'<p>{self.text}</p>'
class BulletedList(Component):
    def __init__(self, items: List[str]): self.items = items
    def render(self) -> str: return f'<ul>{"".join([f"<li>{item}</li>" for item in self.items])}</ul>'
class Chart(Component):
    def __init__(self, chart_path: str, cap: str): 
        self.chart_path, self.cap = chart_path, cap
    def render(self) -> str:
        if not self.chart_path or not os.path.exists(self.chart_path): 
            return '<div class="chart-placeholder"><p>Chart not available</p></div>'
        # Convert to absolute path for WeasyPrint compatibility
        absolute_path = os.path.abspath(self.chart_path).replace('\\', '/')
        file_url = f"file://{absolute_path}"
        return f'<div class="chart-container"><img src="{file_url}" alt="{self.cap}"><p class="caption">{self.cap}</p></div>'