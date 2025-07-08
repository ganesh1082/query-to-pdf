# query-to-pdf/enhanced_visualization_generator.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import os
from typing import Dict, Any, Optional, List
import warnings
from dotenv import load_dotenv
import re
from datetime import datetime

# Load environment variables
load_dotenv()

warnings.simplefilter(action='ignore', category=FutureWarning)

# Import charts from visuals/charts.py
try:
    from visuals.charts import get_chart_catalog, _CHART_REGISTRY
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("⚠️ visuals.charts module not available, using fallback chart implementations")

class PremiumVisualizationGenerator:
    """Creates a diverse variety of professional charts and saves them as image files."""
    
    def __init__(self, brand_colors: Dict[str, str]):
        self.primary_color = brand_colors.get("primary", "#0D203D")
        self.secondary_color = brand_colors.get("secondary", "#666666")
        self.accent_color = brand_colors.get("accent", "#4A90E2")
        self.background_color = brand_colors.get("background", "#F7FAFC")
        
        # Create a custom color palette based on template colors
        self.custom_palette = [
            self.primary_color,
            self.accent_color,
            self.secondary_color,
            self._adjust_color_brightness(self.primary_color, 0.7),
            self._adjust_color_brightness(self.accent_color, 0.7),
            self._adjust_color_brightness(self.secondary_color, 0.7),
        ]
        
        plt.style.use('seaborn-v0_8-whitegrid')
        self.temp_dir = os.getenv("TEMP_DIR", "temp_charts")
        os.makedirs(self.temp_dir, exist_ok=True)

    def _adjust_color_brightness(self, hex_color: str, factor: float) -> str:
        """Adjust the brightness of a hex color by a factor."""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Adjust brightness
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return hex_color

    def _get_template_palette(self, num_colors: int) -> list:
        """Get a color palette based on template colors with gradient shades."""
        print(f"  🎨 Debug - Generating palette for {num_colors} colors")
        
        # Start with base colors
        base_colors = [self.primary_color, self.accent_color, self.secondary_color]
        extended_palette = base_colors.copy()
        
        print(f"  🎨 Debug - Base colors: {base_colors}")
        
        # Generate a comprehensive palette with unique colors
        color_variations = []
        
        # Brightness variations
        for color in base_colors:
            color_variations.extend([
                self._adjust_color_brightness(color, 1.3),  # Lighter
                self._adjust_color_brightness(color, 1.6),  # Much lighter
                self._adjust_color_brightness(color, 0.7),  # Darker
                self._adjust_color_brightness(color, 0.4),  # Much darker
            ])
        
        # Hue variations (complementary and analogous)
        for color in base_colors:
            color_variations.extend([
                self._shift_color_hue(color, 30),   # Analogous
                self._shift_color_hue(color, 60),   # Triadic
                self._shift_color_hue(color, 120),  # Split complementary
                self._shift_color_hue(color, 180),  # Complementary
            ])
        
        # Saturation variations
        for color in base_colors:
            color_variations.extend([
                self._desaturate_color(color, 0.8),  # Slightly desaturated
                self._desaturate_color(color, 0.6),  # More desaturated
                self._desaturate_color(color, 0.4),  # Very desaturated
            ])
        
        # Remove duplicates while preserving order
        unique_colors = []
        seen_colors = set()
        for color in base_colors + color_variations:
            if color not in seen_colors:
                unique_colors.append(color)
                seen_colors.add(color)
        
        # Take the required number of colors
        final_palette = unique_colors[:num_colors]
        
        print(f"  🎨 Debug - Generated {len(final_palette)} unique colors: {final_palette}")
        
        return final_palette

    def _shift_color_hue(self, hex_color: str, shift_degrees: int) -> str:
        """Shift the hue of a hex color by the specified degrees."""
        try:
            import colorsys
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Shift hue
            h = (h + shift_degrees / 360.0) % 1.0
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            
            # Convert to hex
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        except:
            return hex_color

    def _desaturate_color(self, hex_color: str, saturation_factor: float) -> str:
        """Desaturate a hex color by the specified factor."""
        try:
            import colorsys
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            # Convert to HSV
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            
            # Desaturate
            s = s * saturation_factor
            
            # Convert back to RGB
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            
            # Convert to hex
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        except:
            return hex_color

    def _save_plot_to_file(self, fig, filename: str) -> str:
        """Saves the Matplotlib figure to a file and returns the path."""
        try:
            # Ensure temp directory exists
            os.makedirs(self.temp_dir, exist_ok=True)
            
            filepath = os.path.join(self.temp_dir, f"{filename}.png")
            # Set transparent background
            fig.patch.set_alpha(0.0)
            fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight', transparent=True)
            plt.close(fig)
            return filepath
        except Exception as e:
            print(f"  ⚠️ Error saving chart to file: {e}")
            plt.close(fig)  # Make sure to close the figure even if saving fails
            return ""

    def _save_plot_to_assets(self, fig, filename: str) -> str:
        """Saves the Matplotlib figure to assets directory for direct PDF inclusion."""
        try:
            # Ensure assets directory exists
            assets_dir = "assets"
            os.makedirs(assets_dir, exist_ok=True)
            
            filepath = os.path.join(assets_dir, f"{filename}.png")
            # Set transparent background
            fig.patch.set_alpha(0.0)
            fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight', transparent=True)
            plt.close(fig)
            return filepath
        except Exception as e:
            print(f"  ⚠️ Error saving chart to assets: {e}")
            plt.close(fig)  # Make sure to close the figure even if saving fails
            return ""

    def _create_placeholder_chart(self, title: str) -> str:
        """Creates a placeholder image indicating missing data."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            # Set transparent background
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            ax.text(0.5, 0.5, "Data Not Available\nOr Malformed", ha='center', va='center', fontsize=18, color='#999')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(False)
            ax.set_xticks([])
            ax.set_yticks([])
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            return self._save_plot_to_file(fig, f"placeholder_{safe_title}")
        except Exception as e:
            print(f"  ⚠️ Error creating placeholder chart: {e}")
            # Return empty string if even placeholder creation fails
            return ""

    def _get_palette(self, name: Optional[str]) -> str:
        """Returns a valid seaborn color palette name."""
        return name if name in ["viridis", "mako", "husl", "coolwarm", "rocket", "crest"] else "viridis"

    def create_chart(self, section_data: Dict[str, Any]) -> str:
        """Public method to create any chart based on the provided section data."""
        chart_type = section_data.get("chart_type")
        data = section_data.get("chart_data")
        title = section_data.get("title")
        palette = self._get_palette(section_data.get("color_palette"))
        
        print(f"  🔍 Debug - Chart: {title}")
        print(f"  🔍 Debug - Type: {chart_type}")
        print(f"  🔍 Debug - Data: {data}")
        
        # Enhanced validation with better error messages
        if not chart_type or chart_type == "none":
            print(f"  ⚠️ No chart type specified for: {title}")
            return ""
        
        if not data or not isinstance(data, dict) or len(data) == 0:
            print(f"  ⚠️ Missing or empty chart data for: {title}")
            return self._create_placeholder_chart(f"Data Missing: {title}")
        
        if not title:
            print(f"  ⚠️ Missing title for chart")
            return self._create_placeholder_chart("Untitled Chart")

        safe_title = "".join(c for c in (title or "") if c.isalnum()).replace(' ', '_')[:30]

        # Basic charts
        if chart_type in ["bar", "horizontalBar"]:
            return self._create_bar_chart(data, title, palette, chart_type, safe_title)
        if chart_type in ["line", "area"]:
            return self._create_line_or_area_chart(data, title, chart_type, safe_title)
        if chart_type in ["pie", "donut"]:
            return self._create_pie_or_donut_chart(data, title, palette, chart_type, safe_title)
        if chart_type == "scatter":
            return self._create_scatter_plot(data, title, palette, safe_title)
        
        # Multi-series charts
        if chart_type == "stackedBar":
            return self._create_stacked_bar_chart(data, title, palette, safe_title)
        if chart_type == "multiLine":
            return self._create_multi_line_chart(data, title, safe_title)
        
        # Advanced analytics
        if chart_type == "radar":
            return self._create_radar_chart(data, title, safe_title)
        if chart_type == "bubble":
            return self._create_bubble_chart(data, title, safe_title)
        
        # Business process charts
        if chart_type == "waterfall":
            return self._create_waterfall_chart(data, title, safe_title)
        if chart_type == "funnel":
            return self._create_funnel_chart(data, title, safe_title)
        if chart_type == "flowchart":
            return self._create_flowchart_chart(data, title, safe_title)
        
        # Specialized charts
        if chart_type == "heatmap":
            return self._create_heatmap_chart(data, title, safe_title)
        if chart_type == "gauge":
            return self._create_gauge_chart(data, title, safe_title)
        if chart_type == "treeMap":
            return self._create_tree_map_chart(data, title, safe_title)
        if chart_type == "sunburst":
            return self._create_sunburst_chart(data, title, safe_title)
        
        # Financial charts
        if chart_type == "candlestick":
            return self._create_candlestick_chart(data, title, safe_title)
        
        # Statistical charts
        if chart_type == "boxPlot":
            return self._create_box_plot_chart(data, title, safe_title)
        if chart_type == "violinPlot":
            return self._create_violin_plot_chart(data, title, safe_title)
        if chart_type == "histogram":
            return self._create_histogram_chart(data, title, safe_title)
        if chart_type == "pareto":
            return self._create_pareto_chart(data, title, safe_title)
        
        print(f"  ⚠️ Unsupported chart type: {chart_type}")
        return self._create_placeholder_chart(f"Unsupported: {chart_type}")

    def create_chart_for_pdf(self, section_data: Dict[str, Any]) -> str:
        """Creates a chart and saves it to assets directory for direct PDF inclusion."""
        chart_type = section_data.get("chart_type")
        data = section_data.get("chart_data")
        title = section_data.get("title")
        palette = self._get_palette(section_data.get("color_palette"))
        
        print(f"  🔍 Debug - PDF Chart: {title}")
        print(f"  🔍 Debug - Type: {chart_type}")
        print(f"  🔍 Debug - Data: {data}")
        
        # Enhanced validation with better error messages
        if not chart_type or chart_type == "none":
            print(f"  ⚠️ No chart type specified for: {title}")
            return ""
        
        if not data or not isinstance(data, dict) or len(data) == 0:
            print(f"  ⚠️ Missing or empty chart data for: {title}")
            # Try to generate meaningful default data based on chart type
            default_data = self._generate_default_chart_data(chart_type, title)
            if default_data:
                print(f"  🔧 Using generated default data for: {title}")
                data = default_data
            else:
                return self._create_placeholder_chart_for_pdf(f"Data Missing: {title}")
        
        if not title:
            print(f"  ⚠️ Missing title for chart")
            return self._create_placeholder_chart_for_pdf("Untitled Chart")

        safe_title = "".join(c for c in (title or "") if c.isalnum()).replace(' ', '_')[:30]

        # ONLY use charts from visuals/charts.py registry
        if CHARTS_AVAILABLE and chart_type in _CHART_REGISTRY:
            try:
                print(f"  🎨 Using registry chart: {chart_type}")
                return self._create_chart_with_registry(chart_type, data, title, safe_title)
            except Exception as e:
                print(f"  ⚠️ Registry chart failed: {e}")
                return self._create_placeholder_chart_for_pdf(f"Chart creation failed: {title}")
        else:
            print(f"  ⚠️ Chart type '{chart_type}' not available in registry")
            return self._create_placeholder_chart_for_pdf(f"Unsupported chart type: {chart_type}")

    def _create_chart_with_registry(self, chart_type: str, data: Dict[str, Any], title: str, safe_title: str) -> str:
        """Create chart using the centralized chart registry from visuals/charts.py"""
        if not CHARTS_AVAILABLE or chart_type not in _CHART_REGISTRY:
            raise ValueError(f"Chart type {chart_type} not available in registry")
        
        chart_func = _CHART_REGISTRY[chart_type]["func"]
        
        # Create figure with transparent background
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Apply template colors
        self._apply_template_colors(ax)
        
        # Call the chart function
        chart_func(data, ax)
        
        # Set title
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        
        # Style the chart
        self._style_chart(ax)
        
        plt.tight_layout()
        return self._save_plot_to_assets(fig, f"{chart_type}_{safe_title}")

    def _apply_template_colors(self, ax):
        """Apply template colors to the chart"""
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        ax.tick_params(colors=self.secondary_color)

    def _style_chart(self, ax):
        """Apply consistent styling to charts"""
        # Additional styling can be added here
        pass

    def _generate_default_chart_data(self, chart_type: str, title: Optional[str]) -> Optional[Dict[str, Any]]:
        """Generate meaningful default chart data based on chart type and title."""
        try:
            if chart_type == "area":
                # Generate area chart data with trend
                return {
                    "labels": ["2020", "2021", "2022", "2023", "2024", "2025"],
                    "values": [100, 120, 140, 160, 180, 200]
                }
            elif chart_type == "line":
                # Generate line chart data with growth trend
                return {
                    "labels": ["Q1", "Q2", "Q3", "Q4"],
                    "values": [85, 95, 105, 115]
                }
            elif chart_type == "bar":
                # Generate bar chart data
                return {
                    "labels": ["Category A", "Category B", "Category C", "Category D"],
                    "values": [25, 35, 20, 20]
                }
            elif chart_type == "pie":
                # Generate pie chart data
                return {
                    "labels": ["Primary", "Secondary", "Tertiary", "Other"],
                    "values": [40, 30, 20, 10]
                }
            elif chart_type == "donut":
                # Generate donut chart data
                return {
                    "labels": ["Segment 1", "Segment 2", "Segment 3", "Segment 4"],
                    "values": [35, 25, 25, 15]
                }
            elif chart_type == "scatter":
                # Generate scatter plot data
                return {
                    "labels": ["Point A", "Point B", "Point C", "Point D", "Point E"],
                    "x_values": [10, 20, 30, 40, 50],
                    "y_values": [15, 25, 35, 45, 55],
                    "sizes": [100, 150, 200, 250, 300]
                }
            elif chart_type == "horizontalBar":
                # Generate horizontal bar chart data
                return {
                    "labels": ["Group A", "Group B", "Group C", "Group D"],
                    "values": [30, 25, 20, 25]
                }
            elif chart_type == "gauge":
                # Generate gauge chart data
                return {
                    "value": 75,
                    "max": 100,
                    "label": "Performance Score"
                }
            elif chart_type == "radar":
                # Generate radar chart data
                return {
                    "labels": ["Quality", "Speed", "Cost", "Innovation", "Service"],
                    "values": [80, 70, 85, 75, 90]
                }
            else:
                return None
        except Exception as e:
            print(f"  ⚠️ Error generating default data: {e}")
            return None

    def _create_placeholder_chart_for_pdf(self, title: str) -> str:
        """Creates a placeholder image in assets directory for PDF inclusion."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            # Set transparent background
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            ax.text(0.5, 0.5, "Data Not Available\nOr Malformed", ha='center', va='center', fontsize=18, color='#999')
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(False)
            ax.set_xticks([])
            ax.set_yticks([])
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
            return self._save_plot_to_assets(fig, f"placeholder_{safe_title}")
        except Exception as e:
                    print(f"  ⚠️ Error creating placeholder chart for PDF: {e}")
        return ""

    # PDF-specific chart creation methods (wrappers around existing methods)
    def _create_bar_chart_for_pdf(self, data, title, palette, chart_type, safe_title):
        """Create bar chart for PDF inclusion"""
        labels, values = data.get("labels", []), data.get("values", [])
        
        if not all([labels, values, len(labels) == len(values)]): 
            return self._create_placeholder_chart_for_pdf(title)
        
        try:
            clean_values = []
            for val in values:
                if isinstance(val, (list, dict)):
                    if isinstance(val, list) and len(val) > 0:
                        clean_values.append(float(val[0]) if isinstance(val[0], (int, float)) else 0)
                    else:
                        clean_values.append(0)
                else:
                    clean_values.append(float(val) if isinstance(val, (int, float)) else 0)
            
            clean_labels = [str(label) for label in labels]
            
        except (ValueError, TypeError):
            return self._create_placeholder_chart_for_pdf(f"Invalid data for {title}")
        
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        orient = 'h' if chart_type == "horizontalBar" else 'v'
        
        try:
            template_colors = self._get_template_palette(len(clean_labels))
            
            if orient == 'h':
                bars = ax.barh(clean_labels, clean_values, color=template_colors)
            else:
                bars = ax.bar(clean_labels, clean_values, color=template_colors)
            
            for i, bar in enumerate(bars):
                height = bar.get_height() if orient == 'v' else bar.get_width()
                ax.text(bar.get_x() + bar.get_width()/2. if orient == 'v' else height + max(clean_values)*0.01,
                       bar.get_y() + bar.get_height()/2. if orient == 'v' else bar.get_y() + bar.get_height()/2.,
                       f'{height:.1f}',
                       ha='center', va='center', fontweight='bold', fontsize=10, color='white')
            
        except Exception as e:
            print(f"  ⚠️ Error creating bar chart for PDF '{title}': {e}")
            return self._create_placeholder_chart_for_pdf(f"Chart creation failed for {title}")
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xlabel('Values' if orient == 'v' else '', color=self.secondary_color)
        ax.set_ylabel('Categories' if orient == 'v' else 'Values', color=self.secondary_color)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        ax.tick_params(colors=self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_assets(fig, f"bar_{safe_title}")

    def _create_line_or_area_chart_for_pdf(self, data, title, chart_type, safe_title):
        """Create line/area chart for PDF inclusion"""
        labels, values = data.get("labels", []), data.get("values", [])
        series = data.get("series", [])
        
        if series and isinstance(series, list) and len(series) > 0 and isinstance(series[0], dict):
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            template_colors = self._get_template_palette(len(series))
            
            for i, series_obj in enumerate(series):
                if isinstance(series_obj, dict) and 'name' in series_obj and 'values' in series_obj:
                    series_name = series_obj['name']
                    series_values = series_obj['values']
                    if len(series_values) == len(labels):
                        color = template_colors[i % len(template_colors)]
                        ax.plot(labels, series_values, marker='o', color=color, lw=2, label=series_name)
                        if chart_type == "area":
                            ax.fill_between(labels, series_values, alpha=0.2, color=color)
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            ax.legend(frameon=False)
            ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
            ax.tick_params(axis='y', colors=self.secondary_color)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.secondary_color)
            ax.spines['bottom'].set_color(self.secondary_color)
            
            plt.tight_layout()
            return self._save_plot_to_assets(fig, f"{chart_type}_{safe_title}")
        else:
            # Single series
            if not all([labels, values, len(labels) == len(values)]):
                return self._create_placeholder_chart_for_pdf(title)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            try:
                clean_values = [float(val) if isinstance(val, (int, float)) else 0 for val in values]
                clean_labels = [str(label) for label in labels]
                
                ax.plot(clean_labels, clean_values, marker='o', color=self.accent_color, lw=2)
                if chart_type == "area":
                    ax.fill_between(clean_labels, clean_values, alpha=0.2, color=self.accent_color)
                
            except Exception as e:
                print(f"  ⚠️ Error creating line chart for PDF '{title}': {e}")
                return self._create_placeholder_chart_for_pdf(f"Chart creation failed for {title}")
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
            ax.tick_params(axis='y', colors=self.secondary_color)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.secondary_color)
            ax.spines['bottom'].set_color(self.secondary_color)
            
            plt.tight_layout()
            return self._save_plot_to_assets(fig, f"{chart_type}_{safe_title}")

    def _create_pie_or_donut_chart_for_pdf(self, data, title, palette, chart_type, safe_title):
        """Create pie/donut chart for PDF inclusion using visuals/charts.py registry"""
        labels, values = data.get("labels", []), data.get("values", [])
        
        if not all([labels, values, len(labels) == len(values)]):
            return self._create_placeholder_chart_for_pdf(title)
        
        try:
            clean_values = [float(val) if isinstance(val, (int, float)) else 0 for val in values]
            clean_labels = [str(label) for label in labels]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            template_colors = self._get_template_palette(len(clean_labels))
            
            # Use the registry function from visuals/charts.py
            if CHARTS_AVAILABLE and chart_type in _CHART_REGISTRY:
                chart_func = _CHART_REGISTRY[chart_type]["func"]
                # Create data dict in the format expected by the registry
                chart_data = {
                    "labels": clean_labels,
                    "values": clean_values
                }
                chart_func(chart_data, ax)
            else:
                # Fallback to manual implementation
                if chart_type == "donut":
                    pie_result = ax.pie(clean_values, labels=clean_labels, colors=template_colors, 
                                       autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))
                else:
                    pie_result = ax.pie(clean_values, labels=clean_labels, colors=template_colors, 
                                       autopct='%1.1f%%', startangle=90)
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            
            plt.tight_layout()
            return self._save_plot_to_assets(fig, f"{chart_type}_{safe_title}")
            
        except Exception as e:
            print(f"  ⚠️ Error creating pie chart for PDF '{title}': {e}")
            return self._create_placeholder_chart_for_pdf(f"Chart creation failed for {title}")

    def _create_scatter_plot_for_pdf(self, data, title, palette, safe_title):
        """Create scatter plot for PDF inclusion"""
        x_values = data.get("x_values", [])
        y_values = data.get("y_values", [])
        sizes = data.get("sizes", [])
        
        if not all([x_values, y_values, len(x_values) == len(y_values)]):
            return self._create_placeholder_chart_for_pdf(title)
        
        try:
            clean_x = [float(val) if isinstance(val, (int, float)) else 0 for val in x_values]
            clean_y = [float(val) if isinstance(val, (int, float)) else 0 for val in y_values]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            if sizes and len(sizes) == len(clean_x):
                clean_sizes = [float(size) if isinstance(size, (int, float)) else 100 for size in sizes]
                ax.scatter(clean_x, clean_y, s=clean_sizes, alpha=0.6, color=self.accent_color)
            else:
                ax.scatter(clean_x, clean_y, alpha=0.6, color=self.accent_color)
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            ax.set_xlabel('X Values', color=self.secondary_color)
            ax.set_ylabel('Y Values', color=self.secondary_color)
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.secondary_color)
            ax.spines['bottom'].set_color(self.secondary_color)
            ax.tick_params(colors=self.secondary_color)
            
            plt.tight_layout()
            return self._save_plot_to_assets(fig, f"scatter_{safe_title}")
            
        except Exception as e:
            print(f"  ⚠️ Error creating scatter plot for PDF '{title}': {e}")
            return self._create_placeholder_chart_for_pdf(f"Chart creation failed for {title}")

    # Wrapper methods for other chart types (simplified versions)
    def _create_stacked_bar_chart_for_pdf(self, data, title, palette, safe_title):
        """Create stacked bar chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Stacked Bar: {title}")

    def _create_multi_line_chart_for_pdf(self, data, title, safe_title):
        """Create multi-line chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Multi-Line: {title}")

    def _create_radar_chart_for_pdf(self, data, title, safe_title):
        """Create radar chart for PDF inclusion"""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart_for_pdf(title)
        
        # Number of variables
        N = len(labels)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Add the first value at the end to close the polygon
        values = values + values[:1]
        
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Plot the radar chart
        ax.plot(angles, values, 'o-', linewidth=2, color=self.primary_color)
        ax.fill(angles, values, alpha=0.25, color=self.primary_color)
        
        # Set the labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color=self.secondary_color)
        
        # Set the y-axis limits
        ax.set_ylim(0, max(values) * 1.1)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        
        plt.tight_layout()
        return self._save_plot_to_assets(fig, f"radar_{safe_title}")

    def _create_bubble_chart_for_pdf(self, data, title, safe_title):
        """Create bubble chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Bubble: {title}")

    def _create_waterfall_chart_for_pdf(self, data, title, safe_title):
        """Create waterfall chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Waterfall: {title}")

    def _create_funnel_chart_for_pdf(self, data, title, safe_title):
        """Create funnel chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Funnel: {title}")

    def _create_heatmap_chart_for_pdf(self, data, title, safe_title):
        """Create heatmap chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Heatmap: {title}")

    def _create_gauge_chart_for_pdf(self, data, title, safe_title):
        """Create gauge chart for PDF inclusion"""
        value = data.get("value", 0)
        max_val = data.get("max", 100)
        label = data.get("label", "Value")
        
        if not isinstance(value, (int, float)) or not isinstance(max_val, (int, float)):
            return self._create_placeholder_chart_for_pdf(title)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create gauge
        percentage = value / max_val
        
        # Create pie chart for gauge
        sizes = [percentage, 1 - percentage]
        colors = [self.primary_color, self.secondary_color]
        
        pie_result = ax.pie(sizes, colors=colors, startangle=90, 
                           counterclock=False, wedgeprops=dict(width=0.5))
        wedges, texts = pie_result[:2]  # Only take first two elements
        
        # Add center text
        ax.text(0, 0, f'{value}\n{label}', ha='center', va='center', 
               fontsize=16, fontweight='bold', color=self.primary_color)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.axis('equal')
        
        plt.tight_layout()
        return self._save_plot_to_assets(fig, f"gauge_{safe_title}")

    def _create_tree_map_chart_for_pdf(self, data, title, safe_title):
        """Create tree map chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Tree Map: {title}")

    def _create_sunburst_chart_for_pdf(self, data, title, safe_title):
        """Create sunburst chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Sunburst: {title}")

    def _create_candlestick_chart_for_pdf(self, data, title, safe_title):
        """Create candlestick chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Candlestick: {title}")

    def _create_box_plot_chart_for_pdf(self, data, title, safe_title):
        """Create box plot chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Box Plot: {title}")

    def _create_violin_plot_chart_for_pdf(self, data, title, safe_title):
        """Create violin plot chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Violin Plot: {title}")

    def _create_histogram_chart_for_pdf(self, data, title, safe_title):
        """Create histogram chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Histogram: {title}")

    def _create_pareto_chart_for_pdf(self, data, title, safe_title):
        """Create pareto chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Pareto: {title}")

    def _create_flowchart_chart_for_pdf(self, data, title, safe_title):
        """Create flowchart chart for PDF inclusion"""
        return self._create_placeholder_chart_for_pdf(f"Flowchart: {title}")

    def _create_bar_chart(self, data, title, palette, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        print(f"  🔍 Debug - Labels: {labels}")
        print(f"  🔍 Debug - Values: {values}")
        print(f"  🔍 Debug - Labels type: {type(labels)}, Values type: {type(values)}")
        
        if not all([labels, values, len(labels) == len(values)]): 
            print(f"  ⚠️ Data validation failed: labels={bool(labels)}, values={bool(values)}, lengths_match={len(labels) == len(values) if labels and values else False}")
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
        # Set transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        orient = 'h' if chart_type == "horizontalBar" else 'v'
        
        try:
            # Use template-specific colors instead of seaborn palette
            template_colors = self._get_template_palette(len(clean_labels))
            print(f"  🎨 Debug - Bar chart using colors: {template_colors}")
            
            if orient == 'h':
                bars = ax.barh(clean_labels, clean_values, color=template_colors)
            else:
                bars = ax.bar(clean_labels, clean_values, color=template_colors)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height() if orient == 'v' else bar.get_width()
                ax.text(bar.get_x() + bar.get_width()/2. if orient == 'v' else height + max(clean_values)*0.01,
                       bar.get_y() + bar.get_height()/2. if orient == 'v' else bar.get_y() + bar.get_height()/2.,
                       f'{height:.1f}',
                       ha='center', va='center', fontweight='bold', fontsize=10, color='white')
            
        except Exception as e:
            print(f"  ⚠️ Error creating bar chart for '{title}': {e}")
            return self._create_placeholder_chart(f"Chart creation failed for {title}")
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xlabel('Values' if orient == 'v' else '', color=self.secondary_color)
        ax.set_ylabel('Categories' if orient == 'v' else 'Values', color=self.secondary_color)
        
        # Style the chart with template colors
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        ax.tick_params(colors=self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"bar_{safe_title}")

    def _create_line_or_area_chart(self, data, title, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        series = data.get("series", [])
        legend = data.get("legend", [])
        print(f"  🔍 Debug - Line Chart Labels: {labels}")
        print(f"  🔍 Debug - Line Chart Values: {values}")
        print(f"  🔍 Debug - Line Chart Series: {series}")
        print(f"  🔍 Debug - Line Chart Legend: {legend}")
        print(f"  🔍 Debug - Line Chart Labels type: {type(labels)}, Values type: {type(values)}")
        
        # Handle multi-series data with series as array of objects
        if series and isinstance(series, list) and len(series) > 0 and isinstance(series[0], dict):
            print(f"  🔍 Debug - Processing multi-series line chart with object structure")
            fig, ax = plt.subplots(figsize=(10, 6))
            # Set transparent background
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            # Use template-specific colors
            template_colors = self._get_template_palette(len(series))
            print(f"  🎨 Debug - Multi-series line chart using colors: {template_colors}")
            
            for i, series_obj in enumerate(series):
                if isinstance(series_obj, dict) and 'name' in series_obj and 'values' in series_obj:
                    series_name = series_obj['name']
                    series_values = series_obj['values']
                    if len(series_values) == len(labels):
                        color = template_colors[i % len(template_colors)]
                        print(f"  🎨 Debug - Series '{series_name}' using color: {color}")
                        ax.plot(labels, series_values, marker='o', color=color, lw=2, label=series_name)
                        if chart_type == "area":
                            ax.fill_between(labels, series_values, alpha=0.2, color=color)
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            ax.legend(frameon=False)
            ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
            ax.tick_params(axis='y', colors=self.secondary_color)
            
            # Style the chart with template colors
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.secondary_color)
            ax.spines['bottom'].set_color(self.secondary_color)
            
            plt.tight_layout()
            return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")
        
        # Handle multi-series data with either 'series' or 'legend' field (old format)
        if (series or legend) and isinstance(values, list) and len(values) > 0 and isinstance(values[0], list):
            print(f"  🔍 Debug - Processing multi-series line chart with array structure")
            fig, ax = plt.subplots(figsize=(10, 6))
            # Set transparent background
            fig.patch.set_alpha(0.0)
            ax.patch.set_alpha(0.0)
            
            # Use template-specific colors
            template_colors = self._get_template_palette(len(values))
            
            # Use legend if available, otherwise use series, otherwise generate default names
            series_names = legend if legend else (series if series else [f"Series {i+1}" for i in range(len(values))])
            
            for i, (series_name, series_values) in enumerate(zip(series_names, values)):
                if len(series_values) == len(labels):
                    color = template_colors[i % len(template_colors)]
                    ax.plot(labels, series_values, marker='o', color=color, lw=2, label=series_name)
                    if chart_type == "area":
                        ax.fill_between(labels, series_values, alpha=0.2, color=color)
            
            ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
            ax.legend(frameon=False)
            ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
            ax.tick_params(axis='y', colors=self.secondary_color)
            
            # Style the chart with template colors
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.secondary_color)
            ax.spines['bottom'].set_color(self.secondary_color)
            
            plt.tight_layout()
            return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")
        
        # Handle single-series data (original logic)
        if not all([labels, values, len(labels) == len(values)]): 
            print(f"  ⚠️ Line chart data validation failed: labels={bool(labels)}, values={bool(values)}, lengths_match={len(labels) == len(values) if labels and values else False}")
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
        # Set transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        ax.plot(clean_labels, clean_values, marker='o', color=self.primary_color, lw=2)
        if chart_type == "area":
            ax.fill_between(clean_labels, clean_values, alpha=0.2, color=self.primary_color)
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart with template colors
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_pie_or_donut_chart(self, data, title, palette, chart_type, safe_title):
        labels, values = data.get("labels", []), data.get("values", [])
        if not all([labels, values]): return self._create_placeholder_chart(title)
        
        # Use much smaller figure size for pie/donut charts
        fig, ax = plt.subplots(figsize=(3, 2.5))
        # Set transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        wedgeprops = {"width": 0.4, "edgecolor": "w"} if chart_type == "donut" else {}
        
        # Use template-specific colors instead of seaborn palette
        template_colors = self._get_template_palette(len(labels))
        print(f"  🎨 Debug - Pie chart using colors: {template_colors}")
        
        pctdistance = 0.80 if chart_type == "donut" else 0.6
        
        # Create a function to format percentage with smaller font
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return f'{pct:.1f}%' if pct > 5 else ''
            return my_autopct
        
        # Use smaller font sizes for labels and percentages
        ax.pie(values, labels=labels, autopct=make_autopct(values), startangle=90, 
               colors=template_colors, wedgeprops=wedgeprops, pctdistance=pctdistance,
               textprops={'fontsize': 6, 'color': self.secondary_color})  # Even smaller font for compact charts
        
        ax.set_title(title, fontsize=8, fontweight='bold', color=self.primary_color)  # Smaller title font
        ax.axis('equal')
        
        # Adjust layout to prevent text cutoff
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"{chart_type}_{safe_title}")

    def _create_scatter_plot(self, data, title, palette, safe_title):
        # Handle different data formats for scatter plots
        points = data.get("points", [])
        labels = data.get("labels", [])
        values = data.get("values", [])
        x_values = data.get("x_values", [])  # Changed from "x" to "x_values"
        y_values = data.get("y_values", [])  # Changed from "y" to "y_values"
        sizes = data.get("sizes", [])
        
        # If we have labels and values with x,y coordinates, convert to points format
        if labels and values and isinstance(values, list) and len(values) > 0:
            if isinstance(values[0], dict) and 'x' in values[0] and 'y' in values[0]:
                # Convert from labels + values format to points format
                points = []
                for i, (label, value) in enumerate(zip(labels, values)):
                    if isinstance(value, dict) and 'x' in value and 'y' in value:
                        points.append({
                            'x': value['x'],
                            'y': value['y'],
                            'name': label
                        })
        
        # If we have separate x_values and y_values arrays, convert to points format
        elif x_values and y_values and isinstance(x_values, list) and isinstance(y_values, list):
            if len(x_values) == len(y_values):
                points = []
                for i, (x, y) in enumerate(zip(x_values, y_values)):
                    point_name = labels[i] if labels and i < len(labels) else f"Point {i+1}"
                    point_size = sizes[i] if sizes and i < len(sizes) else 150
                    points.append({
                        'x': x,
                        'y': y,
                        'name': point_name,
                        'size': point_size
                    })
        
        # If we have labels and simple numeric values, create a scatter plot with sequential x values
        elif labels and values and isinstance(values, list) and len(values) > 0:
            if all(isinstance(v, (int, float)) for v in values):
                points = []
                for i, (label, value) in enumerate(zip(labels, values)):
                    points.append({
                        'x': i + 1,  # Sequential x values (1, 2, 3, ...)
                        'y': value,   # Use the value as y coordinate
                        'name': label
                    })
        
        if not points or not all('x' in p and 'y' in p for p in points): 
            print(f"  ⚠️ Scatter plot data validation failed: points={bool(points)}, valid_points={all('x' in p and 'y' in p for p in points) if points else False}")
            print(f"  🔍 Debug - Available data: x_values={bool(x_values)}, y_values={bool(y_values)}, labels={bool(labels)}, values={bool(values)}")
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        # Set transparent background
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Use template-specific colors instead of seaborn palette
        template_colors = self._get_template_palette(len(points))
        print(f"  🎨 Debug - Scatter plot using colors: {template_colors}")
        
        for i, p in enumerate(points):
            color = template_colors[i % len(template_colors)]
            print(f"  🎨 Debug - Point '{p.get('name', f'Point {i}')}' using color: {color}")
            ax.scatter(p['x'], p['y'], s=p.get('size', 150), alpha=0.7, label=p.get('name'), color=color)
            if p.get('name'):
                ax.text(p['x'], p['y'], f" {p['name']}", fontsize=9, color=self.secondary_color)
        
        ax.set_title(title, fontweight='bold', color=self.primary_color)
        ax.legend(frameon=False)
        ax.grid(True, alpha=0.3, color=self.secondary_color)
        
        # Style the chart with template colors
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        ax.tick_params(colors=self.secondary_color)
        
        return self._save_plot_to_file(fig, f"scatter_{safe_title}")

    def _create_stacked_bar_chart(self, data, title, palette, safe_title):
        """Create a stacked bar chart."""
        labels = data.get("labels", [])
        series = data.get("series", [])
        
        if not labels or not series:
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Use template colors
        template_colors = self._get_template_palette(len(series))
        
        # Create stacked bars
        bottom: Optional[List[float]] = None
        for i, series_data in enumerate(series):
            if isinstance(series_data, dict) and 'values' in series_data:
                values = series_data['values']
                name = series_data.get('name', f'Series {i+1}')
                color = template_colors[i % len(template_colors)]
                
                if bottom is None:
                    bars = ax.bar(labels, values, color=color, label=name)
                    bottom = values
                else:
                    bars = ax.bar(labels, values, bottom=bottom, color=color, label=name)
                    bottom = [b + v for b, v in zip(bottom, values)]
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.legend(frameon=False)
        ax.tick_params(axis='x', rotation=25, colors=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"stackedBar_{safe_title}")

    def _create_multi_line_chart(self, data, title, safe_title):
        """Create a multi-line chart."""
        # This is already handled in _create_line_or_area_chart for multi-series
        return self._create_line_or_area_chart(data, title, "line", safe_title)

    def _create_radar_chart(self, data, title, safe_title):
        """Create a radar chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        # Number of variables
        N = len(labels)
        
        # Compute angle for each axis
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Add the first value at the end to close the polygon
        values += values[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Plot the radar chart
        ax.plot(angles, values, 'o-', linewidth=2, color=self.primary_color)
        ax.fill(angles, values, alpha=0.25, color=self.primary_color)
        
        # Set the labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color=self.secondary_color)
        
        # Set the y-axis limits
        ax.set_ylim(0, max(values) * 1.1)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"radar_{safe_title}")

    def _create_bubble_chart(self, data, title, safe_title):
        """Create a bubble chart."""
        labels = data.get("labels", [])
        x_values = data.get("x_values", [])
        y_values = data.get("y_values", [])
        sizes = data.get("sizes", [])
        
        if not all([labels, x_values, y_values]) or len(labels) != len(x_values) != len(y_values):
            return self._create_placeholder_chart(title)
        
        # Use sizes if provided, otherwise default to 100
        if not sizes:
            sizes = [100] * len(labels)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Use template colors
        template_colors = self._get_template_palette(len(labels))
        
        for i, (label, x, y, size) in enumerate(zip(labels, x_values, y_values, sizes)):
            color = template_colors[i % len(template_colors)]
            ax.scatter(x, y, s=size, alpha=0.7, color=color, label=label)
            ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points', 
                       fontsize=9, color=self.secondary_color)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.legend(frameon=False)
        ax.grid(True, alpha=0.3, color=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        ax.tick_params(colors=self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"bubble_{safe_title}")

    def _create_waterfall_chart(self, data, title, safe_title):
        """Create a waterfall chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Calculate positions for bars
        positions = list(range(len(labels)))
        
        # Separate positive and negative values
        positive_values = [v if v > 0 else 0 for v in values]
        negative_values = [v if v < 0 else 0 for v in values]
        
        # Calculate cumulative values for positioning
        cumulative = 0
        bar_positions = []
        for i, val in enumerate(values):
            bar_positions.append(cumulative)
            cumulative += val
        
        # Create bars
        colors = []
        for val in values:
            if val > 0:
                colors.append(self.primary_color)
            elif val < 0:
                colors.append(self.accent_color)
            else:
                colors.append(self.secondary_color)
        
        bars = ax.bar(positions, values, bottom=bar_positions, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_y() + height/2.,
                   f'{val:.1f}', ha='center', va='center', fontweight='bold', fontsize=10)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=45, ha='right', color=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"waterfall_{safe_title}")

    def _create_funnel_chart(self, data, title, safe_title):
        """Create a funnel chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(8, 10))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Normalize values to create funnel effect
        max_val = max(values)
        normalized_values = [v / max_val for v in values]
        
        # Create funnel bars
        y_positions = list(range(len(labels)))
        template_colors = self._get_template_palette(len(labels))
        
        for i, (label, value, norm_val, color) in enumerate(zip(labels, values, normalized_values, template_colors)):
            # Create horizontal bar with decreasing width
            bar_width = norm_val * 0.8  # Scale down for visual appeal
            ax.barh(i, bar_width, height=0.6, color=color, alpha=0.8)
            
            # Add value label
            ax.text(bar_width + 0.05, i, f'{value}', va='center', fontweight='bold', 
                   color=self.secondary_color, fontsize=10)
            
            # Add stage label
            ax.text(-0.1, i, label, va='center', ha='right', color=self.secondary_color, fontsize=10)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, len(labels) - 0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"funnel_{safe_title}")

    def _create_heatmap_chart(self, data, title, safe_title):
        """Create a heatmap chart."""
        labels = data.get("labels", [])
        categories = data.get("categories", [])
        values = data.get("values", [])
        
        if not all([labels, categories, values]):
            return self._create_placeholder_chart(title)
        
        # Convert to 2D array if needed
        if isinstance(values[0], list):
            heatmap_data = values
        else:
            # Reshape 1D array to 2D
            import numpy as np
            try:
                heatmap_data = np.array(values).reshape(len(categories), len(labels))
            except (ValueError, TypeError):
                return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create heatmap - convert to list if needed
        if hasattr(heatmap_data, 'tolist'):
            heatmap_data = heatmap_data.tolist()
        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto')  # type: ignore
        
        # Set labels
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(categories)))
        ax.set_xticklabels(labels, rotation=45, ha='right', color=self.secondary_color)
        ax.set_yticklabels(categories, color=self.secondary_color)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.ax.tick_params(colors=self.secondary_color)
        
        # Add value annotations
        for i in range(len(categories)):
            for j in range(len(labels)):
                text = ax.text(j, i, f'{heatmap_data[i][j]:.1f}',
                              ha="center", va="center", color="white", fontweight='bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"heatmap_{safe_title}")

    def _create_gauge_chart(self, data, title, safe_title):
        """Create a gauge chart."""
        value = data.get("value", 0)
        max_val = data.get("max", 100)
        label = data.get("label", "Value")
        
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create gauge
        percentage = value / max_val
        
        # Create pie chart for gauge
        sizes = [percentage, 1 - percentage]
        colors = [self.primary_color, self.secondary_color]
        
        pie_result = ax.pie(sizes, colors=colors, startangle=90, 
                           counterclock=False, wedgeprops=dict(width=0.5))
        wedges, texts = pie_result[:2]  # Only take first two elements
        
        # Add center text
        ax.text(0, 0, f'{value}\n{label}', ha='center', va='center', 
               fontsize=16, fontweight='bold', color=self.primary_color)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.axis('equal')
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"gauge_{safe_title}")

    def _create_tree_map_chart(self, data, title, safe_title):
        """Create a tree map chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        subcategories = data.get("subcategories", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create simple rectangle representation
        total = sum(values)
        template_colors = self._get_template_palette(len(labels))
        
        current_x = 0
        for i, (label, value, color) in enumerate(zip(labels, values, template_colors)):
            width = value / total
            rect = plt.Rectangle((current_x, 0), width, 1, facecolor=color, alpha=0.8)
            ax.add_patch(rect)
            
            # Add label
            ax.text(current_x + width/2, 0.5, f'{label}\n{value}', 
                   ha='center', va='center', fontweight='bold', color='white', fontsize=10)
            
            current_x += width
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"treeMap_{safe_title}")

    def _create_sunburst_chart(self, data, title, safe_title):
        """Create a sunburst chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        children = data.get("children", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create simple nested pie chart representation
        template_colors = self._get_template_palette(len(labels))
        
        # Create outer ring
        pie_result = ax.pie(values, labels=labels, colors=template_colors, 
                           startangle=90, radius=1.0)
        wedges, texts = pie_result[:2]  # Only take first two elements
        
        # Add inner ring if children data is available
        if children and len(children) == len(labels):
            inner_values = []
            inner_labels = []
            for child_list in children:
                if isinstance(child_list, list):
                    inner_values.extend([1] * len(child_list))  # Equal size for simplicity
                    inner_labels.extend(child_list)
            
            if inner_values:
                inner_colors = self._get_template_palette(len(inner_values))
                ax.pie(inner_values, labels=inner_labels, colors=inner_colors, 
                      startangle=90, radius=0.6)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.axis('equal')
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"sunburst_{safe_title}")

    def _create_candlestick_chart(self, data, title, safe_title):
        """Create a candlestick chart."""
        labels = data.get("labels", [])
        open_prices = data.get("open", [])
        high_prices = data.get("high", [])
        low_prices = data.get("low", [])
        close_prices = data.get("close", [])
        
        if not all([labels, open_prices, high_prices, low_prices, close_prices]):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create candlestick representation
        positions = list(range(len(labels)))
        
        for i, (open_price, high_price, low_price, close_price) in enumerate(zip(open_prices, high_prices, low_prices, close_prices)):
            # Determine color based on price movement
            color = self.primary_color if close_price >= open_price else self.accent_color
            
            # Draw the wick (high to low)
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)
            
            # Draw the body
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)
            
            rect = plt.Rectangle((i-0.3, body_bottom), 0.6, body_height, 
                               facecolor=color, alpha=0.8)
            ax.add_patch(rect)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=45, ha='right', color=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"candlestick_{safe_title}")

    def _create_box_plot_chart(self, data, title, safe_title):
        """Create a box plot chart."""
        labels = data.get("labels", [])
        plot_data = data.get("data", [])
        
        if not labels or not plot_data or len(labels) != len(plot_data):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create box plot
        bp = ax.boxplot(plot_data, patch_artist=True)
        
        # Set x-axis labels
        ax.set_xticklabels(labels, rotation=45, ha='right')
        
        # Color the boxes
        template_colors = self._get_template_palette(len(labels))
        for i, patch in enumerate(bp['boxes']):
            color = template_colors[i % len(template_colors)]
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.tick_params(axis='x', rotation=45, colors=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"boxPlot_{safe_title}")

    def _create_violin_plot_chart(self, data, title, safe_title):
        """Create a violin plot chart."""
        labels = data.get("labels", [])
        plot_data = data.get("data", [])
        
        if not labels or not plot_data or len(labels) != len(plot_data):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create violin plot
        vp = ax.violinplot(plot_data, positions=range(len(labels)))
        
        # Color the violins
        template_colors = self._get_template_palette(len(labels))
        bodies = list(vp['bodies'])  # type: ignore # Convert to list for enumeration
        for i, pc in enumerate(bodies):
            color = template_colors[i % len(template_colors)]
            pc.set_facecolor(color)
            pc.set_alpha(0.7)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', color=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"violinPlot_{safe_title}")

    def _create_histogram_chart(self, data, title, safe_title):
        """Create a histogram chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Create histogram
        bars = ax.bar(labels, values, color=self.primary_color, alpha=0.7)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax.tick_params(axis='x', rotation=45, colors=self.secondary_color)
        ax.tick_params(axis='y', colors=self.secondary_color)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.secondary_color)
        ax.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"histogram_{safe_title}")

    def _create_pareto_chart(self, data, title, safe_title):
        """Create a Pareto chart."""
        labels = data.get("labels", [])
        values = data.get("values", [])
        cumulative = data.get("cumulative", [])
        
        if not labels or not values or len(labels) != len(values):
            return self._create_placeholder_chart(title)
        
        fig, ax1 = plt.subplots(figsize=(12, 8))
        fig.patch.set_alpha(0.0)
        ax1.patch.set_alpha(0.0)
        
        # Create secondary y-axis for cumulative line
        ax2 = ax1.twinx()
        
        # Create bar chart
        bars = ax1.bar(labels, values, color=self.primary_color, alpha=0.7)
        
        # Create cumulative line
        if cumulative and len(cumulative) == len(labels):
            line = ax2.plot(labels, cumulative, color=self.accent_color, linewidth=2, marker='o')
        else:
            # Calculate cumulative if not provided
            cumulative_values = []
            total = sum(values)
            running_total = 0
            for value in values:
                running_total += value
                cumulative_values.append((running_total / total) * 100)
            line = ax2.plot(labels, cumulative_values, color=self.accent_color, linewidth=2, marker='o')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                    f'{value}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax1.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color)
        ax1.tick_params(axis='x', rotation=45, colors=self.secondary_color)
        ax1.tick_params(axis='y', colors=self.secondary_color)
        ax2.tick_params(axis='y', colors=self.accent_color)
        
        # Set labels
        ax1.set_ylabel('Frequency', color=self.secondary_color)
        ax2.set_ylabel('Cumulative %', color=self.accent_color)
        
        # Style the chart
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color(self.secondary_color)
        ax1.spines['bottom'].set_color(self.secondary_color)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"pareto_{safe_title}")

    def _create_flowchart_chart(self, data, title, safe_title):
        """Create a flowchart chart using matplotlib."""
        # Extract flowchart data
        nodes = data.get("nodes", [])
        connections = data.get("connections", [])
        
        if not nodes:
            return self._create_placeholder_chart(title)
        
        fig, ax = plt.subplots(figsize=(12, 10))
        fig.patch.set_alpha(0.0)
        ax.patch.set_alpha(0.0)
        
        # Set up the plot
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Define node positions (simple grid layout)
        node_positions = {}
        num_nodes = len(nodes)
        cols = min(3, num_nodes)
        rows = (num_nodes + cols - 1) // cols
        
        for i, node in enumerate(nodes):
            row = i // cols
            col = i % cols
            x = 2 + col * 3
            y = 8 - row * 2.5
            node_positions[node.get("id", f"node_{i}")] = (x, y)
        
        # Draw connections first (so they appear behind nodes)
        template_colors = self._get_template_palette(len(connections) if connections else 1)
        
        for i, connection in enumerate(connections):
            from_node = connection.get("from")
            to_node = connection.get("to")
            label = connection.get("label", "")
            
            if from_node in node_positions and to_node in node_positions:
                x1, y1 = node_positions[from_node]
                x2, y2 = node_positions[to_node]
                
                # Draw arrow
                color = template_colors[i % len(template_colors)]
                ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                           arrowprops=dict(arrowstyle='->', color=color, lw=2))
                
                # Add label if provided
                if label:
                    mid_x = (x1 + x2) / 2
                    mid_y = (y1 + y2) / 2
                    ax.text(mid_x, mid_y, label, ha='center', va='center',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),  # type: ignore
                           fontsize=8, color=self.secondary_color)
        
        # Draw nodes
        for i, node in enumerate(nodes):
            node_id = node.get("id", f"node_{i}")
            node_label = node.get("label", f"Node {i+1}")
            node_type = node.get("type", "process")  # process, decision, start, end
            
            if node_id in node_positions:
                x, y = node_positions[node_id]
                
                # Choose shape based on node type
                if node_type == "decision":
                    # Diamond shape
                    diamond_x = [x, x+0.8, x, x-0.8, x]
                    diamond_y = [y+0.6, y, y-0.6, y, y+0.6]
                    ax.fill(diamond_x, diamond_y, color=self.primary_color, alpha=0.8)
                    ax.plot(diamond_x, diamond_y, color=self.primary_color, lw=2)
                elif node_type == "start":
                    # Oval shape (approximated with ellipse)
                    ellipse = patches.Ellipse((x, y), 1.6, 1.2, 
                                            color=self.accent_color, alpha=0.8)
                    ax.add_patch(ellipse)
                    ellipse = patches.Ellipse((x, y), 1.6, 1.2, 
                                            color=self.accent_color, lw=2, fill=False)
                    ax.add_patch(ellipse)
                elif node_type == "end":
                    # Oval shape (approximated with ellipse)
                    ellipse = patches.Ellipse((x, y), 1.6, 1.2, 
                                            color=self.accent_color, alpha=0.8)
                    ax.add_patch(ellipse)
                    ellipse = patches.Ellipse((x, y), 1.6, 1.2, 
                                            color=self.accent_color, lw=2, fill=False)
                    ax.add_patch(ellipse)
                else:
                    # Rectangle for process nodes
                    rect = plt.Rectangle((x-0.8, y-0.4), 1.6, 0.8, 
                                       color=self.primary_color, alpha=0.8)
                    ax.add_patch(rect)
                    rect = plt.Rectangle((x-0.8, y-0.4), 1.6, 0.8, 
                                       color=self.primary_color, lw=2, fill=False)
                    ax.add_patch(rect)
                
                # Add node label
                ax.text(x, y, node_label, ha='center', va='center', 
                       fontsize=9, fontweight='bold', color='white')
        
        ax.set_title(title, fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        
        plt.tight_layout()
        return self._save_plot_to_file(fig, f"flowchart_{safe_title}")