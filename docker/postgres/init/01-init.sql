-- SAPDOCAI PostgreSQL Database Initialization
-- SAP ME/MII compatible database schema

-- Create database if not exists (handled by POSTGRES_DB env var)
-- \c sapdocai_pg;

-- Create tables for SAP ME/MII analysis results
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(255) NOT NULL,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_files INTEGER DEFAULT 0,
    java_classes INTEGER DEFAULT 0,
    sapui5_views INTEGER DEFAULT 0,
    database_accesses INTEGER DEFAULT 0,
    rest_endpoints INTEGER DEFAULT 0,
    bls_steps INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Java classes analysis
CREATE TABLE IF NOT EXISTS java_classes (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    class_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    package_name VARCHAR(255),
    methods_count INTEGER DEFAULT 0,
    complexity_score INTEGER DEFAULT 0
);

-- SAPUI5 components
CREATE TABLE IF NOT EXISTS sapui5_components (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    component_type VARCHAR(20) NOT NULL CHECK (component_type IN ('controller', 'view', 'fragment', 'model', 'service')),
    component_name VARCHAR(255) NOT NULL,
    file_path TEXT,
    functions_count INTEGER DEFAULT 0,
    event_handlers_count INTEGER DEFAULT 0,
    api_calls_count INTEGER DEFAULT 0
);

-- Database accesses
CREATE TABLE IF NOT EXISTS database_accesses (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    access_type VARCHAR(20) NOT NULL CHECK (access_type IN ('jdbc', 'sql', 'connection', 'sap_specific')),
    pattern_matched TEXT,
    file_path TEXT,
    line_number INTEGER,
    context TEXT
);

-- REST endpoints
CREATE TABLE IF NOT EXISTS rest_endpoints (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    endpoint_path VARCHAR(500) NOT NULL,
    http_method VARCHAR(10) NOT NULL CHECK (http_method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
    file_path TEXT,
    line_number INTEGER,
    context TEXT
);

-- BLS steps
CREATE TABLE IF NOT EXISTS bls_steps (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    step_name VARCHAR(255) NOT NULL,
    step_type VARCHAR(20) NOT NULL CHECK (step_type IN ('BLS', 'Transaction', 'Workflow', 'Process', 'Activity')),
    file_path TEXT,
    line_number INTEGER,
    context TEXT
);

-- Analysis relationships
CREATE TABLE IF NOT EXISTS analysis_relationships (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES analysis_results(id) ON DELETE CASCADE,
    source_component VARCHAR(255) NOT NULL,
    target_component VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(100) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analysis_results_project ON analysis_results(project_name);
CREATE INDEX IF NOT EXISTS idx_analysis_results_date ON analysis_results(analysis_date);
CREATE INDEX IF NOT EXISTS idx_java_classes_analysis ON java_classes(analysis_id);
CREATE INDEX IF NOT EXISTS idx_sapui5_components_analysis ON sapui5_components(analysis_id);
CREATE INDEX IF NOT EXISTS idx_database_accesses_analysis ON database_accesses(analysis_id);
CREATE INDEX IF NOT EXISTS idx_rest_endpoints_analysis ON rest_endpoints(analysis_id);
CREATE INDEX IF NOT EXISTS idx_bls_steps_analysis ON bls_steps(analysis_id);
CREATE INDEX IF NOT EXISTS idx_relationships_analysis ON analysis_relationships(analysis_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO analysis_results (project_name, total_files, java_classes, sapui5_views, database_accesses, rest_endpoints, bls_steps, status) 
VALUES ('SAPDOCAI Sample Project', 25, 5, 10, 18, 11, 4, 'completed');

-- Sample Java classes
INSERT INTO java_classes (analysis_id, class_name, file_path, package_name, methods_count, complexity_score) VALUES
(1, 'BaseController', '/controller/BaseController.js', 'sap.ui.core.mvc', 15, 8),
(1, 'HomeController', '/controller/Home.controller.js', 'sap.ui.core.mvc', 12, 6),
(1, 'TraceabilityController', '/controller/traceability.controller.js', 'sap.ui.core.mvc', 20, 9);

-- Sample SAPUI5 components
INSERT INTO sapui5_components (analysis_id, component_type, component_name, file_path, functions_count, event_handlers_count, api_calls_count) VALUES
(1, 'controller', 'App.controller', '/controller/App.controller.js', 8, 5, 3),
(1, 'view', 'Home.view', '/view/Home.view.xml', 0, 0, 0),
(1, 'fragment', 'OrderDetails.fragment', '/fragments/OrderDetails.fragment.xml', 0, 0, 0);

-- Sample database accesses
INSERT INTO database_accesses (analysis_id, access_type, pattern_matched, file_path, line_number, context) VALUES
(1, 'jdbc', 'jdbc:mysql://sap-me-db.example.com:3306/production', '/application.properties', 4, 'db.url=jdbc:mysql://sap-me-db.example.com:3306/production'),
(1, 'sql', 'SELECT * FROM orders', '/config/orders.xml', 17, 'SELECT * FROM orders WHERE order_id = {OrderID}'),
(1, 'sql', 'UPDATE orders SET', '/config/orders.xml', 26, 'UPDATE orders SET status = {Status} WHERE order_id = {OrderID}');

-- Sample REST endpoints
INSERT INTO rest_endpoints (analysis_id, endpoint_path, http_method, file_path, line_number, context) VALUES
(1, '/api/v2/products', 'GET', '/config/endpoints.properties', 10, 'GET /api/v2/products'),
(1, '/api/v2/orders', 'POST', '/config/endpoints.properties', 15, 'POST /api/v2/orders'),
(1, '/api/v2/orders/{id}', 'PUT', '/config/endpoints.properties', 20, 'PUT /api/v2/orders/{id}');

-- Sample BLS steps
INSERT INTO bls_steps (analysis_id, step_name, step_type, file_path, line_number, context) VALUES
(1, 'Order Processing Step', 'BLS', '/workflow/order.bpmn', 25, 'BLS Step: Order Processing'),
(1, 'Quality Check Step', 'Transaction', '/workflow/quality.bpmn', 30, 'Transaction Step: Quality Check'),
(1, 'Packaging Step', 'Workflow', '/workflow/packaging.bpmn', 35, 'Workflow Step: Packaging');

-- Sample relationships
INSERT INTO analysis_relationships (analysis_id, source_component, target_component, relationship_type) VALUES
(1, 'Route:appHome', 'View:home', 'ROUTE_TO_VIEW'),
(1, 'Controller:Home', 'Service:OrderService', 'CONTROLLER_USES_SERVICE'),
(1, 'Service:OrderService', 'Database:orders', 'SERVICE_ACCESSES_DATABASE');
