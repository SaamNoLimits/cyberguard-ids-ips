-- 📊 CYBERSECURITY REPORTS DATABASE SCHEMA
-- Creates tables for storing incident reports and related data

-- Create reports table
CREATE TABLE IF NOT EXISTS incident_reports (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'incident',
    severity VARCHAR(20) NOT NULL DEFAULT 'medium',
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    analyst VARCHAR(100) NOT NULL,
    resolution TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create affected systems table (many-to-many with reports)
CREATE TABLE IF NOT EXISTS report_affected_systems (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) REFERENCES incident_reports(id) ON DELETE CASCADE,
    system_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create report threats junction table (links reports to threat_alerts)
CREATE TABLE IF NOT EXISTS report_threats (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) REFERENCES incident_reports(id) ON DELETE CASCADE,
    threat_alert_id INTEGER,
    threat_data JSONB, -- Store threat data snapshot
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create report attachments table
CREATE TABLE IF NOT EXISTS report_attachments (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) REFERENCES incident_reports(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    file_path TEXT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create report comments/notes table
CREATE TABLE IF NOT EXISTS report_comments (
    id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) REFERENCES incident_reports(id) ON DELETE CASCADE,
    comment_text TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_incident_reports_created_at ON incident_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_incident_reports_status ON incident_reports(status);
CREATE INDEX IF NOT EXISTS idx_incident_reports_severity ON incident_reports(severity);
CREATE INDEX IF NOT EXISTS idx_incident_reports_type ON incident_reports(type);
CREATE INDEX IF NOT EXISTS idx_report_threats_report_id ON report_threats(report_id);
CREATE INDEX IF NOT EXISTS idx_report_affected_systems_report_id ON report_affected_systems(report_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_incident_reports_updated_at 
    BEFORE UPDATE ON incident_reports 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample reports for testing
INSERT INTO incident_reports (id, title, type, severity, status, description, analyst) VALUES
('RPT-001', 'Suspicious Network Activity Detected', 'incident', 'high', 'investigating', 'Multiple failed login attempts detected from external IP addresses. Potential brute force attack in progress.', 'John Smith'),
('RPT-002', 'Malware Detection on Workstation', 'incident', 'critical', 'resolved', 'Trojan horse detected on employee workstation. System isolated and cleaned.', 'Jane Doe'),
('RPT-003', 'DDoS Attack Mitigation', 'incident', 'high', 'mitigated', 'Large-scale DDoS attack detected and successfully mitigated using traffic filtering.', 'Mike Johnson'),
('RPT-004', 'Data Exfiltration Attempt', 'incident', 'critical', 'open', 'Unusual outbound data transfer patterns detected. Investigation ongoing.', 'Sarah Wilson'),
('RPT-005', 'Phishing Email Campaign', 'incident', 'medium', 'resolved', 'Phishing emails targeting employees detected and blocked. User awareness training conducted.', 'Tom Brown')
ON CONFLICT (id) DO NOTHING;

-- Insert sample affected systems
INSERT INTO report_affected_systems (report_id, system_name) VALUES
('RPT-001', 'Web Server 01'),
('RPT-001', 'Database Server'),
('RPT-002', 'Workstation-PC-045'),
('RPT-003', 'Load Balancer'),
('RPT-003', 'Web Server 01'),
('RPT-003', 'Web Server 02'),
('RPT-004', 'File Server'),
('RPT-004', 'Database Server'),
('RPT-005', 'Email Server')
ON CONFLICT DO NOTHING;

-- Insert sample comments
INSERT INTO report_comments (report_id, comment_text, author) VALUES
('RPT-001', 'Initial investigation shows attacks from multiple IP ranges. Implementing additional firewall rules.', 'John Smith'),
('RPT-001', 'Attack intensity has decreased after implementing countermeasures.', 'John Smith'),
('RPT-002', 'Malware removed successfully. System restored from clean backup.', 'Jane Doe'),
('RPT-003', 'DDoS attack lasted 2 hours. All services remained operational.', 'Mike Johnson'),
('RPT-004', 'Forensic analysis in progress. No confirmed data loss at this time.', 'Sarah Wilson')
ON CONFLICT DO NOTHING;

-- Create view for report summary statistics
CREATE OR REPLACE VIEW report_statistics AS
SELECT 
    COUNT(*) as total_reports,
    COUNT(CASE WHEN status = 'open' THEN 1 END) as open_reports,
    COUNT(CASE WHEN status = 'investigating' THEN 1 END) as investigating_reports,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved_reports,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_reports,
    COUNT(CASE WHEN severity = 'high' THEN 1 END) as high_reports,
    COUNT(CASE WHEN severity = 'medium' THEN 1 END) as medium_reports,
    COUNT(CASE WHEN severity = 'low' THEN 1 END) as low_reports,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '24 hours' THEN 1 END) as reports_last_24h,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 END) as reports_last_7d,
    COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as reports_last_30d
FROM incident_reports;

COMMENT ON TABLE incident_reports IS 'Main table for storing cybersecurity incident reports';
COMMENT ON TABLE report_affected_systems IS 'Systems affected by each incident report';
COMMENT ON TABLE report_threats IS 'Links reports to specific threat alerts';
COMMENT ON TABLE report_attachments IS 'File attachments for reports (PCAP files, screenshots, etc.)';
COMMENT ON TABLE report_comments IS 'Comments and notes added to reports during investigation';
COMMENT ON VIEW report_statistics IS 'Summary statistics for all incident reports';
