import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Pro Analytics Dashboard", layout="wide")

st.title("🎯 Hệ thống Phân tích Dữ liệu Giáo dục Chuyên sâu")

# --- HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def process_data(df):
    cols_numeric = ['Ngữ văn', 'Tiếng Anh', 'Toán']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Tong_Diem'] = df[cols_numeric].sum(axis=1)
    
    # Phân loại học lực (Giả định thang điểm 30)
    def classify(score):
        if score >= 24: return 'Giỏi'
        if score >= 18: return 'Khá'
        if score >= 15: return 'Trung bình'
        return 'Yếu/Kém'
    
    df['Xep_Loai'] = df['Tong_Diem'].apply(classify)
    return df

# --- SIDEBAR: BỘ LỌC ---
uploaded_file = st.sidebar.file_uploader("Tải file dữ liệu (.xlsx/.csv)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file, skiprows=6)
    else:
        df_raw = pd.read_excel(uploaded_file, header=6)
    
    df = process_data(df_raw.dropna(subset=['Số BD']))

    # Bộ lọc lớp
    list_lop = sorted(df['Lớp'].unique().tolist())
    selected_class = st.sidebar.multiselect("Chọn lớp để phân tích:", list_lop, default=list_lop)
    df = df[df['Lớp'].isin(selected_class)]

    # --- CÁC TAB CHUYÊN SÂU ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🔗 Tương quan môn học", "⚠️ Cảnh báo hỗ trợ", "📝 Xuất dữ liệu"])

    with tab1:
        st.subheader("Phân bố học lực")
        col1, col2 = st.columns([1, 2])
        xep_loai_count = df['Xep_Loai'].value_counts()
        col1.pie_chart(xep_loai_count)
        
        fig_box = px.box(df, x="Lớp", y="Tong_Diem", color="Lớp", title="Biến động điểm số giữa các lớp")
        col2.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        st.subheader("Tương quan giữa các môn học")
        # Tính toán ma trận tương quan
        corr = df[['Ngữ văn', 'Tiếng Anh', 'Toán']].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)
        st.write("Giải thích: Số càng gần 1, hai môn càng có tương quan thuận mạnh (HS giỏi môn này thường giỏi môn kia).")

    with tab3:
        st.subheader("Danh sách học sinh cần hỗ trợ")
        df_weak = df[df['Tong_Diem'] < 15] # Ngưỡng cần chú ý
        st.dataframe(df_weak[['Số BD', 'Họ và tên', 'Lớp', 'Tong_Diem', 'Xep_Loai']], use_container_width=True)
        
        # Nút gửi email (Gợi ý)
        st.info("💡 Lưu ý: Các học sinh này cần được lên kế hoạch phụ đạo bổ sung.")

    with tab4:
        st.subheader("Xuất báo cáo chi tiết")
        # Xuất file Excel đã xử lý
        def to_excel(df):
            import io
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
        
        st.download_button("📥 Tải xuống dữ liệu phân tích đầy đủ", data=to_excel(df), file_name="Bao_Cao_Phan_Tich.xlsx")

else:
    st.info("Vui lòng tải file dữ liệu lên thanh bên để bắt đầu.")