with tab1:
        st.header("📊 BÁO CÁO TỔNG QUAN HỌC TẬP")
        
        # 1. Bảng Tổng số HS & Điểm TB
        st.subheader("1. Chỉ số chung")
        summary_data = {
            "Chỉ số": ["Tổng số học sinh", "Điểm trung bình Toán", "Điểm trung bình Văn", "Điểm trung bình Anh"],
            "Giá trị": [
                len(df), 
                round(df['Toán'].mean(), 2), 
                round(df['Ngữ văn'].mean(), 2), 
                round(df['Tiếng Anh'].mean(), 2)
            ]
        }
        st.dataframe(pd.DataFrame(summary_data).set_index("Chỉ số"), use_container_width=True)

        st.markdown("---")

        # 2. Bảng Min/Max
        st.subheader("2. Thống kê cao nhất - thấp nhất")
        min_max_data = {
            "Môn học": ["Toán", "Ngữ văn", "Tiếng Anh"],
            "Cao nhất": [round(df['Toán'].max(), 2), round(df['Ngữ văn'].max(), 2), round(df['Tiếng Anh'].max(), 2)],
            "Thấp nhất": [round(df['Toán'].min(), 2), round(df['Ngữ văn'].min(), 2), round(df['Tiếng Anh'].min(), 2)]
        }
        st.dataframe(pd.DataFrame(min_max_data).set_index("Môn học"), use_container_width=True)

        st.markdown("---")

        # 3. Phân bổ điểm số từng môn (Chi tiết)
        st.subheader("3. Phân bổ điểm số theo thang điểm (Số lượng HS)")
        bins = [0, 5, 6, 7, 8, 9, 10.01]
        labels = ['<5', '5-6', '6-7', '7-8', '8-9', '9-10']
        
        # Tạo bảng phân bổ
        freq_table = pd.DataFrame(index=labels)
        for col in ['Toán', 'Ngữ văn', 'Tiếng Anh']:
            freq_table[col] = pd.cut(df[col], bins=bins, labels=labels, right=False).value_counts().sort_index()
        
        st.dataframe(freq_table.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)

        st.markdown("---")

        # 4. Phân bổ tổng điểm
        st.subheader("4. Phân bổ Tổng điểm")
        # Phân loại theo thang điểm tổng (Giả sử tổng điểm tối đa là 30)
        bins_total = [0, 15, 18, 24, 30]
        labels_total = ['Dưới 15', '15-18', '18-24', 'Trên 24']
        total_dist = pd.cut(df['Tong_Diem'], bins=bins_total, labels=labels_total).value_counts().reset_index()
        total_dist.columns = ['Mức điểm', 'Số lượng HS']
        st.dataframe(total_dist, use_container_width=True)

        # 5. Biểu đồ tròn
        st.subheader("5. Tỷ lệ học lực")
        rank_counts = df['Xep_Loai'].value_counts()
        fig_pie = px.pie(
            values=rank_counts.values, 
            names=rank_counts.index, 
            hole=0.4,
            color=rank_counts.index,
            color_discrete_map={'Giỏi':'#28a745', 'Khá':'#ffc107', 'Trung bình':'#17a2b8', 'Yếu/Kém':'#dc3545'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)