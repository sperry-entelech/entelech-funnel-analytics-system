"""
Entelech Funnel Analytics Database Initialization Script
Creates database tables and populates with sample data
"""

import sqlite3
import os
from datetime import datetime, timedelta, date
import random
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FunnelDatabaseInitializer:
    
    def __init__(self, db_path: str = "funnel_analytics.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute("PRAGMA foreign_keys = ON")
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def create_tables(self):
        """Create all required tables"""
        try:
            cursor = self.conn.cursor()
            
            # Read and execute schema file
            schema_path = "funnel_schema.sql"
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                    
                # Execute schema in parts (SQLite doesn't handle multiple statements well)
                for statement in schema_sql.split(';'):
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        try:
                            cursor.execute(statement)
                        except sqlite3.Error as e:
                            if "already exists" not in str(e):
                                logger.warning(f"Schema statement failed: {e}")
            
            # Create tables directly if schema file not found
            else:
                self._create_tables_directly(cursor)
            
            self.conn.commit()
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def _create_tables_directly(self, cursor):
        """Create tables directly if schema file not available"""
        
        # Lead sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lead_sources (
                source_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                source_category TEXT NOT NULL CHECK(source_category IN ('linkedin', 'referral', 'cold_outreach', 'website', 'social_media', 'event', 'other')),
                attribution_window_days INTEGER DEFAULT 30,
                cost_per_lead REAL DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Prospects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospects (
                prospect_id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                company_name TEXT,
                job_title TEXT,
                phone TEXT,
                linkedin_url TEXT,
                estimated_company_size TEXT CHECK(estimated_company_size IN ('1-10', '11-50', '51-200', '201-500', '501-1000', '1000+')),
                industry TEXT,
                lead_source_id INTEGER,
                lead_score INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_source_id) REFERENCES lead_sources(source_id)
            )
        """)
        
        # Funnel stages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS funnel_stages (
                stage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage_name TEXT NOT NULL,
                stage_order INTEGER NOT NULL,
                stage_description TEXT,
                expected_duration_days INTEGER DEFAULT 7,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Prospect journey table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prospect_journey (
                journey_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                stage_id INTEGER NOT NULL,
                entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exited_at TIMESTAMP NULL,
                duration_hours REAL NULL,
                conversion_probability REAL DEFAULT 0.00,
                notes TEXT,
                sales_rep TEXT,
                FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id),
                FOREIGN KEY (stage_id) REFERENCES funnel_stages(stage_id)
            )
        """)
        
        # Discovery calls table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discovery_calls (
                call_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                scheduled_at TIMESTAMP NOT NULL,
                completed_at TIMESTAMP NULL,
                call_duration_minutes INTEGER DEFAULT 0,
                call_status TEXT DEFAULT 'scheduled' CHECK(call_status IN ('scheduled', 'completed', 'no_show', 'cancelled', 'rescheduled')),
                pain_points TEXT,
                budget_range TEXT CHECK(budget_range IN ('under_10k', '10k_25k', '25k_50k', '50k_100k', '100k_plus', 'not_disclosed')),
                decision_timeline TEXT CHECK(decision_timeline IN ('immediate', '1_month', '3_months', '6_months', 'longer', 'unknown')),
                decision_makers TEXT,
                next_steps TEXT,
                qualification_score INTEGER DEFAULT 0,
                sales_rep TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id)
            )
        """)
        
        # Proposals table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proposals (
                proposal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                proposal_amount REAL NOT NULL,
                proposal_date DATE NOT NULL,
                proposal_status TEXT DEFAULT 'draft' CHECK(proposal_status IN ('draft', 'sent', 'viewed', 'under_review', 'accepted', 'rejected', 'expired')),
                service_type TEXT NOT NULL CHECK(service_type IN ('automation_setup', 'ongoing_management', 'consulting', 'custom_development', 'hybrid')),
                implementation_timeline_months INTEGER DEFAULT 3,
                monthly_retainer REAL DEFAULT 0.00,
                one_time_setup REAL DEFAULT 0.00,
                proposal_sent_at TIMESTAMP NULL,
                proposal_viewed_at TIMESTAMP NULL,
                follow_up_count INTEGER DEFAULT 0,
                last_follow_up TIMESTAMP NULL,
                rejection_reason TEXT,
                competitor_mentioned TEXT,
                sales_rep TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id)
            )
        """)
        
        # Contracts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                contract_id INTEGER PRIMARY KEY AUTOINCREMENT,
                prospect_id INTEGER NOT NULL,
                proposal_id INTEGER,
                contract_value REAL NOT NULL,
                monthly_recurring_revenue REAL DEFAULT 0.00,
                contract_start_date DATE NOT NULL,
                contract_end_date DATE,
                contract_status TEXT DEFAULT 'active' CHECK(contract_status IN ('active', 'completed', 'cancelled', 'paused')),
                payment_terms TEXT DEFAULT 'monthly' CHECK(payment_terms IN ('monthly', 'quarterly', 'annually', 'one_time')),
                services_delivered TEXT,
                client_satisfaction_score INTEGER,
                renewal_probability REAL DEFAULT 0.00,
                sales_rep TEXT,
                account_manager TEXT,
                signed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prospect_id) REFERENCES prospects(prospect_id),
                FOREIGN KEY (proposal_id) REFERENCES proposals(proposal_id)
            )
        """)
    
    def populate_sample_data(self):
        """Populate database with realistic sample data for testing"""
        try:
            cursor = self.conn.cursor()
            
            # Insert lead sources
            lead_sources = [
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
                ('Word of Mouth', 'other', 90, 0.00)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO lead_sources (source_name, source_category, attribution_window_days, cost_per_lead)
                VALUES (?, ?, ?, ?)
            """, lead_sources)
            
            # Insert funnel stages
            funnel_stages = [
                ('Lead Generated', 1, 'Initial lead capture and qualification', 1),
                ('Discovery Call Scheduled', 2, 'Prospect agrees to discovery call', 3),
                ('Discovery Call Completed', 3, 'Discovery call conducted and next steps defined', 1),
                ('Proposal Sent', 4, 'Formal proposal sent to prospect', 7),
                ('Proposal Under Review', 5, 'Prospect reviewing proposal and making decision', 14),
                ('Contract Negotiation', 6, 'Terms and pricing being negotiated', 7),
                ('Contract Signed', 7, 'Deal closed and contract executed', 1),
                ('Lost/Disqualified', 8, 'Prospect dropped out or was disqualified', 0)
            ]
            
            cursor.executemany("""
                INSERT OR IGNORE INTO funnel_stages (stage_name, stage_order, stage_description, expected_duration_days)
                VALUES (?, ?, ?, ?)
            """, funnel_stages)
            
            # Generate sample prospects (last 90 days)
            companies = [
                'TechFlow Solutions', 'Digital Dynamics', 'InnovateCorp', 'Growth Partners',
                'Alpha Industries', 'Beta Systems', 'Gamma Technologies', 'Delta Enterprises',
                'Future Forward LLC', 'Smart Business Co', 'Efficiency Experts', 'ProcessPro Inc',
                'AutomateNow Corp', 'Streamline Solutions', 'OptimalOps LLC', 'WorkflowWorks'
            ]
            
            industries = [
                'Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail',
                'Real Estate', 'Professional Services', 'Construction', 'Transportation', 'Education'
            ]
            
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emma', 'James', 'Anna']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
            
            sales_reps = ['Alex Thompson', 'Jordan Martinez', 'Casey Johnson', 'Morgan Davis']
            
            # Generate prospects over last 90 days
            prospects_data = []
            start_date = datetime.now() - timedelta(days=90)
            
            for i in range(150):  # Generate 150 prospects
                days_ago = random.randint(0, 90)
                created_at = start_date + timedelta(days=days_ago)
                
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                company = random.choice(companies)
                industry = random.choice(industries)
                source_id = random.randint(1, 11)  # Lead source IDs
                lead_score = random.randint(10, 100)
                
                prospects_data.append((
                    first_name, last_name, f"{first_name.lower()}.{last_name.lower()}@{company.replace(' ', '').lower()}.com",
                    company, f"{random.choice(['CEO', 'CTO', 'VP Operations', 'Director', 'Manager'])}",
                    f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                    f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                    random.choice(['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+']),
                    industry, source_id, lead_score, created_at, created_at
                ))
            
            cursor.executemany("""
                INSERT OR IGNORE INTO prospects (
                    first_name, last_name, email, company_name, job_title, phone, linkedin_url,
                    estimated_company_size, industry, lead_source_id, lead_score, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, prospects_data)
            
            # Generate prospect journeys, discovery calls, proposals, and contracts
            cursor.execute("SELECT prospect_id, created_at FROM prospects ORDER BY prospect_id")
            prospects = cursor.fetchall()
            
            for prospect_id, created_at_str in prospects:
                created_at = datetime.fromisoformat(created_at_str)
                current_stage = 1
                current_date = created_at
                
                # Simulate funnel progression with realistic drop-off rates
                while current_stage <= 7:  # Max stage is Contract Signed (7)
                    
                    # Add to prospect_journey
                    cursor.execute("""
                        INSERT INTO prospect_journey (prospect_id, stage_id, entered_at, sales_rep)
                        VALUES (?, ?, ?, ?)
                    """, (prospect_id, current_stage, current_date, random.choice(sales_reps)))
                    
                    # Determine if prospect progresses based on realistic conversion rates
                    progression_rates = {
                        1: 0.65,  # Lead Generated -> Discovery Scheduled (65%)
                        2: 0.80,  # Discovery Scheduled -> Discovery Completed (80%)
                        3: 0.70,  # Discovery Completed -> Proposal Sent (70%)
                        4: 0.85,  # Proposal Sent -> Proposal Review (85%)
                        5: 0.40,  # Proposal Review -> Contract Negotiation (40%)
                        6: 0.75   # Contract Negotiation -> Contract Signed (75%)
                    }
                    
                    if current_stage == 7:  # Contract Signed
                        break
                    
                    if random.random() > progression_rates.get(current_stage, 0.5):
                        # Prospect drops out
                        break
                    
                    # Generate stage-specific data
                    if current_stage == 2:  # Discovery Call Scheduled
                        scheduled_at = current_date + timedelta(days=random.randint(1, 7))
                        completed = random.random() > 0.15  # 15% no-show rate
                        
                        cursor.execute("""
                            INSERT INTO discovery_calls (
                                prospect_id, scheduled_at, completed_at, call_duration_minutes,
                                call_status, pain_points, budget_range, decision_timeline,
                                qualification_score, sales_rep
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            prospect_id, scheduled_at,
                            scheduled_at if completed else None,
                            random.randint(30, 90) if completed else 0,
                            'completed' if completed else 'no_show',
                            'Process inefficiencies, manual tasks, scaling challenges' if completed else None,
                            random.choice(['25k_50k', '50k_100k', '100k_plus', 'not_disclosed']) if completed else None,
                            random.choice(['1_month', '3_months', '6_months']) if completed else None,
                            random.randint(60, 95) if completed else 0,
                            random.choice(sales_reps)
                        ))
                    
                    elif current_stage == 4:  # Proposal Sent
                        proposal_date = current_date + timedelta(days=random.randint(1, 5))
                        proposal_amount = random.randint(25000, 150000)
                        
                        cursor.execute("""
                            INSERT INTO proposals (
                                prospect_id, proposal_amount, proposal_date, proposal_status,
                                service_type, implementation_timeline_months, monthly_retainer,
                                one_time_setup, proposal_sent_at, sales_rep
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            prospect_id, proposal_amount, proposal_date,
                            random.choice(['sent', 'viewed', 'under_review']),
                            random.choice(['automation_setup', 'ongoing_management', 'hybrid']),
                            random.randint(3, 12),
                            proposal_amount * 0.1,  # 10% monthly retainer
                            proposal_amount * 0.3,  # 30% setup fee
                            proposal_date, random.choice(sales_reps)
                        ))
                    
                    elif current_stage == 7:  # Contract Signed
                        # Get the proposal for this prospect
                        cursor.execute("SELECT proposal_id, proposal_amount FROM proposals WHERE prospect_id = ? ORDER BY proposal_date DESC LIMIT 1", (prospect_id,))
                        proposal = cursor.fetchone()
                        
                        if proposal:
                            proposal_id, proposal_amount = proposal
                            contract_value = proposal_amount * random.uniform(0.9, 1.1)  # Some negotiation
                            start_date = current_date + timedelta(days=random.randint(7, 30))
                            
                            cursor.execute("""
                                INSERT INTO contracts (
                                    prospect_id, proposal_id, contract_value, monthly_recurring_revenue,
                                    contract_start_date, contract_status, payment_terms,
                                    sales_rep, account_manager, signed_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                prospect_id, proposal_id, contract_value, contract_value * 0.1,
                                start_date, 'active', random.choice(['monthly', 'quarterly']),
                                random.choice(sales_reps), random.choice(sales_reps), current_date
                            ))
                    
                    # Move to next stage
                    current_stage += 1
                    current_date += timedelta(days=random.randint(1, 14))
            
            self.conn.commit()
            logger.info("Sample data populated successfully")
            
        except Exception as e:
            logger.error(f"Error populating sample data: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            cursor = self.conn.cursor()
            
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_prospects_email ON prospects(email)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_source ON prospects(lead_source_id)",
                "CREATE INDEX IF NOT EXISTS idx_prospects_created ON prospects(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_journey_prospect ON prospect_journey(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_journey_stage ON prospect_journey(stage_id)",
                "CREATE INDEX IF NOT EXISTS idx_journey_dates ON prospect_journey(entered_at)",
                "CREATE INDEX IF NOT EXISTS idx_calls_prospect ON discovery_calls(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_calls_date ON discovery_calls(scheduled_at)",
                "CREATE INDEX IF NOT EXISTS idx_proposals_prospect ON proposals(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_proposals_status ON proposals(proposal_status)",
                "CREATE INDEX IF NOT EXISTS idx_contracts_prospect ON contracts(prospect_id)",
                "CREATE INDEX IF NOT EXISTS idx_contracts_value ON contracts(contract_value)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise
    
    def get_database_stats(self):
        """Get statistics about the created database"""
        try:
            cursor = self.conn.cursor()
            
            stats = {}
            
            # Count records in each table
            tables = ['lead_sources', 'prospects', 'funnel_stages', 'prospect_journey', 
                     'discovery_calls', 'proposals', 'contracts']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            
            # Calculate some business metrics
            cursor.execute("SELECT COUNT(*) FROM contracts WHERE contract_status = 'active'")
            stats['active_contracts'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(contract_value) FROM contracts WHERE contract_status = 'active'")
            total_revenue = cursor.fetchone()[0]
            stats['total_revenue'] = total_revenue if total_revenue else 0
            
            cursor.execute("SELECT AVG(contract_value) FROM contracts WHERE contract_status = 'active'")
            avg_deal_size = cursor.fetchone()[0]
            stats['avg_deal_size'] = avg_deal_size if avg_deal_size else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

def main():
    """Main initialization function"""
    print("🚀 Initializing Entelech Funnel Analytics Database...")
    
    # Initialize database
    db_init = FunnelDatabaseInitializer()
    
    try:
        # Connect to database
        db_init.connect()
        
        # Create tables
        print("📋 Creating database tables...")
        db_init.create_tables()
        
        # Populate sample data
        print("📊 Populating sample data...")
        db_init.populate_sample_data()
        
        # Create indexes
        print("⚡ Creating database indexes...")
        db_init.create_indexes()
        
        # Get and display statistics
        print("📈 Database Statistics:")
        stats = db_init.get_database_stats()
        
        for table, count in stats.items():
            if table in ['total_revenue', 'avg_deal_size']:
                print(f"  {table.replace('_', ' ').title()}: ${count:,.2f}")
            else:
                print(f"  {table.replace('_', ' ').title()}: {count}")
        
        print("\n✅ Database initialization completed successfully!")
        print("🎯 Ready to track leads, conversions, and revenue attribution")
        print("\n🔗 Next steps:")
        print("1. Run: python dashboard/funnel_dashboard.py")
        print("2. Open: http://localhost:5001")
        print("3. Start analyzing your funnel performance!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    finally:
        db_init.close()
    
    return True

if __name__ == "__main__":
    main()