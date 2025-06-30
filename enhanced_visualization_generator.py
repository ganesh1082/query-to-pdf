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
        self.temp_dir = "temp_charts"
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
        filepath = os.path.join(self.temp_dir, f"{filename}.png")
        # Set transparent background
        fig.patch.set_alpha(0.0)
        fig.savefig(filepath, format='png', dpi=300, bbox_inches='tight', transparent=True)
        plt.close(fig)
        return filepath

    def _create_placeholder_chart(self, title: str) -> str:
        """Creates a placeholder image indicating missing data."""
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
        
        if not all([chart_type, data, title]):
            print(f"  ⚠️ Missing required data: chart_type={chart_type}, data={data}, title={title}")
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
        points = data.get("points", [])
        if not points or not all('x' in p and 'y' in p for p in points): return self._create_placeholder_chart(title)
        
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