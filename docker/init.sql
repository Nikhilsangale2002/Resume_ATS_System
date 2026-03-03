-- ATS System Database Initialization
-- MySQL 8.0

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS ats_system;
USE ats_system;

-- Create skill_aliases table
CREATE TABLE IF NOT EXISTS skill_aliases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alias_name VARCHAR(100) NOT NULL UNIQUE,
    standard_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed skill aliases
INSERT INTO skill_aliases (alias_name, standard_name, category) VALUES
('node', 'Node.js', 'backend'),
('nodejs', 'Node.js', 'backend'),
('node.js', 'Node.js', 'backend'),
('node js', 'Node.js', 'backend'),
('react', 'React.js', 'frontend'),
('reactjs', 'React.js', 'frontend'),
('react.js', 'React.js', 'frontend'),
('vue', 'Vue.js', 'frontend'),
('vuejs', 'Vue.js', 'frontend'),
('angular', 'Angular', 'frontend'),
('angularjs', 'AngularJS', 'frontend'),
('python', 'Python', 'backend'),
('py', 'Python', 'backend'),
('python3', 'Python', 'backend'),
('javascript', 'JavaScript', 'frontend'),
('js', 'JavaScript', 'frontend'),
('typescript', 'TypeScript', 'frontend'),
('ts', 'TypeScript', 'frontend'),
('postgres', 'PostgreSQL', 'database'),
('postgresql', 'PostgreSQL', 'database'),
('mysql', 'MySQL', 'database'),
('mongo', 'MongoDB', 'database'),
('mongodb', 'MongoDB', 'database'),
('redis', 'Redis', 'database'),
('docker', 'Docker', 'devops'),
('k8s', 'Kubernetes', 'devops'),
('kubernetes', 'Kubernetes', 'devops'),
('aws', 'AWS', 'cloud'),
('amazon web services', 'AWS', 'cloud'),
('gcp', 'Google Cloud Platform', 'cloud'),
('azure', 'Microsoft Azure', 'cloud'),
('git', 'Git', 'other'),
('github', 'GitHub', 'other'),
('gitlab', 'GitLab', 'other'),
('ci/cd', 'CI/CD', 'devops'),
('cicd', 'CI/CD', 'devops'),
('html', 'HTML', 'frontend'),
('html5', 'HTML5', 'frontend'),
('css', 'CSS', 'frontend'),
('css3', 'CSS3', 'frontend'),
('tailwind', 'Tailwind CSS', 'frontend'),
('tailwindcss', 'Tailwind CSS', 'frontend'),
('sass', 'SASS/SCSS', 'frontend'),
('scss', 'SASS/SCSS', 'frontend'),
('graphql', 'GraphQL', 'backend'),
('rest', 'REST API', 'backend'),
('restful', 'REST API', 'backend'),
('fastapi', 'FastAPI', 'backend'),
('flask', 'Flask', 'backend'),
('django', 'Django', 'backend'),
('express', 'Express.js', 'backend'),
('expressjs', 'Express.js', 'backend'),
('spring', 'Spring Boot', 'backend'),
('springboot', 'Spring Boot', 'backend')
ON DUPLICATE KEY UPDATE standard_name = VALUES(standard_name);
