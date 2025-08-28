"""
Entelech Funnel Insights Generator
Advanced analytics and AI-powered recommendations for funnel optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional, Tuple
import json
import logging
from dataclasses import dataclass
from funnel_analytics_engine import FunnelAnalyticsEngine, ConversionMetrics, BottleneckAnalysis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class StrategicInsight:
    insight_type: str
    priority: str  # HIGH, MEDIUM, LOW
    title: str
    description: str
    impact_estimate: str
    recommended_actions: List[str]
    success_metrics: List[str]
    confidence_score: float

@dataclass
class BenchmarkComparison:
    metric_name: str
    your_value: float
    industry_average: float
    percentile_rank: int
    performance_status: str  # EXCELLENT, GOOD, AVERAGE, BELOW_AVERAGE, POOR

class FunnelInsightsGenerator:
    """Advanced analytics and insights generation for funnel optimization"""
    
    def __init__(self, analytics_engine: FunnelAnalyticsEngine):
        self.analytics_engine = analytics_engine
        
        # Industry benchmarks (can be updated with real data)
        self.industry_benchmarks = {
            "overall_conversion_rate": 8.5,  # B2B SaaS average
            "lead_to_discovery_rate": 42.0,
            "discovery_to_proposal_rate": 78.0,
            "proposal_to_contract_rate": 35.0,
            "avg_sales_cycle_days": 54.0,
            "avg_deal_size": 45000.0
        }
        
        # Cost efficiency thresholds
        self.efficiency_thresholds = {
            "excellent_roi": 300.0,  # 300% ROI or higher
            "good_roi": 150.0,       # 150-300% ROI
            "acceptable_roi": 75.0,   # 75-150% ROI
            "poor_roi": 75.0         # Below 75% ROI
        }
    
    def generate_comprehensive_insights(self, date_range: Tuple[date, date]) -> Dict[str, Any]:
        """
        Generate comprehensive strategic insights for the funnel
        
        Args:
            date_range: Analysis period
            
        Returns:
            Dictionary with comprehensive insights and recommendations
        """
        try:
            logger.info(f"Generating comprehensive insights for {date_range[0]} to {date_range[1]}")
            
            # Get baseline metrics
            overall_metrics = self.analytics_engine.calculate_conversion_rates(date_range)
            source_performance = self.analytics_engine.get_lead_source_performance(date_range)
            bottlenecks = self.analytics_engine.identify_bottlenecks(date_range)
            revenue_attribution = self.analytics_engine.calculate_revenue_attribution(date_range)
            
            # Generate strategic insights
            strategic_insights = self._generate_strategic_insights(
                overall_metrics, source_performance, bottlenecks, revenue_attribution
            )
            
            # Benchmark comparison
            benchmark_comparison = self._compare_to_benchmarks(overall_metrics)
            
            # Opportunity analysis
            opportunities = self._identify_growth_opportunities(
                overall_metrics, source_performance, bottlenecks
            )
            
            # Risk analysis
            risks = self._identify_risks(overall_metrics, source_performance, bottlenecks)
            
            # ROI optimization recommendations
            roi_optimization = self._generate_roi_optimization_plan(source_performance)
            
            # Predictive insights
            predictions = self._generate_predictive_insights(date_range, overall_metrics)
            
            comprehensive_insights = {
                "analysis_period": {
                    "start_date": date_range[0].isoformat(),
                    "end_date": date_range[1].isoformat(),
                    "generated_at": datetime.now().isoformat()
                },
                "executive_summary": self._generate_executive_summary(
                    overall_metrics, strategic_insights, benchmark_comparison
                ),
                "strategic_insights": [insight.__dict__ for insight in strategic_insights],
                "benchmark_comparison": [comp.__dict__ for comp in benchmark_comparison],
                "growth_opportunities": opportunities,
                "risk_analysis": risks,
                "roi_optimization": roi_optimization,
                "predictive_insights": predictions,
                "action_plan": self._create_30_60_90_action_plan(strategic_insights),
                "success_metrics": self._define_success_metrics(overall_metrics)
            }
            
            logger.info(f"Generated {len(strategic_insights)} strategic insights")
            return comprehensive_insights
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return {}
    
    def _generate_strategic_insights(self, metrics: ConversionMetrics, 
                                   source_performance: pd.DataFrame,
                                   bottlenecks: List[BottleneckAnalysis],
                                   revenue_attribution: pd.DataFrame) -> List[StrategicInsight]:
        """Generate strategic insights based on funnel analysis"""
        insights = []
        
        # 1. Conversion Rate Analysis
        if metrics.overall_conversion_rate < 5.0:
            insights.append(StrategicInsight(
                insight_type="CONVERSION_OPTIMIZATION",
                priority="HIGH",
                title="Critical Conversion Rate Issue",
                description=f"Overall conversion rate of {metrics.overall_conversion_rate:.1f}% is significantly below industry standard of 8.5%",
                impact_estimate="Could increase revenue by 60-80% with optimization",
                recommended_actions=[
                    "Implement lead scoring to focus on high-quality prospects",
                    "Review and improve qualification criteria",
                    "Analyze lost prospects for common patterns",
                    "Implement A/B testing for key funnel stages"
                ],
                success_metrics=[
                    "Target: 8%+ overall conversion rate within 90 days",
                    "Intermediate: 6%+ conversion rate within 30 days"
                ],
                confidence_score=0.92
            ))
        elif metrics.overall_conversion_rate > 12.0:
            insights.append(StrategicInsight(
                insight_type="SCALING_OPPORTUNITY",
                priority="HIGH",
                title="Exceptional Conversion Performance",
                description=f"Conversion rate of {metrics.overall_conversion_rate:.1f}% is well above industry average - scaling opportunity",
                impact_estimate="Could 2-3x revenue with increased lead volume",
                recommended_actions=[
                    "Scale investment in top-performing lead sources",
                    "Expand team capacity to handle increased volume",
                    "Document and systematize successful processes",
                    "Consider raising pricing to optimize for deal value"
                ],
                success_metrics=[
                    "Maintain 12%+ conversion while doubling lead volume",
                    "Increase average deal size by 15-25%"
                ],
                confidence_score=0.88
            ))
        
        # 2. Lead Source Optimization
        if not source_performance.empty:
            # Identify top and bottom performers
            top_source = source_performance.iloc[0]
            bottom_sources = source_performance[source_performance['roi'] < 50]
            
            if top_source['roi'] > 200:
                insights.append(StrategicInsight(
                    insight_type="INVESTMENT_SCALING",
                    priority="HIGH",
                    title="High-ROI Source Scaling Opportunity",
                    description=f"{top_source['source_name']} shows exceptional {top_source['roi']:.0f}% ROI",
                    impact_estimate=f"Could generate additional ${top_source['revenue_per_lead'] * 100:,.0f} monthly with 100 more leads",
                    recommended_actions=[
                        f"Double marketing budget allocation to {top_source['source_name']}",
                        "Analyze what makes this source successful",
                        "Replicate successful tactics across other channels",
                        "Set up dedicated tracking and optimization"
                    ],
                    success_metrics=[
                        f"Increase {top_source['source_name']} lead volume by 50%",
                        f"Maintain {top_source['roi']:.0f}%+ ROI at scale"
                    ],
                    confidence_score=0.85
                ))
            
            if len(bottom_sources) > 0:
                worst_sources = bottom_sources['source_name'].tolist()[:3]
                insights.append(StrategicInsight(
                    insight_type="COST_OPTIMIZATION",
                    priority="MEDIUM",
                    title="Underperforming Source Optimization",
                    description=f"Sources showing poor ROI: {', '.join(worst_sources)}",
                    impact_estimate=f"Could save ${bottom_sources['total_acquisition_cost'].sum():,.0f} monthly",
                    recommended_actions=[
                        "Pause or reduce spend on underperforming sources",
                        "Analyze messaging and targeting for these channels",
                        "A/B test different approaches before eliminating",
                        "Reallocate budget to high-performing sources"
                    ],
                    success_metrics=[
                        "Achieve 100%+ ROI on all active sources",
                        "Reduce overall customer acquisition cost by 20%"
                    ],
                    confidence_score=0.78
                ))
        
        # 3. Bottleneck Analysis
        high_priority_bottlenecks = [b for b in bottlenecks if b.bottleneck_severity == "HIGH"]
        if high_priority_bottlenecks:
            primary_bottleneck = high_priority_bottlenecks[0]
            insights.append(StrategicInsight(
                insight_type="PROCESS_OPTIMIZATION",
                priority="HIGH",
                title=f"Critical Bottleneck: {primary_bottleneck.stage_name}",
                description=f"Stage conversion rate of {primary_bottleneck.conversion_rate:.1f}% with {primary_bottleneck.prospects_stuck} stuck prospects",
                impact_estimate="Could improve overall conversion by 25-40%",
                recommended_actions=primary_bottleneck.recommendations[:4],
                success_metrics=[
                    f"Improve {primary_bottleneck.stage_name} conversion rate to 70%+",
                    f"Reduce average stage duration to target levels"
                ],
                confidence_score=0.90
            ))
        
        # 4. Sales Cycle Optimization
        if metrics.avg_sales_cycle_days > 70:
            insights.append(StrategicInsight(
                insight_type="VELOCITY_OPTIMIZATION",
                priority="MEDIUM",
                title="Sales Cycle Length Optimization",
                description=f"Average sales cycle of {metrics.avg_sales_cycle_days:.0f} days is above optimal range",
                impact_estimate="Could increase revenue velocity by 20-30%",
                recommended_actions=[
                    "Implement urgency tactics and deadlines",
                    "Streamline proposal and contract processes",
                    "Improve qualification to focus on ready-to-buy prospects",
                    "Create fast-track options for qualified prospects"
                ],
                success_metrics=[
                    "Reduce average sales cycle to 45-60 days",
                    "Maintain or improve conversion rates"
                ],
                confidence_score=0.75
            ))
        
        # 5. Deal Size Optimization
        if not revenue_attribution.empty and metrics.avg_deal_size < 40000:
            insights.append(StrategicInsight(
                insight_type="VALUE_OPTIMIZATION",
                priority="MEDIUM",
                title="Deal Size Enhancement Opportunity",
                description=f"Average deal size of ${metrics.avg_deal_size:,.0f} has room for improvement",
                impact_estimate="Could increase revenue per deal by 20-40%",
                recommended_actions=[
                    "Implement value-based pricing strategies",
                    "Create tiered service packages",
                    "Focus on larger enterprise prospects",
                    "Improve consultative selling techniques"
                ],
                success_metrics=[
                    f"Increase average deal size to $50,000+",
                    "Maintain current conversion rates"
                ],
                confidence_score=0.70
            ))
        
        return insights
    
    def _compare_to_benchmarks(self, metrics: ConversionMetrics) -> List[BenchmarkComparison]:
        """Compare performance to industry benchmarks"""
        comparisons = []
        
        benchmark_metrics = {
            "Overall Conversion Rate": (metrics.overall_conversion_rate, self.industry_benchmarks["overall_conversion_rate"]),
            "Lead to Discovery Rate": (metrics.lead_to_discovery_rate, self.industry_benchmarks["lead_to_discovery_rate"]),
            "Discovery to Proposal Rate": (metrics.discovery_to_proposal_rate, self.industry_benchmarks["discovery_to_proposal_rate"]),
            "Proposal to Contract Rate": (metrics.proposal_to_contract_rate, self.industry_benchmarks["proposal_to_contract_rate"]),
            "Average Sales Cycle": (metrics.avg_sales_cycle_days, self.industry_benchmarks["avg_sales_cycle_days"]),
            "Average Deal Size": (metrics.avg_deal_size, self.industry_benchmarks["avg_deal_size"])
        }
        
        for metric_name, (your_value, benchmark) in benchmark_metrics.items():
            if your_value == 0:
                continue
                
            # Calculate percentile rank (simplified)
            if "Cycle" in metric_name:
                # For sales cycle, lower is better
                performance_ratio = benchmark / your_value
            else:
                # For other metrics, higher is better
                performance_ratio = your_value / benchmark
            
            if performance_ratio >= 1.5:
                percentile_rank = 95
                status = "EXCELLENT"
            elif performance_ratio >= 1.2:
                percentile_rank = 80
                status = "GOOD"
            elif performance_ratio >= 0.9:
                percentile_rank = 60
                status = "AVERAGE"
            elif performance_ratio >= 0.7:
                percentile_rank = 30
                status = "BELOW_AVERAGE"
            else:
                percentile_rank = 10
                status = "POOR"
            
            comparisons.append(BenchmarkComparison(
                metric_name=metric_name,
                your_value=your_value,
                industry_average=benchmark,
                percentile_rank=percentile_rank,
                performance_status=status
            ))
        
        return comparisons
    
    def _identify_growth_opportunities(self, metrics: ConversionMetrics,
                                     source_performance: pd.DataFrame,
                                     bottlenecks: List[BottleneckAnalysis]) -> List[Dict[str, Any]]:
        """Identify specific growth opportunities"""
        opportunities = []
        
        # 1. High-ROI source scaling
        if not source_performance.empty:
            high_roi_sources = source_performance[source_performance['roi'] > 200]
            for _, source in high_roi_sources.iterrows():
                opportunities.append({
                    "type": "SOURCE_SCALING",
                    "title": f"Scale {source['source_name']}",
                    "potential_impact": f"${source['revenue_per_lead'] * 50:,.0f}/month with 50 more leads",
                    "investment_required": f"${source['cost_per_lead'] * 50:,.0f}/month",
                    "roi_projection": f"{source['roi']:.0f}%+",
                    "risk_level": "LOW"
                })
        
        # 2. Bottleneck elimination
        medium_bottlenecks = [b for b in bottlenecks if b.bottleneck_severity == "MEDIUM"]
        for bottleneck in medium_bottlenecks[:2]:  # Top 2 medium bottlenecks
            opportunities.append({
                "type": "PROCESS_IMPROVEMENT",
                "title": f"Optimize {bottleneck.stage_name}",
                "potential_impact": "15-25% conversion improvement",
                "investment_required": "Process optimization and training",
                "roi_projection": "200-400%",
                "risk_level": "LOW"
            })
        
        # 3. Market expansion
        if metrics.overall_conversion_rate > 10:
            opportunities.append({
                "type": "MARKET_EXPANSION",
                "title": "Expand to New Lead Sources",
                "potential_impact": f"${metrics.total_revenue * 0.5:,.0f} additional revenue",
                "investment_required": "New channel development",
                "roi_projection": "150-300%",
                "risk_level": "MEDIUM"
            })
        
        return opportunities
    
    def _identify_risks(self, metrics: ConversionMetrics,
                       source_performance: pd.DataFrame,
                       bottlenecks: List[BottleneckAnalysis]) -> List[Dict[str, Any]]:
        """Identify potential risks to revenue"""
        risks = []
        
        # 1. Over-dependence on single source
        if not source_performance.empty:
            total_revenue = source_performance['total_revenue'].sum()
            top_source_percentage = (source_performance.iloc[0]['total_revenue'] / total_revenue) * 100
            
            if top_source_percentage > 60:
                risks.append({
                    "type": "CONCENTRATION_RISK",
                    "title": "Over-dependence on Single Lead Source",
                    "description": f"{source_performance.iloc[0]['source_name']} represents {top_source_percentage:.0f}% of revenue",
                    "potential_impact": "High vulnerability to channel disruption",
                    "mitigation": "Diversify lead sources and reduce dependence",
                    "priority": "HIGH"
                })
        
        # 2. Critical bottlenecks
        critical_bottlenecks = [b for b in bottlenecks if b.bottleneck_severity == "HIGH"]
        for bottleneck in critical_bottlenecks:
            risks.append({
                "type": "PROCESS_RISK",
                "title": f"Critical Bottleneck: {bottleneck.stage_name}",
                "description": f"Only {bottleneck.conversion_rate:.1f}% conversion rate",
                "potential_impact": "Significant revenue loss and poor customer experience",
                "mitigation": bottleneck.recommendations[0] if bottleneck.recommendations else "Process optimization needed",
                "priority": "HIGH"
            })
        
        # 3. Low conversion rate
        if metrics.overall_conversion_rate < 5:
            risks.append({
                "type": "PERFORMANCE_RISK",
                "title": "Below-Average Conversion Performance",
                "description": f"Conversion rate of {metrics.overall_conversion_rate:.1f}% is well below industry standard",
                "potential_impact": "Inefficient use of marketing budget and resources",
                "mitigation": "Comprehensive funnel optimization program",
                "priority": "HIGH"
            })
        
        return risks
    
    def _generate_roi_optimization_plan(self, source_performance: pd.DataFrame) -> Dict[str, Any]:
        """Generate ROI optimization recommendations"""
        if source_performance.empty:
            return {}
        
        plan = {
            "current_roi_distribution": {},
            "optimization_recommendations": [],
            "budget_reallocation": {},
            "expected_impact": {}
        }
        
        # Analyze current ROI distribution
        for efficiency_level, threshold in [
            ("Excellent", self.efficiency_thresholds["excellent_roi"]),
            ("Good", self.efficiency_thresholds["good_roi"]),
            ("Acceptable", self.efficiency_thresholds["acceptable_roi"]),
            ("Poor", 0)
        ]:
            if efficiency_level == "Poor":
                sources = source_performance[source_performance['roi'] < self.efficiency_thresholds["poor_roi"]]
            else:
                next_threshold = {
                    "Excellent": float('inf'),
                    "Good": self.efficiency_thresholds["excellent_roi"],
                    "Acceptable": self.efficiency_thresholds["good_roi"]
                }.get(efficiency_level, 0)
                
                sources = source_performance[
                    (source_performance['roi'] >= threshold) & 
                    (source_performance['roi'] < next_threshold)
                ]
            
            plan["current_roi_distribution"][efficiency_level] = {
                "count": len(sources),
                "total_spend": sources['total_acquisition_cost'].sum() if not sources.empty else 0,
                "total_revenue": sources['total_revenue'].sum() if not sources.empty else 0
            }
        
        # Generate optimization recommendations
        excellent_sources = source_performance[source_performance['roi'] >= self.efficiency_thresholds["excellent_roi"]]
        poor_sources = source_performance[source_performance['roi'] < self.efficiency_thresholds["poor_roi"]]
        
        if not excellent_sources.empty:
            plan["optimization_recommendations"].append({
                "action": "SCALE_HIGH_PERFORMERS",
                "sources": excellent_sources['source_name'].tolist(),
                "recommendation": "Increase budget allocation by 50-100%",
                "expected_roi": f"{excellent_sources['roi'].mean():.0f}%+"
            })
        
        if not poor_sources.empty:
            plan["optimization_recommendations"].append({
                "action": "OPTIMIZE_OR_PAUSE",
                "sources": poor_sources['source_name'].tolist(),
                "recommendation": "Reduce spend by 50% or pause while optimizing",
                "potential_savings": f"${poor_sources['total_acquisition_cost'].sum():,.0f}/month"
            })
        
        return plan
    
    def _generate_predictive_insights(self, date_range: Tuple[date, date], 
                                    metrics: ConversionMetrics) -> Dict[str, Any]:
        """Generate predictive insights based on current trends"""
        predictions = {
            "30_day_forecast": {},
            "90_day_forecast": {},
            "trend_analysis": {},
            "scenario_planning": {}
        }
        
        # Simple trend-based predictions (in a real system, use more sophisticated ML)
        period_days = (date_range[1] - date_range[0]).days
        
        # 30-day forecast
        daily_leads = metrics.total_leads / period_days if period_days > 0 else 0
        daily_revenue = metrics.total_revenue / period_days if period_days > 0 else 0
        
        predictions["30_day_forecast"] = {
            "projected_leads": int(daily_leads * 30),
            "projected_contracts": int(daily_leads * 30 * (metrics.overall_conversion_rate / 100)),
            "projected_revenue": daily_revenue * 30,
            "confidence": "MEDIUM"
        }
        
        # 90-day forecast (with growth assumptions)
        growth_multiplier = 1.1  # Assume 10% growth
        predictions["90_day_forecast"] = {
            "projected_leads": int(daily_leads * 90 * growth_multiplier),
            "projected_contracts": int(daily_leads * 90 * growth_multiplier * (metrics.overall_conversion_rate / 100)),
            "projected_revenue": daily_revenue * 90 * growth_multiplier,
            "confidence": "LOW"
        }
        
        # Scenario planning
        predictions["scenario_planning"] = {
            "conservative": {
                "assumption": "No changes to current performance",
                "90_day_revenue": daily_revenue * 90,
                "probability": "HIGH"
            },
            "optimistic": {
                "assumption": "20% improvement in conversion rate",
                "90_day_revenue": daily_revenue * 90 * 1.2,
                "probability": "MEDIUM"
            },
            "aggressive": {
                "assumption": "50% increase in leads + 20% better conversion",
                "90_day_revenue": daily_revenue * 90 * 1.5 * 1.2,
                "probability": "LOW"
            }
        }
        
        return predictions
    
    def _generate_executive_summary(self, metrics: ConversionMetrics,
                                  insights: List[StrategicInsight],
                                  benchmarks: List[BenchmarkComparison]) -> Dict[str, Any]:
        """Generate executive summary of key findings"""
        
        high_priority_insights = [i for i in insights if i.priority == "HIGH"]
        excellent_benchmarks = [b for b in benchmarks if b.performance_status == "EXCELLENT"]
        poor_benchmarks = [b for b in benchmarks if b.performance_status == "POOR"]
        
        return {
            "overall_health_score": self._calculate_health_score(benchmarks),
            "key_findings": [
                f"Overall conversion rate: {metrics.overall_conversion_rate:.1f}%",
                f"Total revenue analyzed: ${metrics.total_revenue:,.0f}",
                f"Average deal size: ${metrics.avg_deal_size:,.0f}",
                f"Sales cycle length: {metrics.avg_sales_cycle_days:.0f} days"
            ],
            "critical_actions_needed": len(high_priority_insights),
            "areas_of_excellence": [b.metric_name for b in excellent_benchmarks],
            "areas_needing_improvement": [b.metric_name for b in poor_benchmarks],
            "revenue_opportunity": self._estimate_revenue_opportunity(insights),
            "recommended_focus": self._determine_recommended_focus(insights)
        }
    
    def _calculate_health_score(self, benchmarks: List[BenchmarkComparison]) -> int:
        """Calculate overall funnel health score (0-100)"""
        if not benchmarks:
            return 50
        
        percentile_sum = sum(b.percentile_rank for b in benchmarks)
        return min(100, int(percentile_sum / len(benchmarks)))
    
    def _estimate_revenue_opportunity(self, insights: List[StrategicInsight]) -> str:
        """Estimate total revenue opportunity from insights"""
        # Simplified estimation based on insight priorities and types
        high_priority_count = len([i for i in insights if i.priority == "HIGH"])
        medium_priority_count = len([i for i in insights if i.priority == "MEDIUM"])
        
        opportunity_score = high_priority_count * 30 + medium_priority_count * 15
        
        if opportunity_score > 80:
            return "Very High (50%+ revenue increase potential)"
        elif opportunity_score > 50:
            return "High (25-50% revenue increase potential)"
        elif opportunity_score > 25:
            return "Medium (10-25% revenue increase potential)"
        else:
            return "Low (0-10% revenue increase potential)"
    
    def _determine_recommended_focus(self, insights: List[StrategicInsight]) -> str:
        """Determine primary recommended focus area"""
        insight_types = [i.insight_type for i in insights if i.priority == "HIGH"]
        
        if "CONVERSION_OPTIMIZATION" in insight_types:
            return "Conversion Rate Optimization"
        elif "PROCESS_OPTIMIZATION" in insight_types:
            return "Bottleneck Elimination"
        elif "INVESTMENT_SCALING" in insight_types:
            return "High-ROI Source Scaling"
        elif "COST_OPTIMIZATION" in insight_types:
            return "Cost Efficiency Improvement"
        else:
            return "Performance Monitoring"
    
    def _create_30_60_90_action_plan(self, insights: List[StrategicInsight]) -> Dict[str, List[str]]:
        """Create a 30-60-90 day action plan"""
        high_priority = [i for i in insights if i.priority == "HIGH"]
        medium_priority = [i for i in insights if i.priority == "MEDIUM"]
        
        return {
            "30_days": [
                action for insight in high_priority[:2] 
                for action in insight.recommended_actions[:2]
            ],
            "60_days": [
                action for insight in high_priority[2:] + medium_priority[:1]
                for action in insight.recommended_actions[:2]
            ],
            "90_days": [
                action for insight in medium_priority[1:]
                for action in insight.recommended_actions[:1]
            ]
        }
    
    def _define_success_metrics(self, current_metrics: ConversionMetrics) -> Dict[str, str]:
        """Define success metrics based on current performance"""
        return {
            "30_day_targets": {
                "conversion_rate": f"{max(current_metrics.overall_conversion_rate * 1.15, 6.0):.1f}%",
                "lead_volume": f"{int(current_metrics.total_leads * 1.1)} leads",
                "revenue": f"${current_metrics.total_revenue * 1.1:,.0f}"
            },
            "90_day_targets": {
                "conversion_rate": f"{max(current_metrics.overall_conversion_rate * 1.3, 8.0):.1f}%",
                "lead_volume": f"{int(current_metrics.total_leads * 1.25)} leads",
                "revenue": f"${current_metrics.total_revenue * 1.4:,.0f}"
            }
        }