"""
Central plot registry.

Every render_* function registers itself with @chart so the LLM planner
can pull a live catalog (name, analytic goal, dimensions, complexity).
"""

from typing import Callable, Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns

# ─── Registry ──────────────────────────────────────────────────────────────
_CHART_REGISTRY: Dict[str, Dict[str, Any]] = {}

def chart(name: str,
          goal: str,
          dims: str,
          complexity: str = "medium"):
    """
    Decorator that captures metadata for each chart type.

    Args:
        name        canonical id, e.g. "scatter"
        goal        trend | correlation | composition | distribution | flow
        dims        "1D" | "2D" | "nD"
        complexity  simple | medium | advanced
    """
    def decorator(fn: Callable):
        _CHART_REGISTRY[name] = {
            "func": fn,
            "goal": goal,
            "dims": dims,
            "complexity": complexity,
            "doc": fn.__doc__ or "",
        }
        return fn
    return decorator

def get_chart_catalog() -> Dict[str, Dict[str, Any]]:
    """Expose the catalog minus the raw callables (LLM doesn't need code refs)."""
    return {k: {kk: vv for kk, vv in v.items() if kk != "func"}
            for k, v in _CHART_REGISTRY.items()}

# ─── Chart Renderers ──────────────────────────────────────────────────────
@chart(name="bar", goal="comparison", dims="1D", complexity="simple")
def render_bar(data: dict, ax: plt.Axes | None = None):
    """Standard vertical bar chart."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.bar(labels, values)

@chart(name="horizontalBar", goal="comparison", dims="1D", complexity="simple")
def render_horizontal_bar(data: dict, ax: plt.Axes | None = None):
    """Horizontal bar chart for better label readability."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.barh(labels, values)

@chart(name="line", goal="trend", dims="1D", complexity="simple")
def render_line(data: dict, ax: plt.Axes | None = None):
    """Line chart for time series and trends."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.plot(labels, values, marker='o')

@chart(name="pie", goal="composition", dims="1D", complexity="simple")
def render_pie(data: dict, ax: plt.Axes | None = None):
    """Pie chart for showing parts of a whole."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.pie(values, labels=labels, autopct='%1.1f%%')

@chart(name="donut", goal="composition", dims="1D", complexity="simple")
def render_donut(data: dict, ax: plt.Axes | None = None):
    """Donut chart for composition with center space."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.pie(values, labels=labels, autopct='%1.1f%%', 
               wedgeprops=dict(width=0.4), pctdistance=0.80)

@chart(name="scatter", goal="correlation", dims="2D", complexity="medium")
def render_scatter(data: dict, ax: plt.Axes | None = None):
    """Scatter plot for correlation analysis."""
    ax = ax or plt.gca()
    x_values = data.get("x_values", [])
    y_values = data.get("y_values", [])
    if x_values and y_values:
        ax.scatter(x_values, y_values)

@chart(name="area", goal="trend", dims="1D", complexity="medium")
def render_area(data: dict, ax: plt.Axes | None = None):
    """Area chart for cumulative trends."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.fill_between(labels, values, alpha=0.3)
        ax.plot(labels, values)

@chart(name="stackedBar", goal="composition", dims="1D", complexity="medium")
def render_stacked_bar(data: dict, ax: plt.Axes | None = None):
    """Stacked bar chart for composition over categories."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    series = data.get("series", [])
    if labels and series:
        bottom = []
        for series_data in series:
            if isinstance(series_data, dict) and 'values' in series_data:
                values = series_data['values']
                if not bottom:
                    ax.bar(labels, values)
                    bottom = values
                else:
                    ax.bar(labels, values, bottom=bottom)
                    bottom = [b + v for b, v in zip(bottom, values)]

@chart(name="multiLine", goal="trend", dims="1D", complexity="medium")
def render_multi_line(data: dict, ax: plt.Axes | None = None):
    """Multi-line chart for comparing trends."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    series = data.get("series", [])
    if labels and series:
        for series_data in series:
            if isinstance(series_data, dict) and 'values' in series_data:
                values = series_data['values']
                name = series_data.get('name', 'Series')
                ax.plot(labels, values, marker='o', label=name)
        ax.legend()

@chart(name="radar", goal="comparison", dims="nD", complexity="advanced")
def render_radar(data: dict, ax: plt.Axes | None = None):
    """Radar chart for multi-dimensional comparison."""
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values and len(labels) == len(values):
        N = len(labels)
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]
        values += values[:1]
        
        ax = plt.subplot(111, projection='polar')
        ax.plot(angles, values, 'o-')
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels)

@chart(name="bubble", goal="correlation", dims="3D", complexity="advanced")
def render_bubble(data: dict, ax: plt.Axes | None = None):
    """Bubble chart for 3D correlation analysis."""
    ax = ax or plt.gca()
    x_values = data.get("x_values", [])
    y_values = data.get("y_values", [])
    sizes = data.get("sizes", [])
    if x_values and y_values:
        if not sizes:
            sizes = [100] * len(x_values)
        ax.scatter(x_values, y_values, s=sizes, alpha=0.6)

@chart(name="heatmap", goal="correlation", dims="2D", complexity="advanced")
def render_heatmap(data: dict, ax: plt.Axes | None = None):
    """Heatmap for correlation matrix or 2D data."""
    ax = ax or plt.gca()
    values = data.get("values", [])
    labels = data.get("labels", [])
    categories = data.get("categories", [])
    
    if values and isinstance(values[0], list):
        # Use seaborn for better heatmap visualization
        import pandas as pd
        
        # Create DataFrame for seaborn heatmap
        df = pd.DataFrame(values, index=categories, columns=labels)
        sns.heatmap(df, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
        ax.set_title('Heatmap Analysis')
    elif values and labels and categories:
        # Fallback: create simple heatmap from 1D data
        import numpy as np
        data_matrix = np.array(values, dtype=float).reshape(len(categories), len(labels))
        im = ax.imshow(data_matrix, cmap='YlOrRd')
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(categories)))
        ax.set_xticklabels(labels)
        ax.set_yticklabels(categories)
        plt.colorbar(im, ax=ax)

@chart(name="waterfall", goal="flow", dims="1D", complexity="advanced")
def render_waterfall(data: dict, ax: plt.Axes | None = None):
    """Waterfall chart for cumulative flow analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        positions = list(range(len(labels)))
        cumulative = 0
        bar_positions = []
        for val in values:
            bar_positions.append(cumulative)
            cumulative += val
        ax.bar(positions, values, bottom=bar_positions)

@chart(name="funnel", goal="flow", dims="1D", complexity="medium")
def render_funnel(data: dict, ax: plt.Axes | None = None):
    """Funnel chart for conversion flow analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        max_val = max(values)
        normalized_values = [v / max_val for v in values]
        y_positions = list(range(len(labels)))
        for i, (label, value, norm_val) in enumerate(zip(labels, values, normalized_values)):
            ax.barh(i, norm_val * 0.8, height=0.6)

@chart(name="gauge", goal="comparison", dims="1D", complexity="simple")
def render_gauge(data: dict, ax: plt.Axes | None = None):
    """Gauge chart for single metric visualization."""
    ax = ax or plt.gca()
    value = data.get("value", 0)
    max_val = data.get("max", 100)
    if value and max_val:
        percentage = value / max_val
        sizes = [percentage, 1 - percentage]
        ax.pie(sizes, startangle=90, counterclock=False)

@chart(name="treeMap", goal="composition", dims="2D", complexity="advanced")
def render_tree_map(data: dict, ax: plt.Axes | None = None):
    """Tree map for hierarchical composition."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        total = sum(values)
        current_x = 0
        for label, value in zip(labels, values):
            width = value / total
            rect = plt.Rectangle((current_x, 0), width, 1, alpha=0.8)
            ax.add_patch(rect)
            current_x += width

@chart(name="sunburst", goal="composition", dims="nD", complexity="advanced")
def render_sunburst(data: dict, ax: plt.Axes | None = None):
    """Sunburst chart for hierarchical composition."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.pie(values, labels=labels, startangle=90, radius=1.0)

@chart(name="candlestick", goal="trend", dims="1D", complexity="advanced")
def render_candlestick(data: dict, ax: plt.Axes | None = None):
    """Candlestick chart for financial time series."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    open_prices = data.get("open", [])
    high_prices = data.get("high", [])
    low_prices = data.get("low", [])
    close_prices = data.get("close", [])
    if all([labels, open_prices, high_prices, low_prices, close_prices]):
        positions = list(range(len(labels)))
        for i, (open_price, high_price, low_price, close_price) in enumerate(zip(open_prices, high_prices, low_prices, close_prices)):
            ax.plot([i, i], [low_price, high_price], linewidth=1)

@chart(name="boxPlot", goal="distribution", dims="1D", complexity="medium")
def render_box_plot(data: dict, ax: plt.Axes | None = None):
    """Box plot for distribution analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    plot_data = data.get("data", [])
    if labels and plot_data:
        ax.boxplot(plot_data)
        ax.set_xticklabels(labels)

@chart(name="violinPlot", goal="distribution", dims="1D", complexity="advanced")
def render_violin_plot(data: dict, ax: plt.Axes | None = None):
    """Violin plot for distribution analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    plot_data = data.get("data", [])
    if labels and plot_data:
        ax.violinplot(plot_data, positions=range(len(labels)))

@chart(name="histogram", goal="distribution", dims="1D", complexity="simple")
def render_histogram(data: dict, ax: plt.Axes | None = None):
    """Histogram for distribution analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    if labels and values:
        ax.bar(labels, values)

@chart(name="pareto", goal="distribution", dims="1D", complexity="advanced")
def render_pareto(data: dict, ax: plt.Axes | None = None):
    """Pareto chart for distribution and cumulative analysis."""
    ax = ax or plt.gca()
    labels = data.get("labels", [])
    values = data.get("values", [])
    cumulative = data.get("cumulative", [])
    
    if labels and values:
        # Create primary axis for bars
        ax.bar(labels, values, alpha=0.7, color='skyblue')
        ax.set_xlabel('Categories')
        ax.set_ylabel('Frequency', color='skyblue')
        
        # Create secondary axis for cumulative line
        if cumulative:
            ax2 = ax.twinx()
            ax2.plot(labels, cumulative, 'r-', marker='o', linewidth=2, color='red')
            ax2.set_ylabel('Cumulative %', color='red')
            ax2.tick_params(axis='y', labelcolor='red')
        
        # Rotate x-axis labels for better readability
        ax.tick_params(axis='x', rotation=45)
        ax.set_title('Pareto Analysis')

@chart(name="flowchart", goal="flow", dims="2D", complexity="advanced")
def render_flowchart(data: dict, ax: plt.Axes | None = None):
    """Flowchart for process visualization."""
    ax = ax or plt.gca()
    nodes = data.get("nodes", [])
    if nodes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')

# ─── Test function ───────────────────────────────────────────────────────
if __name__ == "__main__":
    catalog = get_chart_catalog()
    print("Available charts:")
    for name, metadata in catalog.items():
        print(f"  {name}: {metadata['goal']} ({metadata['dims']}, {metadata['complexity']})")
        print(f"    {metadata['doc']}")
        print() 