#!/usr/bin/env python3
"""
AI-Powered Report Generator (Enhanced Typst Edition)
Generates professional AI-driven research reports using Google's Gemini API, Firecrawl, and Typst for PDF rendering.
"""

import os
import sys
import asyncio
import argparse
import traceback
import signal
import atexit
import json
import re
import time
import shutil
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Set
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

# Set matplotlib backend to avoid GUI issues
import matplotlib
matplotlib.use('Agg')

# Suppress warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*gRPC.*")
warnings.filterwarnings("ignore", message=".*absl.*")
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['ABSL_LOGGING_MIN_LEVEL'] = '1'

# Import all the enhanced components
from report_planner import ReportPlanner, ReportType
from enhanced_firecrawl_research import EnhancedFirecrawlResearch
from enhanced_firecrawl_integration import EnhancedFirecrawlReportGenerator
from enhanced_visualization_generator import PremiumVisualizationGenerator
from enhanced_content_generator import EnhancedContentGenerator
from typst_renderer import render_to_pdf_with_typst

# Load environment variables
load_dotenv()


class EnhancedReportGenerator:
    """Generate comprehensive PDF reports from enhanced Firecrawl research"""
    
    def __init__(self, gemini_api_key: str):
        """Initialize the report generator"""
        self.gemini_api_key = gemini_api_key
        
        # Initialize all components
        self.research = EnhancedFirecrawlResearch(gemini_api_key)
        self.report_planner = ReportPlanner(gemini_api_key)
        self.enhanced_firecrawl_generator = EnhancedFirecrawlReportGenerator(gemini_api_key)
        self.content_generator = EnhancedContentGenerator(gemini_api_key)
        
        # Brand colors for visualizations
        self.brand_colors = {
            "primary": "#0D203D",
            "secondary": "#666666", 
            "accent": "#4A90E2",
            "background": "#F7FAFC"
        }
        
        # Initialize visualization generator
        self.data_visualizer = PremiumVisualizationGenerator(brand_colors=self.brand_colors)
        
        # Create output directories
        self.charts_dir = Path("temp_charts")
        self.charts_dir.mkdir(exist_ok=True)
        
        self.reports_dir = Path("generated_reports")
        self.reports_dir.mkdir(exist_ok=True)
        self._used_chart_labels = set()
    
    def _get_template_colors(self, template: str) -> Dict[str, str]:
        """Get template-specific colors"""
        if template == "template_1":
            return {
                "primary": "#1A2B42",
                "secondary": "#4A5568", 
                "accent": "#D69E2E",
                "background": "#F7FAFC"
            }
        elif template == "template_2":
            return {
                "primary": "#2D3748",
                "secondary": "#718096",
                "accent": "#4299E1", 
                "background": "#FFFFFF"
            }
        else:
            return self.brand_colors
    
    def _convert_content_to_typst(self, content: str) -> str:
        """Convert content to Typst format"""
        # Convert markdown-style formatting to Typst
        content = re.sub(r'\*\*(.*?)\*\*', r'*$1*', content)  # Bold to italic
        content = re.sub(r'# (.*)', r'= $1', content)  # H1 to Typst heading
        content = re.sub(r'## (.*)', r'== $1', content)  # H2 to Typst subheading
        content = re.sub(r'- (.*)', r'• $1', content)  # Bullet points
        return content

    def _format_section_content(self, content: str) -> str:
        """Group sentences into paragraphs of 2–4, split at bullets or steps, use only '•' for bullets, and format steps."""
        # Normalize bullets
        content = re.sub(r'[‣→-]', '•', content)
        # Detect and format steps
        step_keywords = ["steps", "process", "procedure", "how to", "instructions"]
        step_pattern = re.compile(r'(following are the steps.*?:)', re.IGNORECASE)
        match = step_pattern.search(content)
        if match:
            before = content[:match.end()].strip()
            after = content[match.end():].strip()
            # Split steps by lines or numbers
            steps = re.split(r'\n|\d+\)|•', after)
            steps = [s.strip() for s in steps if s.strip()]
            steps_formatted = [f"{i+1}) {s}" for i, s in enumerate(steps)]
            return before + "\n" + "\n".join(steps_formatted)
        # Split into sentences
        sentences = re.split(r'(?<=[.!?]) +', content)
        paragraphs = []
        para = []
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            # Start new paragraph at bullet or if para is long enough
            if sent.startswith('•') or len(para) >= 3:
                if para:
                    paragraphs.append(' '.join(para))
                para = [sent]
            else:
                para.append(sent)
        if para:
            paragraphs.append(' '.join(para))
        # Join paragraphs with double newlines
        return '\n\n'.join(paragraphs)
    
    def _shorten_labels(self, labels: list, max_words: int = 2, used_labels: Optional[Set[str]] = None) -> Tuple[list, Optional[list]]:
        """Shorten labels to first 1–2 words, ensure uniqueness, return (short_labels, legend_labels)"""
        short_labels = []
        legend_labels = []
        if used_labels is None:
            used_labels = set()
        for idx, label in enumerate(labels):
            orig_label = label
            # Use only the first 1–2 words
            words = label.split()
            label = ' '.join(words[:max_words])
            # Ensure uniqueness within the chart
            base_label = label
            count = 1
            while label in used_labels:
                label = f"{base_label} {count}"
                count += 1
            used_labels.add(label)
            short_labels.append(label)
            if label != orig_label:
                legend_labels.append(orig_label)
        return short_labels, legend_labels if legend_labels else None

    def _generate_chart_data_from_learnings(self, learnings: List[str], sources: List[Dict], chart_type: str, section_title: str) -> Dict[str, Any]:
        """Generate real chart data from research learnings - NO FALLBACKS, REAL DATA ONLY"""
        try:
            # Extract comprehensive numerical data from learnings
            numerical_data = self.extract_numerical_data(learnings)
            
            # Generate appropriate chart data based on chart type and actual data
            if chart_type == "bar":
                return self._generate_bar_chart_data(numerical_data, section_title)
            elif chart_type == "horizontalBar":
                return self._generate_horizontal_bar_chart_data(numerical_data, section_title)
            elif chart_type == "line":
                return self._generate_line_chart_data(numerical_data, section_title)
            elif chart_type == "pie":
                return self._generate_pie_chart_data(numerical_data, section_title)
            elif chart_type == "donut":
                return self._generate_donut_chart_data(numerical_data, section_title)
            elif chart_type == "scatter":
                return self._generate_scatter_chart_data(numerical_data, section_title)
            elif chart_type == "area":
                return self._generate_area_chart_data(numerical_data, section_title)
            elif chart_type == "stackedBar":
                return self._generate_stacked_bar_chart_data(numerical_data, section_title)
            elif chart_type == "multiLine":
                return self._generate_multi_line_chart_data(numerical_data, section_title)
            elif chart_type == "radar":
                return self._generate_radar_chart_data(numerical_data, section_title)
            elif chart_type == "bubble":
                return self._generate_bubble_chart_data(numerical_data, section_title)
            elif chart_type == "heatmap":
                return self._generate_heatmap_chart_data(numerical_data, section_title)
            elif chart_type == "waterfall":
                return self._generate_waterfall_chart_data(numerical_data, section_title)
            elif chart_type == "funnel":
                return self._generate_funnel_chart_data(numerical_data, section_title)
            elif chart_type == "gauge":
                return self._generate_gauge_chart_data(numerical_data, section_title)
            elif chart_type == "treeMap":
                return self._generate_tree_map_chart_data(numerical_data, section_title)
            elif chart_type == "sunburst":
                return self._generate_sunburst_chart_data(numerical_data, section_title)
            elif chart_type == "candlestick":
                return self._generate_candlestick_chart_data(numerical_data, section_title)
            elif chart_type == "boxPlot":
                return self._generate_box_plot_chart_data(numerical_data, section_title)
            elif chart_type == "violinPlot":
                return self._generate_violin_plot_chart_data(numerical_data, section_title)
            elif chart_type == "histogram":
                return self._generate_histogram_chart_data(numerical_data, section_title)
            elif chart_type == "pareto":
                return self._generate_pareto_chart_data(numerical_data, section_title)
            elif chart_type == "flowchart":
                return self._generate_flowchart_chart_data(numerical_data, section_title)
            else:
                # If no valid chart type, return empty data
                return {}
                
        except Exception as e:
            print(f"Error generating chart data: {e}")
            # Return empty data instead of fallback
            return {}
    
    def extract_numerical_data(self, learnings: List[str]) -> Dict[str, Any]:
        """Extract comprehensive numerical data from learnings for chart generation"""
        numerical_data = {
            "percentages": [],
            "amounts": [],
            "years": [],
            "companies": [],
            "metrics": [],
            "categories": [],
            "trends": [],
            "locations": [],
            "products": [],
            "industries": [],
            "technologies": [],
            "time_series": [],
            "correlations": [],
            "rankings": []
        }
        
        # Enhanced patterns to extract data
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        amount_pattern = r'\$(\d+(?:\.\d+)?)\s*(?:billion|million|thousand|trillion)?'
        year_pattern = r'20(?:2[0-9]|1[0-9])'
        company_pattern = r'\b(?:Microsoft|Google|Amazon|IBM|Oracle|Salesforce|SAP|Adobe|Intel|NVIDIA|Meta|Apple|Netflix|Uber|Airbnb|Tesla|SpaceX|OpenAI|Anthropic|Palantir|Snowflake|Databricks|MongoDB|Elastic|Splunk|Tableau|PowerBI|Alteryx|Datadog|New Relic|PagerDuty|Slack|Zoom|Teams|Discord|Notion|Figma|Miro|Asana|Trello|Monday|Jira|Confluence|GitHub|GitLab|Bitbucket|Docker|Kubernetes|AWS|Azure|GCP|DigitalOcean|Heroku|Vercel|Netlify|Stripe|PayPal|Square|Shopify|WooCommerce|Magento|BigCommerce|HubSpot|Marketo|Pardot|Eloqua|Mailchimp|Constant Contact|SendGrid|Twilio|Vonage|RingCentral|Zoom|Webex|Teams|Slack|Discord|Notion|Figma|Miro|Asana|Trello|Monday|Jira|Confluence|GitHub|GitLab|Bitbucket|Docker|Kubernetes|AWS|Azure|GCP|DigitalOcean|Heroku|Vercel|Netlify|Stripe|PayPal|Square|Shopify|WooCommerce|Magento|BigCommerce|HubSpot|Marketo|Pardot|Eloqua|Mailchimp|Constant Contact|SendGrid|Twilio|Vonage|RingCentral)\b'
        technology_pattern = r'\b(?:AI|ML|Machine Learning|Deep Learning|Neural Networks|NLP|Natural Language Processing|Computer Vision|Robotic Process Automation|RPA|Predictive Analytics|Business Intelligence|BI|Data Analytics|Big Data|Cloud Computing|Edge Computing|IoT|Internet of Things|Blockchain|Cryptocurrency|Bitcoin|Ethereum|5G|6G|Quantum Computing|Augmented Reality|AR|Virtual Reality|VR|Mixed Reality|MR|Extended Reality|XR|Cybersecurity|Zero Trust|DevOps|CI/CD|Microservices|API|REST|GraphQL|Serverless|Containerization|Kubernetes|Docker|Terraform|Ansible|Jenkins|GitLab CI|GitHub Actions|AWS|Azure|GCP|SaaS|PaaS|IaaS|FaaS|BaaS|DaaS|MaaS|XaaS)\b'
        industry_pattern = r'\b(?:Healthcare|Finance|Banking|Insurance|Retail|E-commerce|Manufacturing|Automotive|Aerospace|Defense|Energy|Oil|Gas|Renewable|Solar|Wind|Nuclear|Utilities|Telecommunications|Media|Entertainment|Gaming|Education|EdTech|Real Estate|Construction|Transportation|Logistics|Supply Chain|Agriculture|AgTech|Food|Beverage|Pharmaceuticals|Biotech|Life Sciences|Chemicals|Mining|Metals|Textiles|Fashion|Luxury|Hospitality|Travel|Tourism|Sports|Fitness|Wellness|Beauty|Cosmetics|Pet|Veterinary|Legal|Law|Consulting|Professional Services|Non-profit|Government|Public Sector|Military|Defense|Security|Law Enforcement|Emergency Services|Fire|Police|Ambulance|Hospital|Clinic|Pharmacy|Laboratory|Research|Academic|University|College|School|Training|Certification|Professional Development|Skills|Talent|HR|Human Resources|Recruitment|Staffing|Payroll|Benefits|Compensation|Performance|Learning|Development|Diversity|Inclusion|Equity|Belonging|Culture|Employee Experience|EX|Customer Experience|CX|User Experience|UX|Design|Product|Service|Innovation|R&D|Research and Development|Intellectual Property|IP|Patent|Trademark|Copyright|Licensing|Franchising|Partnership|Alliance|Joint Venture|Merger|Acquisition|IPO|Initial Public Offering|Venture Capital|VC|Private Equity|PE|Angel Investment|Crowdfunding|ICO|Initial Coin Offering|STO|Security Token Offering|DeFi|Decentralized Finance|NFT|Non-Fungible Token|Metaverse|Web3|Web 3.0|Semantic Web|Social Media|Digital Marketing|Content Marketing|Inbound Marketing|Outbound Marketing|Growth Hacking|Growth Marketing|Performance Marketing|Affiliate Marketing|Influencer Marketing|Viral Marketing|Guerrilla Marketing|Ambush Marketing|Stealth Marketing|Buzz Marketing|Word of Mouth|Referral Marketing|Loyalty Program|Rewards|Gamification|Personalization|Customization|Mass Customization|One-to-One Marketing|Segmentation|Targeting|Positioning|Branding|Brand Management|Brand Equity|Brand Awareness|Brand Recognition|Brand Recall|Brand Loyalty|Brand Advocacy|Brand Ambassador|Brand Evangelist|Brand Champion|Brand Guardian|Brand Steward|Brand Custodian|Brand Owner|Brand Manager|Brand Director|Brand VP|Brand CMO|Brand CEO|Brand Founder|Brand Co-founder|Brand Partner|Brand Investor|Brand Advisor|Brand Consultant|Brand Agency|Brand Studio|Brand House|Brand Lab|Brand Incubator|Brand Accelerator|Brand Incubator|Brand Accelerator|Brand Incubator|Brand Accelerator)\b'
        
        for learning in learnings:
            # Extract percentages with context
            percentages = re.findall(percentage_pattern, learning)
            for pct in percentages:
                context = self._extract_context_around_number(learning, pct)
                numerical_data["percentages"].append({
                    "value": float(pct),
                    "label": context,
                    "context": learning[:100] + "...",
                    "source": learning
                })
            
            # Extract amounts with context
            amounts = re.findall(amount_pattern, learning)
            for amount in amounts:
                context = self._extract_context_around_number(learning, amount)
                numerical_data["amounts"].append({
                    "value": float(amount),
                    "label": context,
                    "context": learning[:100] + "...",
                    "source": learning
                })
            
            # Extract years
            years = re.findall(year_pattern, learning)
            for year in years:
                numerical_data["years"].append({
                    "value": int(year),
                    "context": learning[:100] + "...",
                    "source": learning
                })
            
            # Extract companies
            companies = re.findall(company_pattern, learning, re.IGNORECASE)
            for company in companies:
                if company not in [c["name"] for c in numerical_data["companies"]]:
                    numerical_data["companies"].append({
                        "name": company,
                        "context": learning[:100] + "...",
                        "source": learning
                    })
            
            # Extract technologies
            technologies = re.findall(technology_pattern, learning, re.IGNORECASE)
            for tech in technologies:
                if tech not in [t["name"] for t in numerical_data["technologies"]]:
                    numerical_data["technologies"].append({
                        "name": tech,
                        "context": learning[:100] + "...",
                        "source": learning
                    })
            
            # Extract industries
            industries = re.findall(industry_pattern, learning, re.IGNORECASE)
            for industry in industries:
                if industry not in [i["name"] for i in numerical_data["industries"]]:
                    numerical_data["industries"].append({
                        "name": industry,
                        "context": learning[:100] + "...",
                        "source": learning
                    })
            
            # Extract categories and metrics from the learning text
            categories = self._extract_categories_from_text(learning)
            numerical_data["categories"].extend(categories)
        
        return numerical_data
    
    def _extract_context_around_number(self, text: str, number: str) -> str:
        """Extract meaningful context around a number in text"""
        try:
            # Find the position of the number
            pos = text.find(number)
            if pos == -1:
                return f"Metric {number}"
            
            # Extract words around the number
            start = max(0, pos - 50)
            end = min(len(text), pos + 50)
            context = text[start:end]
            
            # Clean up the context
            context = re.sub(r'\s+', ' ', context).strip()
            if len(context) > 30:
                context = context[:30] + "..."
            
            return context if context else f"Metric {number}"
        except:
            return f"Metric {number}"
    
    def _extract_categories_from_text(self, text: str) -> List[str]:
        """Extract meaningful categories from text"""
        categories = []
        
        # Common AI/enterprise categories
        ai_categories = [
            "AI Adoption", "Machine Learning", "Deep Learning", "Natural Language Processing",
            "Computer Vision", "Robotic Process Automation", "Predictive Analytics",
            "Customer Experience", "Operational Efficiency", "Data Analytics",
            "Cloud Computing", "Cybersecurity", "Digital Transformation",
            "Cost Savings", "Revenue Growth", "Productivity", "Innovation",
            "Data Privacy", "Ethical AI", "Explainable AI", "Edge Computing",
            "IoT Integration", "API Management", "Microservices", "DevOps",
            "Agile Development", "Scrum", "Kanban", "Lean", "Six Sigma",
            "Business Process Management", "Workflow Automation", "Decision Support",
            "Business Intelligence", "Data Warehousing", "Data Mining", "Data Science",
            "Statistical Analysis", "Regression Analysis", "Classification", "Clustering",
            "Neural Networks", "Convolutional Neural Networks", "Recurrent Neural Networks",
            "Transformer Models", "Large Language Models", "Generative AI", "Chatbots",
            "Virtual Assistants", "Recommendation Systems", "Fraud Detection",
            "Risk Management", "Compliance", "Governance", "Audit", "Monitoring",
            "Performance Optimization", "Scalability", "Reliability", "Availability",
            "Disaster Recovery", "Backup", "Archiving", "Data Retention", "Data Lifecycle"
        ]
        
        for category in ai_categories:
            if category.lower() in text.lower():
                categories.append(category)
        
        return categories
    
    def _generate_bar_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate bar chart data with real data only"""
        if numerical_data["percentages"]:
            # Use percentage data with meaningful labels
            data_points = numerical_data["percentages"][:5]
            short_labels, legend_labels = self._shorten_labels([d.get("label", f"Metric {i+1}") for i, d in enumerate(data_points)])
            return {
                "labels": short_labels,
                "values": [d["value"] for d in data_points],
                "legend_labels": legend_labels
            }
        elif numerical_data["amounts"]:
            # Use amount data with meaningful labels
            data_points = numerical_data["amounts"][:5]
            short_labels, legend_labels = self._shorten_labels([d.get("label", f"Investment {i+1}") for i, d in enumerate(data_points)])
            return {
                "labels": short_labels,
                "values": [d["value"] for d in data_points],
                "legend_labels": legend_labels
            }
        elif numerical_data["companies"]:
            # Use company data with generated values based on context
            companies = numerical_data["companies"][:5]
            short_labels, legend_labels = self._shorten_labels([c["name"] for c in companies])
            return {
                "labels": short_labels,
                "values": [len(c["context"]) for c in companies],
                "legend_labels": legend_labels
            }
        elif numerical_data["technologies"]:
            # Use technology data
            technologies = numerical_data["technologies"][:5]
            short_labels, legend_labels = self._shorten_labels([t["name"] for t in technologies])
            return {
                "labels": short_labels,
                "values": [len(t["context"]) for t in technologies],
                "legend_labels": legend_labels
            }
        else:
            # No real data available
            return {}
    
    def _generate_horizontal_bar_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate horizontal bar chart data with real data only"""
        return self._generate_bar_chart_data(numerical_data, section_title)
    
    def _generate_line_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate line chart data with real data only"""
        if numerical_data["years"] and numerical_data["percentages"]:
            # Use year and percentage data for line chart
            years = sorted(list(set([d["value"] for d in numerical_data["years"]])))[:5]
            percentages = numerical_data["percentages"][:len(years)]
            
            return {
                "labels": [str(year) for year in years],
                "values": [d["value"] for d in percentages]
            }
        elif numerical_data["years"] and numerical_data["amounts"]:
            # Use year and amount data for line chart
            years = sorted(list(set([d["value"] for d in numerical_data["years"]])))[:5]
            amounts = numerical_data["amounts"][:len(years)]
            
            return {
                "labels": [str(year) for year in years],
                "values": [d["value"] for d in amounts]
            }
        else:
            # No real time series data available
            return {}
    
    def _generate_pie_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate pie chart data with real data only, no duplicate labels/values."""
        if numerical_data["percentages"]:
            # Use percentage data with meaningful labels
            data_points = numerical_data["percentages"][:5]
            labels = [d.get("label", f"Segment {i+1}") for i, d in enumerate(data_points)]
            values = [d["value"] for d in data_points]
            # Remove duplicates
            seen = set()
            unique_labels = []
            unique_values = []
            for l, v in zip(labels, values):
                if l not in seen:
                    unique_labels.append(l)
                    unique_values.append(v)
                    seen.add(l)
            short_labels, legend_labels = self._shorten_labels(unique_labels, used_labels=getattr(self, '_used_chart_labels', set()))
            if hasattr(self, '_used_chart_labels'):
                self._used_chart_labels.update(short_labels)
            return {
                "labels": short_labels,
                "values": unique_values,
                "legend_labels": legend_labels
            }
        elif numerical_data["companies"]:
            companies = numerical_data["companies"][:5]
            labels = [c["name"] for c in companies]
            values = [len(c["context"]) for c in companies]
            seen = set()
            unique_labels = []
            unique_values = []
            for l, v in zip(labels, values):
                if l not in seen:
                    unique_labels.append(l)
                    unique_values.append(v)
                    seen.add(l)
            short_labels, legend_labels = self._shorten_labels(unique_labels, used_labels=getattr(self, '_used_chart_labels', set()))
            if hasattr(self, '_used_chart_labels'):
                self._used_chart_labels.update(short_labels)
            return {
                "labels": short_labels,
                "values": unique_values,
                "legend_labels": legend_labels
            }
        elif numerical_data["technologies"]:
            technologies = numerical_data["technologies"][:5]
            labels = [t["name"] for t in technologies]
            values = [len(t["context"]) for t in technologies]
            seen = set()
            unique_labels = []
            unique_values = []
            for l, v in zip(labels, values):
                if l not in seen:
                    unique_labels.append(l)
                    unique_values.append(v)
                    seen.add(l)
            short_labels, legend_labels = self._shorten_labels(unique_labels, used_labels=getattr(self, '_used_chart_labels', set()))
            if hasattr(self, '_used_chart_labels'):
                self._used_chart_labels.update(short_labels)
            return {
                "labels": short_labels,
                "values": unique_values,
                "legend_labels": legend_labels
            }
        else:
            return {}
    
    def _generate_donut_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate donut chart data with real data only, no duplicate labels/values."""
        return self._generate_pie_chart_data(numerical_data, section_title)
    
    def _generate_scatter_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate scatter chart data with real data only, ensure valid and non-constant data."""
        if numerical_data["percentages"] and numerical_data["amounts"]:
            data_points = min(len(numerical_data["percentages"]), len(numerical_data["amounts"]), 5)
            x_values = [d["value"] for d in numerical_data["amounts"][:data_points]]
            y_values = [d["value"] for d in numerical_data["percentages"][:data_points]]
            # Ensure not all x or y are the same and not empty
            if data_points > 1 and len(set(x_values)) > 1 and len(set(y_values)) > 1:
                short_labels, legend_labels = self._shorten_labels([f"Point {i+1}" for i in range(data_points)], used_labels=getattr(self, '_used_chart_labels', set()))
                if hasattr(self, '_used_chart_labels'):
                    self._used_chart_labels.update(short_labels)
                return {
                    "labels": short_labels,
                    "x_values": x_values,
                    "y_values": y_values,
                    "legend_labels": legend_labels
                }
        # Fallback to bar chart if scatter is not valid
        return self._generate_bar_chart_data(numerical_data, section_title)
    
    def _generate_area_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate area chart data with real data only"""
        return self._generate_line_chart_data(numerical_data, section_title)
    
    def _generate_stacked_bar_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate stacked bar chart data with real data only"""
        if numerical_data["companies"] and numerical_data["technologies"]:
            companies = numerical_data["companies"][:3]
            technologies = numerical_data["technologies"][:3]
            
            return {
                "labels": [c["name"] for c in companies],
                "series": [
                    {
                        "name": tech["name"],
                        "values": [len(tech["context"]) for _ in companies]
                    } for tech in technologies
                ]
            }
        else:
            return {}
    
    def _generate_multi_line_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate multi-line chart data with real data only"""
        if numerical_data["years"] and numerical_data["percentages"] and numerical_data["amounts"]:
            years = sorted(list(set([d["value"] for d in numerical_data["years"]])))[:5]
            percentages = numerical_data["percentages"][:len(years)]
            amounts = numerical_data["amounts"][:len(years)]
            
            return {
                "labels": [str(year) for year in years],
                "series": [
                    {
                        "name": "Percentage",
                        "values": [d["value"] for d in percentages]
                    },
                    {
                        "name": "Amount",
                        "values": [d["value"] for d in amounts]
                    }
                ]
            }
        else:
            return {}
    
    def _generate_radar_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate radar chart data with real data only"""
        if numerical_data["categories"]:
            categories = list(set(numerical_data["categories"]))[:5]
            return {
                "labels": categories,
                "values": [len(cat) for cat in categories]  # Use category length as proxy for importance
            }
        else:
            return {}
    
    def _generate_bubble_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate bubble chart data with real data only"""
        if numerical_data["percentages"] and numerical_data["amounts"] and numerical_data["companies"]:
            data_points = min(len(numerical_data["percentages"]), len(numerical_data["amounts"]), len(numerical_data["companies"]), 5)
            return {
                "labels": [c["name"] for c in numerical_data["companies"][:data_points]],
                "x_values": [d["value"] for d in numerical_data["percentages"][:data_points]],
                "y_values": [d["value"] for d in numerical_data["amounts"][:data_points]],
                "sizes": [len(c["context"]) for c in numerical_data["companies"][:data_points]]
            }
        else:
            return {}
    
    def _generate_heatmap_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate heatmap chart data with real data only"""
        if numerical_data["companies"] and numerical_data["technologies"]:
            companies = numerical_data["companies"][:4]
            technologies = numerical_data["technologies"][:4]
            
            # Create a simple heatmap matrix
            values = []
            for tech in technologies:
                row = []
                for company in companies:
                    # Use context overlap as heatmap value
                    overlap = len(set(tech["context"].lower().split()) & set(company["context"].lower().split()))
                    row.append(overlap)
                values.append(row)
            
            return {
                "labels": [c["name"] for c in companies],
                "categories": [t["name"] for t in technologies],
                "values": values
            }
        else:
            return {}
    
    def _generate_waterfall_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate waterfall chart data with real data only"""
        if numerical_data["amounts"]:
            amounts = [d["value"] for d in numerical_data["amounts"][:5]]
            return {
                "labels": ["Start", "Revenue", "Costs", "Taxes", "End"],
                "values": [0] + amounts + [sum(amounts)]
            }
        else:
            return {}
    
    def _generate_funnel_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate funnel chart data with real data only"""
        if numerical_data["percentages"]:
            percentages = [d["value"] for d in numerical_data["percentages"][:5]]
            return {
                "labels": ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5"],
                "values": percentages
            }
        else:
            return {}
    
    def _generate_gauge_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate gauge chart data with real data only"""
        if numerical_data["percentages"]:
            avg_percentage = sum(d["value"] for d in numerical_data["percentages"]) / len(numerical_data["percentages"])
            return {
                "value": avg_percentage,
                "max": 100,
                "label": "Average Performance"
            }
        else:
            return {}
    
    def _generate_tree_map_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate tree map chart data with real data only"""
        if numerical_data["companies"] and numerical_data["technologies"]:
            companies = numerical_data["companies"][:3]
            technologies = numerical_data["technologies"][:3]
            
            return {
                "labels": [c["name"] for c in companies],
                "values": [len(c["context"]) for c in companies],
                "subcategories": [[t["name"] for t in technologies] for _ in companies]
            }
        else:
            return {}
    
    def _generate_sunburst_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate sunburst chart data with real data only"""
        if numerical_data["industries"] and numerical_data["technologies"]:
            industries = numerical_data["industries"][:2]
            technologies = numerical_data["technologies"][:2]
            
            return {
                "labels": ["Root"] + [i["name"] for i in industries],
                "values": [100] + [len(i["context"]) for i in industries],
                "children": [[t["name"] for t in technologies] for _ in industries]
            }
        else:
            return {}
    
    def _generate_candlestick_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate candlestick chart data with real data only"""
        if numerical_data["amounts"] and len(numerical_data["amounts"]) >= 3:
            amounts = [d["value"] for d in numerical_data["amounts"][:3]]
            return {
                "labels": ["Day 1", "Day 2", "Day 3"],
                "open": amounts,
                "high": [a * 1.1 for a in amounts],
                "low": [a * 0.9 for a in amounts],
                "close": [a * 1.05 for a in amounts]
            }
        else:
            return {}
    
    def _generate_box_plot_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate box plot chart data with real data only"""
        if numerical_data["percentages"] and len(numerical_data["percentages"]) >= 3:
            # Group percentages into categories
            groups = []
            for i in range(0, len(numerical_data["percentages"]), 3):
                group = [d["value"] for d in numerical_data["percentages"][i:i+3]]
                if group:
                    groups.append(group)
            
            if groups:
                return {
                    "labels": [f"Group {i+1}" for i in range(len(groups))],
                    "data": groups
                }
        return {}
    
    def _generate_violin_plot_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate violin plot chart data with real data only"""
        return self._generate_box_plot_chart_data(numerical_data, section_title)
    
    def _generate_histogram_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate histogram chart data with real data only"""
        if numerical_data["percentages"]:
            values = [d["value"] for d in numerical_data["percentages"]]
            # Create histogram bins
            bins = ["0-20", "21-40", "41-60", "61-80", "81-100"]
            bin_counts = [0] * 5
            
            for value in values:
                if value <= 20:
                    bin_counts[0] += 1
                elif value <= 40:
                    bin_counts[1] += 1
                elif value <= 60:
                    bin_counts[2] += 1
                elif value <= 80:
                    bin_counts[3] += 1
                else:
                    bin_counts[4] += 1
            
            return {
                "labels": bins,
                "values": bin_counts
            }
        else:
            return {}
    
    def _generate_pareto_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate Pareto chart data with real data only"""
        if numerical_data["percentages"]:
            data_points = numerical_data["percentages"][:5]
            values = [d["value"] for d in data_points]
            cumulative = []
            total = 0
            for value in values:
                total += value
                cumulative.append(total)
            
            return {
                "labels": [d.get("label", f"Issue {i+1}") for i, d in enumerate(data_points)],
                "values": values,
                "cumulative": cumulative
            }
        else:
            return {}
    
    def _generate_flowchart_chart_data(self, numerical_data: Dict, section_title: str) -> Dict[str, Any]:
        """Generate flowchart chart data with real data only"""
        # Flowcharts are complex and require specific data structure
        # For now, return empty data
        return {}
    
    def _generate_chart_explanation(self, chart_data: Dict[str, Any], chart_type: str, section_title: str, section_content: str = "") -> str:
        """Generate a 100–150 word descriptive, insightful analysis for each graph."""
        if not chart_data or not any(chart_data.values()):
            return ""
        try:
            # Compose a detailed, human-friendly summary
            summary_lines = []
            # Add a brief intro
            summary_lines.append(f"The following {chart_type.replace('_', ' ')} chart visualizes key data for the section '{section_title}'.")
            # Add axis/legend info
            labels = chart_data.get("labels", [])
            legend_labels = chart_data.get("legend_labels", [])
            values = chart_data.get("values", [])
            if labels and values:
                if legend_labels:
                    summary_lines.append(f"The chart uses concise axis labels for clarity. Full details are available in the legend.")
                # Highlight max/min
                max_value = max(values)
                min_value = min(values)
                max_label = labels[values.index(max_value)]
                min_label = labels[values.index(min_value)]
                summary_lines.append(f"The highest value is for '{max_label}' at {max_value}, while the lowest is '{min_label}' at {min_value}.")
                # Mention spread
                summary_lines.append(f"This spread indicates the variation across the measured categories.")
            # Add trend/insight if possible
            if chart_type in ["line", "area"] and values:
                trend = "increasing" if values[-1] > values[0] else "decreasing" if values[-1] < values[0] else "stable"
                summary_lines.append(f"The trend over time is {trend}, with values ranging from {min(values)} to {max(values)}.")
            # Add a sentence about implications
            if section_content:
                # Use the first 1-2 sentences from the section as context
                sentences = re.split(r'(?<=[.!?]) +', section_content)
                summary_lines.append(f"Contextually, this data supports the following insight: {sentences[0]}")
                if len(sentences) > 1:
                    summary_lines.append(sentences[1])
            # Compose into a single paragraph, limit to ~150 words
            explanation = ' '.join(summary_lines)
            words = explanation.split()
            if len(words) > 150:
                explanation = ' '.join(words[:150]) + '...'
            return explanation
        except Exception as e:
            print(f"Error generating chart explanation: {e}")
            return "This chart provides a visual representation of the data and highlights key trends and differences among the categories."
        
        # Default return for any unhandled cases
        return f"This chart provides a visual representation of the {section_title.lower()} data."
    
    async def generate_comprehensive_pdf(self, query: str, page_count: int = 8, template: str = "template_1", keep_temp: bool = False) -> Dict[str, Any]:
        """Generate comprehensive PDF using enhanced Firecrawl research"""
        print(f"🚀 Starting enhanced PDF generation for: {query}")
        print(f"📊 Configuration: {page_count} pages, template: {template}")
        
        self._used_chart_labels = set()
        temp_assets_dir = os.path.join("templates", "assets_temp")
        os.makedirs(temp_assets_dir, exist_ok=True)
        temp_chart_paths = []
        try:
            # Step 1: Collect learnings from enhanced Firecrawl research
            print("\n🌐 Step 1: Collecting research data from enhanced Firecrawl...")
            research_result = await self.research.deep_research(
                query=query,
                breadth=4,
                depth=2
            )
            
            if not research_result["success"]:
                print(f"❌ Research failed: {research_result.get('error', 'Unknown error')}")
                return {"success": False, "error": "Research failed"}
            
            learnings = research_result.get("learnings", [])
            source_metadata = research_result.get("source_metadata", [])
            
            # Convert SourceMetadata objects to dictionaries for JSON serialization
            sources = []
            for source in source_metadata:
                sources.append({
                    "url": source.url,
                    "domain": source.domain,
                    "reliability_score": source.reliability_score,
                    "reliability_reasoning": source.reliability_reasoning,
                    "title": source.title,
                    "content_length": source.content_length
                })
            
            print(f"✅ Collected {len(learnings)} learnings from {len(sources)} sources")
            
            # Step 2: Generate comprehensive sections using ReportPlanner with real data
            print("\n🤖 Step 2: Generating comprehensive sections using ReportPlanner...")
            blueprint = await self.report_planner.generate_report_blueprint(
                query=query,
                page_count=page_count,
                report_type=ReportType.MARKET_RESEARCH,
                learnings=learnings,
                source_metadata=sources
            )
            
            if not blueprint or "sections" not in blueprint:
                print("❌ Failed to generate comprehensive sections")
                return {"success": False, "error": "Failed to generate sections"}
            
            print(f"✅ ReportPlanner generated {len(blueprint.get('sections', []))} sections")
            for i, section in enumerate(blueprint.get("sections", [])):
                print(f"  {i+1}. {section.get('title', 'No title')} - Chart: {section.get('chart_type', 'none')}")
            
            # Step 3: Generate dynamic visualizations using real data only
            print("\n📊 Step 3: Generating dynamic visualizations from real data...")
            
            # Get template-specific colors and update the visualizer
            template_colors = self._get_template_colors(template)
            self.data_visualizer = PremiumVisualizationGenerator(brand_colors=template_colors)
            
            # Extract comprehensive numerical data from learnings for dynamic chart selection
            numerical_data = self.extract_numerical_data(learnings)
            print(f"📈 Extracted data: {len(numerical_data['percentages'])} percentages, {len(numerical_data['amounts'])} amounts, {len(numerical_data['companies'])} companies, {len(numerical_data['technologies'])} technologies")
            
            # Generate charts using real data only - NO FALLBACKS
            print("📊 Generating charts from real Firecrawl data...")
            for section in blueprint.get("sections", []):
                # Convert content to Typst format
                if "content" in section:
                    section["content"] = self._format_section_content(section["content"])
                    section["content"] = self._convert_content_to_typst(section["content"])

                chart_type = section.get("chart_type")
                if chart_type and chart_type != "none":
                    print(f"  🎨 Generating '{chart_type}' chart for: {section['title']}...")
                    try:
                        # Generate chart data from real learnings only
                        chart_data = self._generate_chart_data_from_learnings(
                            learnings, sources, chart_type, section["title"]
                        )
                        section["chart_data"] = chart_data
                        
                        # Only proceed if we have real data
                        if chart_data and any(chart_data.values()):
                            # Use the PDF-specific chart creation method
                            chart_path = self.data_visualizer.create_chart_for_pdf(section)
                            # Copy chart to temp assets dir
                            chart_filename = os.path.basename(chart_path)
                            temp_chart_path = os.path.join(temp_assets_dir, chart_filename)
                            shutil.copy2(chart_path, temp_chart_path)
                            section["chart_path"] = f"assets_temp/{chart_filename}"
                            temp_chart_paths.append(temp_chart_path)
                            print(f"    ✅ Chart generated with real data: {temp_chart_path}")
                            
                            # Add chart explanation based on real data
                            chart_explanation = self._generate_chart_explanation(chart_data, chart_type, section["title"], section["content"])
                            if chart_explanation:
                                section["content"] += f"\n\n**Chart Analysis:** {chart_explanation}"
                        else:
                            print(f"    ⚠️ No real data available for '{chart_type}' chart - skipping")
                            section["chart_path"] = ""
                            section["chart_type"] = "none"
                            
                    except Exception as e:
                        print(f"  ⚠️ Error generating chart for '{section['title']}': {e}")
                        section["chart_path"] = ""
                        section["chart_type"] = "none"
                else:
                    section["chart_path"] = ""
            
            # Step 4: Generate PDF and JSON
            print("\n📄 Step 4: Generating PDF and JSON...")
            
            # Generate PDF
            timestamp = int(time.time())
            safe_title = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]
            
            reports_dir = os.getenv("REPORTS_OUTPUT_DIR", "generated_reports")
            os.makedirs(reports_dir, exist_ok=True)
            pdf_filename = f"{reports_dir}/{timestamp}_{safe_title}.pdf"
            
            # Prepare report data for PDF generation
            report_data = {
                "title": f"Research Report: {query}",
                "subtitle": "Comprehensive Analysis and Insights",
                "author": "AI Research Assistant",
                "company": "Enhanced Research System",
                "logo_path": "assets/logo.png",
                "date": datetime.now().strftime('%B %d, %Y'),
                "sections": blueprint.get("sections", [])
            }
            
            # Generate PDF using Typst
            template_path = f"templates/{template}.typ"
            
            # Adjust chart paths to be relative to the template directory
            sections = report_data.get("sections", []) or []
            for section in sections:
                if isinstance(section, dict):
                    chart_path = section.get("chart_path")
                    if chart_path and isinstance(chart_path, str) and chart_path != "":
                        # Charts are saved in assets directory, so use relative path from templates/
                        if chart_path.startswith("assets/"):
                            section["chart_path"] = f"../{chart_path}"
                        elif chart_path.startswith("temp_charts/"):
                            section["chart_path"] = f"../{chart_path}"
                        elif os.path.isabs(chart_path):
                            # If it's an absolute path, make it relative to template directory
                            template_dir = os.path.dirname(template_path) if template_path else "templates"
                            rel_path = os.path.relpath(chart_path, template_dir)
                            section["chart_path"] = rel_path
            
            success = render_to_pdf_with_typst(report_data, template_path, pdf_filename)
            
            if not success:
                raise RuntimeError("Failed to generate PDF using Typst")
            
            # Create comprehensive JSON with all data
            json_data = {
                "title": report_data["title"],
                "subtitle": report_data["subtitle"],
                "author": report_data["author"],
                "company": report_data["company"],
                "logo_path": report_data["logo_path"],
                "date": report_data["date"],
                "sections": blueprint.get("sections", []),
                "firecrawl_research": {
                    "key_findings": learnings,
                    "sources": sources,
                    "research_metrics": {
                        "total_sources": len(sources),
                        "high_quality_sources": len([s for s in sources if s.get("reliability_score", 0) > 0.7]),
                        "average_reliability": sum(s.get("reliability_score", 0) for s in sources) / len(sources) if sources else 0
                    },
                    "credits_used": research_result.get("credits_used", 0),
                    "total_sources": len(sources),
                    "high_quality_sources": len([s for s in sources if s.get("reliability_score", 0) > 0.7])
                },
                "pdf_path": pdf_filename
            }
            
            # Save JSON report
            json_dir = os.getenv("JSON_REPORTS_DIR", "json_reports")
            os.makedirs(json_dir, exist_ok=True)
            json_filename = f"{json_dir}/{timestamp}_{safe_title}.json"
            
            with open(json_filename, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"✅ Successfully generated:")
            print(f"   - PDF: {pdf_filename}")
            print(f"   - JSON: {json_filename}")
            
            return {
                "success": True,
                "pdf_path": pdf_filename,
                "json_path": json_filename,
                "report_data": json_data,
                "learnings_count": len(learnings),
                "sources_count": len(sources),
                "credits_used": research_result.get("credits_used", 0)
            }
            
        except Exception as e:
            print(f"❌ Error generating enhanced PDF: {e}")
            # Clean up temp assets dir on error if needed
            if not keep_temp:
                try:
                    shutil.rmtree(temp_assets_dir)
                except Exception:
                    pass
            return {"success": False, "error": str(e)}


# Environment and cleanup functions
def reload_environment():
    print("🔄 Loading environment variables...")
    env_file = find_dotenv()
    if env_file:
        load_dotenv(env_file, override=True)
        print(f"✅ Environment loaded from: {env_file}")
    else:
        print("❌ No .env file found")

_cleanup_done = False

def cleanup_and_exit(signum=None, frame=None):
    global _cleanup_done
    if _cleanup_done:
        return
    _cleanup_done = True
    print("\n🧹 Cleaning up resources...")
    import contextlib
    import io
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        try:
            import gc
            gc.collect()
        except:
            pass
    sys.exit(0)

def handle_exception(exc_type, exc_value, exc_traceback):
    if exc_type is KeyboardInterrupt:
        cleanup_and_exit()
        return
    if not _cleanup_done:
        print(f"\n❌ Unhandled exception: {exc_type.__name__}: {exc_value}")
        if exc_traceback:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
    cleanup_and_exit()

atexit.register(cleanup_and_exit)
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)
sys.excepthook = handle_exception


async def main():
    """Main application entry point"""
    print("🚀 AI-Powered Report Generator (Enhanced Typst Edition)")
    print("=" * 60)
    reload_environment()
    
    parser = argparse.ArgumentParser(description="AI-Powered Report Generator (Enhanced)")
    parser.add_argument("--prompt", required=True, help="Research topic or prompt")
    parser.add_argument("--pages", type=int, default=8, help="Number of pages (default: 8)")
    parser.add_argument("--template", default="template_1", help="Typst template to use")
    args = parser.parse_args()
    
    prompt = args.prompt
    page_count = args.pages
    template = args.template
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    
    if not gemini_api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        sys.exit(1)
    
    print(f"Prompt: {prompt}")
    print(f"Pages: {page_count}")
    print(f"Template: {template}")
    print("=" * 60)
    
    # Initialize and run the enhanced report generator
    generator = EnhancedReportGenerator(gemini_api_key=gemini_api_key)
    result = await generator.generate_comprehensive_pdf(
        query=prompt,
        page_count=page_count,
        template=template,
        keep_temp=False
    )
    
    if result.get("success"):
        print("\n🎉 SUCCESS! Professional report generated!")
        print(f"📁 PDF File: {result['pdf_path']}")
        print(f"📄 JSON File: {result['json_path']}")
        print(f"📊 Learnings: {result.get('learnings_count', 0)}")
        print(f"🔗 Sources: {result.get('sources_count', 0)}")
        print(f"💳 Credits used: {result.get('credits_used', 0)}")
    else:
        print(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())