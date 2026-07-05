# Data Discovery Report

## Overview

The source workbook contains six worksheets representing two years (2024–2025) of FMCG sales operations. An initial inspection was performed to understand the structure, identify candidate keys, assess data quality, and inform the dimensional model and ETL pipeline design.

---

## Workbook Summary

| Sheet | Rows | Columns |
|-------|-----:|--------:|
| Transactions | 3,500 | 16 |
| Products | 18 | 7 |
| Distributors | 15 | 7 |
| Salespersons | 15 | 6 |
| Monthly_Targets | 360 | 8 |
| Date_Table | 731 | 9 |

---

## Key Observations

### Transactions

- Candidate Key: `Transaction Id`
- No duplicate transaction records detected.
- `Distributor Id` contains **66 missing values (1.89%)**.
- `Notes` contains **1,504 missing values (42.97%)**.
- All numeric fields appear valid and complete.

**Observation**

The missing `Distributor Id` values are relatively few and should not result in the removal of sales records. These records should be retained during transformation, with appropriate handling during dimensional modeling.

The `Notes` column appears to be an optional free-text field and does not require imputation for analytical purposes.

---

### Products

- Candidate Keys:
  - `Product Id`
  - `Product Name`
- No missing values.
- No duplicate records.

---

### Distributors

- Candidate Keys:
  - `Distributor Id`
  - `Distributor Name`

- No missing values.
- No duplicate records.

> Although `Onboarding Date` is unique in this dataset, uniqueness alone does not make it a business key and it will not be treated as one during modeling.

---

### Salespersons

- Candidate Keys:
  - `Salesperson Id`
  - `Salesperson Name`

- No missing values.
- No duplicate records.

---

### Monthly_Targets

- Candidate Key:
  - `Record Id`

- No duplicate records.

- `Achievement Pct` contains **360 missing values (100%)**.

**Observation**

`Achievement Pct` appears to be an intentionally unpopulated derived field rather than missing source data.

It can be calculated during transformation using:

```
Achievement % = (Actual Revenue / Target Revenue) × 100
```

rather than treating the values as data quality issues.

---

### Date_Table

- Candidate Key:
  - `Date`

- No missing values.
- No duplicate records.

This table already represents a complete calendar dimension and can be reused directly as the Date Dimension.

---

# Data Quality Summary

| Issue | Impact | Planned Handling |
|--------|--------|------------------|
| Missing Distributor Id | Low | Preserve transaction and handle appropriately during modeling |
| Missing Notes | Low | Leave as NULL |
| Missing Achievement Pct | Expected | Calculate during transformation |
| Duplicate Records | None detected | No action required |

---

# Initial Modeling Assumptions

Based on the inspection, the dataset naturally lends itself to a dimensional (star) schema.

Expected dimensions include:

- Product
- Distributor
- Salesperson
- Date

The Transactions worksheet is expected to become the primary fact table, while Monthly_Targets will likely serve as a second fact table for performance analysis.

Further validation will be performed during the modeling phase before implementing the ETL pipeline.
