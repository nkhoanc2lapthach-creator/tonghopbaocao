import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Phân tích Giáo dục Pro", layout="wide")

st.title("🎯 Hệ thống Phân tích Dữ liệu Giáo dục Chuyên sâu")

# --- HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def process_data(df):
    cols_numeric = ['Ngữ văn', 'Tiếng Anh', 'Toán']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    df['Tong_Diem'] = df[cols_numeric].sum(axis=1)
    
    def classify(score):
        if score >= 24: return 'Giỏi'
        if score >= 18: return 'Khá'
        if score >= 15: return 'Trung bình'
        return 'Yếu/Kém'
    
    df['Xep_Loai'] = df['Tong_Diem'].apply(classify)
    return df

# --- SIDEBAR ---
uploaded_file = st.sidebar.file_uploader("Tải file dữ liệu (.xlsx/.csv)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file, skiprows=6)
    else:
        df_raw = pd.read_excel(uploaded_file, header=6)
    
    df = process_data(df_raw.dropna(subset=['Số BD']))
    list_lop = sorted(df['Lớp'].unique().tolist())
    selected_class = st.sidebar.multiselect("Chọn lớp để phân tích:", list_lop, default=list_lop)
    df = df[df['Lớp'].isin(selected_class)]

    # --- CÁC TAB ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🔗 Tương quan môn học", "⚠️ Cảnh báo hỗ trợ", "📝 Xuất dữ liệu"])

    with tab1:
        st.subheader("📊 Báo cáo chỉ số tổng quát")
        
        # 1. Metrics (Chỉ số nhanh)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tổng HS", len(df))
        col2.metric("TB Toán", f"{df['Toán'].mean():.2f}")
        col3.metric("TB Văn", f"{df['Ngữ văn'].mean():.2f}")
        col4.metric("TB Anh", f"{df['Tiếng Anh'].mean():.2f}")
        
        st.markdown("---")

        # 2. Phân bổ điểm số (Bảng và Biểu đồ)
        st.subheader("📈 Phân bổ điểm số chi tiết các môn")
        
        # Định nghĩa thang điểm (Bins)
        bins = [0, 5, 6, 7, 8, 9, 10.1] # 10.1 để bao gồm cả điểm 10
        labels = ['<5', '5-6', '6-7', '7-8', '8-9', '9-10']
        
        # Tính toán dữ liệu
        dist_data = pd.DataFrame()
        for col in ['Toán', 'Ngữ văn', 'Tiếng Anh']:
            # Sử dụng right=False để [5, 6) là lớn hơn hoặc bằng 5 và nhỏ hơn 6
            counts = pd.cut(df[col], bins=bins, labels=labels, right=False).value_counts().sort_index()
            dist_data[col] = counts
        
        # Vẽ biểu đồ cột chuyên nghiệp
        fig_dist = px.bar(
            dist_data, 
            barmode='group',
            labels={'value': 'Số lượng HS', 'index': 'Khoảng điểm', 'variable': 'Môn học'},
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_dist.update_layout(xaxis_title="Khoảng điểm", yaxis_title="Số lượng học sinh")
        st.plotly_chart(fig_dist, use_container_width=True)
        
        # Hiển thị bảng số liệu với định dạng đẹp
        st.write("**Bảng số liệu chi tiết:**")
        st.dataframe(dist_data.style.background_gradient(cmap='Blues'), use_container_width=True)

        st.markdown("---")
        
        # 3. Biến động điểm số
        fig_box = px.box(df, x="Lớp", y="Tong_Diem", color="Lớp", title="Biến động tổng điểm giữa các lớp")
        st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        # ... (giữ nguyên logic tab 2 như cũ)
        st.subheader("Tương quan giữa các môn học")
        corr = df[['Ngữ văn', 'Tiếng Anh', 'Toán']].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab3:
        # ... (giữ nguyên logic tab 3 như cũ)
        st.subheader("Danh sách học sinh cần hỗ trợ")
        df_weak = df[df['Tong_Diem'] < 15] 
        st.dataframe(df_weak[['Số BD', 'Họ và tên', 'Lớp', 'Tong_Diem', 'Xep_Loai']], use_container_width=True)

    with tab4:
        # ... (giữ nguyên logic tab 4 như cũ)
        st.subheader("Xuất báo cáo chi tiết")
        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
        st.download_button("📥 Tải xuống dữ liệu phân tích đầy đủ", data=to_excel(df), file_name="Bao_Cao_Phan_Tich.xlsx")

else:
    st.info("Vui lòng tải file dữ liệu ở thanh bên trái để bắt đầu phân tích.")