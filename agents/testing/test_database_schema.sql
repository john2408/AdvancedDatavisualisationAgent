-- Database Schema for Testing
CREATE TABLE employees (
    id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),       -- PII
    address VARCHAR(255),      -- PII
    hire_date DATE,
    salary DECIMAL(10, 2),
    department_id INT
);

CREATE TABLE departments (
id INT PRIMARY KEY,
name VARCHAR(50),
location VARCHAR(50)
);

CREATE TABLE sales (
id INT PRIMARY KEY,
employee\_id INT,
product\_id INT,
sale\_date DATE,
amount DECIMAL(10, 2)
);

CREATE TABLE products (
id INT PRIMARY KEY,
name VARCHAR(100),
category VARCHAR(50),
price DECIMAL(10, 2)
);