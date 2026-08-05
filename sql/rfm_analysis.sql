-- =========================================================================================
-- CUSTOMER SEGMENTATION & RFM ANALYSIS (COMMERCIAL TARGETING MATRIX)
-- SQL Script for Data Extraction, Aggregation, and RFM Score Calculation
-- Target Audience: Commercial Analytics Teams (ZS Associates, DecisionTree, Accenture)
-- =========================================================================================

-- 1. Data Cleaning & Transaction Aggregation CTE
WITH CleanTransactions AS (
    SELECT 
        Invoice AS InvoiceNo,
        `Customer ID` AS CustomerID,
        InvoiceDate,
        Price * Quantity AS LineTotal,
        Quantity,
        Price
    FROM raw_online_retail
    WHERE `Customer ID` IS NOT NULL
      AND `Customer ID` != ''
      AND Quantity > 0
      AND Price > 0
      AND Invoice NOT LIKE 'C%' -- Exclude Cancellations
),

-- 2. Reference Date & Raw RFM Metrics Calculation per Customer
CustomerRFM_Raw AS (
    SELECT 
        CustomerID,
        -- Reference Date set to 1 day after max invoice date in dataset
        DATEDIFF('2011-12-10', MAX(InvoiceDate)) AS Recency_Days,
        COUNT(DISTINCT InvoiceNo) AS Frequency_Orders,
        ROUND(SUM(LineTotal), 2) AS Monetary_Value,
        MIN(InvoiceDate) AS First_Purchase_Date,
        MAX(InvoiceDate) AS Last_Purchase_Date
    FROM CleanTransactions
    GROUP BY CustomerID
),

-- 3. NTILE Window Ranking for RFM Quintile Scores (1 to 5)
RFM_Scores AS (
    SELECT 
        CustomerID,
        Recency_Days,
        Frequency_Orders,
        Monetary_Value,
        -- Recency: Lower days = Higher Score (5 is best)
        NTILE(5) OVER (ORDER BY Recency_Days DESC) AS R_Score,
        -- Frequency: Higher orders = Higher Score (5 is best)
        NTILE(5) OVER (ORDER BY Frequency_Orders ASC) AS F_Score,
        -- Monetary: Higher spend = Higher Score (5 is best)
        NTILE(5) OVER (ORDER BY Monetary_Value ASC) AS M_Score
    FROM CustomerRFM_Raw
),

-- 4. Concatenation and Rule-Based Business Segmentation
RFM_Segments AS (
    SELECT 
        CustomerID,
        Recency_Days,
        Frequency_Orders,
        Monetary_Value,
        R_Score,
        F_Score,
        M_Score,
        CONCAT(CAST(R_Score AS CHAR), CAST(F_Score AS CHAR), CAST(M_Score AS CHAR)) AS RFM_Cell,
        ROUND((R_Score + F_Score + M_Score) / 3.0, 2) AS Avg_RFM_Score,
        CASE 
            WHEN R_Score >= 4 AND F_Score >= 4 AND M_Score >= 4 THEN 'Champions (Top Tier)'
            WHEN R_Score >= 3 AND F_Score >= 3 AND M_Score >= 3 THEN 'Loyal Customers'
            WHEN R_Score >= 4 AND F_Score <= 2 THEN 'Promising / New Customers'
            WHEN R_Score <= 2 AND F_Score >= 4 AND M_Score >= 4 THEN 'At-Risk (High Value Churn)'
            WHEN R_Score <= 2 AND F_Score <= 2 AND M_Score >= 4 THEN 'Cant Lose Them (Big Spenders)'
            WHEN R_Score <= 2 AND F_Score <= 2 AND M_Score <= 2 THEN 'Hibernating / Churned'
            ELSE 'Need Attention / Moderate'
        END AS Commercial_Segment
    FROM RFM_Scores
)

-- 5. Final Output: Segment Breakdown & Revenue Contribution
SELECT 
    Commercial_Segment,
    COUNT(CustomerID) AS Total_Customers,
    ROUND(COUNT(CustomerID) * 100.0 / SUM(COUNT(CustomerID)) OVER(), 2) AS Customer_Pct,
    ROUND(SUM(Monetary_Value), 2) AS Total_Revenue,
    ROUND(SUM(Monetary_Value) * 100.0 / SUM(SUM(Monetary_Value)) OVER(), 2) AS Revenue_Pct,
    ROUND(AVG(Recency_Days), 1) AS Avg_Recency_Days,
    ROUND(AVG(Frequency_Orders), 1) AS Avg_Frequency_Orders,
    ROUND(AVG(Monetary_Value), 2) AS Avg_Customer_Value
FROM RFM_Segments
GROUP BY Commercial_Segment
ORDER BY Total_Revenue DESC;
