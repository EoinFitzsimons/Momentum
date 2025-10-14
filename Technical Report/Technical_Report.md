# National College of Ireland
**BSc (Honours) in Computing**  
**Software Development**  
**Academic Year 2024/2025**  

**Student Name:** Eoin Fitzsimons  
**Student Number:** [Your Student Number]  
**Student Email:** [Your Email]

**Project Title:** Momentum - Multi-Discipline Motorsport Simulation System

**Technical Report**

---

## Contents

1. [Executive Summary](#executive-summary)
2. [Introduction](#1-introduction)
   - 1.1 [Background](#11-background)
   - 1.2 [Aims](#12-aims)
   - 1.3 [Technology](#13-technology)
   - 1.4 [Structure](#14-structure)
3. [System](#2-system)
   - 2.1 [Requirements](#21-requirements)
   - 2.2 [Design & Architecture](#22-design--architecture)
   - 2.3 [Implementation](#23-implementation)
   - 2.4 [Testing](#24-testing)
   - 2.5 [Evaluation](#25-evaluation)
4. [Conclusions](#3-conclusions)
5. [Further Development](#4-further-development)
6. [References](#5-references)
7. [Appendices](#6-appendices)

---

## Executive Summary

**Momentum** is a comprehensive multi-discipline motorsport management simulation system developed as a final year Computer Science project. The system implements seven complete racing disciplines (Single Seater, Production/Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, and Endurance) with realistic simulation mechanics based on Monte Carlo statistical methods.

The project addresses the challenge of creating an engaging and realistic motorsport management game that balances complexity with accessibility. Unlike existing motorsport games that focus on a single discipline, Momentum provides a unified platform supporting multiple racing categories with cross-discipline driver and team management.

Key achievements include:
- **50+ driver attributes** across 7 categories with dynamic career progression
- **40+ staff attributes** across 25+ roles with budget-based team scaling
- **Multi-currency financial system** with real-time exchange rates supporting EUR, USD, GBP, JPY, and CHF
- **Seven complete racing engines** each with discipline-specific simulation logic
- **Monte Carlo simulation engine** generating statistically authentic race outcomes
- **AI decision-making framework** for realistic team and driver behaviors
- **RESTful API architecture** enabling frontend integration and scalability

The system successfully demonstrates advanced software engineering principles including object-oriented design, database normalization, API development, and statistical simulation. Performance testing shows sub-second race simulation times with realistic result distributions. The modular architecture enables easy expansion to additional disciplines or gameplay features.

---

## 1. Introduction

### 1.1 Background

Motorsport management simulation games have been a niche but dedicated gaming genre since the 1990s. However, most existing games focus on a single discipline (usually Formula 1) or lack the depth required for authentic simulation. Games like *Football Manager* have shown that deep statistical simulation can create compelling gameplay, but motorsport has remained underserved.

This project was undertaken to create a modern, multi-discipline motorsport simulation that:
1. **Supports multiple racing disciplines** rather than forcing players into a single category
2. **Uses realistic statistical modeling** based on real motorsport data and driver attributes
3. **Implements comprehensive team management** including staff, budgets, and development
4. **Provides an API-first architecture** enabling multiple frontend implementations (Unity, Web, Mobile)
5. **Demonstrates advanced computer science concepts** including Monte Carlo simulation, AI decision-making, and distributed architecture

The motivation stemmed from both personal interest in motorsport and the technical challenge of building a complex simulation system that balances realism with performance.

### 1.2 Aims

The primary objectives of the Momentum project are:

**Technical Objectives:**
1. Design and implement a **multi-discipline racing simulation engine** using Monte Carlo methods
2. Create a **comprehensive data model** supporting 50+ driver attributes and 40+ staff attributes
3. Develop **seven discipline-specific racing engines** with unique simulation characteristics
4. Implement a **RESTful API** for frontend integration and external system access
5. Build a **multi-currency financial system** with real-time exchange rate support
6. Create an **AI decision-making framework** for autonomous team and driver behaviors

**Simulation Quality Objectives:**
1. Generate **statistically realistic race results** with appropriate variance and upset potential
2. Model **cross-discipline driver compatibility** reflecting real-world skill transferability
3. Implement **budget-based team scaling** affecting performance and information access
4. Create **fog-of-war information systems** where data quality depends on staff capabilities

**Software Engineering Objectives:**
1. Apply **object-oriented design patterns** for maintainable and extensible code
2. Implement **database normalization** for data integrity and performance
3. Create **comprehensive unit and integration tests** ensuring system reliability
4. Document code with **clear API specifications** and usage examples

### 1.3 Technology

The Momentum system is built using the following technology stack:

**Backend (Python 3.8+):**
- **FastAPI**: Modern, high-performance web framework for building RESTful APIs
  - Automatic OpenAPI documentation generation
  - Asynchronous request handling for scalability
  - Built-in data validation using Pydantic models
  
- **SQLite**: Embedded relational database for persistent storage
  - Zero-configuration deployment
  - ACID compliance for data integrity
  - Foreign key constraints for referential integrity
  
- **NumPy & SciPy**: Scientific computing libraries for statistical simulation
  - Monte Carlo random sampling
  - Statistical distribution calculations
  - Performance optimization for numerical operations
  
- **PyTorch**: Machine learning framework for AI decision-making
  - Neural network models for strategy prediction
  - Gradient-based optimization
  - Future expansion for deep learning features

**Data Generation:**
- **Faker Library**: Generates culturally-appropriate names with locale support
- **Custom name generation system** with ethnic/regional distributions
- **Multi-currency exchange rate APIs** for real-time financial data

**Development Tools:**
- **Git/GitHub**: Version control and collaboration
- **VS Code**: Primary development environment
- **Uvicorn**: ASGI server for running FastAPI applications
- **Python-dotenv**: Environment variable management for API keys

**Architecture Approach:**
The system follows a **layered architecture** pattern:
1. **API Layer**: FastAPI endpoints handling HTTP requests/responses
2. **Business Logic Layer**: Simulation engines, AI systems, and management modules
3. **Data Access Layer**: Database models and repository patterns
4. **Data Layer**: SQLite database with normalized schema

This separation enables:
- Independent testing of each layer
- Easy replacement of components (e.g., switching databases)
- Clear separation of concerns
- Scalability through horizontal scaling of API servers

### 1.4 Structure

This technical report is organized as follows:

**Section 2 - System**: Provides comprehensive documentation of the system including requirements analysis, design decisions, implementation details, and testing procedures. This section is divided into:
- **Requirements (2.1)**: Functional, data, user, environmental, and usability requirements
- **Design & Architecture (2.2)**: System architecture, component design, and algorithm descriptions
- **Implementation (2.3)**: Key code modules, algorithms, and implementation challenges
- **Testing (2.4)**: Test strategy, test cases, and validation results
- **Evaluation (2.5)**: Performance analysis, user feedback, and system assessment

**Section 3 - Conclusions**: Summarizes the project outcomes, identifies strengths and limitations, and reflects on lessons learned.

**Section 4 - Further Development**: Outlines potential future enhancements and research directions.

**Section 5 - References**: Lists all academic papers, technical documentation, and resources used.

**Section 6 - Appendices**: Contains supplementary materials including project proposal, reflective journals, code samples, and test data.

---

