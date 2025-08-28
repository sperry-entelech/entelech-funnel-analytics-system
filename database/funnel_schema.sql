-- Entelech Funnel Analytics Database Schema
-- Comprehensive lead tracking and conversion analytics

CREATE DATABASE IF NOT EXISTS entelech_funnel_analytics;
USE entelech_funnel_analytics;

-- ================================
-- CORE TABLES
-- ================================

-- Lead Sources and Attribution
CREATE TABLE lead_sources (
    source_id INT PRIMARY KEY AUTO_INCREMENT,
    source_name VARCHAR(100) NOT NULL,
    source_category ENUM('linkedin', 'referral', 'cold_outreach', 'website', 'social_media', 'event', 'other') NOT NULL,
    attribution_window_days INT DEFAULT 30,
    cost_per_lead DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Prospects and Lead Information
CREATE TABLE prospects (
    prospect_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    company_name VARCHAR(200),
    job_title VARCHAR(150),
    phone VARCHAR(20),
    linkedin_url VARCHAR(500),
    estimated_company_size ENUM('1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'),
    industry VARCHAR(100),
    lead_source_id INT,
    lead_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_source_id) REFERENCES lead_sources(source_id)
);

-- Funnel Stages Definition
CREATE TABLE funnel_stages (
    stage_id INT PRIMARY KEY AUTO_INCREMENT,
    stage_name VARCHAR(100) NOT NULL,
    stage_order INT NOT NULL,
    stage_description TEXT,
    expected_duration_days INT DEFAULT 7,
    is_active BOOLEAN DEFAULT TRUE
);

-- Prospect Journey Tracking
CREATE TABLE prospect_journey (
    journey_id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    stage_id INT NOT NULL,
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    exited_at TIMESTAMP NULL,
    duration_hours DECIMAL(10,2) NULL,
    conversion_probability DECIMAL(5,2) DEFAULT 0.00,
    notes TEXT,
    sales_rep VARCHAR(100),
    FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id),
    FOREIGN KEY (stage_id) REFERENCES funnel_stages(stage_id)
);

-- Discovery Calls Tracking
CREATE TABLE discovery_calls (
    call_id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    scheduled_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP NULL,
    call_duration_minutes INT DEFAULT 0,
    call_status ENUM('scheduled', 'completed', 'no_show', 'cancelled', 'rescheduled') DEFAULT 'scheduled',
    pain_points TEXT,
    budget_range ENUM('under_10k', '10k_25k', '25k_50k', '50k_100k', '100k_plus', 'not_disclosed'),
    decision_timeline ENUM('immediate', '1_month', '3_months', '6_months', 'longer', 'unknown'),
    decision_makers TEXT,
    next_steps TEXT,
    qualification_score INT DEFAULT 0,
    sales_rep VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id)
);

-- Proposals Tracking
CREATE TABLE proposals (
    proposal_id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    proposal_amount DECIMAL(12,2) NOT NULL,
    proposal_date DATE NOT NULL,
    proposal_status ENUM('draft', 'sent', 'viewed', 'under_review', 'accepted', 'rejected', 'expired') DEFAULT 'draft',
    service_type ENUM('automation_setup', 'ongoing_management', 'consulting', 'custom_development', 'hybrid') NOT NULL,
    implementation_timeline_months INT DEFAULT 3,
    monthly_retainer DECIMAL(10,2) DEFAULT 0.00,
    one_time_setup DECIMAL(10,2) DEFAULT 0.00,
    proposal_sent_at TIMESTAMP NULL,
    proposal_viewed_at TIMESTAMP NULL,
    follow_up_count INT DEFAULT 0,
    last_follow_up TIMESTAMP NULL,
    rejection_reason TEXT,
    competitor_mentioned VARCHAR(200),
    sales_rep VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id)
);

-- Contracts and Revenue Tracking
CREATE TABLE contracts (
    contract_id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    proposal_id INT,
    contract_value DECIMAL(12,2) NOT NULL,
    monthly_recurring_revenue DECIMAL(10,2) DEFAULT 0.00,
    contract_start_date DATE NOT NULL,
    contract_end_date DATE,
    contract_status ENUM('active', 'completed', 'cancelled', 'paused') DEFAULT 'active',
    payment_terms ENUM('monthly', 'quarterly', 'annually', 'one_time') DEFAULT 'monthly',
    services_delivered TEXT,
    client_satisfaction_score INT,
    renewal_probability DECIMAL(5,2) DEFAULT 0.00,
    sales_rep VARCHAR(100),
    account_manager VARCHAR(100),
    signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id),
    FOREIGN KEY (proposal_id) REFERENCES proposals(proposal_id)
);

-- ================================
-- ANALYTICS AND TRACKING TABLES
-- ================================

-- Conversion Rates by Time Period
CREATE TABLE conversion_metrics (
    metric_id INT PRIMARY KEY AUTO_INCREMENT,
    date_period DATE NOT NULL,
    lead_source_id INT,
    total_leads INT DEFAULT 0,
    discovery_calls_scheduled INT DEFAULT 0,
    discovery_calls_completed INT DEFAULT 0,
    proposals_sent INT DEFAULT 0,
    contracts_signed INT DEFAULT 0,
    total_revenue DECIMAL(12,2) DEFAULT 0.00,
    avg_deal_size DECIMAL(10,2) DEFAULT 0.00,
    avg_sales_cycle_days DECIMAL(8,2) DEFAULT 0.00,
    lead_to_discovery_rate DECIMAL(5,2) DEFAULT 0.00,
    discovery_to_proposal_rate DECIMAL(5,2) DEFAULT 0.00,
    proposal_to_contract_rate DECIMAL(5,2) DEFAULT 0.00,
    overall_conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    cost_per_acquisition DECIMAL(10,2) DEFAULT 0.00,
    lifetime_value DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_source_id) REFERENCES lead_sources(source_id)
);

-- Stage Performance Analytics
CREATE TABLE stage_analytics (
    analytics_id INT PRIMARY KEY AUTO_INCREMENT,
    stage_id INT NOT NULL,
    date_period DATE NOT NULL,
    prospects_entered INT DEFAULT 0,
    prospects_exited INT DEFAULT 0,
    prospects_converted INT DEFAULT 0,
    prospects_dropped INT DEFAULT 0,
    avg_stage_duration_days DECIMAL(8,2) DEFAULT 0.00,
    conversion_rate DECIMAL(5,2) DEFAULT 0.00,
    bottleneck_score DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stage_id) REFERENCES funnel_stages(stage_id)
);

-- Revenue Attribution
CREATE TABLE revenue_attribution (
    attribution_id INT PRIMARY KEY AUTO_INCREMENT,
    contract_id INT NOT NULL,
    lead_source_id INT NOT NULL,
    attribution_percentage DECIMAL(5,2) DEFAULT 100.00,
    attributed_revenue DECIMAL(12,2) NOT NULL,
    attribution_model ENUM('first_touch', 'last_touch', 'linear', 'time_decay', 'position_based') DEFAULT 'first_touch',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(contract_id),
    FOREIGN KEY (lead_source_id) REFERENCES lead_sources(source_id)
);

-- ================================
-- INITIAL DATA
-- ================================

-- Insert default funnel stages
INSERT INTO funnel_stages (stage_name, stage_order, stage_description, expected_duration_days) VALUES
('Lead Generated', 1, 'Initial lead capture and qualification', 1),
('Discovery Call Scheduled', 2, 'Prospect agrees to discovery call', 3),
('Discovery Call Completed', 3, 'Discovery call conducted and next steps defined', 1),
('Proposal Sent', 4, 'Formal proposal sent to prospect', 7),
('Proposal Under Review', 5, 'Prospect reviewing proposal and making decision', 14),
('Contract Negotiation', 6, 'Terms and pricing being negotiated', 7),
('Contract Signed', 7, 'Deal closed and contract executed', 1),
('Lost/Disqualified', 8, 'Prospect dropped out or was disqualified', 0);

-- Insert default lead sources
INSERT INTO lead_sources (source_name, source_category, attribution_window_days, cost_per_lead) VALUES
('LinkedIn Content Marketing', 'linkedin', 30, 15.00),
('LinkedIn Direct Outreach', 'linkedin', 7, 25.00),
('LinkedIn Ads', 'linkedin', 7, 45.00),
('Client Referrals', 'referral', 90, 0.00),
('Partner Referrals', 'referral', 60, 50.00),
('Cold Email Campaigns', 'cold_outreach', 14, 8.00),
('Cold Calling', 'cold_outreach', 7, 35.00),
('Website Organic', 'website', 30, 5.00),
('Website Contact Form', 'website', 1, 3.00),
('Industry Events', 'event', 60, 150.00),
('Word of Mouth', 'other', 90, 0.00);

-- ================================
-- INDEXES FOR PERFORMANCE
-- ================================

CREATE INDEX idx_prospects_email ON prospects(email);
CREATE INDEX idx_prospects_source ON prospects(lead_source_id);
CREATE INDEX idx_prospects_created ON prospects(created_at);
CREATE INDEX idx_journey_prospect ON prospect_journey(prospect_id);
CREATE INDEX idx_journey_stage ON prospect_journey(stage_id);
CREATE INDEX idx_journey_dates ON prospect_journey(entered_at, exited_at);
CREATE INDEX idx_calls_prospect ON discovery_calls(prospect_id);
CREATE INDEX idx_calls_date ON discovery_calls(scheduled_at);
CREATE INDEX idx_proposals_prospect ON proposals(prospect_id);
CREATE INDEX idx_proposals_status ON proposals(proposal_status);
CREATE INDEX idx_contracts_prospect ON contracts(prospect_id);
CREATE INDEX idx_contracts_value ON contracts(contract_value);
CREATE INDEX idx_metrics_date ON conversion_metrics(date_period);
CREATE INDEX idx_attribution_contract ON revenue_attribution(contract_id);