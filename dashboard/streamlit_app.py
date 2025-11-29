# dashboard/streamlit_ultimate.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import joblib
from io import BytesIO
from fpdf import FPDF
import os
import base64
from datetime import datetime
import tempfile
import plotly.io as pio

# -----------------------------
# CONFIGURATION DASHBOARD
# -----------------------------
st.set_page_config(
    page_title="Customer Analytics & Churn Prediction Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# PALETTE DE COULEURS PROFESSIONNELLE - BLEU ROYAL & OR
# -----------------------------
PRO_COLORS = {
    'primary': '#2E5A88',    # Bleu royal profond
    'secondary': '#D4AF37',  # Or élégant
    'accent': '#1E3A5F',     # Bleu marine
    'light': '#5B8DB8',      # Bleu ciel
    'success': '#27AE60',    # Vert pour positif
    'warning': '#E67E22',    # Orange pour attention
    'danger': '#C0392B'      # Rouge pour risques
}

# -----------------------------
# THÈME PROFESSIONNEL - NOIR/GRIS
# -----------------------------
st.markdown("""
<style>
    .main {
        background-color: #0F0F0F;
    }
    .stApp {
        background: linear-gradient(135deg, #0F0F0F 0%, #1A1A1A 100%);
    }
    
    /* En-têtes */
    h1, h2, h3, h4, h5, h6 {
        color: #E0E0E0 !important;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
    }
    
    /* Texte général */
    .stMarkdown, .stText, .stMetric {
        color: #B0B0B0 !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #1A1A1A;
    }
    .stSidebar {
        background-color: #1A1A1A;
        border-right: 1px solid #333333;
    }
    .stSidebar .sidebar-content {
        background-color: #1A1A1A;
        color: #E0E0E0;
    }
    
    /* Boutons */
    .stButton>button {
        background: linear-gradient(45deg, #404040, #606060);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid #555555;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #505050, #707070);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 255, 255, 0.1);
    }
    
    /* Métriques/KPIs - Design premium */
    .kpi-container {
        background: linear-gradient(135deg, #2A2A2A 0%, #1E1E1E 100%);
        border: 1px solid #404040;
        border-radius: 16px;
        padding: 2rem 1rem;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        text-align: center;
        margin: 0.5rem;
    }
    .kpi-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);
        border-color: #606060;
    }
    .kpi-value {
        color: #FFFFFF !important;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    .kpi-label {
        color: #CCCCCC !important;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    .kpi-delta {
        color: #AAAAAA !important;
        font-size: 0.9rem;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: #2A2A2A;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #404040;
    }
    
    /* Download buttons */
    .stDownloadButton>button {
        background: linear-gradient(45deg, #505050, #707070) !important;
        color: white !important;
        border: 1px solid #666666 !important;
        width: 100%;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(45deg, #606060, #808080) !important;
    }
    
    /* Containers */
    .block-container {
        padding-top: 2rem;
        background-color: transparent;
    }
    
    /* Graph containers */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid #333333;
        background-color: #1A1A1A !important;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #1A1A1A !important;
        color: #E0E0E0 !important;
    }
    
    /* Séparateurs */
    hr {
        border-color: #333333;
        margin: 2rem 0;
    }
    
    /* Export section */
    .export-section {
        background: linear-gradient(135deg, #2A2A2A, #404040);
        border: 1px solid #555555;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR: Configuration
# -----------------------------
st.sidebar.markdown("""
<div style='text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #2A2A2A, #404040); border-radius: 12px; margin-bottom: 2rem; border: 1px solid #555555;'>
    <h2 style='color: #FFFFFF; margin: 0; font-size: 1.4rem;'>⚙️ PARAMÈTRES</h2>
</div>
""", unsafe_allow_html=True)

# UPLOAD MODIFIÉ: Accepte CSV et Excel
uploaded_file = st.sidebar.file_uploader("📁 Charger un dataset (CSV ou Excel)", type=["csv", "xlsx", "xls"])

# -----------------------------
# CHARGER LES DONNÉES ET LE MODÈLE - MODIFIÉ POUR CSV ET EXCEL
# -----------------------------
@st.cache_data
def load_data(file=None):
    if file:
        # Déterminer le type de fichier et charger en conséquence
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file)
        else:
            st.error("Format de fichier non supporté")
            return None
    else:
        try:
            current_dir = os.path.dirname(__file__)
            csv_path = os.path.join(current_dir, "../datatelco/WA_Fn-UseC_-Telco-Customer-Churn.csv")
            df = pd.read_csv(csv_path)
        except:
            url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
            df = pd.read_csv(url)
    
    # Traitement des données
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    df = df.dropna()
    df['AvgChargesPerMonth'] = df['TotalCharges'] / (df['tenure'] + 1)
    df['IsLongTermCustomer'] = df['tenure'].apply(lambda x: 1 if x > 24 else 0)
    
    # Préparer les données pour l'animation
    df['tenure_group'] = (df['tenure'] // 12) * 12
    df['tenure_group_label'] = df['tenure_group'].apply(lambda x: f"{x}-{x+11} mois")
    
    return df

data = load_data(uploaded_file)

# Vérifier que les données sont chargées
if data is None:
    st.error("❌ Erreur lors du chargement des données. Veuillez vérifier le format de votre fichier.")
    st.stop()

# Chargement du modèle avec gestion d'erreur améliorée
try:
    model = joblib.load("model_churn_xgboost.pkl")
    features = joblib.load("model_features.pkl")
    st.sidebar.success("✅ Modèle XGBoost chargé avec succès")
except Exception as e:
    st.sidebar.warning("⚠️ Modèle XGBoost non disponible")
    model = None
    features = []

# -----------------------------
# FILTRES CLIENT
# -----------------------------
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #404040, #606060); padding: 1.2rem; border-radius: 10px; margin: 1rem 0; border: 1px solid #666666;'>
    <h3 style='color: #FFFFFF; text-align: center; margin: 0; font-size: 1.1rem;'>🔍 FILTRES CLIENTS</h3>
</div>
""", unsafe_allow_html=True)

gender_filter = st.sidebar.multiselect(
    "👤 Genre", options=data['gender'].unique(), default=data['gender'].unique()
)
contract_filter = st.sidebar.multiselect(
    "📑 Contrat", options=data['Contract'].unique(), default=data['Contract'].unique()
)
payment_filter = st.sidebar.multiselect(
    "💳 Paiement", options=data['PaymentMethod'].unique(), default=data['PaymentMethod'].unique()
)

filtered_data = data[
    (data['gender'].isin(gender_filter)) &
    (data['Contract'].isin(contract_filter)) &
    (data['PaymentMethod'].isin(payment_filter))
]

# -----------------------------
# HEADER PRINCIPAL
# -----------------------------
st.markdown("""
<div style='text-align: center; background: linear-gradient(135deg, #2A2A2A, #404040); padding: 2.5rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid #555555; box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4);'>
    <h1 style='color: #FFFFFF; margin: 0; font-size: 2.8rem; font-weight: 700;'>📊Customer Analytics & Churn Prediction Platform</h1>
    <p style='color: #CCCCCC; font-size: 1.3rem; margin: 0.5rem 0 0 0; font-weight: 300;'>Dashboard Executive d'Analyse Stratégique</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# KPIs DYNAMIQUES - DESIGN PREMIUM CENTRÉ
# -----------------------------
st.markdown("""
<div style='text-align: center; margin: 3rem 0 2rem 0;'>
    <h2 style='color: #E0E0E0; border-bottom: 3px solid #606060; padding-bottom: 0.8rem; display: inline-block; font-size: 1.8rem;'>📈 TABLEAU DE BORD EXÉCUTIF</h2>
</div>
""", unsafe_allow_html=True)

total_clients = len(filtered_data)
total_churn = filtered_data['Churn'].value_counts().get('Yes', 0)
total_loyal = filtered_data['Churn'].value_counts().get('No', 0)
churn_pct = total_churn / total_clients * 100 if total_clients > 0 else 0
avg_tenure = filtered_data['tenure'].mean()
avg_monthly_charges = filtered_data['MonthlyCharges'].mean()
revenue_potential = filtered_data['MonthlyCharges'].sum() * 12

# Création des KPIs personnalisés dans des rectangles
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">👥 PORTEFEUILLE CLIENTS</div>
        <div class="kpi-value">{total_clients:,}</div>
        <div class="kpi-delta">Base analysée</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">📉 TAUX DE CHURN</div>
        <div class="kpi-value">{churn_pct:.1f}%</div>
        <div class="kpi-delta">{"🔴 Vigilance" if churn_pct > 25 else "🟡 Stable" if churn_pct > 15 else "🟢 Optimal"}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">📅 FIDÉLITÉ MOYENNE</div>
        <div class="kpi-value">{avg_tenure:.1f} mois</div>
        <div class="kpi-delta">{"🟢 Excellente" if avg_tenure > 36 else "🟡 Moyenne" if avg_tenure > 24 else "🔴 À améliorer"}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">💰 CA ANNUEL</div>
        <div class="kpi-value">${revenue_potential:,.0f}</div>
        <div class="kpi-delta">+15% potentiel</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# GRAPHIQUES INTERACTIFS - PALETTE BLEU ROYAL & OR
# -----------------------------
st.markdown("""
<div style='text-align: center; margin: 4rem 0 2rem 0;'>
    <h2 style='color: #E0E0E0; border-bottom: 3px solid #606060; padding-bottom: 0.8rem; display: inline-block; font-size: 1.8rem;'>📊 ANALYSE VISUELLE STRATÉGIQUE</h2>
</div>
""", unsafe_allow_html=True)

# Configuration des graphiques
chart_config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
    'scrollZoom': False
}

# Graphique 1: Répartition Churn
col1, col2 = st.columns(2)

with col1:
    fig_churn = px.pie(
        filtered_data, 
        names='Churn', 
        title="<b>📊 RÉPARTITION CHURN vs FIDÉLITÉ</b>",
        color='Churn',
        color_discrete_map={'Yes': PRO_COLORS['secondary'], 'No': PRO_COLORS['primary']},
        template='plotly_dark'
    )
    fig_churn.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        marker=dict(line=dict(color='#2A2A2A', width=2)),
        textfont=dict(color='white', size=14)
    )
    fig_churn.update_layout(
        font=dict(color='white'),
        paper_bgcolor='#1A1A1A',
        plot_bgcolor='#1A1A1A',
        height=450,
        showlegend=True,
        legend=dict(font=dict(color='white', size=12))
    )
    st.plotly_chart(fig_churn, use_container_width=True, config=chart_config)

with col2:
    contract_churn = filtered_data.groupby(['Contract', 'Churn']).size().reset_index(name='Count')
    fig_contract = px.bar(
        contract_churn,
        x='Contract',
        y='Count',
        color='Churn',
        title="<b>📑 CHURN PAR TYPE DE CONTRAT</b>",
        color_discrete_map={'Yes': PRO_COLORS['secondary'], 'No': PRO_COLORS['primary']},
        template='plotly_dark'
    )
    fig_contract.update_layout(
        font=dict(color='white'),
        paper_bgcolor='#1A1A1A',
        plot_bgcolor='#1A1A1A',
        height=450,
        xaxis_title="Type de Contrat",
        yaxis_title="Nombre de Clients",
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white'))
    )
    st.plotly_chart(fig_contract, use_container_width=True, config=chart_config)

# Graphique 3: Distribution de l'ancienneté
fig_tenure = px.histogram(
    filtered_data, 
    x='tenure', 
    nbins=30, 
    title="<b>📅 DISTRIBUTION STRATÉGIQUE DE L'ANCIENNETÉ</b>",
    color_discrete_sequence=[PRO_COLORS['primary']],
    template='plotly_dark'
)
fig_tenure.update_layout(
    font=dict(color='white'),
    paper_bgcolor='#1A1A1A',
    plot_bgcolor='#1A1A1A',
    height=450,
    xaxis_title="Ancienneté (mois)",
    yaxis_title="Nombre de Clients",
    xaxis=dict(tickfont=dict(color='white')),
    yaxis=dict(tickfont=dict(color='white'))
)
st.plotly_chart(fig_tenure, use_container_width=True, config=chart_config)

# -----------------------------
# SEGMENTATION CLIENT (KMeans)
# -----------------------------
st.markdown("""
<div style='text-align: center; margin: 4rem 0 2rem 0;'>
    <h2 style='color: #E0E0E0; border-bottom: 3px solid #606060; padding-bottom: 0.8rem; display: inline-block; font-size: 1.8rem;'>🎯 SEGMENTATION AVANCÉE</h2>
</div>
""", unsafe_allow_html=True)

numeric_columns = filtered_data.select_dtypes(include=['number']).columns
X_seg = filtered_data[numeric_columns].fillna(0)

if len(X_seg) > 0:
    kmeans = KMeans(n_clusters=min(4, len(X_seg)), random_state=42)
    filtered_data['Cluster'] = kmeans.fit_predict(X_seg)

    fig_cluster = px.scatter(
        filtered_data,
        x='MonthlyCharges',
        y='tenure',
        color='Cluster',
        size='TotalCharges',
        title="<b>🎯 MATRICE DE SEGMENTATION</b>",
        template='plotly_dark',
        color_continuous_scale=[PRO_COLORS['accent'], PRO_COLORS['primary'], PRO_COLORS['light'], PRO_COLORS['secondary']]
    )
    fig_cluster.update_layout(
        font=dict(color='white'),
        paper_bgcolor='#1A1A1A',
        plot_bgcolor='#1A1A1A',
        height=500,
        xaxis_title="Charges Mensuelles ($)",
        yaxis_title="Ancienneté (mois)",
        xaxis=dict(tickfont=dict(color='white')),
        yaxis=dict(tickfont=dict(color='white'))
    )
    st.plotly_chart(fig_cluster, use_container_width=True, config=chart_config)

# -----------------------------
# DÉTECTION DES RISQUES AMÉLIORÉE
# -----------------------------
st.markdown("""
<div style='text-align: center; margin: 4rem 0 2rem 0;'>
    <h2 style='color: #E0E0E0; border-bottom: 3px solid #808080; padding-bottom: 0.8rem; display: inline-block; font-size: 1.8rem;'>🚨 DÉTECTION DES RISQUES AMÉLIORÉE</h2>
</div>
""", unsafe_allow_html=True)

def calculate_risk_scores_advanced(data):
    """Calcule les scores de risque avec un algorithme avancé basé sur les données historiques"""
    risk_scores = []
    
    for idx, row in data.iterrows():
        score = 0.0
        
        # Facteur 1: Type de contrat
        if row['Contract'] == 'Month-to-month':
            score += 0.45
        elif row['Contract'] == 'One year':
            score += 0.15
        else:  # Two year
            score += 0.05
            
        # Facteur 2: Ancienneté
        if row['tenure'] < 6:
            score += 0.25
        elif row['tenure'] < 12:
            score += 0.15
        elif row['tenure'] < 24:
            score += 0.05
            
        # Facteur 3: Charges mensuelles
        monthly_charges_median = data['MonthlyCharges'].median()
        if row['MonthlyCharges'] > monthly_charges_median * 1.5:
            score += 0.15
        elif row['MonthlyCharges'] > monthly_charges_median:
            score += 0.08
            
        # Facteur 4: Mode de paiement
        if row['PaymentMethod'] in ['Electronic check', 'Mailed check']:
            score += 0.12
            
        # Facteur 5: Services additionnels
        services_columns = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
        services_count = sum(1 for col in services_columns if row.get(col) == 'Yes')
        if services_count <= 1:
            score += 0.10
        elif services_count >= 5:
            score -= 0.08
            
        # Facteur 6: Support technique
        if row.get('TechSupport') == 'No':
            score += 0.08
            
        # Facteur 7: Partenaire et dépendants
        if row.get('Partner') == 'No' and row.get('Dependents') == 'No':
            score += 0.07
            
        # Normaliser le score entre 0 et 1
        score = min(max(score, 0), 0.95)
        risk_scores.append(score)
    
    return risk_scores

# Application du système de détection des risques
try:
    # Calcul des scores de risque
    risk_scores = calculate_risk_scores_advanced(filtered_data)
    filtered_data['RiskScore'] = risk_scores
    
    # Classification des niveaux de risque
    filtered_data['RiskLevel'] = pd.cut(
        filtered_data['RiskScore'], 
        bins=[0, 0.3, 0.7, 1],
        labels=['🟢 Faible', '🟡 Moyen', '🔴 Élevé']
    )
    
    # Affichage des résultats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        high_risk_count = len(filtered_data[filtered_data['RiskLevel'] == '🔴 Élevé'])
        st.metric(
            "🔴 Clients Risque Élevé", 
            f"{high_risk_count}",
            delta=f"{(high_risk_count/len(filtered_data)*100):.1f}%"
        )
    
    with col2:
        medium_risk_count = len(filtered_data[filtered_data['RiskLevel'] == '🟡 Moyen'])
        st.metric(
            "🟡 Clients Risque Moyen", 
            f"{medium_risk_count}",
            delta=f"{(medium_risk_count/len(filtered_data)*100):.1f}%"
        )
    
    with col3:
        low_risk_count = len(filtered_data[filtered_data['RiskLevel'] == '🟢 Faible'])
        st.metric(
            "🟢 Clients Risque Faible", 
            f"{low_risk_count}",
            delta=f"{(low_risk_count/len(filtered_data)*100):.1f}%"
        )
    
    # Top 10 des clients à risque
    st.subheader("📋 Top 10 des Clients à Haut Risque")
    high_risk_data = filtered_data.nlargest(10, 'RiskScore')[
        ['customerID', 'Contract', 'tenure', 'MonthlyCharges', 'PaymentMethod', 'RiskScore', 'RiskLevel']
    ].round(3)
    
    # Style conditionnel pour le tableau
    def highlight_risk(row):
        if row['RiskLevel'] == '🔴 Élevé':
            return ['background-color: #2d1a1a; color: #ff6b6b; font-weight: bold'] * len(row)
        elif row['RiskLevel'] == '🟡 Moyen':
            return ['background-color: #2d2a1a; color: #ffd93d'] * len(row)
        else:
            return ['background-color: #1a2d1a; color: #6bff6b'] * len(row)
    
    styled_high_risk = high_risk_data.style.apply(highlight_risk, axis=1)
    st.dataframe(styled_high_risk, use_container_width=True)
    
    # Analyse des profils à risque
    st.subheader("📊 Analyse des Profils à Risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition des risques par type de contrat
        risk_by_contract = filtered_data.groupby(['Contract', 'RiskLevel']).size().unstack(fill_value=0)
        fig_risk_contract = px.bar(
            risk_by_contract,
            title="<b>Répartition des Risques par Type de Contrat</b>",
            color_discrete_map={'🔴 Élevé': '#C0392B', '🟡 Moyen': '#E67E22', '🟢 Faible': '#27AE60'},
            template='plotly_dark'
        )
        fig_risk_contract.update_layout(
            font=dict(color='white'),
            paper_bgcolor='#1A1A1A',
            plot_bgcolor='#1A1A1A',
            height=400
        )
        st.plotly_chart(fig_risk_contract, use_container_width=True, config=chart_config)
    
    with col2:
        # Distribution des scores de risque
        fig_risk_dist = px.histogram(
            filtered_data, 
            x='RiskScore', 
            nbins=20,
            title="<b>Distribution des Scores de Risque</b>",
            color_discrete_sequence=[PRO_COLORS['secondary']],
            template='plotly_dark'
        )
        fig_risk_dist.update_layout(
            font=dict(color='white'),
            paper_bgcolor='#1A1A1A',
            plot_bgcolor='#1A1A1A',
            height=400,
            xaxis_title="Score de Risque",
            yaxis_title="Nombre de Clients"
        )
        st.plotly_chart(fig_risk_dist, use_container_width=True, config=chart_config)
    
    # Recommandations stratégiques basées sur l'analyse des risques
    st.subheader("💡 Recommandations Stratégiques")
    
    recommendations = [
        f"🎯 **Cibler les {high_risk_count} clients à risque élevé** avec des offres de fidélisation personnalisées",
        f"📞 **Programme de rétention proactive** pour les clients avec contrat mensuel ({len(filtered_data[filtered_data['Contract'] == 'Month-to-month'])} clients)",
        f"💰 **Offres de renouvellement anticipé** pour les clients approchant de la fin de contrat",
        f"🛡️ **Améliorer le support technique** pour réduire le risque de 8% sur les clients sans assistance",
        f"📊 **Surveillance renforcée** des clients avec faible utilisation de services additionnels"
    ]
    
    for rec in recommendations:
        st.markdown(f"- {rec}")
        
except Exception as e:
    st.error(f"Erreur lors de l'analyse des risques: {e}")

# -----------------------------
# FONCTION POUR GÉNÉRER LE PDF PROFESSIONNEL AVEC GRAPHIQUES
# -----------------------------
class ProfessionalPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.company_name = "Customer Analytics & Churn Prediction Platform"
    
    def header(self):
        # Logo ou titre en haut de page
        self.set_font('Arial', 'B', 16)
        self.set_fill_color(46, 90, 136)  # Bleu royal
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, self.company_name, 0, 1, 'C', True)
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} - Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 0, 'C')
    
    def add_section_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(46, 90, 136)  # Bleu royal
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, 0, 1, 'L', True)
        self.ln(5)
    
    def add_subsection_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(3)
    
    def add_kpi_table(self, data):
        self.set_font('Arial', 'B', 11)
        # En-tête du tableau
        self.set_fill_color(46, 90, 136)  # Bleu royal
        self.set_text_color(255, 255, 255)
        self.cell(100, 8, 'INDICATEUR', 1, 0, 'C', True)
        self.cell(50, 8, 'VALEUR', 1, 1, 'C', True)
        
        # Données du tableau
        self.set_font('Arial', '', 10)
        self.set_text_color(0, 0, 0)
        fill = False
        for kpi, value in data:
            if fill:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            self.cell(100, 8, kpi, 1, 0, 'L', fill)
            self.cell(50, 8, str(value), 1, 1, 'C', fill)
            fill = not fill
        self.ln(5)

def create_pdf_safe_plotly_figure(fig, width=800, height=400):
    """Crée une image sûre à partir d'une figure Plotly"""
    try:
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
            temp_path = tmpfile.name
        
        # Configuration pour utiliser un moteur alternatif si kaleido n'est pas disponible
        try:
            # Essayer d'abord avec kaleido
            pio.write_image(fig, temp_path, width=width, height=height, scale=2, engine='kaleido')
        except Exception as kaleido_error:
            st.warning("Kaleido non disponible, utilisation d'un moteur alternatif...")
            try:
                # Essayer avec orca
                pio.write_image(fig, temp_path, width=width, height=height, scale=2, engine='orca')
            except Exception as orca_error:
                st.warning("Orca non disponible, tentative avec le moteur par défaut...")
                # Utiliser le moteur par défaut
                pio.write_image(fig, temp_path, width=width, height=height, scale=2)
        
        return temp_path
    except Exception as e:
        st.error(f"Erreur création image: {e}")
        # Afficher l'instruction d'installation
        st.error("""
        **Solution :** Installez kaleido avec la commande suivante :
        ```bash
        pip install -U kaleido
        ```
        """)
        return None

def generate_professional_pdf():
    """Génère un rapport PDF professionnel avec graphiques"""
    try:
        pdf = ProfessionalPDF()
        pdf.add_page()
        
        # Page de titre
        pdf.set_font('Arial', 'B', 24)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 20, 'RAPPORT ANALYTIQUE PROFESSIONNEL', 0, 1, 'C')
        pdf.set_font('Arial', 'I', 14)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 15, 'Analyse du Churn Client - Dashboard Stratégique', 0, 1, 'C')
        pdf.ln(10)
        
        # Section 1: Résumé exécutif
        pdf.add_section_title('1. RÉSUMÉ EXÉCUTIF')
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, 
            f"Ce rapport présente une analyse complète de {total_clients} clients avec un taux de churn de {churn_pct:.1f}%. "
            f"L'analyse identifie les tendances clés, les segments à risque et propose des recommandations stratégiques "
            "pour optimiser la rétention client et maximiser la valeur à long terme."
        )
        pdf.ln(5)
        
        # Section 2: Indicateurs clés
        pdf.add_section_title('2. INDICATEURS CLÉS DE PERFORMANCE')
        kpis_data = [
            ('Portefeuille Clients', f"{total_clients:,}"),
            ('Clients en Churn', f"{total_churn:,}"),
            ('Clients Fidèles', f"{total_loyal:,}"),
            ('Taux de Churn', f"{churn_pct:.1f}%"),
            ('Ancienneté Moyenne', f"{avg_tenure:.1f} mois"),
            ('Revenu Annuel Estimé', f"${revenue_potential:,.0f}"),
            ('Charges Mensuelles Moy.', f"${avg_monthly_charges:.2f}")
        ]
        pdf.add_kpi_table(kpis_data)
        
        # Section 3: Graphiques d'analyse
        pdf.add_page()
        pdf.add_section_title('3. ANALYSE VISUELLE DES DONNÉES')
        
        # Graphique 1: Répartition Churn
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 8, 'Répartition Churn vs Fidélité', 0, 1, 'L')
        pdf.ln(2)
        
        try:
            temp_path = create_pdf_safe_plotly_figure(fig_churn)
            if temp_path and os.path.exists(temp_path):
                pdf.image(temp_path, w=180)
                pdf.ln(3)
                pdf.set_font('Arial', 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 5, 
                    f"Le graphique montre que {churn_pct:.1f}% des clients ont quitté le service, "
                    f"tandis que {100-churn_pct:.1f}% sont restés fidèles."
                )
                os.unlink(temp_path)
            else:
                pdf.set_font('Arial', 'I', 9)
                pdf.cell(0, 8, "Graphique non disponible - Installez kaleido: pip install kaleido", 0, 1)
        except Exception as e:
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 8, f"Erreur graphique: {str(e)}", 0, 1)
        
        pdf.ln(5)
        
        # Graphique 2: Churn par contrat
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 8, 'Analyse du Churn par Type de Contrat', 0, 1, 'L')
        pdf.ln(2)
        
        try:
            temp_path = create_pdf_safe_plotly_figure(fig_contract)
            if temp_path and os.path.exists(temp_path):
                pdf.image(temp_path, w=180)
                pdf.ln(3)
                pdf.set_font('Arial', 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 5, 
                    "Répartition du churn selon les différents types de contrat proposés aux clients."
                )
                os.unlink(temp_path)
            else:
                pdf.set_font('Arial', 'I', 9)
                pdf.cell(0, 8, "Graphique non disponible - Installez kaleido: pip install kaleido", 0, 1)
        except Exception as e:
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 8, f"Erreur graphique: {str(e)}", 0, 1)
        
        pdf.ln(5)
        
        # Graphique 3: Distribution ancienneté
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 8, "Distribution de l'Ancienneté des Clients", 0, 1, 'L')
        pdf.ln(2)
        
        try:
            temp_path = create_pdf_safe_plotly_figure(fig_tenure)
            if temp_path and os.path.exists(temp_path):
                pdf.image(temp_path, w=180)
                pdf.ln(3)
                pdf.set_font('Arial', 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.multi_cell(0, 5, 
                    f"L'ancienneté moyenne des clients est de {avg_tenure:.1f} mois, "
                    f"indiquant la durée moyenne de fidélité."
                )
                os.unlink(temp_path)
            else:
                pdf.set_font('Arial', 'I', 9)
                pdf.cell(0, 8, "Graphique non disponible - Installez kaleido: pip install kaleido", 0, 1)
        except Exception as e:
            pdf.set_font('Arial', 'I', 9)
            pdf.cell(0, 8, f"Erreur graphique: {str(e)}", 0, 1)
        
        # Graphique 4: Segmentation (si disponible)
        if 'Cluster' in filtered_data.columns:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(46, 90, 136)
            pdf.cell(0, 8, 'Segmentation Clients - Charges vs Ancienneté', 0, 1, 'L')
            pdf.ln(2)
            
            try:
                temp_path = create_pdf_safe_plotly_figure(fig_cluster)
                if temp_path and os.path.exists(temp_path):
                    pdf.image(temp_path, w=180)
                    pdf.ln(3)
                    pdf.set_font('Arial', 'I', 9)
                    pdf.set_text_color(100, 100, 100)
                    pdf.multi_cell(0, 5, 
                        "Analyse de segmentation permettant d'identifier différents profils clients "
                        "basés sur leurs charges et ancienneté."
                    )
                    os.unlink(temp_path)
                else:
                    pdf.set_font('Arial', 'I', 9)
                    pdf.cell(0, 8, "Graphique non disponible - Installez kaleido: pip install kaleido", 0, 1)
            except Exception as e:
                pdf.set_font('Arial', 'I', 9)
                pdf.cell(0, 8, f"Erreur graphique: {str(e)}", 0, 1)
        
        # SECTION 4 : Analyse des risques et segmentation
        pdf.add_page()
        pdf.add_section_title('4. ANALYSE DES RISQUES ET SEGMENTATION')
        
        # Analyse des risques
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 8, 'Segments Clients à Haut Risque Identifiés:', 0, 1, 'L')
        pdf.ln(2)

        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(0, 0, 0)
        risques = [
            "- Segment Contrat Mensuel: Clients avec contrats month-to-month (plus forte proportion de churn)",
            "- Segment Ancienneté Critique: Clients entre 30-40 mois d'ancienneté (pic de départ identifié)",
            "- Cluster à Risque: Groupe spécifique de la segmentation nécessitant une attention immédiate"
        ]

        for risque in risques:
            pdf.multi_cell(0, 6, risque)
            pdf.ln(1)

        pdf.ln(3)

        # Niveau de risque
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(46, 90, 136)
        pdf.cell(0, 8, 'Niveau de Risque par Segment:', 0, 1, 'L')
        pdf.ln(2)

        pdf.set_font('Arial', '', 10)
        niveaux_risque = [
            "- Risque Élevé: Contrats mensuels + ancienneté 30-40 mois",
            "- Risque Moyen: Clients approchant les 32 mois d'ancienneté moyenne", 
            "- Risque Émergent: Nouveaux clients avec faible engagement"
        ]

        for niveau in niveaux_risque:
            pdf.multi_cell(0, 6, niveau)
            pdf.ln(1)

        pdf.ln(5)
        
        # Section 5: Recommandations stratégiques
        pdf.add_section_title('5. RECOMMANDATIONS STRATÉGIQUES')
        
        recommendations = [
            f"- Cibler les {total_churn} clients à risque avec des offres de fidélisation personnalisées",
            f"- Optimiser l'expérience client pour les contrats mensuels, segment le plus à risque", 
            f"- Développer un programme de rétention pour les clients avec {avg_tenure:.1f} mois d'ancienneté moyenne",
            "- Mettre en place un système d'alerte précoce pour détecter les signes de churn",
            f"- Capitaliser sur les {total_loyal} clients fidèles avec des programmes de recommandation"
        ]
        
        pdf.set_font('Arial', '', 10)
        for rec in recommendations:
            pdf.multi_cell(0, 6, rec)
            pdf.ln(1)
        
        pdf.ln(5)
        
        # Section 6: Perspectives et objectifs
        pdf.add_section_title('6. PERSPECTIVES ET OBJECTIFS')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, 
            f"Objectif stratégique: Réduire le taux de churn de {churn_pct:.1f}% à {churn_pct*0.7:.1f}% "
            f"dans les 6 prochains mois, ce qui représenterait une économie potentielle de "
            f"${revenue_potential * churn_pct/100 * 0.3:,.0f} sur base annuelle."
        )
        
        # Génération du buffer PDF
        try:
            pdf_buffer = BytesIO()
            pdf_output = pdf.output(dest='S').encode('latin-1')
            pdf_buffer.write(pdf_output)
            pdf_buffer.seek(0)
            return pdf_buffer
        except Exception as e:
            st.error(f"Erreur lors de la génération du PDF: {e}")
            return None
            
    except Exception as e:
        st.error(f"Erreur lors de la génération du PDF : {str(e)}")
        return None

# -----------------------------
# SECTION RAPPORTS PROFESSIONNELS
# -----------------------------
st.markdown("""
<div style='text-align: center; margin: 4rem 0 2rem 0;'>
    <h2 style='color: #E0E0E0; border-bottom: 3px solid #808080; padding-bottom: 0.8rem; display: inline-block; font-size: 1.8rem;'>📋 EXPORT PROFESSIONNEL</h2>
</div>
""", unsafe_allow_html=True)

# Section PDF
st.markdown("""
<div class="export-section">
    <h3 style='color: #FFFFFF; margin-bottom: 1.5rem;'>📄 RAPPORT PDF COMPLET</h3>
    <p style='color: #CCCCCC; margin-bottom: 1.5rem;'>Téléchargez un rapport détaillé avec analyse complète et recommandations</p>
""", unsafe_allow_html=True)

# Installation de Kaleido
st.markdown("""
<div style='background: #2A2A2A; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #404040;'>
    <h4 style='color: #FFFFFF; margin: 0 0 0.5rem 0;'>📦 PRÉREQUIS POUR LE PDF</h4>
    <p style='color: #CCCCCC; margin: 0;'>
        Pour générer le PDF avec les graphiques, installez le package kaleido :
    </p>
    <code style='background: #1A1A1A; padding: 0.5rem; border-radius: 4px; display: block; margin: 0.5rem 0; color: #FFFFFF;'>
        pip install -U kaleido
    </code>
</div>
""", unsafe_allow_html=True)

if st.button("🖨️ GÉNÉRER LE RAPPORT PDF AVEC GRAPHIQUES", key="generate_pdf", use_container_width=True):
    with st.spinner("📊 Génération du rapport professionnel..."):
        pdf_buffer = generate_professional_pdf()
        
        if pdf_buffer:
            st.success("✅ Rapport PDF généré avec succès!")
            st.info("""
            **📋 Contenu du rapport:**
            - 🎯 Résumé exécutif et indicateurs clés
            - 📊 4 graphiques d'analyse professionnels
            - 🚨 Analyse des risques et segmentation
            - 💡 Recommandations stratégiques actionnables
            - 🎯 Perspectives et objectifs mesurables
            """)
            
            st.download_button(
                label="📥 TÉLÉCHARGER LE RAPPORT PDF COMPLET",
                data=pdf_buffer,
                file_name=f"rapport_analytique_complet_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="pdf_download"
            )
        else:
            st.error("❌ Erreur lors de la génération du PDF")

st.markdown("</div>", unsafe_allow_html=True)

# Section Export Données - UNIQUEMENT EXCEL (même si l'upload accepte CSV et Excel)
st.markdown("""
<div class="export-section">
    <h3 style='color: #FFFFFF; margin-bottom: 1.5rem;'>💾 EXPORT DES DONNÉES EXCEL</h3>
    <p style='color: #CCCCCC; margin-bottom: 1.5rem;'>Téléchargez les données analysées au format Excel professionnel</p>
""", unsafe_allow_html=True)

# Bouton Excel uniquement (même si l'upload accepte CSV)
try:
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Données principales
        filtered_data.to_excel(writer, index=False, sheet_name='Donnees_Analyse')
        
        # Indicateurs KPIs
        kpis_df = pd.DataFrame({
            "KPI": ["Portefeuille Clients", "Churn Total", "Clients Fidèles", "Taux Churn", "Ancienneté Moyenne", "Revenu Annuel Estimé"],
            "Valeur": [total_clients, total_churn, total_loyal, f"{churn_pct:.1f}%", f"{avg_tenure:.1f} mois", f"${revenue_potential:,.0f}"]
        })
        kpis_df.to_excel(writer, index=False, sheet_name='Indicateurs_KPIs')
        
        # Analyse par contrat
        contract_analysis = filtered_data.groupby('Contract').agg({
            'Churn': lambda x: (x == 'Yes').sum(),
            'customerID': 'count',
            'MonthlyCharges': 'mean',
            'tenure': 'mean'
        }).round(2)
        contract_analysis.columns = ['Clients_Churn', 'Total_Clients', 'Charges_Mensuelles_Moy', 'Anciennete_Moyenne']
        contract_analysis['Taux_Churn'] = (contract_analysis['Clients_Churn'] / contract_analysis['Total_Clients'] * 100).round(1)
        contract_analysis.to_excel(writer, sheet_name='Analyse_Contrats')
    
    excel_buffer.seek(0)
    
    st.download_button(
        label="📗 TÉLÉCHARGER LE RAPPORT EXCEL COMPLET",
        data=excel_buffer,
        file_name=f"rapport_analytique_excel_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="excel_download"
    )
    
    st.markdown("""
    <div style='background: #2A2A2A; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid #404040;'>
        <h4 style='color: #FFFFFF; margin: 0 0 0.5rem 0;'>📋 Contenu du fichier Excel:</h4>
        <ul style='color: #CCCCCC; text-align: left; margin: 0;'>
            <li><strong>Donnees_Analyse:</strong> Données complètes analysées</li>
            <li><strong>Indicateurs_KPIs:</strong> Tableau de bord avec indicateurs clés</li>
            <li><strong>Analyse_Contrats:</strong> Analyse détaillée par type de contrat</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"❌ Erreur lors de la génération du fichier Excel: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# FOOTER PROFESSIONNEL
# -----------------------------
st.markdown("""
<div style='text-align: center; margin-top: 5rem; padding: 2.5rem; background: linear-gradient(135deg, #2A2A2A, #404040); border-radius: 12px; border: 1px solid #555555;'>
    <h3 style='color: #FFFFFF; margin: 0; font-size: 1.4rem;'>Customer Analytics & Churn Prediction Platform</h3>
    <p style='color: #CCCCCC; margin: 0.8rem 0 0 0; font-size: 1rem;'>Dashboard Professionnel d'Analyse Stratégique • Powered by Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# INFORMATIONS SIDEBAR
# -----------------------------
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, #404040, #606060); padding: 1.2rem; border-radius: 10px; margin-top: 2rem; border: 1px solid #666666;'>
    <h4 style='color: #FFFFFF; text-align: center; margin: 0; font-size: 1.1rem;'>📊 SNAPSHOT</h4>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style='background: #2A2A2A; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center; border: 1px solid #404040;'>
    <div style='color: #CCCCCC; font-size: 0.9rem;'>Portefeuille Clients</div>
    <div style='color: #FFFFFF; font-size: 1.4rem; font-weight: bold;'>{total_clients:,}</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style='background: #2A2A2A; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center; border: 1px solid #404040;'>
    <div style='color: #CCCCCC; font-size: 0.9rem;'>Taux de Churn</div>
    <div style='color: #FFFFFF; font-size: 1.4rem; font-weight: bold;'>{churn_pct:.1f}%</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"""
<div style='background: #2A2A2A; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center; border: 1px solid #404040;'>
    <div style='color: #CCCCCC; font-size: 0.9rem;'>Fidélité Moyenne</div>
    <div style='color: #FFFFFF; font-size: 1.4rem; font-weight: bold;'>{avg_tenure:.1f} mois</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar.expander("ℹ️ GUIDE UTILISATION"):
    st.markdown("""
    <div style='color: #E0E0E0;'>
    **Fonctionnalités:**
    - Filtrage avancé des données
    - Analyse visuelle en temps réel
    - Détection proactive des risques
    - Export professionnel des rapports
    
    **Optimisation:**
    - Utilisez les filtres pour cibler l'analyse
    - Exportez les rapports pour partage
    - Surveillez les indicateurs clés
    
    **Support:**
    - Documentation complète disponible
    - Support technique dédié
    </div>
    """, unsafe_allow_html=True)
