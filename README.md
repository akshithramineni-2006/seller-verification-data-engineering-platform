# Seller Verification Data Engineering Platform

> End-to-end Data Engineering project inspired by large-scale seller verification workflows. This project demonstrates data ingestion, ETL, dimensional modeling, automated data quality validation, SQL analytics, and Power BI reporting using Python and DuckDB.

---

## Project Overview

This project simulates a seller verification pipeline for an e-commerce platform.

The pipeline ingests multiple operational datasets, processes them through a Bronze–Silver–Gold architecture, builds a dimensional data warehouse, executes analytical SQL queries, and prepares business-ready datasets for Power BI dashboards.

The project was designed to demonstrate practical Data Engineering concepts including ETL pipelines, data warehousing, dimensional modeling, quality validation, and business analytics.

---

## Features

- Synthetic seller data generation using Faker
- Bronze → Silver → Gold ETL architecture
- Automated data cleaning and preprocessing
- Star schema data warehouse using DuckDB
- Dimension and Fact table modeling
- SQL-based business analytics
- Automated data quality validation
- Power BI-ready analytical datasets
- Modular Python project structure

---

## Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Data Processing | Pandas |
| Database | DuckDB |
| Storage | CSV, Parquet |
| SQL | DuckDB SQL |
| Data Generation | Faker |
| Visualization | Power BI |
| Version Control | Git & GitHub |

---

## Project Architecture

```text
                 Synthetic Data Generation
                           │
                           ▼
                    Raw CSV Files
                           │
                           ▼
                  Bronze Layer (Raw)
                           │
                           ▼
              Silver Layer (Cleaned Data)
                           │
                           ▼
            DuckDB Data Warehouse (Gold)
                           │
                           ▼
                 SQL Analytics Layer
                           │
                           ▼
                  Power BI Dashboard
```

---

## Folder Structure

```text
seller-verification-data-engineering-platform/

│
├── app/
│   ├── analytics.py
│   ├── clean.py
│   ├── config.py
│   ├── data_generator.py
│   ├── ingest.py
│   ├── quality.py
│   ├── run_pipeline.py
│   ├── warehouse.py
│   └── utils.py
│
├── dashboard/
│
├── sql/
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

---

## ETL Workflow

### Step 1 — Data Generation

Synthetic seller, verification, transaction, fraud, and login datasets are generated using Faker.

### Step 2 — Bronze Layer

Raw datasets are ingested without modification.

### Step 3 — Silver Layer

Data cleaning includes:

- Missing value handling
- Duplicate removal
- Data type corrections
- Validation checks

### Step 4 — Gold Layer

A dimensional warehouse is created using:

- Fact Table
- Country Dimension
- Business Dimension
- Date Dimension
- Verification Dimension
- Risk Dimension

### Step 5 — Analytics

Business KPIs are generated using SQL including:

- Revenue by Country
- Revenue by Business Type
- Monthly Seller Registrations
- Refund Analysis
- High Risk Sellers
- Industry Revenue

### Step 6 — Data Quality

Automated validation checks verify:

- Duplicate Seller IDs
- Missing Revenue
- Invalid Risk Scores
- Missing Verification Data
- Negative Sales

---

## Example Business Questions

The warehouse supports analytical queries such as:

- Which countries generate the highest seller revenue?
- Which industries have the highest average revenue?
- What is the monthly seller growth trend?
- Which sellers have the highest fraud risk?
- Which business type has the highest refund rate?

---

## How to Run

Clone the repository

```bash
git clone https://github.com/akshithramineni-2006/seller-verification-data-engineering-platform.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the complete pipeline

```bash
python -m app.run_pipeline
```

---

## Power BI Dashboard

The exported analytical datasets can be connected directly to Power BI to create executive dashboards showing:

- Seller KPIs
- Revenue Analysis
- Verification Status
- Fraud Insights
- Data Quality Metrics

---

## Future Improvements

- Apache Airflow orchestration
- AWS S3 integration
- Apache Spark processing
- Docker containerization
- CI/CD using GitHub Actions
- Real-time streaming using Kafka

---

## Author

**Akshith Ramineni**

B.Tech CSE (Data Science)

Manipal Institute of Technology Bengaluru