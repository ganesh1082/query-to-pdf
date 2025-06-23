#!/usr/bin/env python3
"""
Enhanced Visualization Generator for Premium PDF Reports
Creates real, professional charts and visualizations
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime, timedelta
import random
from typing import Dict, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class PremiumVisualizationGenerator:
    """Professional visualization generator for premium reports"""
    
    def __init__(self, brand_colors: Dict[str, str]):
        self.brand_colors = brand_colors
        self.primary_color = brand_colors.get("primary", "#1a365d")
        self.accent_color = brand_colors.get("accent", "#3182ce")
        self.secondary_color = brand_colors.get("secondary", "#2d3748")
        
        # Set professional style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette([self.primary_color, self.accent_color, "#22c55e", "#f59e0b", "#ef4444"])
        
    def _save_plot_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none', pad_inches=0.1)
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        plt.close(fig)
        
        return base64.b64encode(plot_data).decode('utf-8')
    
    def create_executive_dashboard(self) -> str:
        """Create a comprehensive executive dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Executive Market Intelligence Dashboard', fontsize=16, fontweight='bold', color=self.primary_color)
        
        # Market Growth Trend (top-left)
        quarters = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024', 'Q2 2024']
        growth = [2.3, 3.1, 4.2, 5.8, 6.5, 7.2]
        ax1.plot(quarters, growth, marker='o', linewidth=3, markersize=8, color=self.primary_color)
        ax1.set_title('Market Growth Trajectory', fontweight='bold', color=self.primary_color)
        ax1.set_ylabel('Growth Rate (%)')
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Market Share Distribution (top-right)
        companies = ['Our Company', 'Competitor A', 'Competitor B', 'Competitor C', 'Others']
        market_share = [28, 22, 18, 15, 17]
        colors = [self.primary_color, self.accent_color, '#22c55e', '#f59e0b', '#94a3b8']
        wedges, texts, autotexts = ax2.pie(market_share, labels=companies, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        ax2.set_title('Market Share Analysis', fontweight='bold', color=self.primary_color)
        
        # Revenue Trends (bottom-left)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        revenue_2023 = [85, 88, 92, 89, 95, 98]
        revenue_2024 = [102, 108, 115, 118, 125, 132]
        
        x = np.arange(len(months))
        width = 0.35
        
        ax3.bar(x - width/2, revenue_2023, width, label='2023', color=self.accent_color, alpha=0.8)
        ax3.bar(x + width/2, revenue_2024, width, label='2024', color=self.primary_color)
        ax3.set_title('Revenue Performance Comparison', fontweight='bold', color=self.primary_color)
        ax3.set_ylabel('Revenue ($ Millions)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(months)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Customer Satisfaction Metrics (bottom-right)
        metrics = ['Product Quality', 'Customer Service', 'Value for Money', 'Innovation', 'Overall']
        our_scores = [4.2, 4.5, 4.1, 4.6, 4.3]
        industry_avg = [3.8, 3.9, 3.7, 3.6, 3.8]
        
        x = np.arange(len(metrics))
        ax4.bar(x - 0.2, our_scores, 0.4, label='Our Performance', color=self.primary_color)
        ax4.bar(x + 0.2, industry_avg, 0.4, label='Industry Average', color=self.accent_color, alpha=0.7)
        ax4.set_title('Customer Satisfaction Benchmarking', fontweight='bold', color=self.primary_color)
        ax4.set_ylabel('Rating (1-5 Scale)')
        ax4.set_xticks(x)
        ax4.set_xticklabels(metrics, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 5)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_market_growth_trends(self) -> str:
        """Create detailed market growth analysis"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate realistic growth data
        dates = pd.date_range(start='2020-01-01', end='2024-06-01', freq='Q')
        base_growth = 100
        growth_data = []
        
        for i, date in enumerate(dates):
            # Add seasonal variation and upward trend
            seasonal = 5 * np.sin(2 * np.pi * i / 4)  # Quarterly seasonality
            trend = i * 2.5  # Upward trend
            noise = np.random.normal(0, 3)  # Random variation
            growth_data.append(base_growth + trend + seasonal + noise)
        
        # Plot the main trend line
        ax.plot(dates, growth_data, linewidth=3, color=self.primary_color, label='Market Size')
        
        # Add trend line
        z = np.polyfit(range(len(growth_data)), growth_data, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(range(len(growth_data))), "--", color=self.accent_color, 
                linewidth=2, alpha=0.8, label='Growth Trend')
        
        # Fill area under curve
        ax.fill_between(dates, growth_data, alpha=0.2, color=self.primary_color)
        
        ax.set_title('Strategic Market Growth Analysis 2020-2024', 
                    fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        ax.set_xlabel('Time Period', fontweight='bold')
        ax.set_ylabel('Market Size (Index: 100 = 2020 Q1)', fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Add annotations for key insights
        ax.annotate('COVID Impact', xy=(dates[4], growth_data[4]), xytext=(dates[6], growth_data[4] - 10),
                   arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                   fontsize=10, color='red', fontweight='bold')
        
        ax.annotate('Recovery Phase', xy=(dates[8], growth_data[8]), xytext=(dates[10], growth_data[8] + 15),
                   arrowprops=dict(arrowstyle='->', color='green', alpha=0.7),
                   fontsize=10, color='green', fontweight='bold')
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_competitive_positioning(self) -> str:
        """Create competitive positioning matrix"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Company data for positioning
        companies = {
            'Our Company': (7.5, 8.2, 150),
            'Competitor A': (6.8, 7.1, 120),
            'Competitor B': (5.5, 6.8, 100),
            'Competitor C': (4.2, 5.5, 80),
            'Emerging Player 1': (8.1, 5.8, 60),
            'Emerging Player 2': (6.2, 4.5, 40),
            'Traditional Leader': (5.8, 8.8, 200)
        }
        
        colors = [self.primary_color, self.accent_color, '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
        
        for i, (company, (innovation, market_pos, size)) in enumerate(companies.items()):
            color = colors[i % len(colors)]
            alpha = 1.0 if company == 'Our Company' else 0.7
            
            ax.scatter(innovation, market_pos, s=size*2, c=color, alpha=alpha, 
                      edgecolors='white', linewidth=2, label=company)
            
            # Add company labels
            ax.annotate(company, (innovation, market_pos), 
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, fontweight='bold' if company == 'Our Company' else 'normal')
        
        ax.set_xlabel('Innovation Index', fontsize=12, fontweight='bold')
        ax.set_ylabel('Market Position Strength', fontsize=12, fontweight='bold')
        ax.set_title('Competitive Positioning Matrix\n(Bubble size represents market share)',
                    fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        
        # Add quadrant lines
        ax.axhline(y=6.5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=6.5, color='gray', linestyle='--', alpha=0.5)
        
        # Add quadrant labels
        ax.text(3, 9, 'Traditional\nLeaders', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(9, 9, 'Innovation\nLeaders', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(3, 3, 'Struggling\nPlayers', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(9, 3, 'Niche\nInnovators', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        
        ax.set_xlim(2, 10)
        ax.set_ylim(2, 10)
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_customer_segmentation(self) -> str:
        """Create customer segmentation analysis"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Left chart: Segment sizes
        segments = ['Enterprise', 'Mid-Market', 'Small Business', 'Startup']
        sizes = [35, 28, 22, 15]
        colors = [self.primary_color, self.accent_color, '#22c55e', '#f59e0b']
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=segments, autopct='%1.1f%%',
                                          colors=colors, startangle=90, explode=(0.05, 0, 0, 0))
        ax1.set_title('Customer Segment Distribution', fontweight='bold', color=self.primary_color)
        
        # Right chart: Segment profitability
        segments_short = ['Enterprise', 'Mid-Market', 'Small Biz', 'Startup']
        revenue_per_customer = [125000, 45000, 12000, 3500]
        customer_count = [150, 380, 950, 1200]
        
        # Create bubble chart
        for i, (segment, revenue, count) in enumerate(zip(segments_short, revenue_per_customer, customer_count)):
            ax2.scatter(count, revenue, s=sizes[i]*20, c=colors[i], alpha=0.7, 
                       edgecolors='white', linewidth=2)
            ax2.annotate(segment, (count, revenue), xytext=(5, 5), 
                        textcoords='offset points', fontsize=9, fontweight='bold')
        
        ax2.set_xlabel('Number of Customers', fontweight='bold')
        ax2.set_ylabel('Average Revenue per Customer ($)', fontweight='bold')
        ax2.set_title('Customer Value Analysis', fontweight='bold', color=self.primary_color)
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_technology_adoption(self) -> str:
        """Create technology adoption trends"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        technologies = ['AI/ML', 'Cloud Computing', 'IoT', 'Blockchain', 'AR/VR', '5G', 'Edge Computing']
        adoption_2023 = [45, 78, 62, 23, 18, 35, 28]
        adoption_2024 = [68, 89, 75, 35, 32, 58, 45]
        
        x = np.arange(len(technologies))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, adoption_2023, width, label='2023', 
                      color=self.accent_color, alpha=0.8)
        bars2 = ax.bar(x + width/2, adoption_2024, width, label='2024', 
                      color=self.primary_color)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height}%',
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 3),  # 3 points vertical offset
                           textcoords="offset points",
                           ha='center', va='bottom', fontsize=9)
        
        ax.set_xlabel('Technology Categories', fontweight='bold')
        ax.set_ylabel('Adoption Rate (%)', fontweight='bold')
        ax.set_title('Technology Adoption Trends: 2023 vs 2024', 
                    fontweight='bold', color=self.primary_color, pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(technologies, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, 100)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_cover_image(self) -> str:
        """Create professional cover image"""
        fig, ax = plt.subplots(figsize=(10, 7))
        
        # Create an abstract professional visualization
        x = np.linspace(0, 10, 100)
        y1 = 3 + 2 * np.sin(x) + np.random.normal(0, 0.2, 100)
        y2 = 5 + 1.5 * np.cos(x * 1.2) + np.random.normal(0, 0.15, 100)
        y3 = 4 + np.sin(x * 0.8) * np.cos(x * 1.5) + np.random.normal(0, 0.1, 100)
        
        ax.plot(x, y1, linewidth=3, color=self.primary_color, alpha=0.8, label='Market Trend')
        ax.plot(x, y2, linewidth=3, color=self.accent_color, alpha=0.8, label='Performance')
        ax.plot(x, y3, linewidth=3, color='#22c55e', alpha=0.8, label='Growth')
        
        ax.fill_between(x, y1, alpha=0.2, color=self.primary_color)
        ax.fill_between(x, y2, alpha=0.2, color=self.accent_color)
        ax.fill_between(x, y3, alpha=0.2, color='#22c55e')
        
        ax.set_title('Strategic Market Intelligence\nData-Driven Business Insights', 
                    fontsize=18, fontweight='bold', color=self.primary_color, pad=30)
        
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 8)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', framealpha=0.9)
        
        # Remove axis labels for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_methodology_visualization(self) -> str:
        """Create research methodology flowchart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create flowchart boxes
        boxes = [
            {'name': 'Data Collection', 'pos': (2, 7), 'color': self.primary_color},
            {'name': 'Primary Research', 'pos': (1, 5.5), 'color': self.accent_color},
            {'name': 'Secondary Research', 'pos': (3, 5.5), 'color': self.accent_color},
            {'name': 'Data Validation', 'pos': (2, 4), 'color': '#22c55e'},
            {'name': 'Statistical Analysis', 'pos': (0.5, 2.5), 'color': '#f59e0b'},
            {'name': 'Qualitative Analysis', 'pos': (2, 2.5), 'color': '#f59e0b'},
            {'name': 'Market Modeling', 'pos': (3.5, 2.5), 'color': '#f59e0b'},
            {'name': 'Insights Generation', 'pos': (2, 1), 'color': self.primary_color}
        ]
        
        # Draw boxes
        for box in boxes:
            rect = patches.FancyBboxPatch(
                (box['pos'][0] - 0.4, box['pos'][1] - 0.3),
                0.8, 0.6,
                boxstyle="round,pad=0.1",
                facecolor=box['color'],
                edgecolor='white',
                linewidth=2,
                alpha=0.8
            )
            ax.add_patch(rect)
            
            ax.text(box['pos'][0], box['pos'][1], box['name'],
                   ha='center', va='center', fontweight='bold',
                   color='white', fontsize=10)
        
        # Draw arrows
        arrow_props = dict(arrowstyle='->', connectionstyle='arc3', 
                          color='gray', linewidth=2)
        
        # Main flow arrows
        ax.annotate('', xy=(1, 5.8), xytext=(1.6, 6.7), arrowprops=arrow_props)
        ax.annotate('', xy=(3, 5.8), xytext=(2.4, 6.7), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 4.3), xytext=(1, 5.2), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 4.3), xytext=(3, 5.2), arrowprops=arrow_props)
        ax.annotate('', xy=(0.5, 2.8), xytext=(1.6, 3.7), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 2.8), xytext=(2, 3.7), arrowprops=arrow_props)
        ax.annotate('', xy=(3.5, 2.8), xytext=(2.4, 3.7), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 1.3), xytext=(0.5, 2.2), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 1.3), xytext=(2, 2.2), arrowprops=arrow_props)
        ax.annotate('', xy=(2, 1.3), xytext=(3.5, 2.2), arrowprops=arrow_props)
        
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(0, 8)
        ax.set_title('Research Methodology Framework', 
                    fontsize=16, fontweight='bold', color=self.primary_color, pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_risk_assessment_chart(self) -> str:
        """Create risk assessment matrix"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Risk categories
        risks = {
            'Market Volatility': (7, 8, 'High'),
            'Technology Disruption': (8, 6, 'Medium'),
            'Regulatory Changes': (5, 7, 'Medium'),
            'Competitive Pressure': (6, 9, 'High'),
            'Economic Downturn': (4, 8, 'Low'),
            'Supply Chain Issues': (6, 5, 'Medium'),
            'Cybersecurity Threats': (9, 7, 'High'),
            'Talent Shortage': (7, 6, 'Medium')
        }
        
        colors = {'High': '#ef4444', 'Medium': '#f59e0b', 'Low': '#22c55e'}
        
        # Track which severity levels we've already added to legend
        added_to_legend = set()
        
        for risk, (probability, impact, severity) in risks.items():
            color = colors[severity]
            size = 150 if severity == 'High' else 100 if severity == 'Medium' else 80
            
            # Only add to legend if we haven't seen this severity level before
            label = severity if severity not in added_to_legend else ""
            if severity not in added_to_legend:
                added_to_legend.add(severity)
            
            ax.scatter(probability, impact, s=size, c=color, alpha=0.7, 
                      edgecolors='white', linewidth=2, label=label)
            
            ax.annotate(risk, (probability, impact), xytext=(5, 5), 
                       textcoords='offset points', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Probability of Occurrence', fontsize=12, fontweight='bold')
        ax.set_ylabel('Potential Business Impact', fontsize=12, fontweight='bold')
        ax.set_title('Strategic Risk Assessment Matrix', fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        
        # Add quadrant lines
        ax.axhline(y=6.5, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=6.5, color='gray', linestyle='--', alpha=0.5)
        
        # Add quadrant labels
        ax.text(3, 9.5, 'Low Probability\nHigh Impact', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(8.5, 9.5, 'High Probability\nHigh Impact', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(3, 3, 'Low Probability\nLow Impact', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        ax.text(8.5, 3, 'High Probability\nLow Impact', ha='center', va='center', 
                fontsize=10, alpha=0.6, fontweight='bold')
        
        ax.set_xlim(1, 10)
        ax.set_ylim(1, 10)
        ax.grid(True, alpha=0.3)
        ax.legend(title='Risk Level', loc='upper left')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_implementation_roadmap(self) -> str:
        """Create implementation timeline chart"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Timeline data
        phases = ['Phase 1: Foundation', 'Phase 2: Development', 'Phase 3: Implementation', 'Phase 4: Optimization']
        start_dates = [0, 3, 8, 14]
        durations = [3, 5, 6, 4]
        colors = [self.primary_color, self.accent_color, '#22c55e', '#f59e0b']
        
        # Create Gantt chart
        for i, (phase, start, duration, color) in enumerate(zip(phases, start_dates, durations, colors)):
            ax.barh(i, duration, left=start, height=0.6, color=color, alpha=0.8, 
                   edgecolor='white', linewidth=2)
            
            # Add phase labels
            ax.text(start + duration/2, i, phase, ha='center', va='center', 
                   fontweight='bold', color='white', fontsize=10)
            
            # Add duration labels
            ax.text(start + duration + 0.2, i, f'{duration} months', 
                   va='center', fontsize=9, fontweight='bold')
        
        ax.set_xlabel('Timeline (Months)', fontsize=12, fontweight='bold')
        ax.set_title('Strategic Implementation Roadmap', fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        ax.set_yticks(range(len(phases)))
        ax.set_yticklabels([])
        ax.set_xlim(0, 20)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add milestone markers
        milestones = [3, 8, 14, 18]
        milestone_names = ['Foundation Complete', 'Development Ready', 'Implementation Live', 'Optimization Complete']
        
        for milestone, name in zip(milestones, milestone_names):
            ax.axvline(x=milestone, color='red', linestyle='--', alpha=0.7)
            ax.text(milestone, len(phases), name, rotation=45, ha='left', va='bottom', 
                   fontsize=8, color='red', fontweight='bold')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_market_analysis_framework(self) -> str:
        """Create market analysis framework diagram"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create a comprehensive market analysis framework
        # Central hub
        center = (5, 4)
        ax.add_patch(plt.Circle(center, 1, color=self.primary_color, alpha=0.8))
        ax.text(center[0], center[1], 'Market\nAnalysis', ha='center', va='center', 
               fontsize=12, fontweight='bold', color='white')
        
        # Framework components
        components = [
            {'name': 'Customer\nSegmentation', 'pos': (2, 7), 'color': self.accent_color},
            {'name': 'Competitive\nLandscape', 'pos': (8, 7), 'color': '#22c55e'},
            {'name': 'Market\nTrends', 'pos': (2, 1), 'color': '#f59e0b'},
            {'name': 'Technology\nImpact', 'pos': (8, 1), 'color': '#ef4444'},
            {'name': 'Regulatory\nEnvironment', 'pos': (1, 4), 'color': '#8b5cf6'},
            {'name': 'Economic\nFactors', 'pos': (9, 4), 'color': '#06b6d4'}
        ]
        
        for comp in components:
            # Draw component circles
            ax.add_patch(plt.Circle(comp['pos'], 0.7, color=comp['color'], alpha=0.8))
            ax.text(comp['pos'][0], comp['pos'][1], comp['name'], ha='center', va='center', 
                   fontsize=10, fontweight='bold', color='white')
            
            # Draw connecting lines
            ax.plot([center[0], comp['pos'][0]], [center[1], comp['pos'][1]], 
                   color='gray', linewidth=2, alpha=0.6)
        
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 8.5)
        ax.set_title('Comprehensive Market Analysis Framework', 
                    fontsize=14, fontweight='bold', color=self.primary_color, pad=20)
        ax.axis('off')
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def create_financial_performance_chart(self) -> str:
        """Create financial performance dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('Financial Performance Analysis', fontsize=16, fontweight='bold', color=self.primary_color)
        
        # Revenue Growth (top-left)
        years = ['2020', '2021', '2022', '2023', '2024F']
        revenue = [120, 135, 158, 187, 215]
        ax1.plot(years, revenue, marker='o', linewidth=3, markersize=8, color=self.primary_color)
        ax1.fill_between(years, revenue, alpha=0.2, color=self.primary_color)
        ax1.set_title('Revenue Growth Trajectory', fontweight='bold', color=self.primary_color)
        ax1.set_ylabel('Revenue ($M)')
        ax1.grid(True, alpha=0.3)
        
        # Profit Margins (top-right)
        margins = ['Gross Margin', 'Operating Margin', 'Net Margin']
        values_2023 = [45, 18, 12]
        values_2024 = [48, 22, 15]
        
        x = np.arange(len(margins))
        width = 0.35
        ax2.bar(x - width/2, values_2023, width, label='2023', color=self.accent_color, alpha=0.8)
        ax2.bar(x + width/2, values_2024, width, label='2024F', color=self.primary_color)
        ax2.set_title('Profitability Margins', fontweight='bold', color=self.primary_color)
        ax2.set_ylabel('Margin (%)')
        ax2.set_xticks(x)
        ax2.set_xticklabels(margins, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Cash Flow (bottom-left)
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        operating_cf = [25, 28, 32, 35]
        free_cf = [18, 22, 26, 28]
        
        x = np.arange(len(quarters))
        ax3.bar(x - 0.2, operating_cf, 0.4, label='Operating CF', color=self.primary_color)
        ax3.bar(x + 0.2, free_cf, 0.4, label='Free CF', color=self.accent_color, alpha=0.7)
        ax3.set_title('Cash Flow Performance', fontweight='bold', color=self.primary_color)
        ax3.set_ylabel('Cash Flow ($M)')
        ax3.set_xticks(x)
        ax3.set_xticklabels(quarters)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Key Ratios (bottom-right)
        ratios = ['ROE', 'ROA', 'ROIC', 'Debt/Equity']
        current_values = [15.2, 8.7, 12.3, 0.45]
        industry_avg = [12.8, 6.9, 9.8, 0.62]
        
        x = np.arange(len(ratios))
        ax4.bar(x - 0.2, current_values, 0.4, label='Company', color=self.primary_color)
        ax4.bar(x + 0.2, industry_avg, 0.4, label='Industry Avg', color=self.accent_color, alpha=0.7)
        ax4.set_title('Key Financial Ratios', fontweight='bold', color=self.primary_color)
        ax4.set_ylabel('Ratio Value')
        ax4.set_xticks(x)
        ax4.set_xticklabels(ratios)
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._save_plot_to_base64(fig)
    
    def generate_all_visualizations(self):
        """Generate comprehensive professional visualizations"""
        
        try:
            visualizations = {}
            
            # List of visualization methods with descriptions
            viz_methods = [
                ("executive_dashboard", self.create_executive_dashboard, "Creating executive dashboard"),
                ("market_growth_trends", self.create_market_growth_trends, "Analyzing market growth trends"),
                ("competitive_positioning", self.create_competitive_positioning, "Mapping competitive landscape"),
                ("customer_segmentation", self.create_customer_segmentation, "Segmenting customer data"),
                ("technology_adoption", self.create_technology_adoption, "Tracking technology adoption"),
                ("methodology_visualization", self.create_methodology_visualization, "Visualizing methodology"),
                ("risk_assessment_chart", self.create_risk_assessment_chart, "Assessing risk factors"),
                ("implementation_roadmap", self.create_implementation_roadmap, "Creating implementation roadmap"),
                ("market_analysis_framework", self.create_market_analysis_framework, "Framework analysis"),
                ("financial_performance_chart", self.create_financial_performance_chart, "Financial performance metrics")
            ]
            
            successful_count = 0
            for viz_name, viz_method, description in viz_methods:
                try:
                    print(f"  📊 {description}...")
                    viz_data = viz_method()
                    
                    # Validate the visualization data
                    if viz_data and len(viz_data) > 100:  # Ensure it's a valid base64 string
                        visualizations[viz_name] = viz_data
                        successful_count += 1
                    else:
                        print(f"  ⚠️ Skipping {viz_name} - invalid data generated")
                        
                except Exception as e:
                    print(f"  ❌ Error generating {viz_name}: {e}")
                    # Continue with other visualizations
                    continue
            
            print(f"✅ Generated {successful_count} professional visualizations!")
            return visualizations
            
        except Exception as e:
            print(f"❌ Error in visualization generation: {e}")
            # Return empty dict instead of hardcoded fallback
            print("⚠️ No visualizations available - check data sources and try again")
            return {}

if __name__ == "__main__":
    # Test visualization generation
    brand_colors = {
        "primary": "#1a365d",
        "secondary": "#2d3748", 
        "accent": "#3182ce"
    }
    
    generator = PremiumVisualizationGenerator(brand_colors)
    visualizations = generator.generate_all_visualizations()
    
    print(f"Generated {len(visualizations)} visualizations successfully!") 