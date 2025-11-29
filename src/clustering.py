import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

data = pd.read_csv("datatelco/WA_Fn-UseC_-Telco-Customer-Churn.csv")

data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
data = data.dropna()

X = data[['tenure', 'MonthlyCharges', 'TotalCharges']]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=4, random_state=42)
clusters = kmeans.fit_predict(X_scaled)

data['Cluster'] = clusters

print(data[['tenure','MonthlyCharges','Cluster']].head())

# Visualisation
plt.figure()
plt.scatter(data['tenure'], data['MonthlyCharges'], c=data['Cluster'])
plt.xlabel("Tenure")
plt.ylabel("Monthly Charges")
plt.title("Segmentation Clients")
plt.show()
