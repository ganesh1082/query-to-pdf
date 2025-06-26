# query-to-pdf/enhanced_visualization_generator.py

import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Dict, Any, Optional
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

class PremiumVisualizationGenerator:
    """Creates a diverse variety of professional charts and saves them as image files."""
    
    def __init__(self, brand_colors: Dict[str, str]):
        self.primary_color = brand_colors.get("primary", "#0D203D")
        plt.style.use('seaborn-v0_8-whitegrid')
        self.temp_dir = "temp_charts"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _save_plot_to_file(self, fig, filename: str) -> str:
        """Saves the Matplotlib figure to a file and returns the path."""
        filepath = os.path.join(self.temp_dir, f"{filename}.png")
        fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filepath

    def _create_placeholder_chart(self, title: str) -> str:
        """Creates a placeholder image indicating missing data."""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "Data Not Available\nOr Malformed", ha='center', va='center', fontsize=18, color='#999')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
        return self._save_plot_to_file(fig, f"placeholder_{safe_title}")

    def _get_palette(self, name: Optional[str]) -> str:
        """Returns a valid seaborn color palette name."""
        return name if name in ["viridis", "mako", "husl", "coolwarm", "rocket", "crest"] else "viridis"

    def create_chart(self, section_data: Dict[str, Any]) -> str:
        """Public method to create any chart based on the provided section data."""
        chart_type = section_data.get("chart_type")
        data = section_data.get("chart_data")
        title = section_data.get("title")
        palette = self._get_palette(section_data.get("color_palette"))
        
        if not all([chart_type, data, title]):
            return self._create_placeholder_chart("Chart Data Missing")

        safe_title = "".join(c for c in (title or "") if c.isalnum()).replace(' ', '_')[:30]

        if chart_type in ["bar", "horizontalBar"]:
            return self._create_bar_chart(data, title, palette, chart_type, safe_title)
        if chart_type in ["line", "area"]:
            return self._create_line_or_area_chart(data, title, chart_type, safe_title)
        if chart_type in ["pie", "donut"]:
            return self._create_pie_or_donut_chart(data, title, palette, chart_type, safe_title)
        if chart_type == "scatter":
            return self._create_scatter_plot(data, title, palette, safe_title)
        
        return self._create_placeholder_chart(f"Unsupported Chart: {chart_type}")

    def _create_bar_chart(self, data, title, palette, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        if not all([labels, values, len(labels) == len(values)]): 
            return self._create_placeholder_chart(title)
        
        # Validate that values are numeric and not lists
        try:
            # Convert to simple numeric values
            clean_values = []
            for val in values:
                if isinstance(val, (list, dict)):
                    # If it's a list or dict, try to extract a numeric value
                    if isinstance(val, list) and len(val) > 0:
                        clean_values.append(float(val[0]) if isinstance(val[0], (int, float)) else 0)
                    else:
                        clean_values.append(0)
                else:
                    clean_values.append(float(val) if isinstance(val, (int, float)) else 0)
            
            # Ensure labels are strings
            clean_labels = [str(label) for label in labels]
            
        except (ValueError, TypeError):
            return self._create_placeholder_chart(f"Invalid data for {title}")
        
        fig, ax = plt.subplots(figsize=(10, 7))
        orient = 'h' if chart_type == "horizontalBar" else 'v'
        
        try:
            sns.barplot(x=clean_values if orient == 'h' else clean_labels, 
                       y=clean_labels if orient == 'h' else clean_values, 
                       ax=ax, palette=palette, orient=orient)
        except Exception as e:
            print(f"  ⚠️ Error creating bar chart for '{title}': {e}")
            return self._create_placeholder_chart(f"Chart creation failed for {title}")
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"bar_{safe_title}")

    def _create_line_or_area_chart(self, data, title, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        if not all([labels, values, len(labels) == len(values)]): 
            return self._create_placeholder_chart(title)
        
        # Validate that values are numeric and not lists
        try:
            # Convert to simple numeric values
            clean_values = []
            for val in values:
                if isinstance(val, (list, dict)):
                    # If it's a list or dict, try to extract a numeric value
                    if isinstance(val, list) and len(val) > 0:
                        clean_values.append(float(val[0]) if isinstance(val[0], (int, float)) else 0)
                    else:
                        clean_values.append(0)
                else:
                    clean_values.append(float(val) if isinstance(val, (int, float)) else 0)
            
            # Ensure labels are strings
            clean_labels = [str(label) for label in labels]
            
        except (ValueError, TypeError):
            return self._create_placeholder_chart(f"Invalid data for {title}")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(clean_labels, clean_values, marker='o', color=self.primary_color, lw=2)
        if chart_type == "area":
            ax.fill_between(clean_labels, clean_values, alpha=0.2, color=self.primary_color)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.tick_params(axis='x', rotation=25)
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_pie_or_donut_chart(self, data, title, palette, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        if not all([labels, values]): return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        wedgeprops = {"width": 0.4, "edgecolor": "w"} if chart_type == "donut" else {}
        colors = list(sns.color_palette(palette, len(labels)))  # type: ignore
        pctdistance = 0.80 if chart_type == "donut" else 0.6
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=wedgeprops, pctdistance=pctdistance)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('equal')
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_scatter_plot(self, data, title, palette, safe_title):
        points = data.get("points", [])
        if not points or not all('x' in p and 'y' in p for p in points): return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = list(sns.color_palette(palette, len(points)))  # type: ignore
        for i, p in enumerate(points):
            ax.scatter(p['x'], p['y'], s=p.get('size', 150), alpha=0.7, label=p.get('name'), color=colors[i])
            if p.get('name'):
                ax.text(p['x'], p['y'], f" {p['name']}", fontsize=9)
        ax.set_title(title, fontweight='bold')
        ax.legend()
        ax.grid(True)
        return self._save_plot_to_file(fig, f"scatter_{safe_title}")