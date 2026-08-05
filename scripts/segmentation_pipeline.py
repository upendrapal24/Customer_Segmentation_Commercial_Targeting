import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

# Set styling for publication-ready charts
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.family': 'sans-serif', 'figure.dpi': 300})

def load_data(data_dir):
    """Load and combine retail datasets."""
    print("--> Loading dataset files...")
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    xlsx_files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]
    
    df_list = []
    if csv_files:
        for f in csv_files:
            file_path = os.path.join(data_dir, f)
            print(f"    Reading CSV: {f}")
            df_temp = pd.read_csv(file_path, encoding='unicode_escape')
            df_list.append(df_temp)
    elif xlsx_files:
        excel_path = os.path.join(data_dir, xlsx_files[0])
        print(f"    Reading Excel: {xlsx_files[0]}")
        xls = pd.ExcelFile(excel_path)
        for sheet_name in xls.sheet_names:
            print(f"    Reading sheet: {sheet_name}")
            df_temp = pd.read_excel(xls, sheet_name=sheet_name)
            df_list.append(df_temp)
    else:
        raise FileNotFoundError(f"No CSV or XLSX files found in {data_dir}")
        
    df = pd.concat(df_list, ignore_index=True)
    print(f"--> Combined Raw Data Shape: {df.shape}")
    return df

def preprocess_data(df):
    """Clean dataset by removing missing IDs, cancellations, and invalid prices."""
    print("--> Preprocessing raw data...")
    # Standardize column names
    col_map = {
        'Invoice': 'InvoiceNo', 'InvoiceNo': 'InvoiceNo',
        'Customer ID': 'CustomerID', 'CustomerID': 'CustomerID',
        'Price': 'UnitPrice', 'UnitPrice': 'UnitPrice',
        'InvoiceDate': 'InvoiceDate'
    }
    df = df.rename(columns=col_map)
    
    # Drop rows without CustomerID
    df = df.dropna(subset=['CustomerID'])
    df['CustomerID'] = df['CustomerID'].astype(int).astype(str)
    
    # Filter valid non-cancelled orders with positive quantity and unit price
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    df = df[~df['InvoiceNo'].str.startswith('C')]
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # Calculate Line Total
    df['LineTotal'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    print(f"--> Cleaned Data Shape: {df.shape} ({df['CustomerID'].nunique()} unique customers)")
    return df

def calculate_rfm(df):
    """Compute Recency, Frequency, and Monetary metrics per customer."""
    print("--> Computing RFM metrics...")
    reference_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda dates: (reference_date - dates.max()).days,
        'InvoiceNo': 'nunique',
        'LineTotal': 'sum'
    }).reset_index()
    
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
    rfm['Monetary'] = rfm['Monetary'].round(2)
    
    # Filter monetary > 0
    rfm = rfm[rfm['Monetary'] > 0]
    
    # Assign RFM Scores (1-5) using quantile binning
    rfm['R_Score'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    rfm['RFM_Sum'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
    
    # Define Rule-Based Commercial Segments
    def segment_customer(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions (Top Tier)'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'New / Promising'
        elif r <= 2 and f >= 4:
            return 'At Risk (High Frequency)'
        elif r <= 2 and f <= 2 and m >= 4:
            return 'Cant Lose Them (High Spend)'
        elif r <= 2 and f <= 2 and m <= 2:
            return 'Hibernating / Churned'
        else:
            return 'Need Attention'

    rfm['Rule_Segment'] = rfm.apply(segment_customer, axis=1)
    print(f"--> RFM Calculation complete for {len(rfm)} customers.")
    return rfm

def run_kmeans(rfm, output_charts_dir):
    """Log-transform, scale, and run K-Means clustering + PCA visualization."""
    print("--> Running K-Means Machine Learning Clustering...")
    rfm_features = rfm[['Recency', 'Frequency', 'Monetary']].copy()
    
    # Log transformation to reduce right skewness
    rfm_log = np.log1p(rfm_features)
    
    # StandardScaler
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)
    
    # Evaluate Elbow & Silhouette
    wcss = []
    silhouette_scores = []
    k_range = range(2, 9)
    
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(rfm_scaled)
        wcss.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(rfm_scaled, kmeans.labels_))
        
    # Plot Elbow & Silhouette
    fig, ax1 = plt.subplots(figsize=(8, 4))
    color = 'tab:blue'
    ax1.set_xlabel('Number of Clusters (K)')
    ax1.set_ylabel('Inertia (WCSS)', color=color)
    ax1.plot(k_range, wcss, marker='o', color=color, linewidth=2)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Silhouette Score', color=color)
    ax2.plot(k_range, silhouette_scores, marker='s', color=color, linestyle='--', linewidth=2)
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title('K-Means Evaluation: Elbow Curve & Silhouette Analysis', fontsize=12, fontweight='bold', pad=10)
    plt.tight_layout()
    plt.savefig(os.path.join(output_charts_dir, 'elbow_silhouette.png'), dpi=300)
    plt.close()
    
    # Select K=4 optimal clusters
    optimal_k = 4
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    rfm['KMeans_Cluster'] = kmeans.fit_predict(rfm_scaled)
    
    # PCA 2D Visualization
    pca = PCA(n_components=2)
    pca_coords = pca.fit_transform(rfm_scaled)
    rfm['PCA1'] = pca_coords[:, 0]
    rfm['PCA2'] = pca_coords[:, 1]
    
    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        x='PCA1', y='PCA2', hue='KMeans_Cluster', data=rfm, 
        palette='Set1', alpha=0.7, s=50
    )
    plt.title(f'K-Means Customer Clusters (2D PCA Projection, K={optimal_k})', fontsize=12, fontweight='bold')
    plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]*100:.1f}% Variance)')
    plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]*100:.1f}% Variance)')
    plt.legend(title='Cluster ID', loc='best')
    plt.tight_layout()
    plt.savefig(os.path.join(output_charts_dir, 'kmeans_clusters_pca.png'), dpi=300)
    plt.close()
    
    print(f"--> K-Means (K={optimal_k}) completed successfully.")
    return rfm

def generate_business_reports(rfm, output_dir, output_charts_dir):
    """Generate business summary metrics and revenue contribution charts."""
    print("--> Generating Commercial Strategy Reports and Visuals...")
    
    # Segment Summary Table
    summary = rfm.groupby('Rule_Segment').agg(
        Total_Customers=('CustomerID', 'count'),
        Total_Revenue=('Monetary', 'sum'),
        Avg_Recency_Days=('Recency', 'mean'),
        Avg_Order_Frequency=('Frequency', 'mean'),
        Avg_Spend_Per_Customer=('Monetary', 'mean')
    ).reset_index()
    
    total_revenue_all = rfm['Monetary'].sum()
    total_cust_all = len(rfm)
    
    summary['Customer_Share_%'] = (summary['Total_Customers'] / total_cust_all * 100).round(2)
    summary['Revenue_Share_%'] = (summary['Total_Revenue'] / total_revenue_all * 100).round(2)
    summary['Total_Revenue'] = summary['Total_Revenue'].round(2)
    summary['Avg_Recency_Days'] = summary['Avg_Recency_Days'].round(1)
    summary['Avg_Order_Frequency'] = summary['Avg_Order_Frequency'].round(1)
    summary['Avg_Spend_Per_Customer'] = summary['Avg_Spend_Per_Customer'].round(2)
    
    summary = summary.sort_values(by='Total_Revenue', ascending=False)
    summary.to_csv(os.path.join(output_dir, 'segment_summary_metrics.csv'), index=False)
    rfm.to_csv(os.path.join(output_dir, 'rfm_segmented_customers.csv'), index=False)
    
    # Revenue Contribution Bar Chart
    plt.figure(figsize=(10, 5))
    ax = sns.barplot(
        x='Revenue_Share_%', y='Rule_Segment', data=summary, palette='Blues_r'
    )
    plt.title('Commercial Segment Revenue Contribution (%)', fontsize=12, fontweight='bold')
    plt.xlabel('Percentage of Total Revenue (%)')
    plt.ylabel('Commercial Customer Segment')
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f'{width:.1f}%', 
                    (width + 0.5, p.get_y() + p.get_height() / 2.),
                    ha='left', va='center', fontsize=10, color='black')
                    
    plt.tight_layout()
    plt.savefig(os.path.join(output_charts_dir, 'revenue_by_segment.png'), dpi=300)
    plt.close()
    
    print(f"--> Saved output files to {output_dir}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(os.path.dirname(base_dir), "data set")
    output_dir = os.path.join(base_dir, "outputs")
    output_charts_dir = os.path.join(output_dir, "charts")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_charts_dir, exist_ok=True)
    
    df_raw = load_data(data_dir)
    df_clean = preprocess_data(df_raw)
    rfm = calculate_rfm(df_clean)
    rfm_clustered = run_kmeans(rfm, output_charts_dir)
    generate_business_reports(rfm_clustered, output_dir, output_charts_dir)
    
    print("\n=======================================================")
    print(" SUCCESS: Customer Segmentation Pipeline Executed!")
    print("=======================================================\n")

if __name__ == '__main__':
    main()
