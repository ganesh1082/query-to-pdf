# query-to-pdf copy/html_renderer.py

from jinja2 import Environment, FileSystemLoader
from typing import Dict, Any, List
from html_components import Component, Header1, Paragraph, BulletedList, Chart, PageBreak
from datetime import datetime
import re

def parse_content_to_components(content_text: str) -> List[Component]:
    """A robust parser for converting AI-generated markdown-like text into HTML components."""
    if not content_text: return []
    components: List[Component] = []
    blocks = re.split(r'\n\s*\n', content_text.strip())
    for block in blocks:
        block = block.strip()
        if not block: continue
        lines = block.split('\n')
        if all(line.strip().startswith(('* ', '• ')) for line in lines):
            items = [re.sub(r'^\s*[\*•]\s*', '', item).strip() for item in lines]
            components.append(BulletedList(items))
        else:
            components.append(Paragraph(block))
    return components

def generate_html_from_blueprint(config: Any, blueprint: Dict[str, Any], visualizations: Dict[str, str]) -> str:
    """Creates the final HTML string from the AI-generated unified report data object."""
    
    # --- 1. Build Table of Contents Data ---
    toc_items = []
    for section in blueprint.get("sections", []):
        title = section.get("title")
        if title:
            toc_items.append({
                "title": title,
                "id": re.sub(r'[^a-zA-Z0-9]', '-', title.lower())
            })

    # --- 2. Build the main body components ---
    body_components: List[Component] = []
    for section in blueprint.get("sections", []):
        title = section.get("title", "Untitled Section")
        element_id = re.sub(r'[^a-zA-Z0-9]', '-', title.lower())
        
        body_components.append(Header1(title, element_id))
        
        content = section.get("content", "No content provided for this section.")
        body_components.extend(parse_content_to_components(content))
        
        # Check if a chart was generated for this section's title
        if title in visualizations:
            body_components.append(Chart(visualizations[title], f"Visualization for: {title}"))
        
        body_components.append(PageBreak())

    # --- 3. Render the Full HTML Template ---
    rendered_body = [comp.render() for comp in body_components]
    
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('report_template.html')
        
    current_date = datetime.now().strftime('%B %d, %Y')
    
    return template.render(
        report_title=config.title,
        report_subtitle=config.subtitle,
        author=config.author,
        company=config.company,
        current_date=current_date,
        toc_items=toc_items,
        body_components=rendered_body
    )