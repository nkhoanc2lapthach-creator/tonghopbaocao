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
    # Đảm bảo các cột số là kiểu số
    cols_numeric = ['Ngữ văn', 'Tiếng Anh', 'Toán']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Tính tổng điểm
    df['Tong_Diem'] = df[cols_numeric].sum(axis=1)
    
    # Phân loại học lực
    def classify(score):
        if score >= 24: return 'Giỏi'
        if score >= 18: return 'Khá'
        if score >= 15: return 'Trung bình'
        return 'Yếu/Kém'
    
    df['Xep_Loai'] = df['Tong_Diem'].apply(classify)
    return df

# --- SIDEBAR: TẢI FILE VÀ LỌC ---
uploaded_file = st.sidebar.file_uploader("Tải file dữ liệu (.xlsx/.csv)", type=["xlsx", "csv"])

if uploaded_file:
    # Đọc file
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file, skiprows=6)
    else:
        df_raw = pd.read_excel(uploaded_file, header=6)
    
    # Xử lý
    df = process_data(df_raw.dropna(subset=['Số BD']))

    # Bộ lọc lớp
    list_lop = sorted(df['Lớp'].unique().tolist())
    selected_class = st.sidebar.multiselect("Chọn lớp để phân tích:", list_lop, default=list_lop)
    df = df[df['Lớp'].isin(selected_class)]

    # --- CÁC TAB CHUYÊN SÂU ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🔗 Tương quan môn học", "⚠️ Cảnh báo hỗ trợ", "📝 Xuất dữ liệu"])

    with tab1:
        st.subheader("📊 Báo cáo chỉ số chi tiết")
        
        # 1. Các chỉ số cơ bản (Metrics)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Tổng HS dự thi", len(df))
        col2.metric("TB Toán", round(df['Toán'].mean(), 2))
        col3.metric("TB Văn", round(df['Ngữ văn'].mean(), 2))
        col4.metric("TB Anh", round(df['Tiếng Anh'].mean(), 2))
        
        st.markdown("---")
        
        # 2. Bảng Min/Max
        st.subheader("Giá trị Cao nhất & Thấp nhất")
        summary_stats = pd.DataFrame({
            "Môn học": ["Toán", "Ngữ văn", "Tiếng Anh"],
            "Điểm cao nhất": [df['Toán'].max(), df['Ngữ văn'].max(), df['Tiếng Anh'].max()],
            "Điểm thấp nhất": [df['Toán'].min(), df['Ngữ văn'].min(), df['Tiếng Anh'].min()]
        })
        st.table(summary_stats)
        
        # 3. Bảng phân bổ điểm số (Binning)
        st.subheader("Phân bổ điểm số theo thang điểm")
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        labels = ['<1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
        
        # Tạo bảng thống kê cho từng môn
        dist_data = {}
        for col in ['Toán', 'Ngữ văn', 'Tiếng Anh']:
            dist_data[col] = pd.cut(df[col], bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
        
        dist_df = pd.DataFrame(dist_data)
        st.table(dist_df)
        
        # 4. Biểu đồ đi kèm
        st.markdown("---")
        fig_box = px.box(df, x="Lớp", y="Tong_Diem", color="Lớp", title="Biến động tổng điểm giữa các lớp")
        st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        st.subheader("Tương quan giữa các môn học")
        if not df.empty:
            corr = df[['Ngữ văn', 'Tiếng Anh', 'Toán']].corr()
            fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Chưa có đủ dữ liệu để tính tương quan.")

    with tab3:
        st.subheader("Danh sách học sinh cần hỗ trợ")
        df_weak = df[df['Tong_Diem'] < 15] 
        if not df_weak.empty:
            st.dataframe(df_weak[['Số BD', 'Họ và tên', 'Lớp', 'Tong_Diem', 'Xep_Loai']], use_container_width=True)
        else:
            st.success("Tuyệt vời! Không có học sinh nào nằm trong danh sách cần hỗ trợ đặc biệt.")

    with tab4:
        st.subheader("Xuất báo cáo chi tiết")
        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
        
        st.download_button("📥 Tải xuống dữ liệu phân tích đầy đủ", data=to_excel(df), file_name="Bao_Cao_Phan_Tich.xlsx")

else:
    st.info("Vui lòng tải file dữ liệu ở thanh bên trái để bắt đầu phân tích.")