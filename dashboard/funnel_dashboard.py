"""
Entelech Funnel Analytics Dashboard
Interactive web dashboard for funnel performance and revenue attribution
"""

from flask import Flask, render_template, jsonify, request, send_file
import json
import sqlite3
import pandas as pd
from datetime import datetime, timedelta, date
import plotly.graph_objs as go
import plotly.utils
from typing import Dict, List, Any
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from funnel_analytics_engine import FunnelAnalyticsEngine, ConversionMetrics

app = Flask(__name__)
app.config['SECRET_KEY'] = 'entelech-funnel-analytics-2025'

# Initialize analytics engine
analytics_engine = FunnelAnalyticsEngine("../database/funnel_analytics.db")

# ================================
# DASHBOARD ROUTES
# ================================

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('funnel_dashboard.html')

@app.route('/api/overview')
def api_overview():
    """Get funnel overview data"""
    try:
        # Default to last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Get custom date range if provided
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        # Calculate conversion metrics
        metrics = analytics_engine.calculate_conversion_rates((start_date, end_date))
        
        # Get lead source performance
        source_performance = analytics_engine.get_lead_source_performance((start_date, end_date))
        
        # Get bottleneck analysis
        bottlenecks = analytics_engine.identify_bottlenecks((start_date, end_date))
        high_priority_bottlenecks = len([b for b in bottlenecks if b.bottleneck_severity == "HIGH"])
        
        overview_data = {
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "key_metrics": {
                "total_leads": metrics.total_leads,
                "discovery_calls_scheduled": metrics.discovery_calls_scheduled,
                "proposals_sent": metrics.proposals_sent,
                "contracts_signed": metrics.contracts_signed,
                "total_revenue": f"${metrics.total_revenue:,.2f}",
                "avg_deal_size": f"${metrics.avg_deal_size:,.2f}",
                "overall_conversion_rate": f"{metrics.overall_conversion_rate:.1f}%",
                "avg_sales_cycle_days": f"{metrics.avg_sales_cycle_days:.0f} days"
            },
            "conversion_funnel": {
                "lead_to_discovery": f"{metrics.lead_to_discovery_rate:.1f}%",
                "discovery_to_proposal": f"{metrics.discovery_to_proposal_rate:.1f}%",
                "proposal_to_contract": f"{metrics.proposal_to_contract_rate:.1f}%"
            },
            "alerts": {
                "high_priority_bottlenecks": high_priority_bottlenecks,
                "low_converting_sources": len(source_performance[source_performance['conversion_rate'] < 5]) if not source_performance.empty else 0
            },
            "top_sources": source_performance.head(3).to_dict('records') if not source_performance.empty else []
        }
        
        return jsonify(overview_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversion-funnel')
def api_conversion_funnel():
    """Get conversion funnel visualization data"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        metrics = analytics_engine.calculate_conversion_rates((start_date, end_date))
        
        # Create funnel data
        funnel_data = {
            "stages": [
                "Leads Generated",
                "Discovery Calls Scheduled", 
                "Discovery Calls Completed",
                "Proposals Sent",
                "Contracts Signed"
            ],
            "values": [
                metrics.total_leads,
                metrics.discovery_calls_scheduled,
                metrics.discovery_calls_completed,
                metrics.proposals_sent,
                metrics.contracts_signed
            ],
            "conversion_rates": [
                100.0,
                metrics.lead_to_discovery_rate if metrics.total_leads > 0 else 0,
                (metrics.discovery_calls_completed / metrics.total_leads * 100) if metrics.total_leads > 0 else 0,
                (metrics.proposals_sent / metrics.total_leads * 100) if metrics.total_leads > 0 else 0,
                metrics.overall_conversion_rate
            ]
        }
        
        return jsonify(funnel_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lead-sources')
def api_lead_sources():
    """Get lead source performance data"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)  # 90 days for lead sources
        
        if request.args.get('start_date'):
            start_date = datetime.strpython(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        source_performance = analytics_engine.get_lead_source_performance((start_date, end_date))
        
        if source_performance.empty:
            return jsonify({"sources": [], "charts": {}})
        
        # Prepare data for different visualizations
        charts_data = {
            "revenue_by_source": {
                "labels": source_performance['source_name'].tolist(),
                "values": source_performance['total_revenue'].tolist(),
                "colors": ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA']
            },
            "conversion_rates": {
                "sources": source_performance['source_name'].tolist(),
                "rates": source_performance['conversion_rate'].tolist()
            },
            "roi_analysis": {
                "sources": source_performance['source_name'].tolist(),
                "roi": source_performance['roi'].tolist(),
                "costs": source_performance['total_acquisition_cost'].tolist()
            }
        }
        
        return jsonify({
            "sources": source_performance.to_dict('records'),
            "charts": charts_data
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bottlenecks')
def api_bottlenecks():
    """Get bottleneck analysis data"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        bottlenecks = analytics_engine.identify_bottlenecks((start_date, end_date))
        
        bottleneck_data = []
        for bottleneck in bottlenecks:
            bottleneck_data.append({
                "stage_name": bottleneck.stage_name,
                "conversion_rate": bottleneck.conversion_rate,
                "avg_duration_days": bottleneck.avg_duration_days,
                "prospects_stuck": bottleneck.prospects_stuck,
                "bottleneck_severity": bottleneck.bottleneck_severity,
                "recommendations": bottleneck.recommendations
            })
        
        return jsonify({
            "bottlenecks": bottleneck_data,
            "summary": {
                "high_priority": len([b for b in bottlenecks if b.bottleneck_severity == "HIGH"]),
                "medium_priority": len([b for b in bottlenecks if b.bottleneck_severity == "MEDIUM"]),
                "low_priority": len([b for b in bottlenecks if b.bottleneck_severity == "LOW"])
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/revenue-attribution')
def api_revenue_attribution():
    """Get revenue attribution analysis"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        attribution_model = request.args.get('model', 'first_touch')
        revenue_attribution = analytics_engine.calculate_revenue_attribution((start_date, end_date), attribution_model)
        
        if revenue_attribution.empty:
            return jsonify({"attribution": [], "total_revenue": 0})
        
        return jsonify({
            "attribution": revenue_attribution.to_dict('records'),
            "total_revenue": revenue_attribution['total_attributed_revenue'].sum(),
            "model": attribution_model,
            "chart_data": {
                "labels": revenue_attribution['source_name'].tolist(),
                "values": revenue_attribution['total_attributed_revenue'].tolist(),
                "percentages": revenue_attribution['revenue_percentage'].tolist()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/insights')
def api_insights():
    """Get comprehensive funnel insights"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        insights = analytics_engine.generate_comprehensive_insights((start_date, end_date))
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trends')
def api_trends():
    """Get funnel performance trends over time"""
    try:
        # Get last 12 weeks of data for trending
        end_date = date.today()
        start_date = end_date - timedelta(weeks=12)
        
        conn = sqlite3.connect("../database/funnel_analytics.db")
        
        # Weekly conversion metrics
        query = """
            SELECT 
                DATE(p.created_at, 'weekday 0', '-6 days') as week_start,
                COUNT(DISTINCT p.prospect_id) as leads,
                COUNT(DISTINCT CASE WHEN c.contract_id IS NOT NULL THEN p.prospect_id END) as contracts,
                COALESCE(SUM(c.contract_value), 0) as revenue,
                ROUND(
                    CAST(COUNT(DISTINCT CASE WHEN c.contract_id IS NOT NULL THEN p.prospect_id END) AS FLOAT) / 
                    CAST(COUNT(DISTINCT p.prospect_id) AS FLOAT) * 100, 2
                ) as conversion_rate
            FROM prospects p
            LEFT JOIN contracts c ON p.prospect_id = c.prospect_id
            WHERE p.created_at BETWEEN ? AND ?
            GROUP BY DATE(p.created_at, 'weekday 0', '-6 days')
            ORDER BY week_start
        """
        
        df = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        trends_data = {
            "weekly_trends": {
                "weeks": df['week_start'].tolist(),
                "leads": df['leads'].tolist(),
                "contracts": df['contracts'].tolist(),
                "revenue": df['revenue'].tolist(),
                "conversion_rates": df['conversion_rate'].tolist()
            }
        }
        
        return jsonify(trends_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export/<report_type>')
def api_export(report_type):
    """Export funnel data to CSV"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        if request.args.get('start_date'):
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
        if request.args.get('end_date'):
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
        
        filename = f"entelech_funnel_{report_type}_{start_date}_{end_date}.csv"
        
        if report_type == "lead_sources":
            data = analytics_engine.get_lead_source_performance((start_date, end_date))
        elif report_type == "revenue_attribution":
            data = analytics_engine.calculate_revenue_attribution((start_date, end_date))
        elif report_type == "comprehensive":
            insights = analytics_engine.generate_comprehensive_insights((start_date, end_date))
            # Convert insights to DataFrame for export
            data = pd.DataFrame([insights])
        else:
            return jsonify({"error": "Invalid report type"}), 400
        
        if data.empty:
            return jsonify({"error": "No data available for export"}), 404
        
        # Save to temp file and send
        export_path = f"/tmp/{filename}"
        data.to_csv(export_path, index=False)
        
        return send_file(export_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ================================
# ERROR HANDLERS
# ================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ================================
# MAIN APPLICATION
# ================================

if __name__ == '__main__':
    # Ensure database exists
    if not os.path.exists("../database/funnel_analytics.db"):
        print("Warning: Database not found. Please run database initialization first.")
    
    print("Starting Entelech Funnel Analytics Dashboard...")
    print("Dashboard will be available at: http://localhost:5001")
    print("API endpoints available at: /api/overview, /api/conversion-funnel, /api/lead-sources, etc.")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )