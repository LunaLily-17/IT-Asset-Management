# IT Asset Management System

## 1. Project Overview

The **IT Asset Management System** is a software product based on Python language and developed with FastAPI framework for asset management, asset assignment to employees, system administration and auditing purposes.

The application divides its functionalities in order to facilitate its code organization, maintainability and testing.

For the current project implementation, data is stored using in-memory Python data structures instead of a database.

## 2. Technologies Used

- **Programming Language:** Python
- **Backend Framework:** FastAPI
- **Data Validation:** Pydantic
- **Development Environment:** PyCharm
- **API Documentation and Testing:** Swagger UI
- **Data Storage:** In-memory dictionaries and lists
- **Version Control:** Git and GitHub

## 3. User Roles and Responsibilities

The system works with four user roles.

| User Role | Assigned Team Member | Responsibilities |
|---|---|---|
| Asset Manager | Win | Manage IT asset records, assign, return assets, lifecycle information and asset disposition. |
| Employee | Franklin | View assigned assets, acknowledge asset assignment, provide information concerning asset returns. |
| Auditor | Rohit | Review asset records, comply with the compliance requirements, identify discrepancies and prepare audits. |
| System Administrator | Tino | Manage system configurations, user roles, and administration.
