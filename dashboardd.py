import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Samsung Smartphone Recommendation Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Light Theme CSS ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f5f7fa !important;
    color: #1a1a2e !important;
}
.main { background-color: #f5f7fa !important; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; color: #1a1a2e !important; }

section[data-testid="stSidebar"] { background-color: #1a1a2e !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.kpi-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 22px 18px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.kpi-card .kpi-label {
    font-size: 11px; color: #64748b; letter-spacing: 1.5px;
    text-transform: uppercase; font-weight: 600; margin-bottom: 8px;
}
.kpi-card .kpi-value {
    font-family: 'Space Grotesk', sans-serif; font-size: 26px;
    font-weight: 700; color: #1e3a5f;
}
.kpi-card .kpi-sub { font-size: 12px; color: #10b981; font-weight: 500; margin-top: 4px; }

.section-header {
    font-family: 'Space Grotesk', sans-serif; font-size: 13px;
    letter-spacing: 2px; text-transform: uppercase; color: #3b5bdb;
    margin-bottom: 14px; border-left: 4px solid #3b5bdb;
    padding-left: 12px; font-weight: 600;
}

.rec-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 18px; margin-bottom: 12px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.rec-card .rc-city { font-size: 11px; color: #3b5bdb; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600; }
.rec-card .rc-user { font-size: 16px; font-weight: 700; color: #1a1a2e; margin: 6px 0 4px; }
.rec-card .rc-profile { font-size: 12px; color: #64748b; margin-bottom: 10px; }
.rec-card .rc-upsell { color: #059669; font-size: 13px; font-weight: 500; margin-bottom: 4px; }
.rec-card .rc-cross  { color: #d97706; font-size: 13px; font-weight: 500; margin-bottom: 4px; }
.rec-card .rc-down   { color: #dc2626; font-size: 13px; font-weight: 500; }

.met-row {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 10px;
    display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.met-row .ml { color: #475569; font-size: 13px; font-weight: 500; }
.met-row .mv { color: #1e3a5f; font-family: 'Space Grotesk', sans-serif; font-size: 15px; font-weight: 700; }
.met-row.profit { border-left: 4px solid #10b981; }
.met-row.profit .mv { color: #059669; }
.met-row.roi { border-left: 4px solid #f59e0b; }
.met-row.roi .mv { color: #d97706; }
</style>
""", unsafe_allow_html=True)

# ─── Shared chart layout ───────────────────────────────────────────────────────
LIGHT = dict(
    paper_bgcolor='#ffffff', plot_bgcolor='#f8fafc',
    font=dict(color='#1a1a2e', family='Inter'),
    margin=dict(t=30, b=20, l=10, r=10),
)
GRID = dict(gridcolor='#e2e8f0', zerolinecolor='#cbd5e1')
C = ['#3b5bdb', '#f59e0b', '#10b981']

# ─── Data ─────────────────────────────────────────────────────────────────────
np.random.seed(42)

@st.cache_data
def load_data():
    cities    = ['Mumbai', 'Hyderabad', 'Bangalore']
    user_cats = ['Entry Level User', 'Balanced User', 'High-End User']
    accs      = ['Phone Case', 'Screen Protector', 'Power Bank', 'Earbuds', 'Charger']
    n = 500
    df = pd.DataFrame({
        'User_ID':         range(1, n+1),
        'City':            np.random.choice(cities, n, p=[0.40, 0.35, 0.25]),
        'User_Category':   np.random.choice(user_cats, n, p=[0.45, 0.35, 0.20]),
        'Budget':          np.random.choice(['<15K','10k-30k','Above 30k'], n),
        'Preferred_RAM':   np.random.choice(['4GB','6GB','8GB','12GB'], n),
        'Camera_Priority': np.random.choice(['Low','Medium','High'], n),
        'Accessories':     np.random.choice(accs, n),
        'Purchase_Intent': np.random.choice(['Low','Medium','High'], n),
        'Age':             np.random.randint(22, 55, n),
    })
    rev_map = {'Entry Level User':(8000,20000),'Balanced User':(18000,45000),'High-End User':(40000,120000)}
    df['Revenue'] = df['User_Category'].apply(lambda x: np.random.randint(*rev_map[x]))
    return df

df = load_data()

rev_summary = pd.DataFrame({
    'User_Category':    ['Entry Level User', 'Balanced User', 'High-End User'],
    'Users':            [227, 175, 98],
    'Upsell_Revenue':   [2996400, 3500000, 9408000],
    'CrossSell_Revenue':[249700, 525000, 940800],
    'Total_Revenue':    [3246100, 4025000, 10348800]
})

city_rev = pd.DataFrame({
    'City':        ['Mumbai', 'Hyderabad', 'Bangalore'],
    'Revenue_Pct': [58.73, 22.84, 18.42],
    'Revenue':     [17619900*0.5873, 17619900*0.2284, 17619900*0.1842]
})

assoc_rules = pd.DataFrame({
    'Antecedents': ['Galaxy M14','Galaxy M14','Galaxy S23','Galaxy M14','Galaxy M14',
                    'Galaxy F54','Galaxy F54','Galaxy M14','Galaxy M14'],
    'Consequents': ['Screen Protector','Wireless Charger','Phone Case','Screen Protector',
                    'Power Bank','Phone Case','Power Bank','Power Bank','Screen Protector'],
    'Support':    [0.353,0.163,0.184,0.066,0.124,0.081,0.155,0.115,0.060],
    'Confidence': [1.0]*9,
    'Lift':       [1.98]*9
})

rec_data = [
    {'City':'Bangalore','User_Category':'Entry Level User',
     'Features':'Price <₹15K · 4GB RAM · 64GB Storage · Basic Camera · 4000mAh',
     'Upsell':'Galaxy F14 (₹12K) → Galaxy M34 (₹18K | 6GB, 128GB, Triple Cam)',
     'CrossSell':'Basic Earphones, Charging Cable, Phone Case',
     'Downgrade':'Samsung Galaxy M04 (₹8K) for lower budget'},
    {'City':'Hyderabad','User_Category':'Balanced User',
     'Features':'₹15K–₹30K · 6GB RAM · 128GB Storage · Good Camera · 5000mAh',
     'Upsell':'Galaxy M34 (₹18K) → Galaxy S21 FE (₹32K | 8GB, 128GB, Premium Cam)',
     'CrossSell':'Bluetooth Earbuds, Fast Charger, Power Bank',
     'Downgrade':'Samsung Galaxy F14 (₹12K) for cost saving'},
    {'City':'Mumbai','User_Category':'High-End User',
     'Features':'>₹30K · 8–12GB RAM · 256GB Storage · High Camera · 5000mAh+',
     'Upsell':'Galaxy S23 (₹75K) → Galaxy S24 Ultra (₹1.2L | 12GB, 256GB, 200MP)',
     'CrossSell':'Galaxy Buds, Wireless Charger, Premium Power Bank',
     'Downgrade':'Samsung Galaxy A34 (₹25K) as budget flagship alternative'},
]

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📱 Movate Internship")
    st.markdown("**Samsung Smartphone Recommendation**")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠 Overview", "🔍 Recommendations",
        "📊 Revenue Analysis", "🔗 Association Rules", "🗺️ City Insights"
    ])
    st.markdown("---")
    st.markdown("**Filters**")
    city_filter = st.multiselect("City", ['Mumbai','Hyderabad','Bangalore'],
                                  default=['Mumbai','Hyderabad','Bangalore'])
    user_filter = st.multiselect("User Category",
                                  ['Entry Level User','Balanced User','High-End User'],
                                  default=['Entry Level User','Balanced User','High-End User'])
    st.markdown("---")
    st.caption("Week 8 Final Deliverable · Medha Vemula")

df_f = df[df['City'].isin(city_filter) & df['User_Category'].isin(user_filter)]

# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Overview":
    st.markdown("# 📱 Samsung Smartphone Recommendation Dashboard")
    st.markdown("*Upsell & Cross-Sell Analysis — Movate Internship Project*")
    st.markdown("---")

    cols = st.columns(5)
    kpis = [
        ("Total Revenue", "₹1.76 Cr", "Grand Total"),
        ("Net Profit", "₹1.57 Cr", "ROI: 873.33%"),
        ("Total Users", "500", "Across 3 cities"),
        ("High-End Share", "58.73%", "of total revenue"),
        ("Rules Generated", "9", "Apriori algorithm"),
    ]
    for col, (label, val, sub) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                        f'<div class="kpi-value">{val}</div>'
                        f'<div class="kpi-sub">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca, cb = st.columns(2)

    with ca:
        st.markdown('<div class="section-header">Revenue by User Segment</div>', unsafe_allow_html=True)
        fig = px.bar(rev_summary, x='User_Category', y='Total_Revenue',
                     color='User_Category', color_discrete_sequence=C, text='Total_Revenue')
        fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside', marker_line_width=0)
        fig.update_layout(**LIGHT, showlegend=False,
                          yaxis=dict(title='Revenue (₹)', **GRID), xaxis=dict(title='', showgrid=False))
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown('<div class="section-header">User Distribution</div>', unsafe_allow_html=True)
        fig2 = px.pie(rev_summary, values='Users', names='User_Category',
                      color_discrete_sequence=C, hole=0.42)
        fig2.update_traces(textposition='outside', textinfo='percent+label', textfont_size=13)
        fig2.update_layout(**LIGHT, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Dataset Sample</div>', unsafe_allow_html=True)
    st.dataframe(df_f.head(10).reset_index(drop=True), use_container_width=True, height=280)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 Recommendations":
    st.markdown("# 🔍 Smart Recommendation Engine")
    st.markdown("*Upsell · Cross-Sell · Downgrade recommendations by city & user type*")
    st.markdown("---")

    st.markdown('<div class="section-header">Try the Recommender</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    sel_city = c1.selectbox("Select City", ['Bangalore', 'Hyderabad', 'Mumbai'])
    sel_user = c2.selectbox("Select User Type",
                             ['Entry Level User', 'Balanced User', 'High-End User'])
    rec = next((r for r in rec_data if r['User_Category'] == sel_user), rec_data[0])
    st.markdown(f"""
    <div class="rec-card">
        <div class="rc-city">📍 {sel_city}</div>
        <div class="rc-user">{sel_user}</div>
        <div class="rc-profile">Customer Profile: {rec['Features']}</div>
        <div class="rc-upsell">⬆️ Upsell: {rec['Upsell']}</div>
        <div class="rc-cross">🔀 Cross-Sell: {rec['CrossSell']}</div>
        <div class="rc-down">⬇️ Downgrade: {rec['Downgrade']}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">All Recommendations</div>', unsafe_allow_html=True)
    for r in rec_data:
        st.markdown(f"""
        <div class="rec-card">
            <div class="rc-city">📍 {r['City']}</div>
            <div class="rc-user">{r['User_Category']}</div>
            <div class="rc-profile">{r['Features']}</div>
            <div class="rc-upsell">⬆️ {r['Upsell']}</div>
            <div class="rc-cross">🔀 {r['CrossSell']}</div>
            <div class="rc-down">⬇️ {r['Downgrade']}</div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Revenue Analysis":
    st.markdown("# 📊 Revenue Analysis")
    st.markdown("*Cost, Profit & ROI breakdown from the recommendation strategy*")
    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="section-header">Cost Breakdown</div>', unsafe_allow_html=True)
        cost_df = pd.DataFrame({
            'Item': ['Marketing Cost','Operational Cost','Variable Cost'],
            'Amount': [500000, 300000, 1000000]
        })
        fig = px.pie(cost_df, values='Amount', names='Item', hole=0.45,
                     color_discrete_sequence=['#3b5bdb','#f59e0b','#10b981'])
        fig.update_traces(textinfo='percent+label', textfont_size=12)
        fig.update_layout(**LIGHT, showlegend=True, legend=dict(orientation='h', y=-0.15))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Revenue vs Cost vs Profit</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        for name, val, color in [('Revenue',17619900,'#10b981'),('Cost',1800000,'#ef4444'),('Net Profit',15719900,'#3b5bdb')]:
            fig2.add_trace(go.Bar(name=name, x=[name], y=[val], marker_color=color,
                                  text=f'₹{val:,.0f}', textposition='outside'))
        fig2.update_layout(**LIGHT, showlegend=False,
                           yaxis=dict(title='Amount (₹)', **GRID), xaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)

    with c3:
        st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="met-row"><span class="ml">Total Revenue</span><span class="mv">₹1,76,19,900</span></div>
        <div class="met-row"><span class="ml">Total Cost</span><span class="mv">₹18,00,000</span></div>
        <div class="met-row"><span class="ml">Depreciation (10%)</span><span class="mv">₹1,00,000</span></div>
        <div class="met-row profit"><span class="ml">Net Profit</span><span class="mv">₹1,57,19,900</span></div>
        <div class="met-row roi"><span class="ml">ROI</span><span class="mv">873.33%</span></div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Revenue by Strategy Type (Upsell vs Cross-Sell)</div>', unsafe_allow_html=True)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='Upsell Revenue', x=rev_summary['User_Category'],
                          y=rev_summary['Upsell_Revenue'], marker_color='#3b5bdb',
                          text=rev_summary['Upsell_Revenue'],
                          texttemplate='₹%{text:,.0f}', textposition='outside'))
    fig3.add_trace(go.Bar(name='Cross-Sell Revenue', x=rev_summary['User_Category'],
                          y=rev_summary['CrossSell_Revenue'], marker_color='#f59e0b',
                          text=rev_summary['CrossSell_Revenue'],
                          texttemplate='₹%{text:,.0f}', textposition='outside'))
    fig3.update_layout(**LIGHT, barmode='group',
                       yaxis=dict(title='Revenue (₹)', **GRID), xaxis=dict(showgrid=False),
                       legend=dict(bgcolor='#ffffff', bordercolor='#e2e8f0', borderwidth=1))
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔗 Association Rules":
    st.markdown("# 🔗 Apriori Association Rules")
    st.markdown("*Market basket analysis — customers who buy X also tend to buy Y*")
    st.markdown("---")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="section-header">Top Association Rules</div>', unsafe_allow_html=True)
        st.dataframe(
            assoc_rules.style.format({'Support':'{:.3f}','Confidence':'{:.1f}','Lift':'{:.3f}'}),
            use_container_width=True, height=360)

    with c2:
        st.markdown('<div class="section-header">Support Distribution</div>', unsafe_allow_html=True)
        fig = px.bar(assoc_rules.sort_values('Support', ascending=True),
                     x='Support', y='Antecedents', orientation='h',
                     color='Support', color_continuous_scale=['#93c5fd','#1e40af'])
        fig.update_layout(**LIGHT, coloraxis_showscale=False,
                          yaxis=dict(showgrid=False), xaxis=dict(**GRID))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-header">Accessories Count (from dataset)</div>', unsafe_allow_html=True)
    acc_counts = pd.DataFrame({
        'Accessory': ['Phone Case','Screen Protector','Power Bank','Earbuds','Charger'],
        'Count': [348, 297, 128, 118, 109]
    })
    fig2 = px.bar(acc_counts, x='Accessory', y='Count',
                  color='Count', color_continuous_scale=['#93c5fd','#1e40af'], text='Count')
    fig2.update_traces(textposition='outside')
    fig2.update_layout(**LIGHT, coloraxis_showscale=False,
                       yaxis=dict(**GRID), xaxis=dict(showgrid=False))
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ City Insights":
    st.markdown("# 🗺️ City-wise Revenue Insights")
    st.markdown("*Regional revenue trends to prioritize high-performing markets*")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">Revenue Share by City</div>', unsafe_allow_html=True)
        fig = px.pie(city_rev, values='Revenue_Pct', names='City', hole=0.42,
                     color_discrete_sequence=C)
        fig.update_traces(textposition='outside', textinfo='percent+label', textfont_size=13)
        fig.update_layout(**LIGHT, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-header">Revenue Amount by City</div>', unsafe_allow_html=True)
        fig2 = px.bar(city_rev, x='City', y='Revenue',
                      color='City', color_discrete_sequence=C, text='Revenue')
        fig2.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside', marker_line_width=0)
        fig2.update_layout(**LIGHT, showlegend=False,
                           yaxis=dict(title='Revenue (₹)', **GRID), xaxis=dict(showgrid=False))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">User Distribution by City (Filtered)</div>', unsafe_allow_html=True)
    if len(df_f) > 0:
        city_user = df_f.groupby(['City','User_Category']).size().reset_index(name='Count')
        fig3 = px.bar(city_user, x='City', y='Count', color='User_Category',
                      color_discrete_sequence=C, barmode='group', text='Count')
        fig3.update_traces(textposition='outside')
        fig3.update_layout(**LIGHT, yaxis=dict(**GRID), xaxis=dict(showgrid=False),
                           legend=dict(title='User Category', bgcolor='#ffffff',
                                       bordercolor='#e2e8f0', borderwidth=1))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data for the current filter selection.")
