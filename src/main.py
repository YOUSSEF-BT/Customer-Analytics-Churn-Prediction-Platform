import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Charger le dataset depuis le dossier datatelco
data = pd.read_csv("datatelco/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Aperçu des données
print(data.head())
print(data.info())
print(data.describe())

# Conversion TotalCharges en numérique
data['TotalCharges'] = pd.to_numeric(data['TotalCharges'], errors='coerce')

# Vérifier les valeurs manquantes
print("\nValeurs manquantes :")
print(data.isnull().sum())

# Supprimer les lignes avec valeurs manquantes
data = data.dropna()

print("\nDonnées après nettoyage :", data.shape)

# Répartition du churn
print("\nRépartition Churn :")
print(data['Churn'].value_counts())

# Type de contrat
print("\nTypes de contrat :")
print(data['Contract'].value_counts())

# Services Internet
print("\nInternet Services :")
print(data['InternetService'].value_counts())

# Visualisations
# Churn distribution
plt.figure()
sns.countplot(x='Churn', data=data)
plt.title("Répartition du Churn")
plt.show()

# Tenure distribution
plt.figure()
sns.histplot(data['tenure'], bins=30)
plt.title("Distribution de l'ancienneté (tenure)")
plt.show()

# MonthlyCharges vs Churn
plt.figure()
sns.boxplot(x='Churn', y='MonthlyCharges', data=data)
plt.title("Monthly Charges vs Churn")
plt.show()

# Encodage
X = data.drop(columns=['customerID', 'Churn'])
y = data['Churn'].map({'Yes': 1, 'No': 0})

X = pd.get_dummies(X)

print("Shape X :", X.shape)
print("Shape y :", y.shape)

# ------------------------------
# XGBoost pour prédiction Churn
# ------------------------------
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

model = XGBClassifier(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss',
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\nAccuracy (XGBoost) :", accuracy_score(y_test, y_pred))
print("\nRapport de classification :\n", classification_report(y_test, y_pred))

# Matrice de confusion
cm = confusion_matrix(y_test, y_pred)
plt.figure()
sns.heatmap(cm, annot=True, fmt="d")
plt.title("Matrice de Confusion")
plt.xlabel("Prédit")
plt.ylabel("Réel")
plt.show()

# AUC
auc = roc_auc_score(y_test, y_proba)
print("AUC :", auc)

# ------------------------------
# Nouvelles features utiles
# ------------------------------
data['AvgChargesPerMonth'] = data['TotalCharges'] / (data['tenure'] + 1)
data['IsLongTermCustomer'] = data['tenure'].apply(lambda x: 1 if x > 24 else 0)

print(data[['AvgChargesPerMonth', 'IsLongTermCustomer']].head())

# ------------------------------
# Feature importance
# ------------------------------
importances = model.feature_importances_
features = X.columns

imp_df = pd.DataFrame({
    'Feature': features,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print(imp_df.head(10))
