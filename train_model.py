import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# Charger dataset
data = pd.read_csv("datatelco/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Nettoyage
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')
data = data.dropna()

# Feature engineering
data['AvgChargesPerMonth'] = data['TotalCharges'] / (data['tenure'] + 1)
data['IsLongTermCustomer'] = data['tenure'].apply(lambda x: 1 if x > 24 else 0)

# Encodage
X = data.drop(columns=['customerID', 'Churn'])
y = data['Churn'].map({'Yes': 1, 'No': 0})
X = pd.get_dummies(X)

# Train / Test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modèle XGBoost
model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

model.fit(X_train, y_train)

# Sauvegarde
joblib.dump(model, "model_churn_xgboost.pkl")
joblib.dump(X_train.columns.tolist(), "model_features.pkl")

print("✅ Modèle et features sauvegardés avec succès !")
