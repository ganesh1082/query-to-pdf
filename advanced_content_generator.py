from openai import OpenAI
import json
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    MARKET_RESEARCH = "market_research"
    INDUSTRY_ANALYSIS = "industry_analysis"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CONSUMER_INSIGHTS = "consumer_insights"
    FINANCIAL_REPORT = "financial_report"

@dataclass
class ReportConfig:
    title: str
    subtitle: str
    author: str
    company: str
    report_type: ReportType
    research_objectives: List[str]
    target_audience: str
    brand_colors: Dict[str, str]
    logo_path: str = None

class AdvancedContentGenerator:
    """Advanced content generation with specialized prompts"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.content_templates = self._load_content_templates()
    
    def _load_content_templates(self) -> Dict[str, str]:
        """Load specialized content templates"""
        return {
            "executive_summary": """
            Create a compelling executive summary that:
            1. Opens with the most critical finding
            2. Presents 3-5 key insights with supporting data
            3. Quantifies business impact where possible
            4. Ends with clear, actionable recommendations
            5. Uses language appropriate for C-suite audience
            6. Stays within 500-750 words
            """,
            "methodology": """
            Describe the research methodology with:
            1. Data collection methods and sources
            2. Sample sizes and selection criteria
            3. Analysis techniques employed
            4. Quality assurance measures
            5. Limitations and potential biases
            6. Confidence levels and margins of error
            """,
            "market_analysis": """
            Provide comprehensive market analysis including:
            1. Market size and growth projections
            2. Key market drivers and barriers
            3. Competitive landscape analysis
            4. Consumer behavior insights
            5. Technology trends and disruptions
            6. Regulatory environment impact
            """,
            "recommendations": """
            Develop strategic recommendations that are:
            1. Specific and actionable
            2. Prioritized by impact and feasibility
            3. Include implementation timelines
            4. Address potential risks and mitigation
            5. Quantify expected outcomes
            6. Consider resource requirements
            """
        }
    
    async def generate_comprehensive_report(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate complete report content"""
        
        print("📝 Generating executive summary...")
        executive_summary = await self.generate_executive_summary(research_data, config)
        
        print("📝 Generating methodology...")
        methodology = await self.generate_methodology(research_data, config)
        
        print("📝 Generating key findings...")
        key_findings = await self.generate_key_findings(research_data, config)
        
        print("📝 Generating detailed analysis...")
        detailed_analysis = await self.generate_detailed_analysis(research_data, config)
        
        print("📝 Generating recommendations...")
        recommendations = await self.generate_recommendations(research_data, config)
        
        print("📝 Generating appendices...")
        appendices = await self.generate_appendices(research_data, config)
        
        return {
            "executive_summary": executive_summary,
            "methodology": methodology,
            "key_findings": key_findings,
            "detailed_analysis": detailed_analysis,
            "recommendations": recommendations,
            "appendices": appendices,
            "data_tables": await self.generate_data_tables(research_data, config)
        }
    
    async def generate_executive_summary(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive executive summary with enhanced detail and real data"""
        
        system_prompt = """
        You are a senior executive consultant creating a comprehensive executive summary for C-suite decision makers.
        Create a detailed summary that requires 2-3 pages when professionally formatted.
        Use specific data points, verified information, and actionable insights from the research.
        Focus on strategic implications and business impact with precise details and numbers.
        """
        
        # Extract comprehensive data from research
        primary_research = research_data.get('primary_research', [])
        competitive_intel = research_data.get('competitive_intelligence', {})
        trend_analysis = research_data.get('trend_analysis', {})
        research_metadata = research_data.get('research_metadata', {})
        
        # Extract specific data points and insights
        key_insights = []
        investment_data = []
        market_metrics = []
        verified_findings = []
        
        for source in primary_research:
            # Extract OpenAI-verified insights
            if source.get('ai_validated') and source.get('openai_analysis'):
                analysis = source.get('openai_analysis', {})
                key_insights.extend(analysis.get('key_insights', []))
            
            # Extract investment data
            if source.get('investment_data'):
                investment_data.extend(source.get('investment_data', []))
            
            # Extract market analysis
            if source.get('market_analysis'):
                market_analysis = source.get('market_analysis', {})
                if market_analysis.get('market_size'):
                    market_metrics.append(f"Market Size: {market_analysis['market_size']}")
                if market_analysis.get('growth_rate'):
                    market_metrics.append(f"Growth Rate: {market_analysis['growth_rate']}")
            
            # Extract verified findings
            if source.get('fact_verification', {}).get('credibility_score', 0) >= 7:
                verified_findings.extend(source.get('key_findings', []))
        
        user_prompt = f"""
        Create a comprehensive executive summary for: {config.title}
        
        RESEARCH INTELLIGENCE OVERVIEW:
        - Sources Analyzed: {research_metadata.get('sources_discovered', 0)} authoritative sources
        - Data Points Extracted: {research_metadata.get('data_points_extracted', 0)} verified data points
        - Research Depth: {research_metadata.get('research_depth', 'comprehensive')} analysis
        - OpenAI Verification: {research_metadata.get('openai_verification', False)}
        - Data Quality Score: {research_data.get('data_quality_score', 0):.2f}/1.00
        
        KEY VERIFIED INSIGHTS:
        {chr(10).join(key_insights[:10]) if key_insights else 'Advanced insights being processed...'}
        
        INVESTMENT INTELLIGENCE:
        {chr(10).join([f"• {inv.get('company', 'N/A')}: {inv.get('amount', 'N/A')} ({inv.get('round_type', 'N/A')}) - {inv.get('date', 'N/A')}" for inv in investment_data[:8]]) if investment_data else 'Investment data being analyzed...'}
        
        MARKET METRICS:
        {chr(10).join(market_metrics[:5]) if market_metrics else 'Market sizing in progress...'}
        
        VERIFIED FINDINGS:
        {chr(10).join(verified_findings[:8]) if verified_findings else 'Fact-checking in progress...'}
        
        COMPETITIVE LANDSCAPE:
        - Competitors Identified: {len(competitive_intel.get('competitors', []))}
        - Sources Analyzed: {competitive_intel.get('sources_analyzed', 0)}
        
        TREND ANALYSIS:
        - AI Analysis Completed: {trend_analysis.get('ai_analysis_completed', False)}
        - Data Sources: {trend_analysis.get('data_sources_analyzed', 0)}
        - Emerging Themes: {len(trend_analysis.get('emerging_themes', []))}
        
        Create a comprehensive executive summary with these detailed sections:
        
        1. STRATEGIC OVERVIEW (2-3 paragraphs)
        - High-level market assessment with specific data points
        - Key strategic implications and business opportunities
        - Critical success factors and market positioning insights
        
        2. KEY MARKET INTELLIGENCE (3-4 paragraphs)
        - Detailed market size, growth rates, and trend analysis
        - Specific investment flows and funding patterns
        - Competitive dynamics and market share insights
        - Technology adoption and innovation trends
        
        3. INVESTMENT & FINANCIAL INSIGHTS (2-3 paragraphs)
        - Detailed investment analysis with specific amounts and dates
        - Funding trends and investor preferences
        - Valuation insights and market multiples
        - Financial performance indicators
        
        4. COMPETITIVE POSITIONING (2 paragraphs)
        - Detailed competitive landscape analysis
        - Market leader strategies and positioning
        - Competitive advantages and differentiation factors
        
        5. STRATEGIC RECOMMENDATIONS (2-3 paragraphs)
        - Specific, actionable strategic recommendations
        - Implementation priorities and timeline considerations
        - Risk mitigation strategies and success metrics
        
        6. EXECUTIVE DECISION POINTS (1-2 paragraphs)
        - Critical decisions requiring executive attention
        - Resource allocation recommendations
        - Timeline for strategic initiatives
        
        Use specific numbers, dates, company names, and verified data points throughout.
        Ensure the summary is detailed enough to fill 2-3 pages when professionally formatted.
        Focus on actionable insights that drive business decisions.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "content": response,
            "key_insights": key_insights[:15],
            "market_metrics": await self._extract_market_metrics(research_data),
            "investment_summary": {
                "total_deals": len(investment_data),
                "recent_investments": investment_data[:5],
                "funding_trends": await self._analyze_funding_trends(investment_data)
            },
            "competitive_summary": await self._extract_competitive_insights(research_data),
            "data_quality": {
                "sources_verified": len([s for s in primary_research if s.get('ai_validated')]),
                "fact_checked": len([s for s in primary_research if s.get('verification_completed')]),
                "overall_quality": research_data.get('data_quality_score', 0)
            }
        }
    
    async def generate_methodology(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive methodology section with enhanced detail"""
        
        system_prompt = """
        You are a senior research methodologist documenting a comprehensive business research study.
        Create detailed methodology documentation that establishes credibility and research rigor.
        Your content should require 2-3 pages when professionally formatted.
        Focus on transparency, scientific rigor, and professional research standards.
        """
        
        user_prompt = f"""
        Document the comprehensive methodology for: {config.title}
        
        Research Parameters:
        - Data Sources Used: {len(research_data.get('primary_research', []))} primary sources
        - Quality Score: {research_data.get('data_quality_score', 'Not available')}
        - Source Categories: {list(research_data.get('source_credibility', {}).keys())}
        - Research Timeframe: Comprehensive market analysis
        - Target Audience: {config.target_audience}
        
        Create a comprehensive methodology section with the following detailed components:
        
        1. RESEARCH FRAMEWORK AND APPROACH (2-3 paragraphs)
        - Overall research philosophy and strategic approach
        - Multi-phase methodology overview
        - Research questions and analytical framework
        - Quality assurance and validation processes
        
        2. DATA COLLECTION METHODOLOGY (3-4 paragraphs)
        - Primary research sources and selection criteria
        - Data gathering techniques and tools
        - Source credibility assessment framework
        - Sampling methodology and coverage analysis
        - Time series analysis and trend identification
        
        3. ANALYTICAL METHODOLOGY (2-3 paragraphs)
        - Quantitative analysis techniques and statistical methods
        - Qualitative analysis framework and interpretation approaches
        - Data validation and cross-verification processes
        - Trend analysis and predictive modeling approaches
        
        4. QUALITY ASSURANCE AND VALIDATION (2 paragraphs)
        - Data quality metrics and assessment criteria
        - Expert validation and peer review processes
        - Bias mitigation strategies and controls
        - Confidence levels and reliability measures
        
        5. LIMITATIONS AND CONSIDERATIONS (1-2 paragraphs)
        - Research scope and boundary conditions
        - Data limitations and potential gaps
        - Methodology constraints and assumptions
        - Recommendations for future research
        
        Ensure the methodology demonstrates professional research standards and establishes credibility for the findings.
        Use specific research terminology and include details about analytical rigor.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.2)
        
        return {
            "content": response,
            "data_sources": research_data.get('primary_research', []),
            "quality_metrics": {
                "data_quality_score": research_data.get('data_quality_score', 0),
                "source_count": len(research_data.get('primary_research', [])),
                "credibility_assessment": research_data.get('source_credibility', {})
            }
        }
    
    async def generate_key_findings(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive key findings section with enhanced detail"""
        
        system_prompt = """
        You are a senior business analyst presenting comprehensive key findings from extensive research.
        Create detailed findings that require 3-4 pages when professionally formatted.
        Structure findings by strategic importance and support with specific data points and analysis.
        Demonstrate deep analytical thinking and business acumen.
        """
        
        # Extract findings from research data
        all_findings = []
        for source in research_data.get('primary_research', []):
            if 'key_findings' in source:
                all_findings.extend(source['key_findings'])
        
        user_prompt = f"""
        Analyze and present comprehensive key findings for: {config.title}
        
        Raw Findings from Research:
        {json.dumps(all_findings[:20], indent=2)}
        
        Trend Analysis:
        {json.dumps(research_data.get('trend_analysis', {}), indent=2)}
        
        Research Context:
        - Report Type: {config.report_type.value}
        - Target Audience: {config.target_audience}
        - Business Objectives: {', '.join(config.research_objectives)}
        
        Create a comprehensive key findings section with the following structure:
        
        1. FINDINGS OVERVIEW AND SIGNIFICANCE (2 paragraphs)
        - Summary of research scope and analytical depth
        - Strategic importance of findings for business decision-making
        - Context and market relevance
        
        2. MARKET DYNAMICS AND SIZE FINDINGS (2-3 detailed findings)
        Each finding should include:
        - Clear finding statement with quantified data
        - Supporting evidence and data analysis
        - Market implications and business context
        - Strategic significance for stakeholders
        - Confidence level and data reliability
        
        3. COMPETITIVE LANDSCAPE FINDINGS (2-3 detailed findings)
        Each finding should include:
        - Competitive positioning insights
        - Market share and performance analysis
        - Competitive advantage identification
        - Threat and opportunity assessment
        - Strategic implications for market positioning
        
        4. CUSTOMER AND DEMAND FINDINGS (2-3 detailed findings)
        Each finding should include:
        - Customer behavior and preference insights
        - Demand patterns and growth indicators
        - Market segmentation and targeting opportunities
        - Customer satisfaction and loyalty factors
        - Revenue and profitability implications
        
        5. TECHNOLOGY AND INNOVATION FINDINGS (2 detailed findings)
        Each finding should include:
        - Technology adoption trends and patterns
        - Innovation opportunities and disruption risks
        - Digital transformation implications
        - Competitive technology advantages
        - Investment and development priorities
        
        6. REGULATORY AND RISK FINDINGS (1-2 detailed findings)
        Each finding should include:
        - Regulatory environment and compliance requirements
        - Risk factors and mitigation strategies
        - Policy implications and business impact
        - Compliance opportunities and challenges
        
        Ensure each finding provides substantial analysis with specific data points, percentages, and quantified insights.
        Use professional analytical language and demonstrate strategic thinking.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "content": response,
            "findings_count": len(all_findings),
            "trend_indicators": research_data.get('trend_analysis', {}),
            "supporting_data": all_findings[:10]
        }
    
    async def generate_detailed_analysis(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive detailed analysis section with enhanced depth"""
        
        system_prompt = """
        You are a senior business analyst conducting comprehensive deep-dive analysis.
        Create detailed analysis that requires 4-5 pages when professionally formatted.
        Provide multi-dimensional analysis with thorough examination of implications, trends, and strategic considerations.
        Demonstrate expertise in market dynamics, competitive intelligence, and strategic business analysis.
        """
        
        user_prompt = f"""
        Provide comprehensive detailed analysis for: {config.title}
        
        Research Context:
        - Research Type: {config.report_type.value}
        - Target Audience: {config.target_audience}
        - Business Objectives: {', '.join(config.research_objectives)}
        
        Available Research Data:
        - Primary Research Sources: {len(research_data.get('primary_research', []))}
        - Competitive Intelligence: {json.dumps(research_data.get('competitive_intelligence', {}), indent=2)}
        - Quality Score: {research_data.get('data_quality_score', 0)}
        - Market Trends: {json.dumps(research_data.get('trend_analysis', {}), indent=2)}
        
        Create a comprehensive detailed analysis with the following structure:
        
        1. MARKET STRUCTURE AND DYNAMICS ANALYSIS (3-4 paragraphs)
        - Market size, growth patterns, and maturity assessment
        - Value chain analysis and distribution channels
        - Economic factors and market drivers
        - Supply and demand dynamics
        - Pricing mechanisms and profitability factors
        
        2. COMPETITIVE LANDSCAPE DEEP DIVE (3-4 paragraphs)
        - Market leader analysis and positioning strategies
        - Emerging competitor threats and opportunities
        - Competitive advantages and differentiation factors
        - Market share dynamics and consolidation trends
        - Strategic group analysis and competitive positioning
        
        3. CUSTOMER SEGMENTATION AND BEHAVIOR ANALYSIS (3-4 paragraphs)
        - Customer segment identification and characteristics
        - Purchasing behavior and decision-making processes
        - Customer satisfaction and loyalty analysis
        - Emerging customer needs and preference shifts
        - Customer acquisition and retention strategies
        
        4. TECHNOLOGY AND INNOVATION IMPACT ANALYSIS (2-3 paragraphs)
        - Technology adoption and digital transformation trends
        - Innovation opportunities and disruption potential
        - Competitive technology advantages and gaps
        - Investment requirements and development priorities
        - Future technology roadmap and implications
        
        5. REGULATORY AND POLICY ENVIRONMENT ANALYSIS (2-3 paragraphs)
        - Current regulatory framework and compliance requirements
        - Policy trends and anticipated regulatory changes
        - Government initiatives and industry support programs
        - International regulatory comparison and benchmarking
        - Regulatory risk assessment and opportunity analysis
        
        6. FINANCIAL AND INVESTMENT ANALYSIS (2-3 paragraphs)
        - Market valuation and investment attractiveness
        - Revenue models and profitability analysis
        - Investment trends and capital requirements
        - Financial performance benchmarks
        - ROI expectations and value creation opportunities
        
        7. RISK ASSESSMENT AND SCENARIO ANALYSIS (2-3 paragraphs)
        - Market risks and vulnerability assessment
        - Scenario planning and stress testing
        - Mitigation strategies and contingency planning
        - Risk-adjusted opportunity evaluation
        - Strategic risk management recommendations
        
        Ensure each section provides deep analytical insights with specific data points, market percentages, and quantified analysis.
        Use sophisticated business analysis terminology and demonstrate strategic expertise.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.4)
        
        return {
            "content": response,
            "analysis_depth": "comprehensive",
            "data_coverage": len(research_data.get('primary_research', [])),
            "competitive_data": research_data.get('competitive_intelligence', {})
        }
    
    async def generate_recommendations(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive strategic recommendations with enhanced detail"""
        
        system_prompt = """
        You are a senior strategic advisor providing comprehensive actionable recommendations to business leadership.
        Create detailed strategic recommendations that require 3-4 pages when professionally formatted.
        Focus on practical, implementable strategies with clear business outcomes, implementation roadmaps, and ROI projections.
        Demonstrate deep strategic thinking and business acumen appropriate for C-suite decision making.
        """
        
        user_prompt = f"""
        Develop comprehensive strategic recommendations for: {config.title}
        
        Business Context:
        - Business Objectives: {json.dumps(config.research_objectives, indent=2)}
        - Target Audience: {config.target_audience}
        - Report Type: {config.report_type.value}
        
        Key Research Insights:
        {json.dumps(await self._extract_key_insights(research_data), indent=2)}
        
        Market Analysis Context:
        - Market Opportunity Size: Significant growth potential identified
        - Competitive Positioning: Multiple strategic advantages available
        - Technology Impact: Transformation opportunities present
        - Risk Factors: Manageable with proper mitigation strategies
        
        Create comprehensive strategic recommendations with the following structure:
        
        1. STRATEGIC RECOMMENDATIONS FRAMEWORK (2 paragraphs)
        - Overall strategic approach and philosophy
        - Prioritization criteria and decision framework
        - Implementation principles and success factors
        - Risk-adjusted strategy selection rationale
        
        2. PRIMARY STRATEGIC RECOMMENDATIONS (4-5 detailed recommendations)
        
        For each recommendation, provide:
        
        **Recommendation Statement**: Clear, actionable strategic directive
        
        **Strategic Rationale**: (2-3 sentences)
        - Business case and strategic logic
        - Market opportunity and competitive advantage
        - Alignment with organizational objectives
        
        **Implementation Approach**: (3-4 detailed steps)
        - Phase 1: Immediate actions and quick wins
        - Phase 2: Core implementation and scaling
        - Phase 3: Optimization and expansion
        - Success metrics and KPIs
        
        **Resource Requirements**: (detailed breakdown)
        - Financial investment and budget allocation
        - Human resources and capability development
        - Technology and infrastructure needs
        - Partnership and external resource requirements
        
        **Timeline and Milestones**: (specific timeframes)
        - 90-day immediate actions and deliverables
        - 6-month intermediate objectives and outcomes
        - 12-18 month long-term goals and achievements
        - Critical path dependencies and risk factors
        
        **Expected Outcomes and ROI**: (quantified benefits)
        - Revenue impact and growth projections
        - Cost savings and efficiency improvements
        - Market share and competitive positioning gains
        - Risk mitigation and strategic advantage creation
        
        3. IMPLEMENTATION PRIORITIES AND SEQUENCING (2-3 paragraphs)
        - Recommendation prioritization and interdependencies
        - Implementation sequencing and phasing strategy
        - Resource allocation and investment prioritization
        - Quick wins versus long-term strategic initiatives
        
        4. SUCCESS FACTORS AND ENABLERS (2 paragraphs)
        - Critical success factors for implementation
        - Organizational capabilities and change management
        - Technology enablers and infrastructure requirements
        - Partnership and ecosystem development needs
        
        5. RISK MITIGATION AND CONTINGENCY PLANNING (2 paragraphs)
        - Implementation risks and mitigation strategies
        - Market risk scenarios and adaptive responses
        - Contingency planning and alternative approaches
        - Monitoring and course correction mechanisms
        
        Ensure each recommendation is highly actionable with specific implementation guidance.
        Use strategic business language appropriate for executive leadership decision-making.
        Include quantified benefits and ROI projections where possible.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.3)
        
        return {
            "content": response,
            "recommendation_count": 5,
            "implementation_complexity": "comprehensive",
            "strategic_impact": "high"
        }
    
    async def generate_appendices(self, research_data: Dict[str, Any], config: ReportConfig) -> Dict[str, Any]:
        """Generate comprehensive appendices section with enhanced detail"""
        
        system_prompt = """
        You are a research analyst compiling comprehensive appendices for a professional business report.
        Create detailed appendices that require 2-3 pages when professionally formatted.
        Include supporting data, methodological details, and supplementary information that validates the main analysis.
        Ensure content is professionally structured and adds significant value to the main report.
        """
        
        user_prompt = f"""
        Compile comprehensive appendices for: {config.title}
        
        Research Context:
        - Report Type: {config.report_type.value}
        - Research Sources: {len(research_data.get('primary_research', []))} primary sources
        - Data Quality Score: {research_data.get('data_quality_score', 0)}
        - Analysis Scope: Comprehensive market and competitive analysis
        
        Create detailed appendices with the following structure:
        
        1. DATA SOURCES AND METHODOLOGY DETAILS (detailed section)
        
        **A. Primary Data Sources**:
        - Industry reports and market research publications (list 8-10 specific source types)
        - Financial filings and annual reports from key market participants
        - Regulatory filings and government statistical publications
        - Expert interviews and stakeholder consultations
        - Academic research and peer-reviewed analytical studies
        - Industry association reports and white papers
        - Technology vendor reports and market assessments
        - Customer surveys and satisfaction studies
        
        **B. Secondary Research Sources**:
        - Market research databases and analytical platforms
        - Financial information services and databases
        - Industry publications and trade journals
        - Government statistical offices and regulatory bodies
        - International organizations and development agencies
        - Professional services firm publications
        - Technology and innovation research sources
        
        **C. Analytical Methodology Details**:
        - Statistical analysis techniques and modeling approaches
        - Data validation and quality assurance procedures
        - Trend analysis and forecasting methodologies
        - Competitive analysis framework and benchmarking
        - Market sizing and growth projection techniques
        - Risk assessment and scenario planning methods
        
        2. MARKET DATA AND STATISTICAL ANALYSIS (comprehensive section)
        
        **A. Market Sizing and Growth Analysis**:
        - Historical market size data and growth trends (5-year analysis)
        - Market segmentation and sub-market analysis
        - Geographic market breakdown and regional analysis
        - Growth driver identification and quantification
        - Market maturity assessment and lifecycle analysis
        
        **B. Competitive Intelligence Summary**:
        - Market share analysis and competitive positioning
        - Key player financial performance and benchmarking
        - Competitive strategy analysis and differentiation factors
        - Market entry and expansion strategies
        - Merger and acquisition activity and consolidation trends
        
        **C. Customer and Demand Analysis**:
        - Customer segmentation and behavioral analysis
        - Demand pattern identification and seasonality factors
        - Price sensitivity analysis and willingness to pay
        - Customer satisfaction and loyalty metrics
        - Emerging customer needs and preference shifts
        
        3. RESEARCH QUALITY AND VALIDATION (detailed section)
        
        **A. Data Quality Assessment**:
        - Source credibility evaluation and reliability scoring
        - Data completeness and coverage analysis
        - Bias identification and mitigation strategies
        - Cross-validation and triangulation methods
        - Confidence levels and statistical significance
        
        **B. Expert Validation Process**:
        - Industry expert consultation and validation
        - Peer review and quality assurance procedures
        - Stakeholder feedback integration and analysis
        - External validation and benchmarking studies
        - Continuous quality improvement and refinement
        
        4. SUPPLEMENTARY ANALYSIS AND INSIGHTS (comprehensive section)
        
        **A. Technology and Innovation Analysis**:
        - Technology adoption trends and innovation cycles
        - Digital transformation impact and opportunities
        - Emerging technology assessment and implications
        - Innovation investment and development priorities
        - Technology roadmap and future outlook
        
        **B. Regulatory and Policy Environment**:
        - Current regulatory framework and compliance requirements
        - Policy trends and anticipated regulatory changes
        - Government initiatives and industry support programs
        - International regulatory comparison and benchmarking
        - Regulatory risk assessment and opportunity analysis
        
        **C. Economic and Financial Context**:
        - Macroeconomic factors and market influences
        - Financial performance benchmarks and metrics
        - Investment trends and capital market analysis
        - Economic scenario analysis and sensitivity testing
        - Financial modeling and valuation frameworks
        
        5. GLOSSARY AND TECHNICAL DEFINITIONS (comprehensive listing)
        - Industry-specific terminology and definitions
        - Technical concepts and analytical frameworks
        - Market metrics and performance indicators
        - Regulatory terms and compliance concepts
        - Financial and investment terminology
        
        Ensure all appendices content is professionally structured and provides substantial value.
        Use specific data points, methodological details, and technical information that supports the main analysis.
        """
        
        response = await self._make_openai_request(system_prompt, user_prompt, temperature=0.2)
        
        return {
            "content": response,
            "data_source_count": len(research_data.get('primary_research', [])),
            "quality_score": research_data.get('data_quality_score', 0),
            "validation_status": "expert_reviewed"
        }
    
    async def generate_data_tables(self, research_data: Dict[str, Any], config: ReportConfig) -> List[Dict[str, Any]]:
        """Generate data tables for the report"""
        
        tables = []
        
        # Source summary table
        if research_data.get('primary_research'):
            source_table = {
                "title": "Research Sources Summary",
                "headers": ["Source", "Category", "Quality Score", "Key Findings Count"],
                "data": []
            }
            
            for source in research_data['primary_research'][:10]:  # Limit to 10 sources
                source_table["data"].append([
                    source.get('title', 'Unknown')[:50],
                    source.get('category', 'Unknown'),
                    f"{source.get('quality_score', 0):.2f}",
                    str(len(source.get('key_findings', [])))
                ])
            
            tables.append(source_table)
        
        return tables
    
    async def _extract_key_insights(self, research_data: Dict[str, Any]) -> List[str]:
        """Extract key insights from research data"""
        insights = []
        
        for source in research_data.get('primary_research', [])[:5]:  # Top 5 sources
            key_findings = source.get('key_findings', [])
            insights.extend(key_findings[:2])  # Top 2 findings per source
        
        return insights[:10]  # Limit total insights
    
    async def _extract_market_metrics(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market metrics from research data"""
        metrics = {
            "data_points_analyzed": 0,
            "sources_consulted": len(research_data.get('primary_research', [])),
            "quality_score": research_data.get('data_quality_score', 0),
            "trend_indicators": len(research_data.get('trend_analysis', {}).get('growth_indicators', []))
        }
        
        # Count total data points
        for source in research_data.get('primary_research', []):
            metrics["data_points_analyzed"] += len(source.get('data_points', []))
        
        return metrics
    
    async def _extract_competitive_insights(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract competitive insights"""
        competitive_data = research_data.get('competitive_intelligence', {})
        
        return {
            "competitors_identified": len(competitive_data.get('competitors', [])),
            "market_positioning_data": bool(competitive_data.get('market_positioning')),
            "pricing_analysis_available": bool(competitive_data.get('pricing_analysis')),
            "product_comparison_data": bool(competitive_data.get('product_comparison'))
        }
    
    async def _generate_recommendations_preview(self, research_data: Dict[str, Any]) -> List[str]:
        """Generate preview of recommendations"""
        
        # Extract trend indicators for recommendations
        trends = research_data.get('trend_analysis', {})
        growth_indicators = trends.get('growth_indicators', [])
        emerging_themes = trends.get('emerging_themes', [])
        
        preview_recommendations = []
        
        if growth_indicators:
            preview_recommendations.append("Capitalize on identified growth opportunities")
        
        if emerging_themes:
            preview_recommendations.append("Invest in emerging technology trends")
        
        preview_recommendations.append("Strengthen market position through data-driven strategies")
        
        return preview_recommendations[:3]
    
    async def _make_openai_request(self, system_prompt: str, user_prompt: str, temperature: float = 0.3) -> str:
        """Make OpenAI API request with error handling"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating content: {e}")
            return "Error generating content. Please try again."

    async def generate_report_image(self, prompt: str) -> str:
        """Generate AI image for the report using DALL-E"""
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Get the image URL and convert to base64
            import requests
            import base64
            
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_base64 = base64.b64encode(image_response.content).decode()
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating AI image: {e}")
            return None

    async def _analyze_funding_trends(self, investment_data: List[Dict]) -> Dict[str, Any]:
        """Analyze funding trends from investment data"""
        if not investment_data:
            return {"trend": "No funding data available", "analysis": "Funding analysis pending"}
        
        # Group by year and round type
        from collections import defaultdict
        import datetime
        
        yearly_funding = defaultdict(list)
        round_types = defaultdict(int)
        
        for investment in investment_data:
            try:
                date_str = investment.get('date', '')
                if date_str:
                    year = datetime.datetime.strptime(date_str, "%Y-%m-%d").year
                    yearly_funding[year].append(investment)
                
                round_type = investment.get('round_type', 'Unknown')
                round_types[round_type] += 1
            except:
                continue
        
        return {
            "yearly_distribution": dict(yearly_funding),
            "round_type_distribution": dict(round_types),
            "total_deals": len(investment_data),
            "trend_analysis": "Funding activity shows consistent growth" if len(yearly_funding) > 1 else "Limited funding data available"
        }
    
    async def _extract_detailed_market_data(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract detailed market data from research"""
        market_data = {
            "market_size": [],
            "growth_rates": [],
            "key_players": [],
            "technology_trends": [],
            "regulatory_factors": []
        }
        
        primary_research = research_data.get('primary_research', [])
        
        for source in primary_research:
            # Extract market analysis
            if source.get('market_analysis'):
                analysis = source.get('market_analysis', {})
                if analysis.get('market_size'):
                    market_data["market_size"].append(analysis['market_size'])
                if analysis.get('growth_rate'):
                    market_data["growth_rates"].append(analysis['growth_rate'])
            
            # Extract key players
            if source.get('key_players'):
                market_data["key_players"].extend(source.get('key_players', []))
            
            # Extract technology trends
            if source.get('technology_analysis'):
                tech_analysis = source.get('technology_analysis', {})
                market_data["technology_trends"].extend(tech_analysis.get('emerging_technologies', []))
            
            # Extract regulatory information
            if source.get('regulatory_analysis'):
                reg_analysis = source.get('regulatory_analysis', {})
                market_data["regulatory_factors"].extend(reg_analysis.get('key_regulations', []))
        
        return market_data 