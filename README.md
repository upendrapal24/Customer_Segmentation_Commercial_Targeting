# Customer Segmentation & Commercial Targeting Matrix

> **Commercial Analytics Case Study & Machine Learning Portfolio Project**  
> **Author:** [Upendra Pal](https://github.com/upendrapal24)  
> *Domain:* Commercial Strategy, Customer Analytics, RFM Scoring, K-Means Clustering

---

## 📌 Executive Summary

In commercial and retail analytics, treating all customers uniformly results in misallocated marketing budgets, churn among premium accounts, and uncaptured lifetime value.

This project delivers an end-to-end **Customer Segmentation & Commercial Targeting Framework** built on **1,067,371 raw transaction logs** across **5,878 unique commercial customers**. By combining statistical **RFM (Recency, Frequency, Monetary) Quantile Scoring** with **Unsupervised K-Means Machine Learning**, we segment customers into actionable commercial tiers and formulate high-ROI retention strategies.

---

## 📊 Key Commercial Findings & Empirical Results

Analysis of **805,549 cleaned transactions** yielded **$17.74 Million in cumulative revenue**.

| Commercial Segment | Total Customers | Customer Share (%) | Total Revenue ($) | Revenue Share (%) | Avg. Recency (Days) | Avg. Order Freq | Avg. Customer Spend ($) | Strategic Action / Recommendation |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 🌟 **Champions (Top Tier)** | 1,300 | **22.1%** | **$12,128,115** | **68.35%** | 20.0 | 17.1 | $9,329.32 | **Executive VIP Program**: Dedicated relationship management & early product access. |
| 💎 **Loyal Customers** | 1,403 | **23.9%** | **$2,713,960** | **15.30%** | 71.4 | 5.4 | $1,934.40 | **Cross-Sell / Upsell**: Targeted cross-category product recommendations. |
| ⚠️ **At-Risk (High Value)** | 353 | **6.0%** | **$1,126,231** | **6.35%** | 344.2 | 7.6 | $3,190.46 | **High-Priority Winback**: Personal sales calls & custom incentive packages. |
| 🔍 **Need Attention** | 1,041 | **17.7%** | **$871,600** | **4.91%** | 288.5 | 2.1 | $837.27 | **Re-activation Campaigns**: Time-sensitive discount vouchers. |
| 🌱 **New / Promising** | 443 | **7.5%** | **$394,639** | **2.22%** | 28.1 | 1.5 | $890.83 | **Onboarding Series**: Welcome drip campaign to drive 2nd & 3rd orders. |
| 💤 **Hibernating / Churned** | 1,275 | **21.7%** | **$327,643** | **1.85%** | 467.8 | 1.2 | $256.98 | **Automated Emailing**: Standard low-cost marketing automation. |
| 🚨 **Can't Lose Them** | 63 | **1.1%** | **$181,241** | **1.02%** | 422.2 | 1.6 | $2,876.83 | **Executive Outreach**: High-value survey outreach & contract renewals. |

> 🔑 **Core Strategic Takeaway (Pareto Principle):** The top two segments (**Champions + Loyal Customers**) account for **45.99% of the customer base** but generate **83.65% ($14.84 Million) of total revenue**. Prioritizing 65% of retention spend on these top tiers preserves over four-fifths of enterprise value.

---

## 🛠️ Repository Architecture

```text
02_Customer_Segmentation_Commercial_Targeting/
├── README.md                          <-- Executive Summary & Commercial Strategy (Author: Upendra Pal)
├── requirements.txt                    <-- Python dependencies
├── sql/
│   └── rfm_analysis.sql                <-- CTE-based SQL queries for RFM & NTILE score calculation
├── scripts/
│   └── segmentation_pipeline.py        <-- Master Python pipeline (Data cleaning, RFM, K-Means, PCA visuals)
└── outputs/
    ├── rfm_segmented_customers.csv     <-- Clean customer dataset with RFM Scores & Cluster Labels (5,878 rows)
    ├── segment_summary_metrics.csv     <-- Empirical business metric aggregates
    └── charts/
        ├── elbow_silhouette.png        <-- K-Means Elbow Curve & Silhouette evaluation plot
        ├── kmeans_clusters_pca.png     <-- 2D PCA visual cluster separation
        └── revenue_by_segment.png      <-- Commercial revenue contribution bar plot
```

---

## 🔬 Methodology & Technical Framework

1. **Data Preprocessing & Hygiene (SQL & Python):**
   * Processed **1.06M+ records**, dropping unassigned customer IDs and non-commercial test entries.
   * Filtered transaction cancellations (`InvoiceNo` starting with 'C') and zero/negative pricing anomalies.
   * Aggregated `LineTotal = Quantity * UnitPrice`.

2. **Statistical RFM Scoring (1 to 5 Quantiles):**
   * **Recency ($R$):** Days elapsed since last invoice relative to reference date (`2011-12-10`).
   * **Frequency ($F$):** Total count of unique completed invoices per customer.
   * **Monetary ($M$):** Total cumulative monetary spend per customer.

3. **Machine Learning Clustering (K-Means & PCA):**
   * Log-transformed skewed features ($\ln(1 + x)$) and normalized via `StandardScaler`.
   * Determined $K=4$ clusters via **Elbow Method (WCSS)** & **Silhouette Scores**.
   * Projected multi-dimensional feature space onto 2D using **Principal Component Analysis (PCA)**.

---

## 💻 Code Snippets

### Advanced SQL Query (`sql/rfm_analysis.sql`)
```sql
-- Calculating RFM Quintile Scores using Window Functions
RFM_Scores AS (
    SELECT 
        CustomerID,
        Recency_Days,
        Frequency_Orders,
        Monetary_Value,
        NTILE(5) OVER (ORDER BY Recency_Days DESC) AS R_Score,
        NTILE(5) OVER (ORDER BY Frequency_Orders ASC) AS F_Score,
        NTILE(5) OVER (ORDER BY Monetary_Value ASC) AS M_Score
    FROM CustomerRFM_Raw
)
```

---

## 🚀 How to Run & Reproduce

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/upendrapal24/Customer_Segmentation_Commercial_Targeting.git
   cd Customer_Segmentation_Commercial_Targeting
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute the Complete Analytics Pipeline:**
   ```bash
   python scripts/segmentation_pipeline.py
   ```

---

### 📩 Author & Contact
* **Author:** Upendra Pal
* **GitHub:** [@upendrapal24](https://github.com/upendrapal24)
* **Project Repository:** [Customer_Segmentation_Commercial_Targeting](https://github.com/upendrapal24/Customer_Segmentation_Commercial_Targeting)
