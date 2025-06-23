import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime, timedelta
import json
import os

class EnhancedDataVisualizer:
    """Advanced data visualization for research reports"""
    
    def __init__(self, brand_colors: Dict[str, str], chart_style: str = "plotly_white"):
        self.brand_colors = brand_colors
        self.chart_style = chart_style if chart_style in ['plotly', 'plotly_white', 'plotly_dark', 'ggplot2', 'seaborn', 'simple_white'] else 'plotly_white'
        self.output_dir = "temp"
        os.makedirs(self.output_dir, exist_ok=True)
        self.color_palette = [
            brand_colors.get("primary", "#1f4e79"),
            brand_colors.get("secondary", "#666666"),
            brand_colors.get("accent", "#e74c3c"),
            "#2ecc71",
            "#f39c12",
            "#9b59b6",
            "#34495e",
            "#e67e22"
        ]
    
    def generate_all_visualizations(self, research_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive visualization suite"""
        
        visualizations = {}
        
        # Executive dashboard
        visualizations["executive_dashboard"] = self.create_executive_dashboard(research_data)
        
        # Market trends analysis
        if research_data.get("trend_data"):
            visualizations["trend_analysis"] = self.create_trend_analysis_chart(research_data["trend_data"])
        
        # Key findings summary
        if research_data.get("key_findings"):
            visualizations["findings_summary"] = self.create_findings_summary_chart(research_data["key_findings"])
        
        # Data quality metrics
        if research_data.get("quality_metrics"):
            visualizations["quality_metrics"] = self.create_quality_metrics_chart(research_data["quality_metrics"])
        
        # Source distribution
        if research_data.get("source_analysis"):
            visualizations["source_distribution"] = self.create_source_distribution_chart(research_data["source_analysis"])
        
        # Competitive landscape
        if research_data.get("competitive_data"):
            visualizations["competitive_landscape"] = self.create_competitive_landscape_chart(research_data["competitive_data"])
        
        # Growth indicators
        if research_data.get("growth_indicators"):
            visualizations["growth_indicators"] = self.create_growth_indicators_chart(research_data["growth_indicators"])
        
        return visualizations
    
    def create_executive_dashboard(self, research_data: Dict[str, Any]) -> str:
        """Create comprehensive executive dashboard based on actual research data"""
        
        # Create subplot layout
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=[
                "Research Coverage", "Data Quality Score", "Key Metrics",
                "Source Distribution", "Trend Indicators", "Quality Assessment"
            ],
            specs=[
                [{"type": "indicator"}, {"type": "indicator"}, {"type": "bar"}],
                [{"type": "pie"}, {"type": "scatter"}, {"type": "bar"}]
            ]
        )
        
        # Extract real data from research results
        validated_data = research_data.get("validated_data", [])
        sources_count = len(validated_data)
        
        # Research coverage indicator - based on actual sources found
        coverage_score = min(sources_count / 50.0, 1.0)  # Scale based on target of 50 sources
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=coverage_score * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Sources Found: {sources_count}"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.color_palette[0]},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Data quality indicator - based on actual quality scores
        if validated_data:
            avg_quality = sum(source.get("quality_score", 0.7) for source in validated_data) / len(validated_data)
        else:
            avg_quality = 0.7
        
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=avg_quality * 100,
                title={'text': "Avg Quality Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': self.color_palette[2]},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 90], 'color': "gray"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        # Key metrics bar chart - extract from actual data
        category_counts = {}
        for source in validated_data:
            category = source.get("source_metadata", {}).get("category", "unknown")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        if category_counts:
            metric_names = list(category_counts.keys())[:5]
            metric_values = [category_counts[name] for name in metric_names]
        else:
            metric_names = ["No Data"]
            metric_values = [0]
        
        fig.add_trace(
            go.Bar(
                x=metric_names,
                y=metric_values,
                marker_color=self.color_palette[1],
                name="Source Categories"
            ),
            row=1, col=3
        )
        
        # Source distribution pie chart - based on actual source types
        source_types = {}
        for source in validated_data:
            discovery_method = source.get("source_metadata", {}).get("discovery_method", "unknown")
            source_types[discovery_method] = source_types.get(discovery_method, 0) + 1
        
        if source_types:
            fig.add_trace(
                go.Pie(
                    labels=list(source_types.keys()),
                    values=list(source_types.values()),
                    marker_colors=self.color_palette[:len(source_types)]
                ),
                row=2, col=1
            )
        else:
            fig.add_trace(
                go.Pie(
                    labels=["No Data"],
                    values=[1],
                    marker_colors=[self.color_palette[0]]
                ),
                row=2, col=1
            )
        
        # Trend indicators - extract actual trend data if available
        trend_data = research_data.get("trend_data", {})
        if trend_data and hasattr(trend_data, 'items'):
            dates = list(trend_data.keys())[:10]  # Limit to 10 points
            values = list(trend_data.values())[:10]
            
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=values,
                    mode='lines+markers',
                    line=dict(color=self.color_palette[0], width=3),
                    marker=dict(size=8),
                    name="Trend Analysis"
                ),
                row=2, col=2
            )
        else:
            # Create trend from source quality over time if no trend data
            if validated_data:
                sample_dates = [f"2024-{i+1:02d}" for i in range(min(6, len(validated_data)))]
                sample_values = [source.get("quality_score", 0.7) * 100 for source in validated_data[:6]]
                
                fig.add_trace(
                    go.Scatter(
                        x=sample_dates,
                        y=sample_values,
                        mode='lines+markers',
                        line=dict(color=self.color_palette[0], width=3),
                        marker=dict(size=8),
                        name="Quality Trend"
                    ),
                    row=2, col=2
                )
        
        # Quality assessment - based on actual data quality metrics
        if validated_data:
            real_validated = [s for s in validated_data if s.get("source_metadata", {}).get("discovery_method") == "web_scraping"]
            ai_generated = [s for s in validated_data if s.get("source_metadata", {}).get("discovery_method") == "ai_generation"]
            fallback = [s for s in validated_data if s.get("source_metadata", {}).get("discovery_method") == "fallback_generation"]
            
            quality_categories = ["Real Sources", "AI Generated", "Fallback Data"]
            quality_scores = [
                len(real_validated),
                len(ai_generated), 
                len(fallback)
            ]
        else:
            quality_categories = ["No Data Available"]
            quality_scores = [0]
        
        fig.add_trace(
            go.Bar(
                x=quality_categories,
                y=quality_scores,
                marker_color=self.color_palette[3],
                name="Source Types"
            ),
            row=2, col=3
        )
        
        # Update layout with query-specific title
        query_topic = research_data.get("query", {}).get("topic", "Research Analysis")
        fig.update_layout(
            title={
                'text': f"Executive Dashboard: {query_topic}",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': self.color_palette[0]}
            },
            showlegend=False,
            height=600,
            template=self.chart_style,
            font=dict(size=12)
        )
        
        return self._fig_to_base64(fig)
    
    def create_trend_analysis_chart(self, trend_data: Dict[str, Any]) -> str:
        """Create trend analysis based on actual research data"""
        
        fig = go.Figure()
        
        # Check if we have actual trend data
        if not trend_data or not isinstance(trend_data, dict):
            # Create a simple message chart if no data
            fig.add_annotation(
                text="No trend data available for this query",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color=self.color_palette[0])
            )
            
            fig.update_layout(
                title="Trend Analysis",
                height=400,
                template=self.chart_style
            )
            
            return self._fig_to_base64(fig)
        
        # Extract dates and values from actual data
        dates = list(trend_data.keys())
        values = list(trend_data.values())
        
        if not dates or not values:
            fig.add_annotation(
                text="Insufficient data for trend analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False,
                font=dict(size=16, color=self.color_palette[0])
            )
        else:
            # Sort data by date if possible
            try:
                date_value_pairs = list(zip(dates, values))
                date_value_pairs.sort(key=lambda x: x[0])
                dates, values = zip(*date_value_pairs)
            except:
                pass  # Keep original order if sorting fails
            
            # Create the main trend line
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name='Trend',
                line=dict(color=self.color_palette[0], width=3),
                marker=dict(size=8, color=self.color_palette[0])
            ))
            
            # Add a trend line if we have enough data points
            if len(values) >= 3:
                try:
                    # Calculate linear trend
                    x_numeric = list(range(len(values)))
                    z = np.polyfit(x_numeric, values, 1)
                    p = np.poly1d(z)
                    trend_line = [p(x) for x in x_numeric]
                    
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=trend_line,
                        mode='lines',
                        name='Trend Line',
                        line=dict(color=self.color_palette[1], width=2, dash='dash'),
                        opacity=0.7
                    ))
                except ImportError:
                    # If numpy is not available, create a simple average line
                    avg_value = sum(values) / len(values)
                    fig.add_trace(go.Scatter(
                        x=dates,
                        y=[avg_value] * len(dates),
                        mode='lines',
                        name='Average',
                        line=dict(color=self.color_palette[1], width=2, dash='dash'),
                        opacity=0.7
                    ))
                except Exception:
                    pass  # Skip trend line if calculation fails
            
            # Add area fill
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                fill='tonexty',
                mode='none',
                fillcolor=f'rgba({self._hex_to_rgb(self.color_palette[0])}, 0.1)',
                showlegend=False
            ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="Trend Analysis - Based on Research Data",
                x=0.5,
                xanchor='center',
                font=dict(size=16, color=self.color_palette[0])
            ),
            xaxis_title="Time Period",
            yaxis_title="Value",
            height=400,
            template=self.chart_style,
            hovermode='x unified'
        )
        
        return self._fig_to_base64(fig)
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string"""
        try:
            hex_color = hex_color.lstrip('#')
            return ','.join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))
        except:
            return "26,54,93"  # Default blue RGB
    
    def create_findings_summary_chart(self, findings_data: Dict[str, Any]) -> str:
        """Create key findings summary visualization"""
        
        # Key findings distribution
        finding_categories = findings_data.get("categories", [])
        finding_counts = findings_data.get("counts", [])
        finding_importance = findings_data.get("importance_scores", [])
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Findings Distribution", "Importance vs Frequency"],
            specs=[[{"type": "bar"}, {"type": "scatter"}]]
        )
        
        # Findings distribution bar chart
        fig.add_trace(
            go.Bar(
                x=finding_categories,
                y=finding_counts,
                marker_color=self.color_palette[0],
                name="Finding Counts"
            ),
            row=1, col=1
        )
        
        # Importance vs frequency scatter
        fig.add_trace(
            go.Scatter(
                x=finding_counts,
                y=finding_importance,
                mode='markers+text',
                marker=dict(
                    size=[count * 2 for count in finding_counts],
                    color=self.color_palette[2],
                    opacity=0.7
                ),
                text=finding_categories,
                textposition="top center",
                name="Importance Analysis"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title={
                'text': "Key Findings Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette[0]}
            },
            template=self.chart_style,
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def create_quality_metrics_chart(self, quality_data: Dict[str, Any]) -> str:
        """Create data quality metrics visualization"""
        
        # Quality dimensions radar chart
        categories = ["Accuracy", "Completeness", "Consistency", "Timeliness", "Relevance", "Credibility"]
        values = [
            quality_data.get("accuracy", 0.9),
            quality_data.get("completeness", 0.85),
            quality_data.get("consistency", 0.92),
            quality_data.get("timeliness", 0.88),
            quality_data.get("relevance", 0.94),
            quality_data.get("credibility", 0.91)
        ]
        
        fig = go.Figure()
        
        # Convert hex color to rgba format for transparency
        primary_color = self.color_palette[0]
        rgba_color = f"rgba({int(primary_color[1:3], 16)}, {int(primary_color[3:5], 16)}, {int(primary_color[5:7], 16)}, 0.3)"
        
        fig.add_trace(go.Scatterpolar(
            r=[v * 100 for v in values],
            theta=categories,
            fill='toself',
            name='Quality Metrics',
            line_color=self.color_palette[0],
            fillcolor=rgba_color
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            title={
                'text': "Data Quality Assessment",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette[0]}
            },
            template=self.chart_style,
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def create_source_distribution_chart(self, source_data: Dict[str, Any]) -> str:
        """Create source distribution and credibility analysis"""
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Source Type Distribution", "Source Credibility"],
            specs=[[{"type": "pie"}, {"type": "bar"}]]
        )
        
        # Source distribution pie
        source_types = list(source_data.get("distribution", {}).keys())
        source_counts = list(source_data.get("distribution", {}).values())
        
        fig.add_trace(
            go.Pie(
                labels=source_types,
                values=source_counts,
                marker_colors=self.color_palette[:len(source_types)],
                name="Source Distribution"
            ),
            row=1, col=1
        )
        
        # Credibility scores
        credibility_scores = source_data.get("credibility_scores", {})
        if credibility_scores:
            fig.add_trace(
                go.Bar(
                    x=list(credibility_scores.keys()),
                    y=[score * 100 for score in credibility_scores.values()],
                    marker_color=self.color_palette[1],
                    name="Credibility Scores"
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title={
                'text': "Source Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette[0]}
            },
            template=self.chart_style,
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def create_competitive_landscape_chart(self, competitive_data: Dict[str, Any]) -> str:
        """Create competitive landscape visualization"""
        
        # Market positioning bubble chart
        companies = competitive_data.get("companies", [])
        market_share = competitive_data.get("market_share", [])
        growth_rate = competitive_data.get("growth_rate", [])
        revenue = competitive_data.get("revenue", [])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=market_share,
            y=growth_rate,
            mode='markers+text',
            marker=dict(
                size=[r/1000000 for r in revenue] if revenue else [20] * len(companies),
                color=self.color_palette[:len(companies)],
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=companies,
            textposition="top center",
            name="Competitive Position"
        ))
        
        fig.update_layout(
            title={
                'text': "Competitive Landscape Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette[0]}
            },
            xaxis_title="Market Share (%)",
            yaxis_title="Growth Rate (%)",
            template=self.chart_style,
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def create_growth_indicators_chart(self, growth_data: List[Dict[str, Any]]) -> str:
        """Create growth indicators visualization"""
        
        # Extract data
        indicators = [item.get("name", f"Indicator {i+1}") for i, item in enumerate(growth_data)]
        current_values = [item.get("current_value", 0) for item in growth_data]
        projected_values = [item.get("projected_value", 0) for item in growth_data]
        
        fig = go.Figure()
        
        # Current values
        fig.add_trace(go.Bar(
            x=indicators,
            y=current_values,
            name='Current Values',
            marker_color=self.color_palette[0]
        ))
        
        # Projected values
        fig.add_trace(go.Bar(
            x=indicators,
            y=projected_values,
            name='Projected Values',
            marker_color=self.color_palette[2]
        ))
        
        fig.update_layout(
            title={
                'text': "Growth Indicators Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': self.color_palette[0]}
            },
            xaxis_title="Growth Indicators",
            yaxis_title="Values",
            barmode='group',
            template=self.chart_style,
            height=500
        )
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert plotly figure to base64 string"""
        img_bytes = fig.to_image(format="png", width=1200, height=800, scale=2)
        img_base64 = base64.b64encode(img_bytes).decode()
        return img_base64 