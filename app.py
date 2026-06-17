import streamlit as st
import pandas as pd
import plotly.express as px
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
    # Đọc file
    if uploaded_file.name.endswith('.csv'):
        df_raw = pd.read_csv(uploaded_file, skiprows=6)
    else:
        df_raw = pd.read_excel(uploaded_file, header=6)
    
    # Xử lý dữ liệu
    df = process_data(df_raw.dropna(subset=['Số BD']))
    
    # Bộ lọc
    list_lop = sorted(df['Lớp'].unique().tolist())
    selected_class = st.sidebar.multiselect("Chọn lớp:", list_lop, default=list_lop)
    df = df[df['Lớp'].isin(selected_class)]

    # --- KHỞI TẠO CÁC TAB (Bắt buộc phải có dòng này) ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Tổng quan", "🔗 Tương quan môn học", "⚠️ Cảnh báo hỗ trợ", "📝 Xuất dữ liệu"])

    with tab1:
        st.header("📊 BÁO CÁO TỔNG QUAN HỌC TẬP")
        
        # 1. Chỉ số chung
        st.subheader("1. Chỉ số chung")
        summary_data = {
            "Chỉ số": ["Tổng số học sinh", "Điểm TB Toán", "Điểm TB Văn", "Điểm TB Anh"],
            "Giá trị": [len(df), round(df['Toán'].mean(), 2), round(df['Ngữ văn'].mean(), 2), round(df['Tiếng Anh'].mean(), 2)]
        }
        st.dataframe(pd.DataFrame(summary_data).set_index("Chỉ số"), use_container_width=True)

        # 2. Min/Max
        st.subheader("2. Thống kê cao nhất - thấp nhất")
        min_max_data = {
            "Môn học": ["Toán", "Ngữ văn", "Tiếng Anh"],
            "Cao nhất": [df['Toán'].max(), df['Ngữ văn'].max(), df['Tiếng Anh'].max()],
            "Thấp nhất": [df['Toán'].min(), df['Ngữ văn'].min(), df['Tiếng Anh'].min()]
        }
        st.dataframe(pd.DataFrame(min_max_data).set_index("Môn học"), use_container_width=True)

        # 3. Phân bổ điểm chi tiết các môn
        st.subheader("3. Phân bổ điểm số theo thang điểm (Số lượng HS)")
        bins = [0, 5, 6, 7, 8, 9, 10.01]
        labels = ['<5', '5-6', '6-7', '7-8', '8-9', '9-10']
        freq_table = pd.DataFrame(index=labels)
        for col in ['Toán', 'Ngữ văn', 'Tiếng Anh']:
            freq_table[col] = pd.cut(df[col], bins=bins, labels=labels, right=False).value_counts().sort_index()
        st.dataframe(freq_table.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)

        # 4. Phân bổ tổng điểm
        st.subheader("4. Phân bổ Tổng điểm")
        bins_total = [0, 15, 18, 24, 30]
        labels_total = ['Dưới 15', '15-18', '18-24', 'Trên 24']
        total_dist = pd.cut(df['Tong_Diem'], bins=bins_total, labels=labels_total).value_counts().reset_index()
        total_dist.columns = ['Mức điểm', 'Số lượng HS']
        st.dataframe(total_dist, use_container_width=True)

        # 5. Tỷ lệ học lực
        st.subheader("5. Tỷ lệ học lực")
        rank_counts = df['Xep_Loai'].value_counts()
        fig_pie = px.pie(values=rank_counts.values, names=rank_counts.index, hole=0.4, 
                         color_discrete_map={'Giỏi':'#28a745', 'Khá':'#ffc107', 'Trung bình':'#17a2b8', 'Yếu/Kém':'#dc3545'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.subheader("Tương quan giữa các môn học")
        corr = df[['Ngữ văn', 'Tiếng Anh', 'Toán']].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr, use_container_width=True)

    with tab3:
        st.subheader("Danh sách học sinh cần hỗ trợ")
        df_weak = df[df['Tong_Diem'] < 15] 
        st.dataframe(df_weak[['Số BD', 'Họ và tên', 'Lớp', 'Tong_Diem', 'Xep_Loai']], use_container_width=True)

    with tab4:
        st.subheader("Xuất báo cáo chi tiết")
        def to_excel(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            return output.getvalue()
        st.download_button("📥 Tải xuống báo cáo", data=to_excel(df), file_name="Bao_Cao_Phan_Tich.xlsx")

else:
    st.info("Vui lòng tải file dữ liệu ở thanh bên trái để bắt đầu.")