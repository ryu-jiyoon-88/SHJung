import streamlit as st
import pandas as pd
import plotly.express as px

# 웹 페이지 설정
st.set_page_config(page_title="통합 광고 보고서 대시보드", layout="wide")

st.title("📊 통합 온라인 광고 보고서")
st.info("네이버, 구글, 카카오 등의 엑셀 파일을 업로드하세요.")

# 1. 파일 업로드 (여러 개 선택 가능)
uploaded_files = st.file_uploader("엑셀 파일을 선택하세요", type=['xlsx', 'csv'], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    
    for file in uploaded_files:
        # 파일 읽기
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 매체명 자동 인식 (파일명 기준 또는 선택)
        media_name = st.sidebar.text_input(f"{file.name}의 매체명", value=file.name.split('.')[0])
        df['매체'] = media_name
        all_data.append(df)

    if all_data:
        # 데이터 통합
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 필수 항목 컬럼 매핑 (매체마다 컬럼명이 다를 수 있으므로 사용자 지정 필요)
        st.subheader("📍 데이터 컬럼 매핑")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1: date_col = st.selectbox("날짜(기간) 컬럼 선택", combined_df.columns)
        with col2: campaign_col = st.selectbox("캠페인 컬럼 선택", combined_df.columns)
        with col3: group_col = st.selectbox("그룹 컬럼 선택", combined_df.columns)
        with col4: metric_col = st.selectbox("성과지표(예: 클릭수, 비용)", combined_df.columns)

        # 데이터 정리
        combined_df[date_col] = pd.to_datetime(combined_df[date_col]).dt.date
        
        # --- 시각화 섹션 ---
        st.divider()
        st.subheader("📈 성과 분석 그래프")
        
        tab1, tab2, tab3 = st.tabs(["매체별", "기간별", "캠페인/그룹별"])
        
        with tab1:
            fig1 = px.pie(combined_df, values=metric_col, names='매체', title=f'매체별 {metric_col} 비중')
            st.plotly_chart(fig1, use_container_width=True)
            
        with tab2:
            df_trend = combined_df.groupby(date_col)[metric_col].sum().reset_index()
            fig2 = px.line(df_trend, x=date_col, y=metric_col, title=f'일자별 {metric_col} 추이')
            st.plotly_chart(fig2, use_container_width=True)
            
        with tab3:
            fig3 = px.bar(combined_df, x=campaign_col, y=metric_col, color='매체', title=f'캠페인별 {metric_col} 성과')
            st.plotly_chart(fig3, use_container_width=True)

        # --- 데이터 표 출력 ---
        st.subheader("📋 통합 데이터 상세")
        st.dataframe(combined_df, use_container_width=True)

        # 엑셀 다운로드 버튼 (통합본)
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8-sig')

        csv = convert_df(combined_df)
        st.download_button("통합 데이터 다운로드 (CSV)", data=csv, file_name="integrated_report.csv", mime="text/csv")
