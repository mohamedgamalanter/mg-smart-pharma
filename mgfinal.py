
def display_card(row, extra_data=None):
    trade = row.get("Trade Name", "N/A")
    sci = row.get("Scientific Name", "N/A")
    price = row.get("Public price", "N/A")
    shelf = row.get("Shelf Life", "N/A")
    legal = row.get("Legal Status", "N/A")
    control = row.get("Product Control", "N/A")
    extra_html = ""
    if extra_data is not None:
        details = " | ".join([f"<b>{k.replace('Extra_', '')}:</b> {v}" for k, v in extra_data.items() if k.startswith("Extra_")])
        extra_html = f"<p style='color:#2ecc71; font-size: 14px;'>📦 <b>Branch Data:</b> {details}</p>"
    html = (
        f"<div style='padding:15px; border:2px solid #dcdde1; border-radius:12px; margin-bottom:15px; background-color:#f9f9f9;'>"
        f"<h4 style='margin-bottom:4px; color:#2c3e50;'>{trade}</h4>"
        f"<p><b>Scientific Name:</b> {sci}</p>"
        f"<p><b>Price:</b> {price}</p>"
        f"<p><b>Shelf Life:</b> {shelf} months</p>"
        f"<p><b>Status:</b> {legal} | {control}</p>"
        f"{extra_html}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)



import streamlit as st
import pandas as pd
import re

# إعداد الصفحة
st.set_page_config(page_title="MG Smart Pharma", page_icon="💊", layout="centered")

# عرض اللوجو في المنتصف فعليًا باستخدام الأعمدة
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("logo.png", width=400)

# عنوان ترحيبي بخط أخف وأصغر
st.markdown("<h3 style='text-align: center; color:#34495e; font-weight:300;'>Make your own drug index</h3>", unsafe_allow_html=True)
st.markdown("---")

# تحميل قاعدة البيانات
@st.cache_data
def load_database():
    df = pd.read_excel("database.xlsx", sheet_name=0)
    df['Normalized Trade Name'] = df['Trade Name'].astype(str).str.lower().apply(lambda x: re.sub(r'[^a-z0-9]', '', x))
    return df

db = load_database()

# قسم البحث
st.markdown("### 💊 <span style='color:#e74c3c;'>Search for Medicines</span>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    search_ingredient = st.text_input("Search by Active Ingredient", placeholder="e.g. amoxicillin")

with col2:
    search_trade = st.text_input("Search by Trade Name", placeholder="e.g. augmentin")

# عرض النتائج بتنسيق مبسط وجذاب
def display_results(result_df):
    for _, row in result_df.iterrows():
        name = row['Trade Name']
        sci = row['Scientific Name']
        price = row.get('Public price', 'N/A')
        life = row.get('Shelf Life', 'N/A')
        legal = row.get('Legal Status', 'N/A')
        control = row.get('Product Control', '')

        html = (
            f"<div style='padding:15px; border:1px solid #e0e0e0; border-radius:12px; margin-bottom:10px; background-color:#f9f9f9;'>"
            f"<h4 style='margin-bottom:8px; color:#2c3e50;'>{name}</h4>"
            f"<p style='margin:0;'><b>Scientific Name:</b> {sci}</p>"
            f"<p style='margin:0;'><b>Public Price:</b> {price}</p>"
            f"<p style='margin:0;'><b>Shelf Life:</b> {life} months</p>"
            f"<p style='margin:0;'><b>Status:</b> {legal} | {control}</p>"
            f"</div>"
        )
        st.markdown(html, unsafe_allow_html=True)

# تنفيذ البحث
if search_ingredient or search_trade:
    result = db.copy()
    selected_ingredient = None

    if search_trade:
        normalized_input = re.sub(r'[^a-z0-9]', '', search_trade.lower())
        matched = result[result["Normalized Trade Name"].str.contains(normalized_input)]
        if not matched.empty:
            selected_ingredient = matched["Scientific Name"].values[0]
            st.write("### 🧾 Product Match:")
            display_results(matched)

    if search_ingredient or selected_ingredient:
        ingredient_to_search = search_ingredient if search_ingredient else selected_ingredient
        alternatives = result[result["Scientific Name"].str.lower().str.contains(ingredient_to_search.lower())]
        st.write("### 💊 Alternatives with Same Active Ingredient:")
        display_results(alternatives)

st.markdown("---")

# قسم الذكاء الصناعي
st.markdown("### 🤖 Ask MG AI", unsafe_allow_html=True)
ai_question = st.text_input("Type your medical or product question here...", placeholder="e.g. Best alternative for augmentin?")
if st.button("Ask AI"):
    st.info("🔧 This feature is under development. Your question has been logged.")

st.markdown("---")

# رفع الملفات
st.markdown("### 📤 Upload Branch Data", unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload your Excel sheet here", type=["xlsx", "xls", "csv"])
if uploaded_file:
    st.success(f"✅ File '{uploaded_file.name}' received and ready for processing.")



# ⬇️ نتائج البحث بالاسم التجاري أو المادة الفعالة
if search_trade:
    query = smart_normalize(search_trade)
    matches = main_db[main_db["Smart Name"] == query]
    if not matches.empty:
        for _, row in matches.iterrows():
            extra_row = merged_uploaded[merged_uploaded["Smart Name"] == query]
            display_card(row, extra_row.iloc[0] if not extra_row.empty else None)

elif search_ingredient:
    results = main_db[main_db["Scientific Name"].str.lower().str.contains(search_ingredient.lower())]
    for _, row in results.iterrows():
        extra_row = merged_uploaded[merged_uploaded["Smart Name"] == row["Smart Name"]]
        display_card(row, extra_row.iloc[0] if not extra_row.empty else None)
