-- ============================================
-- Rehabilitation System - Database Schema
-- ============================================

-- Create database
CREATE DATABASE IF NOT EXISTS rehabilitation_system;
USE rehabilitation_system;

-- ============================================
-- Users table (base table for both patients and doctors)
-- ============================================
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor') NOT NULL,
    phone VARCHAR(20) NOT NULL,
    avatar VARCHAR(255) DEFAULT 'default-avatar.png',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ============================================
-- Patients table
-- ============================================
CREATE TABLE IF NOT EXISTS patients (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    patient_id VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    medical_condition VARCHAR(100) NOT NULL,
    therapy_type VARCHAR(100) NOT NULL,
    current_level INT DEFAULT 1,
    assigned_doctor_id INT NULL,
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Saudi Arabia',
    shoulder_strength INT DEFAULT 0,
    elbow_strength INT DEFAULT 0,
    wrist_strength INT DEFAULT 0,
    grip_strength INT DEFAULT 0,
    external_rotation INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- Doctors table
-- ============================================
CREATE TABLE IF NOT EXISTS doctors (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    doctor_id VARCHAR(20) UNIQUE NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    hospital VARCHAR(200) NOT NULL,
    experience INT DEFAULT 0,
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- Messages table
-- ============================================
CREATE TABLE IF NOT EXISTS messages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);

-- ============================================
-- Game sessions table
-- ============================================
CREATE TABLE IF NOT EXISTS game_sessions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    game_type ENUM('catching-stars', 'matching-game', 'catching-objects') NOT NULL,
    level INT NOT NULL,
    score INT NOT NULL,
    duration INT NOT NULL,
    accuracy INT,
    stars_caught INT DEFAULT 0,
    matches_made INT DEFAULT 0,
    objects_caught INT DEFAULT 0,
    shoulder_activation INT DEFAULT 0,
    elbow_activation INT DEFAULT 0,
    wrist_activation INT DEFAULT 0,
    grip_activation INT DEFAULT 0,
    external_rotation INT DEFAULT 0,
    shoulder_shrug BOOLEAN DEFAULT FALSE,
    completed BOOLEAN DEFAULT TRUE,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- ============================================
-- Insert sample data (patients and doctors)
-- ============================================

-- Insert patients into users table
INSERT INTO users (name, email, password, role, phone) VALUES
('Ali Ahmed', 'ali@rehab.com', '$2a$10$NkM3QqZkXmYxLqRqLqRqLuQqRqLqRqLqRqLqRqLqRqLqRqLqRqLq', 'patient', '0501111111'),
('Sara Khaled', 'sara@rehab.com', '$2a$10$NkM3QqZkXmYxLqRqLqRqLuQqRqLqRqLqRqLqRqLqRqLqRqLqRqLq', 'patient', '0502222222'),
('Omar Hassan', 'omar@rehab.com', '$2a$10$NkM3QqZkXmYxLqRqLqRqLuQqRqLqRqLqRqLqRqLqRqLqRqLqRqLq', 'patient', '0503333333');

-- Insert patients data
INSERT INTO patients (user_id, patient_id, date_of_birth, gender, medical_condition, therapy_type) VALUES
(1, 'PT001', '2018-01-15', 'male', 'Motor Disability', 'Physical Therapy'),
(2, 'PT002', '2019-03-20', 'female', 'Arm Weakness', 'Occupational Therapy'),
(3, 'PT003', '2017-11-05', 'male', 'Movement Disorder', 'Developmental Therapy');

-- Insert doctors into users table
INSERT INTO users (name, email, password, role, phone) VALUES
('Dr. Ahmad', 'dr.ahmad@clinic.com', '$2a$10$NkM3QqZkXmYxLqRqLqRqLuQqRqLqRqLqRqLqRqLqRqLqRqLqRqLq', 'doctor', '0500000000'),
('Dr. Sarah', 'dr.sarah@clinic.com', '$2a$10$NkM3QqZkXmYxLqRqLqRqLuQqRqLqRqLqRqLqRqLqRqLqRqLqRqLq', 'doctor', '0501111111');

-- Insert doctors data
INSERT INTO doctors (user_id, doctor_id, specialty, license_number, hospital, experience) VALUES
(4, 'DR001', 'Physiotherapy', 'LIC001', 'Central Hospital', 10),
(5, 'DR002', 'Occupational Therapy', 'LIC002', 'Rehabilitation Center', 8);
