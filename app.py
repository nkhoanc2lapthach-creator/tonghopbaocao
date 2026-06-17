import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, ColumnsAutoSizeMode

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Hệ thống Phân tích Giáo dục Pro", layout="wide")

st.title("🎯 Hệ thống Phân tích Dữ liệu Giáo dục Chuyên sâu")

# --- HÀM HỖ TRỢ AG-GRID ---
def render_pro_table(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, wrapText=True)
    gb.configure_column(df.columns[0], pinned='left') # Ghim cột đầu
    grid_options = gb.build()
    
    return AgGrid(
        df, 
        gridOptions=grid_options, 
        theme='alpine', # Giao diện chuyên nghiệp
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=400
    )

# --- XỬ LÝ DỮ LIỆU ---
@st.cache_data
def process_data(df):
    cols_numeric = ['Ngữ văn', 'Tiếng Anh', 'Toán']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['Tong_Diem'] = df[cols_numeric].sum(axis=1)
    df['Xep_Loai'] = pd.cut(df['Tong_Diem'], bins=[0, 15, 18, 24, 31], labels=['Yếu/Kém', 'Trung bình', 'Khá', 'Giỏi'], right=False)
    return df

# --- SIDEBAR ---
uploaded_file = st.sidebar.file_uploader("Tải file dữ liệu (.xlsx/.csv)", type=["xlsx", "csv"])

if uploaded_file:
    df_raw = pd.read_csv(uploaded_file, skiprows=6) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file, header=6)
    df = process_data(df_raw.dropna(subset=['Số BD']))
    
    list_lop = sorted(df['Lớp'].unique().tolist())
    selected_class = st.sidebar.multiselect("Chọn lớp:", list_lop, default=list_lop)
    df = df[df['Lớp'].isin(selected_class)]

    # --- CÁC TAB ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🔗 Tương quan môn học", "⚠️ Cảnh báo hỗ trợ", "📝 Xuất dữ liệu"])

    with tab1:
        st.header("📊 BÁO CÁO TỔNG QUAN")
        
        # 1. Khung chứa chỉ số chính (Container có Border)
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Tổng HS", len(df))
            col2.metric("TB Toán", f"{df['Toán'].mean():.2f}")
            col3.metric("TB Văn", f"{df['Ngữ văn'].mean():.2f}")
            col4.metric("TB Anh", f"{df['Tiếng Anh'].mean():.2f}")

        # 2. Bảng nhiệt (Heatmap)
        st.subheader("Bảng phân bổ điểm số (Heatmap)")
        bins = [0, 5, 6, 7, 8, 9, 10.01]
        labels = ['<5', '5-6', '6-7', '7-8', '8-9', '9-10']
        freq_table = pd.DataFrame(index=labels)
        for col in ['Toán', 'Ngữ văn', 'Tiếng Anh']:
            freq_table[col] = pd.cut(df[col], bins=bins, labels=labels, right=False).value_counts().sort_index()
        
        # Sử dụng Styler Heatmap
        st.dataframe(freq_table.style.background_gradient(cmap='Blues', axis=0), use_container_width=True)

        # 3. Biểu đồ tròn
        rank_counts = df['Xep_Loai'].value_counts()
        fig_pie = px.pie(values=rank_counts.values, names=rank_counts.index, title="Tỷ lệ học lực", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Tương quan môn học")
        corr = df[['Ngữ văn', 'Tiếng Anh', 'Toán']].corr()
        st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)

    with tab3:
        st.subheader("Danh sách học sinh cần hỗ trợ (Tương tác cao cấp)")
        df_weak = df[df['Tong_Diem'] < 15] 
        if not df_weak.empty:
            # Dùng AG-Grid tại đây
            render_pro_table(df_weak[['Số BD', 'Họ và tên', 'Lớp', 'Tong_Diem', 'Xep_Loai']])
        else:
            st.success("Tuyệt vời! Không có học sinh nào cần hỗ trợ đặc biệt.")

    with tab4:
        st.subheader("Xuất báo cáo")
        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()
        st.download_button("📥 Tải xuống dữ liệu", data=to_excel(df), file_name="Bao_Cao.xlsx")

else:
    st.info("Vui lòng tải file dữ liệu ở thanh bên trái.")