import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Hệ thống Báo cáo", layout="wide")
st.title("📊 Hệ thống Báo cáo Tự động THCS")

uploaded_file = st.sidebar.file_uploader("Tải file Excel/CSV của trường:", type=["xlsx", "csv"])

if uploaded_file:
    # Đọc dữ liệu
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, skiprows=6) # Lấy từ dòng thứ 7 trở đi
    else:
        df = pd.read_excel(uploaded_file, header=6)
    
    st.success("Tải dữ liệu thành công!")
    
    # Làm sạch dữ liệu
    df = df.dropna(subset=['Số BD'])
    cols_numeric = ['Ngữ văn', 'Tiếng Anh', 'Toán']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Tong_Diem'] = df[cols_numeric].sum(axis=1)

    # Hiển thị
    st.subheader("1. Bảng dữ liệu đã xử lý")
    st.dataframe(df.head(10))

    # Báo cáo tổng hợp
    st.subheader("2. Báo cáo tổng hợp theo Lớp")
    dashboard = df.groupby('Lớp')[['Ngữ văn', 'Tiếng Anh', 'Toán', 'Tong_Diem']].mean().round(2)
    st.table(dashboard)

    # Tải xuống
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Du_Lieu_Chi_Tiet')
        dashboard.to_excel(writer, sheet_name='Dashboard')
    
    st.download_button(
        label="📥 Tải xuống Báo cáo Tổng hợp (.xlsx)",
        data=buffer.getvalue(),
        file_name="Bao_Cao_Tong_Hop.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("Vui lòng tải file để bắt đầu.")