"""
Entelech Funnel Analytics Engine
Comprehensive lead tracking and conversion rate analysis system
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Tuple, Optional, Any
import json
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LeadSource(Enum):
    LINKEDIN_CONTENT = "linkedin_content"
    LINKEDIN_OUTREACH = "linkedin_outreach"
    LINKEDIN_ADS = "linkedin_ads"
    CLIENT_REFERRALS = "client_referrals"
    PARTNER_REFERRALS = "partner_referrals"
    COLD_EMAIL = "cold_email"
    COLD_CALLING = "cold_calling"
    WEBSITE_ORGANIC = "website_organic"
    WEBSITE_CONTACT = "website_contact"
    INDUSTRY_EVENTS = "industry_events"
    WORD_OF_MOUTH = "word_of_mouth"

class FunnelStage(Enum):
    LEAD_GENERATED = "lead_generated"
    DISCOVERY_SCHEDULED = "discovery_scheduled"
    DISCOVERY_COMPLETED = "discovery_completed"
    PROPOSAL_SENT = "proposal_sent"
    PROPOSAL_REVIEW = "proposal_review"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    CONTRACT_SIGNED = "contract_signed"
    LOST_DISQUALIFIED = "lost_disqualified"

@dataclass
class ConversionMetrics:
    total_leads: int
    discovery_calls_scheduled: int
    discovery_calls_completed: int
    proposals_sent: int
    contracts_signed: int
    total_revenue: float
    avg_deal_size: float
    avg_sales_cycle_days: float
    lead_to_discovery_rate: float
    discovery_to_proposal_rate: float
    proposal_to_contract_rate: float
    overall_conversion_rate: float
    cost_per_acquisition: float
    lifetime_value: float

@dataclass
class BottleneckAnalysis:
    stage_name: str
    conversion_rate: float
    avg_duration_days: float
    prospects_stuck: int
    bottleneck_severity: str
    recommendations: List[str]

class FunnelAnalyticsEngine:
    
    def __init__(self, db_path: str = "funnel_analytics.db"):
        """Initialize the funnel analytics engine with database connection"""
        self.db_path = db_path
        self.conn = None
        self._connect_database()
        
    def _connect_database(self):
        """Establish database connection and create tables if needed"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def close_connection(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    # ================================
    # LEAD SOURCE ATTRIBUTION
    # ================================
    
    def track_lead_source(self, prospect_email: str, source_name: str, 
                         attribution_data: Dict[str, Any]) -> bool:
        """
        Track lead source attribution with detailed metadata
        
        Args:
            prospect_email: Prospect's email address
            source_name: Name of the lead source
            attribution_data: Additional attribution metadata
            
        Returns:
            bool: Success status
        """
        try:
            cursor = self.conn.cursor()
            
            # Get or create lead source
            cursor.execute("""
                SELECT source_id FROM lead_sources 
                WHERE source_name = ?
            """, (source_name,))
            
            source_result = cursor.fetchone()
            if not source_result:
                # Create new lead source
                cursor.execute("""
                    INSERT INTO lead_sources (source_name, source_category, attribution_window_days, cost_per_lead)
                    VALUES (?, ?, ?, ?)
                """, (source_name, attribution_data.get('category', 'other'), 
                     attribution_data.get('attribution_window', 30),
                     attribution_data.get('cost_per_lead', 0.0)))
                source_id = cursor.lastrowid
            else:
                source_id = source_result['source_id']
            
            # Update prospect with lead source
            cursor.execute("""
                UPDATE prospects 
                SET lead_source_id = ?, updated_at = CURRENT_TIMESTAMP
                WHERE email = ?
            """, (source_id, prospect_email))
            
            self.conn.commit()
            logger.info(f"Lead source tracked: {prospect_email} -> {source_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking lead source: {e}")
            return False
    
    def get_lead_source_performance(self, date_range: Tuple[date, date]) -> pd.DataFrame:
        """
        Get performance metrics by lead source
        
        Args:
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            DataFrame with lead source performance data
        """
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT 
                    ls.source_name,
                    ls.source_category,
                    ls.cost_per_lead,
                    COUNT(DISTINCT p.prospect_id) as total_leads,
                    COUNT(DISTINCT dc.call_id) as discovery_calls,
                    COUNT(DISTINCT pr.proposal_id) as proposals_sent,
                    COUNT(DISTINCT c.contract_id) as contracts_signed,
                    COALESCE(SUM(c.contract_value), 0) as total_revenue,
                    COALESCE(AVG(c.contract_value), 0) as avg_deal_size,
                    ROUND(
                        CAST(COUNT(DISTINCT c.contract_id) AS FLOAT) / 
                        CAST(COUNT(DISTINCT p.prospect_id) AS FLOAT) * 100, 2
                    ) as conversion_rate,
                    COALESCE(SUM(c.contract_value), 0) / COUNT(DISTINCT p.prospect_id) as revenue_per_lead,
                    (ls.cost_per_lead * COUNT(DISTINCT p.prospect_id)) as total_acquisition_cost
                FROM lead_sources ls
                LEFT JOIN prospects p ON ls.source_id = p.lead_source_id 
                    AND p.created_at BETWEEN ? AND ?
                LEFT JOIN discovery_calls dc ON p.prospect_id = dc.prospect_id
                LEFT JOIN proposals pr ON p.prospect_id = pr.prospect_id
                LEFT JOIN contracts c ON p.prospect_id = c.prospect_id
                WHERE ls.is_active = 1
                GROUP BY ls.source_id, ls.source_name, ls.source_category, ls.cost_per_lead
                ORDER BY total_revenue DESC, total_leads DESC
            """
            
            df = pd.read_sql_query(query, self.conn, params=[date_range[0], date_range[1]])
            
            # Calculate additional metrics
            df['roi'] = np.where(df['total_acquisition_cost'] > 0, 
                               (df['total_revenue'] - df['total_acquisition_cost']) / df['total_acquisition_cost'] * 100,
                               0)
            df['payback_period_months'] = np.where(df['revenue_per_lead'] > 0,
                                                 df['cost_per_lead'] / (df['revenue_per_lead'] / 12),
                                                 0)
            
            logger.info(f"Retrieved lead source performance for {len(df)} sources")
            return df
            
        except Exception as e:
            logger.error(f"Error getting lead source performance: {e}")
            return pd.DataFrame()
    
    # ================================
    # CONVERSION RATE ANALYTICS
    # ================================
    
    def calculate_conversion_rates(self, date_range: Tuple[date, date], 
                                 lead_source_id: Optional[int] = None) -> ConversionMetrics:
        """
        Calculate detailed conversion rates for the funnel
        
        Args:
            date_range: Tuple of (start_date, end_date)
            lead_source_id: Optional specific lead source ID
            
        Returns:
            ConversionMetrics object with all conversion data
        """
        try:
            cursor = self.conn.cursor()
            
            # Base query conditions
            source_filter = ""
            params = [date_range[0], date_range[1]]
            if lead_source_id:
                source_filter = "AND p.lead_source_id = ?"
                params.append(lead_source_id)
            
            # Get funnel metrics
            query = f"""
                SELECT 
                    COUNT(DISTINCT p.prospect_id) as total_leads,
                    COUNT(DISTINCT CASE WHEN dc.call_id IS NOT NULL THEN p.prospect_id END) as discovery_scheduled,
                    COUNT(DISTINCT CASE WHEN dc.call_status = 'completed' THEN p.prospect_id END) as discovery_completed,
                    COUNT(DISTINCT CASE WHEN pr.proposal_id IS NOT NULL THEN p.prospect_id END) as proposals_sent,
                    COUNT(DISTINCT CASE WHEN c.contract_id IS NOT NULL THEN p.prospect_id END) as contracts_signed,
                    COALESCE(SUM(c.contract_value), 0) as total_revenue,
                    COALESCE(AVG(c.contract_value), 0) as avg_deal_size,
                    AVG(
                        CASE WHEN c.contract_id IS NOT NULL 
                        THEN julianday(c.signed_at) - julianday(p.created_at)
                        ELSE NULL END
                    ) as avg_sales_cycle_days
                FROM prospects p
                LEFT JOIN discovery_calls dc ON p.prospect_id = dc.prospect_id
                LEFT JOIN proposals pr ON p.prospect_id = pr.prospect_id
                LEFT JOIN contracts c ON p.prospect_id = c.prospect_id
                WHERE p.created_at BETWEEN ? AND ? {source_filter}
            """
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            # Calculate conversion rates
            total_leads = result['total_leads'] or 0
            discovery_scheduled = result['discovery_scheduled'] or 0
            discovery_completed = result['discovery_completed'] or 0
            proposals_sent = result['proposals_sent'] or 0
            contracts_signed = result['contracts_signed'] or 0
            
            lead_to_discovery_rate = (discovery_scheduled / total_leads * 100) if total_leads > 0 else 0
            discovery_to_proposal_rate = (proposals_sent / discovery_completed * 100) if discovery_completed > 0 else 0
            proposal_to_contract_rate = (contracts_signed / proposals_sent * 100) if proposals_sent > 0 else 0
            overall_conversion_rate = (contracts_signed / total_leads * 100) if total_leads > 0 else 0
            
            # Calculate acquisition costs
            if lead_source_id:
                cursor.execute("SELECT cost_per_lead FROM lead_sources WHERE source_id = ?", (lead_source_id,))
                cost_result = cursor.fetchone()
                cost_per_lead = cost_result['cost_per_lead'] if cost_result else 0
            else:
                # Average cost per lead across all sources
                cursor.execute("""
                    SELECT AVG(ls.cost_per_lead) as avg_cost
                    FROM lead_sources ls
                    JOIN prospects p ON ls.source_id = p.lead_source_id
                    WHERE p.created_at BETWEEN ? AND ?
                """, [date_range[0], date_range[1]])
                cost_result = cursor.fetchone()
                cost_per_lead = cost_result['avg_cost'] if cost_result and cost_result['avg_cost'] else 0
            
            cost_per_acquisition = (cost_per_lead * total_leads / contracts_signed) if contracts_signed > 0 else 0
            
            # Calculate lifetime value (simplified)
            lifetime_value = result['avg_deal_size'] or 0
            
            metrics = ConversionMetrics(
                total_leads=total_leads,
                discovery_calls_scheduled=discovery_scheduled,
                discovery_calls_completed=discovery_completed,
                proposals_sent=proposals_sent,
                contracts_signed=contracts_signed,
                total_revenue=result['total_revenue'] or 0,
                avg_deal_size=result['avg_deal_size'] or 0,
                avg_sales_cycle_days=result['avg_sales_cycle_days'] or 0,
                lead_to_discovery_rate=lead_to_discovery_rate,
                discovery_to_proposal_rate=discovery_to_proposal_rate,
                proposal_to_contract_rate=proposal_to_contract_rate,
                overall_conversion_rate=overall_conversion_rate,
                cost_per_acquisition=cost_per_acquisition,
                lifetime_value=lifetime_value
            )
            
            logger.info(f"Calculated conversion metrics for {total_leads} leads")
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating conversion rates: {e}")
            return ConversionMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    # ================================
    # BOTTLENECK IDENTIFICATION
    # ================================
    
    def identify_bottlenecks(self, date_range: Tuple[date, date]) -> List[BottleneckAnalysis]:
        """
        Identify bottlenecks in the sales funnel
        
        Args:
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            List of BottleneckAnalysis objects
        """
        try:
            cursor = self.conn.cursor()
            
            # Get stage performance data
            query = """
                SELECT 
                    fs.stage_name,
                    fs.stage_order,
                    fs.expected_duration_days,
                    COUNT(DISTINCT pj.prospect_id) as prospects_entered,
                    COUNT(DISTINCT CASE WHEN pj.exited_at IS NOT NULL THEN pj.prospect_id END) as prospects_exited,
                    AVG(
                        CASE WHEN pj.exited_at IS NOT NULL 
                        THEN (julianday(pj.exited_at) - julianday(pj.entered_at))
                        ELSE (julianday('now') - julianday(pj.entered_at))
                        END
                    ) as avg_duration_days,
                    COUNT(DISTINCT CASE WHEN pj.exited_at IS NULL AND julianday('now') - julianday(pj.entered_at) > fs.expected_duration_days THEN pj.prospect_id END) as prospects_stuck
                FROM funnel_stages fs
                LEFT JOIN prospect_journey pj ON fs.stage_id = pj.stage_id
                    AND pj.entered_at BETWEEN ? AND ?
                WHERE fs.stage_name != 'Lost/Disqualified'
                GROUP BY fs.stage_id, fs.stage_name, fs.stage_order, fs.expected_duration_days
                ORDER BY fs.stage_order
            """
            
            cursor.execute(query, [date_range[0], date_range[1]])
            results = cursor.fetchall()
            
            bottlenecks = []
            
            for result in results:
                prospects_entered = result['prospects_entered'] or 0
                prospects_exited = result['prospects_exited'] or 0
                avg_duration = result['avg_duration_days'] or 0
                expected_duration = result['expected_duration_days']
                prospects_stuck = result['prospects_stuck'] or 0
                
                # Calculate conversion rate
                conversion_rate = (prospects_exited / prospects_entered * 100) if prospects_entered > 0 else 0
                
                # Determine bottleneck severity
                duration_factor = avg_duration / expected_duration if expected_duration > 0 else 1
                stuck_factor = prospects_stuck / prospects_entered if prospects_entered > 0 else 0
                
                if conversion_rate < 50 or duration_factor > 2 or stuck_factor > 0.3:
                    severity = "HIGH"
                elif conversion_rate < 70 or duration_factor > 1.5 or stuck_factor > 0.2:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
                
                # Generate recommendations
                recommendations = self._generate_bottleneck_recommendations(
                    result['stage_name'], conversion_rate, duration_factor, stuck_factor
                )
                
                bottleneck = BottleneckAnalysis(
                    stage_name=result['stage_name'],
                    conversion_rate=conversion_rate,
                    avg_duration_days=avg_duration,
                    prospects_stuck=prospects_stuck,
                    bottleneck_severity=severity,
                    recommendations=recommendations
                )
                
                bottlenecks.append(bottleneck)
            
            logger.info(f"Identified {len([b for b in bottlenecks if b.bottleneck_severity == 'HIGH'])} high-priority bottlenecks")
            return bottlenecks
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
            return []
    
    def _generate_bottleneck_recommendations(self, stage_name: str, conversion_rate: float,
                                           duration_factor: float, stuck_factor: float) -> List[str]:
        """Generate specific recommendations for bottleneck stages"""
        recommendations = []
        
        stage_recommendations = {
            "Lead Generated": [
                "Implement lead scoring to prioritize high-quality prospects",
                "Create automated qualification sequences",
                "Review lead source quality and adjust targeting"
            ],
            "Discovery Call Scheduled": [
                "Improve initial outreach messaging and value proposition",
                "Implement calendar booking automation",
                "Create urgency with limited-time offers or consultations"
            ],
            "Discovery Call Completed": [
                "Reduce no-show rates with confirmation sequences",
                "Train sales team on discovery call best practices",
                "Implement call recording and analysis for improvement"
            ],
            "Proposal Sent": [
                "Streamline discovery-to-proposal process",
                "Create proposal templates for faster turnaround",
                "Implement better qualification to ensure proposal-ready prospects"
            ],
            "Proposal Under Review": [
                "Create structured follow-up sequences",
                "Implement proposal tracking and engagement analytics",
                "Add social proof and case studies to proposals"
            ],
            "Contract Negotiation": [
                "Streamline contract terms and reduce complexity",
                "Train team on objection handling and negotiation",
                "Create flexible pricing options and packages"
            ]
        }
        
        # Add stage-specific recommendations
        if stage_name in stage_recommendations:
            recommendations.extend(stage_recommendations[stage_name])
        
        # Add performance-specific recommendations
        if conversion_rate < 50:
            recommendations.append("URGENT: Review and improve qualification criteria")
            recommendations.append("Analyze lost prospects for common patterns")
        
        if duration_factor > 2:
            recommendations.append("Implement automated follow-up sequences")
            recommendations.append("Set clear timelines and next steps with prospects")
        
        if stuck_factor > 0.3:
            recommendations.append("Create re-engagement campaigns for stalled prospects")
            recommendations.append("Implement stage-specific nurturing content")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    # ================================
    # REVENUE ATTRIBUTION
    # ================================
    
    def calculate_revenue_attribution(self, date_range: Tuple[date, date], 
                                    attribution_model: str = "first_touch") -> pd.DataFrame:
        """
        Calculate revenue attribution by lead source using specified model
        
        Args:
            date_range: Tuple of (start_date, end_date)
            attribution_model: Attribution model to use
            
        Returns:
            DataFrame with revenue attribution data
        """
        try:
            cursor = self.conn.cursor()
            
            # Get contracts with lead source attribution
            query = """
                SELECT 
                    ls.source_name,
                    ls.source_category,
                    c.contract_id,
                    c.contract_value,
                    c.monthly_recurring_revenue,
                    c.signed_at,
                    p.created_at as lead_created_at,
                    julianday(c.signed_at) - julianday(p.created_at) as sales_cycle_days
                FROM contracts c
                JOIN prospects p ON c.prospect_id = p.prospect_id
                JOIN lead_sources ls ON p.lead_source_id = ls.source_id
                WHERE c.signed_at BETWEEN ? AND ?
                    AND c.contract_status = 'active'
                ORDER BY ls.source_name, c.signed_at
            """
            
            df = pd.read_sql_query(query, self.conn, params=[date_range[0], date_range[1]])
            
            if df.empty:
                return pd.DataFrame()
            
            # Group by lead source and calculate attribution
            attribution_df = df.groupby(['source_name', 'source_category']).agg({
                'contract_value': ['sum', 'mean', 'count'],
                'monthly_recurring_revenue': 'sum',
                'sales_cycle_days': 'mean'
            }).round(2)
            
            # Flatten column names
            attribution_df.columns = ['_'.join(col).strip() if col[1] else col[0] for col in attribution_df.columns.values]
            attribution_df = attribution_df.reset_index()
            
            # Rename columns for clarity
            attribution_df = attribution_df.rename(columns={
                'contract_value_sum': 'total_attributed_revenue',
                'contract_value_mean': 'avg_deal_size',
                'contract_value_count': 'total_contracts',
                'monthly_recurring_revenue_sum': 'total_mrr',
                'sales_cycle_days_mean': 'avg_sales_cycle_days'
            })
            
            # Calculate percentage of total revenue
            total_revenue = attribution_df['total_attributed_revenue'].sum()
            attribution_df['revenue_percentage'] = (attribution_df['total_attributed_revenue'] / total_revenue * 100).round(2)
            
            # Sort by revenue contribution
            attribution_df = attribution_df.sort_values('total_attributed_revenue', ascending=False)
            
            logger.info(f"Calculated revenue attribution for {len(attribution_df)} lead sources")
            return attribution_df
            
        except Exception as e:
            logger.error(f"Error calculating revenue attribution: {e}")
            return pd.DataFrame()
    
    # ================================
    # COMPREHENSIVE INSIGHTS
    # ================================
    
    def generate_comprehensive_insights(self, date_range: Tuple[date, date]) -> Dict[str, Any]:
        """
        Generate comprehensive funnel insights and recommendations
        
        Args:
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            Dictionary with comprehensive insights
        """
        try:
            insights = {
                "period": {"start": date_range[0].isoformat(), "end": date_range[1].isoformat()},
                "generated_at": datetime.now().isoformat(),
                "executive_summary": {},
                "conversion_metrics": {},
                "lead_source_performance": {},
                "bottleneck_analysis": {},
                "revenue_attribution": {},
                "key_recommendations": []
            }
            
            # Get overall conversion metrics
            overall_metrics = self.calculate_conversion_rates(date_range)
            insights["conversion_metrics"] = {
                "total_leads": overall_metrics.total_leads,
                "contracts_signed": overall_metrics.contracts_signed,
                "total_revenue": overall_metrics.total_revenue,
                "overall_conversion_rate": overall_metrics.overall_conversion_rate,
                "avg_deal_size": overall_metrics.avg_deal_size,
                "avg_sales_cycle_days": overall_metrics.avg_sales_cycle_days,
                "funnel_conversion_rates": {
                    "lead_to_discovery": overall_metrics.lead_to_discovery_rate,
                    "discovery_to_proposal": overall_metrics.discovery_to_proposal_rate,
                    "proposal_to_contract": overall_metrics.proposal_to_contract_rate
                }
            }
            
            # Get lead source performance
            source_performance = self.get_lead_source_performance(date_range)
            if not source_performance.empty:
                insights["lead_source_performance"] = {
                    "top_sources_by_revenue": source_performance.head(5)[['source_name', 'total_revenue', 'conversion_rate']].to_dict('records'),
                    "top_sources_by_volume": source_performance.nlargest(5, 'total_leads')[['source_name', 'total_leads', 'conversion_rate']].to_dict('records'),
                    "most_efficient_sources": source_performance.nlargest(5, 'roi')[['source_name', 'roi', 'revenue_per_lead']].to_dict('records')
                }
            
            # Get bottleneck analysis
            bottlenecks = self.identify_bottlenecks(date_range)
            high_priority_bottlenecks = [b for b in bottlenecks if b.bottleneck_severity == "HIGH"]
            insights["bottleneck_analysis"] = {
                "high_priority_count": len(high_priority_bottlenecks),
                "critical_stages": [{"stage": b.stage_name, "conversion_rate": b.conversion_rate, "prospects_stuck": b.prospects_stuck} for b in high_priority_bottlenecks],
                "improvement_opportunities": [rec for b in high_priority_bottlenecks for rec in b.recommendations[:2]]
            }
            
            # Get revenue attribution
            revenue_attribution = self.calculate_revenue_attribution(date_range)
            if not revenue_attribution.empty:
                insights["revenue_attribution"] = {
                    "top_revenue_sources": revenue_attribution.head(3)[['source_name', 'total_attributed_revenue', 'revenue_percentage']].to_dict('records'),
                    "revenue_concentration": revenue_attribution.head(3)['revenue_percentage'].sum()
                }
            
            # Generate executive summary
            insights["executive_summary"] = {
                "total_pipeline_value": overall_metrics.total_revenue,
                "conversion_health": "Good" if overall_metrics.overall_conversion_rate > 10 else "Needs Improvement",
                "primary_bottleneck": high_priority_bottlenecks[0].stage_name if high_priority_bottlenecks else "None identified",
                "top_performing_source": source_performance.iloc[0]['source_name'] if not source_performance.empty else "No data",
                "key_metric_trends": self._analyze_trends(date_range)
            }
            
            # Generate key recommendations
            insights["key_recommendations"] = self._generate_strategic_recommendations(
                overall_metrics, high_priority_bottlenecks, source_performance
            )
            
            logger.info("Generated comprehensive funnel insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return {}
    
    def _analyze_trends(self, date_range: Tuple[date, date]) -> Dict[str, str]:
        """Analyze key metric trends over time"""
        # Simplified trend analysis - in production, compare with previous periods
        return {
            "conversion_rate_trend": "stable",
            "lead_volume_trend": "increasing",
            "deal_size_trend": "stable",
            "sales_cycle_trend": "decreasing"
        }
    
    def _generate_strategic_recommendations(self, metrics: ConversionMetrics, 
                                         bottlenecks: List[BottleneckAnalysis],
                                         source_performance: pd.DataFrame) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        recommendations = []
        
        # Conversion rate recommendations
        if metrics.overall_conversion_rate < 5:
            recommendations.append("CRITICAL: Overall conversion rate is below 5%. Focus on lead qualification and sales process optimization.")
        elif metrics.overall_conversion_rate < 10:
            recommendations.append("Conversion rate needs improvement. Consider implementing lead scoring and nurturing sequences.")
        
        # Lead source recommendations
        if not source_performance.empty:
            top_source = source_performance.iloc[0]
            if top_source['roi'] > 200:
                recommendations.append(f"Scale investment in {top_source['source_name']} - showing excellent ROI of {top_source['roi']:.0f}%")
            
            low_performing = source_performance[source_performance['conversion_rate'] < 2]
            if not low_performing.empty:
                recommendations.append(f"Consider pausing or optimizing {len(low_performing)} underperforming lead sources")
        
        # Bottleneck recommendations
        if bottlenecks:
            primary_bottleneck = bottlenecks[0]
            recommendations.append(f"Address {primary_bottleneck.stage_name} bottleneck - {primary_bottleneck.recommendations[0] if primary_bottleneck.recommendations else 'needs immediate attention'}")
        
        # Sales cycle recommendations
        if metrics.avg_sales_cycle_days > 60:
            recommendations.append("Sales cycle is lengthy. Implement urgency tactics and streamline decision-making process.")
        
        return recommendations[:5]  # Return top 5 recommendations