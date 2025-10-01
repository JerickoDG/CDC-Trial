CREATE DATABASE IF NOT EXISTS jobdb;

USE jobdb;

CREATE TABLE job_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_order_number VARCHAR(50) NOT NULL UNIQUE,
    desired_qty INT NOT NULL,
    current_qty INT DEFAULT 0,
    percent_completion DECIMAL(5,2) DEFAULT 0.00,
    status ENUM('ONGOING', 'COMPLETED') DEFAULT 'ONGOING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO job_orders (job_order_number, desired_qty, current_qty, percent_completion, status) VALUES
('JO-001', 100, 25, 25.00, 'ONGOING'),
('JO-002', 200, 150, 75.00, 'ONGOING'),
('JO-003', 50, 50, 100.00, 'COMPLETED');