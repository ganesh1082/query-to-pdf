# query-to-pdf copy/enhanced_visualization_generator.py

import matplotlib.pyplot as plt
import seaborn as sns
import base64
import os
from io import BytesIO
from typing import Dict, Any, Optional
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

class PremiumVisualizationGenerator:
    """Creates a diverse variety of professional charts based on dynamic data."""
    def __init__(self, brand_colors: Dict[str, str]):
        self.primary_color = brand_colors.get("primary", "#0D203D")
        plt.style.use('seaborn-v0_8-whitegrid')
        # Create temp directory for chart images
        self.temp_dir = "temp_charts"
        os.makedirs(self.temp_dir, exist_ok=True)

    def _save_plot_to_file(self, fig, filename: str) -> str:
        """Save plot to file and return the file path."""
        filepath = os.path.join(self.temp_dir, f"{filename}.png")
        fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight')
        plt.close(fig)
        return filepath

    def _save_plot_to_base64(self, fig) -> str:
        buf = BytesIO(); fig.savefig(buf, format='png', dpi=300, bbox_inches='tight'); plt.close(fig); return base64.b64encode(buf.getvalue()).decode('utf-8')

    def _create_placeholder_chart(self, title: str) -> str:
        fig, ax = plt.subplots(figsize=(10, 6)); ax.text(0.5, 0.5, "Data Not Available\nOr Malformed", ha='center', va='center', fontsize=18, color='#999')
        ax.set_title(title, fontsize=14, fontweight='bold'); ax.grid(False); ax.set_xticks([]); ax.set_yticks([])
        # Save as file instead of base64 for WeasyPrint compatibility
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        return self._save_plot_to_file(fig, f"placeholder_{safe_title}")

    def _get_palette(self, name: Optional[str]) -> str:
        return name if name in ["viridis", "mako", "husl", "coolwarm", "rocket", "crest"] else "viridis"

    def create_chart(self, details: Dict[str, Any]) -> str:
        """Public method to create any chart based on the provided details."""
        if not details or not isinstance(details, dict): 
            return self._create_placeholder_chart("Invalid Chart Details")
        
        chart_type = details.get("chart_type")
        data_for_chart = details.get("data")
        title = details.get("title")
        palette = self._get_palette(details.get("color_palette"))

        if not all([chart_type, data_for_chart, title]): 
            return self._create_placeholder_chart("Chart Data Missing")

        # Create safe filename from title
        if not title:
            title = "Unknown_Chart"
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')

        if chart_type in ["bar", "horizontalBar"]: 
            return self._create_bar_chart(data_for_chart, title, palette, chart_type, safe_title)
        if chart_type in ["line", "area"]: 
            return self._create_line_or_area_chart(data_for_chart, title, chart_type, safe_title)
        if chart_type in ["pie", "donut"]: 
            return self._create_pie_or_donut_chart(data_for_chart, title, palette, chart_type, safe_title)
        if chart_type == "scatter": 
            return self._create_scatter_plot(data_for_chart, title, palette, safe_title)
        
        return self._create_placeholder_chart(f"Unsupported Chart Type: {chart_type}")

    def _normalize_chart_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Chart.js format to simple format that our generators expect."""
        if not isinstance(data, dict):
            return data
        
        # If it's already in simple format, return as-is
        if 'values' in data:
            return data
        
        # Convert from Chart.js format to simple format
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        if datasets and isinstance(datasets, list) and len(datasets) > 0:
            first_dataset = datasets[0]
            if isinstance(first_dataset, dict):
                # For scatter plots, handle {x, y} format
                if 'data' in first_dataset and isinstance(first_dataset['data'], list):
                    dataset_data = first_dataset['data']
                    if dataset_data and isinstance(dataset_data[0], dict) and 'x' in dataset_data[0] and 'y' in dataset_data[0]:
                        # Scatter plot format
                        return {
                            'points': [{'x': point['x'], 'y': point['y'], 'name': f'Point {i+1}'} for i, point in enumerate(dataset_data)]
                        }
                    else:
                        # Regular dataset format
                        return {
                            'labels': labels,
                            'values': dataset_data
                        }
        
        # Fallback to original data if conversion fails
        return data

    def _create_bar_chart(self, data, title, palette, chart_type, safe_title):
        normalized_data = self._normalize_chart_data(data)
        labels, values = normalized_data.get("labels", []), normalized_data.get("values", []);
        if not all([labels, values, len(labels)==len(values)]): return self._create_placeholder_chart(title)
        fig, ax = plt.subplots(figsize=(10, 7)); orient = 'h' if chart_type == "horizontalBar" else 'v'
        sns.barplot(x=values if orient=='h' else labels, y=labels if orient=='h' else values, ax=ax, palette=palette, orient=orient)
        ax.set_title(title, fontsize=14, fontweight='bold'); plt.tight_layout()
        return self._save_plot_to_file(fig, f"bar_{safe_title}")

    def _create_line_or_area_chart(self, data, title, chart_type, safe_title):
        normalized_data = self._normalize_chart_data(data)
        labels, values = normalized_data.get("labels", []), normalized_data.get("values", []);
        if not all([labels, values, len(labels)==len(values)]): return self._create_placeholder_chart(title)
        fig, ax = plt.subplots(figsize=(10, 6)); ax.plot(labels, values, marker='o', color=self.primary_color, lw=2)
        if chart_type == "area": ax.fill_between(labels, values, alpha=0.2, color=self.primary_color)
        ax.set_title(title, fontsize=14, fontweight='bold'); ax.tick_params(axis='x', rotation=45); plt.tight_layout()
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_pie_or_donut_chart(self, data, title, palette, chart_type, safe_title):
        normalized_data = self._normalize_chart_data(data)
        labels, values = normalized_data.get("labels", []), normalized_data.get("values", []);
        if not all([labels, values]): return self._create_placeholder_chart(title)
        fig, ax = plt.subplots(figsize=(8, 8)); wedgeprops = {"width": 0.4, "edgecolor": "w"} if chart_type == "donut" else {}
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette(palette, len(labels)), wedgeprops=wedgeprops)  # type: ignore
        ax.set_title(title, fontsize=14, fontweight='bold'); ax.axis('equal')
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_scatter_plot(self, data, title, palette, safe_title):
        normalized_data = self._normalize_chart_data(data)
        points = normalized_data.get("points", []);
        if not points or not all('x' in p and 'y' in p for p in points): return self._create_placeholder_chart(title)
        fig, ax = plt.subplots(figsize=(10, 8)); colors = sns.color_palette(palette, len(points))
        for i, p in enumerate(points):
            ax.scatter(p['x'], p['y'], s=p.get('size', 150), alpha=0.7, label=p.get('name'), color=colors[i])  # type: ignore
            ax.text(p['x'] + 0.1, p['y'] + 0.1, p.get('name', ''), fontsize=9)
        ax.set_title(title, fontweight='bold'); ax.legend(); ax.grid(True)
        return self._save_plot_to_file(fig, f"scatter_{safe_title}")