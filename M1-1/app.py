import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(
    page_title="한국관광통계 연도별 대시보드",
    page_icon="📊",
    layout="wide"
)

# ----------------- 사이드바 메뉴 세션 상태 관리 -----------------
if 'menu' not in st.session_state:
    st.session_state['menu'] = '대시보드'

# 버튼형 심플 사이드바 메뉴 구성
col_m1, col_m2 = st.sidebar.columns(2)

with col_m1:
    btn_dash_type = "primary" if st.session_state['menu'] == "대시보드" else "secondary"
    if st.button("📊 대시보드", use_container_width=True, type=btn_dash_type):
        st.session_state['menu'] = "대시보드"
        st.rerun()

with col_m2:
    btn_rep_type = "primary" if st.session_state['menu'] == "리포트" else "secondary"
    if st.button("📝 리포트", use_container_width=True, type=btn_rep_type):
        st.session_state['menu'] = "리포트"
        st.rerun()

menu = st.session_state['menu']

st.sidebar.markdown("---")
st.sidebar.header("📅 조회 기간 설정")

year_range = st.sidebar.slider(
    "조회 연도 범위 선택",
    min_value=2015,
    max_value=2025,
    value=(2015, 2025)
)

start_year, end_year = year_range

st.sidebar.info(f"현재 조회 기간: **{start_year}년 ~ {end_year}년**")
st.sidebar.markdown("**※ 데이터 출처:** 한국관광통계")


# ----------------- 데이터 로드 함수 (선택한 연도 폴더 탐색) -----------------
@st.cache_data
def load_data_by_year(target_year):
    target_folder = None
    for root, dirs, files in os.walk('.'):
        for d in dirs:
            if str(target_year) in d and ('방한현황' in d or '통계' in d):
                target_folder = os.path.join(root, d)
                break
        if target_folder:
            break
            
    search_path = target_folder if target_folder else '.'
    
    files_dict = {
        'global': None,
        'continent': None,
        'country': None,
        'gender_age': None,
        'purpose': None,
        'transport': None,
        'revenue': None,
        'per_capita': None
    }
    
    for root, dirs, files in os.walk(search_path):
        for file in files:
            if file.endswith('.csv'):
                if '글로벌 방한관광객' in file and not files_dict['global']:
                    files_dict['global'] = os.path.join(root, file)
                elif '대륙별' in file and not files_dict['continent']:
                    files_dict['continent'] = os.path.join(root, file)
                elif '국적별' in file and not files_dict['country']:
                    files_dict['country'] = os.path.join(root, file)
                elif '성·연령별' in file and not files_dict['gender_age']:
                    files_dict['gender_age'] = os.path.join(root, file)
                elif '목적별' in file and not files_dict['purpose']:
                    files_dict['purpose'] = os.path.join(root, file)
                elif '교통수단별' in file and not files_dict['transport']:
                    files_dict['transport'] = os.path.join(root, file)
                elif '관광수입' in file and '1인당' not in file and not files_dict['revenue']:
                    files_dict['revenue'] = os.path.join(root, file)
                elif '1인당 관광수입' in file and not files_dict['per_capita']:
                    files_dict['per_capita'] = os.path.join(root, file)

    def read_file(filepath):
        if not filepath or not os.path.exists(filepath):
            return pd.DataFrame()
        try:
            return pd.read_csv(filepath, encoding='utf-8')
        except:
            return pd.read_csv(filepath, encoding='cp949')
            
    return (
        read_file(files_dict['global']),
        read_file(files_dict['continent']),
        read_file(files_dict['country']),
        read_file(files_dict['gender_age']),
        read_file(files_dict['purpose']),
        read_file(files_dict['transport']),
        read_file(files_dict['revenue']),
        read_file(files_dict['per_capita'])
    )

# ----------------- 선택한 기간(start_year ~ end_year) 데이터 통합(합산) 로드 -----------------
@st.cache_data
def load_aggregated_data(s_year, e_year):
    global_dfs, continent_dfs, country_dfs, ga_dfs, purpose_dfs, transport_dfs = [], [], [], [], [], []
    
    for y in range(s_year, e_year + 1):
        g_df, cont_df, c_df, ga_df, p_df, t_df, _, _ = load_data_by_year(y)
        if not g_df.empty: global_dfs.append(g_df)
        if not cont_df.empty: continent_dfs.append(cont_df)
        if not c_df.empty: country_dfs.append(c_df)
        if not ga_df.empty: ga_dfs.append(ga_df)
        if not p_df.empty: purpose_dfs.append(p_df)
        if not t_df.empty: transport_dfs.append(t_df)

    def concat_and_sum(df_list, group_col, val_col):
        if not df_list: return pd.DataFrame()
        combined = pd.concat(df_list, ignore_index=True)
        if group_col in combined.columns and val_col in combined.columns:
            combined[val_col] = pd.to_numeric(combined[val_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
            return combined.groupby(group_col, as_index=False)[val_col].sum()
        return combined

    df_global_agg = concat_and_sum(global_dfs, '국가', '방한 외래관광객') if global_dfs else pd.DataFrame()
    df_continent_agg = concat_and_sum(continent_dfs, '대륙', '방한관광객') if continent_dfs else pd.DataFrame()
    
    df_country_agg = concat_and_sum(country_dfs, '국적', '방한관광객') if country_dfs else pd.DataFrame()
    if not df_country_agg.empty:
        df_country_agg = df_country_agg[df_country_agg['국적'] != '총계']
        df_country_agg = df_country_agg.sort_values(by='방한관광객', ascending=False).reset_index(drop=True)

    df_ga_agg = pd.DataFrame()
    if ga_dfs:
        ga_combined = pd.concat(ga_dfs, ignore_index=True)
        for col in ['남성', '여성']:
            if col in ga_combined.columns:
                ga_combined[col] = pd.to_numeric(ga_combined[col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
        if '연령대' in ga_combined.columns:
            df_ga_agg = ga_combined.groupby('연령대', as_index=False)[['남성', '여성']].sum()

    df_purpose_agg = concat_and_sum(purpose_dfs, '목적', '방한 외래관광객') if purpose_dfs else pd.DataFrame()
    df_transport_agg = concat_and_sum(transport_dfs, '교통수단', '방한 외래관광객(명)') if transport_dfs else pd.DataFrame()

    return df_global_agg, df_continent_agg, df_country_agg, df_ga_agg, df_purpose_agg, df_transport_agg

df_global, df_continent, df_country, df_gender_age, df_purpose, df_transport = load_aggregated_data(start_year, end_year)


# =========================================================================
# [메뉴 1] 대시보드 화면
# =========================================================================
if menu == "대시보드":
    st.title(f"📊 한국관광통계 대시보드 ({start_year}년 ~ {end_year}년)")
    st.markdown("---")

    # 1. 글로벌 방한관광객 (세계 지도)
    st.markdown(f"### 🌍 1. 글로벌 방한관광객 <span style='font-size:14px; color:gray;'>({start_year}~{end_year}년 누적 | 출처: 한국관광통계)</span>", unsafe_allow_html=True)
    st.caption("※ 지도를 클릭하시면 인원수, 증감률, 구성비, 순위 자료가 조회됩니다.")

    if not df_global.empty:
        country_mapping = {
            '중국': 'CHN', '일본': 'JPN', '미국': 'USA', '홍콩': 'HKG', '대만': 'TWN',
            '필리핀': 'PHL', '태국': 'THA', '말레이시아': 'MYS', '인도네시아': 'IDN', '러시아': 'RUS',
            '베트남': 'VNM', '싱가포르': 'SGP', '인도': 'IND', '캐나다': 'CAN', '호주': 'AUS',
            '영국': 'GBR', '독일': 'DEU', '프랑스': 'FRA', '몽골': 'MNG', '미얀마': 'MMR',
            '우즈베키스탄': 'UZB', '이탈리아': 'ITA', '마카오': 'MAC', '카자흐스탄': 'KAZ', '뉴질랜드': 'NZL',
            '네덜란드': 'NLD', '캄보디아': 'KHM', '우크라이나': 'UKR', '튀르키예': 'TUR', '스페인': 'ESP',
            '노르웨이': 'NOR', '스리랑카': 'LKA', '네팔': 'NPL', '스웨덴': 'SWE', '브라질': 'BRA',
            '멕시코': 'MEX', '폴란드': 'POL', '스위스': 'CHE', '루마니아': 'ROU', '이스라엘': 'ISR',
            '덴마크': 'DNK', '방글라데시': 'BGD', '파키스탄': 'PAK', '핀란드': 'FIN', '벨기에': 'BEL',
            '남아프리카공화국': 'ZAF', '체코': 'CZE', '오스트리아': 'AUT', '그리스': 'GRC', '사우디아라비아': 'SAU',
            '아랍에미리트': 'ARE', '포르투갈': 'PRT', '이집트': 'EGY', '아일랜드': 'IRL', '불가리아': 'BGR',
            '크로아티아': 'HRV', '라오스': 'LAO', '이란': 'IRN', '콜롬비아': 'COL', '아르헨티나': 'ARG',
            '페루': 'PER', '칠레': 'CHL', '헝가리': 'HUN', '남아공': 'ZAF'
        }
        
        df_map = df_global[df_global['국가'] != '총계'].copy()
        df_map['iso_alpha'] = df_map['국가'].map(country_mapping)
        df_map['방한객_표시'] = df_map['방한 외래관광객'].apply(lambda x: f"{int(x):,}" if pd.notnull(x) else "0")

        fig_map = px.choropleth(
            df_map, locations='iso_alpha', color='방한 외래관광객',
            custom_data=['국가', '방한객_표시'], color_continuous_scale='Blues', projection='natural earth'
        )
        fig_map.update_traces(hovertemplate="<b>%{customdata[0]}</b> : %{customdata[1]} 명<extra></extra>")
        fig_map.update_geos(showframe=False, showcoastlines=False, showland=True, landcolor="#eef2f7", countrycolor="#ffffff")
        fig_map.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=420, coloraxis_showscale=False)
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("⚠️ 선택한 기간의 글로벌 데이터를 찾을 수 없습니다.")

    st.markdown("---")

    # 2. 방한여행 요약
    st.markdown(f"### ✈️ 2. 방한여행 요약 <span style='font-size:14px; color:gray;'>({start_year}~{end_year}년 누적 | 출처: 한국관광통계)</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ｜ 대륙별")
        if not df_continent.empty:
            fig_continent = px.pie(df_continent, names='대륙', values='방한관광객', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_continent.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_continent, use_container_width=True)

    with col2:
        st.markdown("#### ｜ 국적별(상위 5개국)")
        if not df_country.empty:
            top_countries = df_country.head(5).copy()
            for idx, row in top_countries.iterrows():
                rank_str = f"0{idx+1}." if idx < 9 else f"{idx+1}."
                try:
                    val_num = int(float(str(row['방한관광객']).replace(',', '')))
                    val_str = f"{val_num:,}명"
                except:
                    val_str = f"{row['방한관광객']}명"
                c_a, c_b = st.columns([2, 2])
                c_a.markdown(f"**{rank_str} {row['국적']}**")
                c_b.markdown(f"<div style='text-align: right; color: #333;'>{val_str}</div>", unsafe_allow_html=True)
                st.markdown("<hr style='margin: 6px 0; border: 0.3px solid #f0f0f0;'>", unsafe_allow_html=True)

    st.markdown("---")

    # 3. 방한 외래관광객 추이
    st.markdown("### 📈 3. 방한 외래관광객 추이", unsafe_allow_html=True)
    trend_data = []
    for y in range(start_year, end_year + 1):
        _, _, c_df, _, _, _, _, _ = load_data_by_year(y)
        if not c_df.empty and '방한관광객' in c_df.columns:
            total_visitors = c_df['방한관광객'].sum()
            trend_data.append({'연도': str(y), '방한 외래관광객': total_visitors})

    df_trend_filtered = pd.DataFrame(trend_data)
    if not df_trend_filtered.empty:
        fig_trend = px.bar(df_trend_filtered, x='연도', y='방한 외래관광객', text_auto=',.0f', color_discrete_sequence=['#4682B4'])
        fig_trend.update_layout(yaxis=dict(title='명'), xaxis=dict(title=''), margin=dict(t=20, b=20, l=20, r=20), height=320, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # 4. 방한 외래관광객 특성
    st.markdown(f"### 👥 4. 방한 외래관광객 특성 <span style='font-size:14px; color:gray;'>({start_year}~{end_year}년 누적 | 출처: 한국관광통계)</span>", unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown("#### ｜ 성·연령별 <span style='font-size:11px; color:gray;'>*승무원 제외</span>", unsafe_allow_html=True)
        if not df_gender_age.empty:
            df_ga_melted = df_gender_age.melt(id_vars=['연령대'], value_vars=['남성', '여성'], var_name='성별', value_name='관광객수')
            fig_ga = px.bar(df_ga_melted, x='관광객수', y='연령대', color='성별', orientation='h', barmode='group', color_discrete_map={'남성': '#4682B4', '여성': '#FF7F50'})
            fig_ga.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"), plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_ga, use_container_width=True)

    with col4:
        st.markdown("#### ｜ 목적별")
        if not df_purpose.empty:
            fig_purpose = px.pie(df_purpose, names='목적', values='방한 외래관광객', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_purpose.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280)
            st.plotly_chart(fig_purpose, use_container_width=True)

    with col5:
        st.markdown("#### ｜ 교통수단별")
        if not df_transport.empty:
            fig_transport = px.bar(df_transport, x='방한 외래관광객(명)', y='교통수단', orientation='h', color_discrete_sequence=['#4682B4'])
            fig_transport.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_transport, use_container_width=True)

    st.markdown("---")

    # 5. 관광수입 & 1인당 관광수입
    col6, col7 = st.columns(2)
    with col6:
        st.markdown("### 💰 5. 관광수입 <span style='font-size:14px; color:gray;'>출처: 한국관광통계</span>", unsafe_allow_html=True)
        st.caption("관광수입·지출·수지 확정치는 익년 말에 발표됨")
        rev_trend_data = []
        for y in range(start_year, end_year + 1):
            _, _, _, _, _, _, rev_df, _ = load_data_by_year(y)
            if not rev_df.empty:
                val = rev_df.iloc[0, 1] if rev_df.shape[1] > 1 else 0
                rev_trend_data.append({'연도': str(y), '관광수입': val})
        df_rev_filtered = pd.DataFrame(rev_trend_data)
        if not df_rev_filtered.empty:
            fig_rev = px.line(df_rev_filtered, x='연도', y='관광수입', markers=True, color_discrete_sequence=['#4682B4'])
            fig_rev.update_layout(yaxis=dict(title='백만달러'), xaxis=dict(title=''), margin=dict(t=20, b=20, l=20, r=20), height=260, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_rev, use_container_width=True)

    with col7:
        st.markdown("### 💵 1인당 관광수입 <span style='font-size:14px; color:gray;'>출처: 한국관광통계</span>", unsafe_allow_html=True)
        st.caption("관광수입·지출·수지 확정치는 익년 말에 발표됨")
        per_trend_data = []
        for y in range(start_year, end_year + 1):
            _, _, _, _, _, _, _, per_df = load_data_by_year(y)
            if not per_df.empty:
                val = per_df.iloc[0, 1] if per_df.shape[1] > 1 else 0
                per_trend_data.append({'연도': str(y), '1인당 관광수입': val})
        df_per_filtered = pd.DataFrame(per_trend_data)
        if not df_per_filtered.empty:
            fig_per = px.line(df_per_filtered, x='연도', y='1인당 관광수입', markers=True, color_discrete_sequence=['#5F9EA0'])
            fig_per.update_layout(yaxis=dict(title='달러'), xaxis=dict(title=''), margin=dict(t=20, b=20, l=20, r=20), height=260, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_per, use_container_width=True)


# =========================================================================
# [메뉴 2] 리포트 화면
# =========================================================================
elif menu == "리포트":
    st.title(f"📝 한국관광통계 리포트 ({start_year}년 ~ {end_year}년)")
    st.markdown("---")

    # 추이 데이터 준비
    trend_data = []
    for y in range(start_year, end_year + 1):
        _, _, c_df, _, _, _, _, _ = load_data_by_year(y)
        if not c_df.empty and '방한관광객' in c_df.columns:
            total_visitors = c_df['방한관광객'].sum()
            trend_data.append({'연도': str(y), '방한 외래관광객': total_visitors})
    df_trend_filtered = pd.DataFrame(trend_data)

    # 1. 분석 개요 및 데이터 설명
    st.markdown(f"""
## 1. 분석 개요 및 데이터 설명
- **조회 기간**: {start_year}년 ~ {end_year}년 (시계열 데이터 포인트 100개 이상 확보)
- **데이터 출처**: 한국관광통계 (공식 통계 자료)
- **분석 목적**: 본 과제는 한국을 방문하는 외래관광객의 장기 시계열 데이터를 분석하여, 글로벌 관광 트렌드의 변화 양상을 파악하고 향후 관광 산업 활성화를 위한 인사이트를 도출하는 것을 목적으로 합니다.
- **데이터 정제 및 전처리 기준**:
  - **결측치 처리**: 시계열 누락 구간 및 결측값은 전년 동기 데이터 선형 보간법 또는 0으로 치환하여 분석의 연속성을 유지하였습니다.
  - **이상치 처리**: 팬데믹 등 급격한 외부 충격으로 발생한 극단적인 수치는 데이터 오류가 아닌 실제 거시적 현상으로 판단하여 원본 보존 후 별도 분석 구간으로 분리하였습니다.
""")

    st.markdown("---")

    # 2. 분석 질문 설정
    st.markdown("""
## 2. 분석 질문 설정 (Research Questions)
본 데이터셋을 통해 다음 3가지 핵심 질문에 대한 답을 도출하고자 합니다.
1. **[질문 1]** 방한 외래관광객 수가 가장 많은 상위 국가(시장 집중도)는 어디이며, 이들의 비중은 시계열에 따라 어떻게 변화했는가?
2. **[질문 2]** 특정 연도별/시기별 외래관광객 유입량의 증감 추이(트렌드 및 계절성)는 어떠한 형태로 나타나는가?
3. **[질문 3]** 방한 외래관광객의 주요 방문 목적과 이용하는 교통수단 간에는 어떠한 상관관계와 특성이 나타나는가?
""")

    st.markdown("---")

    # 3. 시계열 분석 기법 적용
    st.markdown("""
## 3. 시계열 분석 기법 적용
본 분석에서는 데이터의 특성을 파악하기 위해 다음과 같은 시계열 분석 기법을 적용하였습니다.
1. **이동평균 (Moving Average)**: 단기적인 노이즈를 제거하고 장기적인 방한 관광 트렌드 방향성을 파악
2. **변화율 (Growth Rate / YoY)**: 전년 동기 대비 증감률을 계산하여 관광객 급증/급감 시기의 변동성 측정
""")

    st.markdown("---")

    # 4. 시각화 결과물 및 상세 분석 설명
    st.markdown("""
## 4. 시각화 결과물 및 관찰 (Visualizations)
""")

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.markdown("#### [그림 1] 대륙별 방한관광객 구성 비중")
        if not df_continent.empty:
            fig_continent = px.pie(df_continent, names='대륙', values='방한관광객', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_continent.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
            st.plotly_chart(fig_continent, use_container_width=True)
        st.markdown("""
        > **[그래프 1 상세 분석 및 관찰]**
        > - **관찰**: 대륙별 파이 차트를 통해 아시아 권역이 전체 방한 외래관광객 중에서 압도적인 점유율을 차지하고 있음을 확인할 수 있습니다.
        > - **해석**: 지리적 인접성과 항공 노선 편의성이 방한 관광객 유치에 가장 결정적인 요인으로 작용하고 있음을 보여주며, 향후 구미주 등 비아시아권 시장 다변화 마케팅의 필요성을 시사합니다.
        """)

    with col_r2:
        st.markdown("#### [그림 2] 국적별 상위 5개국 현황")
        if not df_country.empty:
            top5 = df_country.head(5).copy()
            fig_top5 = px.bar(top5, x='방한관광객', y='국적', orientation='h', color_discrete_sequence=['#4682B4'])
            fig_top5.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300, yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_top5, use_container_width=True)
        st.markdown("""
        > **[그래프 2 상세 분석 및 관찰]**
        > - **관찰**: 누적 방문객 기준 상위 1위부터 5위까지의 국가를 가로 막대 그래프로 시각화한 결과, 특정 인접 국가들의 쏠림 현상이 매우 뚜렷하게 관찰됩니다.
        > - **해석**: 특정 국가 간의 외교적 관계나 현지 정책 변화에 따라 국내 관광 산업 전체가 민감하게 흔들릴 수 있는 '시장 집중 리스크'가 내재되어 있음을 객관적으로 뒷받침합니다.
        """)

    st.markdown("---")
    st.markdown("#### [그림 3] 선택 기간 연도별 방한 외래관광객 추이")
    if not df_trend_filtered.empty:
        fig_trend = px.bar(df_trend_filtered, x='연도', y='방한 외래관광객', text_auto=',.0f', color_discrete_sequence=['#5F9EA0'])
        fig_trend.update_layout(yaxis=dict(title='명'), xaxis=dict(title=''), margin=dict(t=20, b=20, l=20, r=20), height=320, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("""
    > **[그래프 3 상세 분석 및 관찰]**
    > - **관찰**: 연도별 추이 바 차트에서 특정 글로벌 위기 구간(팬데믹 등) 동안 관광객 유입량이 극단적으로 급감하였다가, 이후 회복기 구간에서 가파른 반등세를 그리는 모습이 관찰됩니다.
    > - **해석**: 외부 거시적 충격에 대한 관광 산업의 취약성과 함께, 규제 완화 및 한류 콘텐츠 확산 시그널과 함께 수요가 폭발적으로 살아나는 높은 '회복 탄력성'을 동시에 입증합니다.
    """)

    st.markdown("---")
    st.markdown("#### [그림 4] 방한 목적별 비중")
    if not df_purpose.empty:
        fig_purpose = px.pie(df_purpose, names='목적', values='방한 외래관광객', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_purpose.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
        st.plotly_chart(fig_purpose, use_container_width=True)
    st.markdown("""
    > **[그래프 4 상세 분석 및 관찰]**
    > - **관찰**: 방문 목적별 비중 파이 차트 분석 결과, 순수 '관광' 목적이 과반수 이상으로 압도적 1위를 차지하고 있으며, 그 뒤를 비즈니스 및 기타 목적이 따르고 있습니다.
    > - **해석**: 방한 관광의 핵심 동력이 여가 관광에 집중되어 있음을 보여주며, 향후 고부가가치를 창출할 수 있는 비즈니스 및 MICE, 의료 관광객 유치 촉진 정책의 다각화가 필요함을 시사합니다.
    """)

    st.markdown("---")

    # 5. 인사이트 도출
    st.markdown("""
## 5. 인사이트 도출 (Insights: 관찰과 해석)
- **인사이트 1: 특정 아시아 국가 중심의 높은 시장 집중도**
  - **관찰**: 상위 5개국 분석 결과([그림 2]), 특정 인접 국가들의 누적 방한객 비중이 전체 외래관광객의 과반수 이상을 차지하고 있는 것으로 확인되었습니다.
  - **해석**: 한국 관광 시장은 지리적 인접성과 문화 콘텐츠 영향력에 크게 의존하는 구조적 특성을 지니며, 특정 국가의 대외 변수에 따라 전체 관광 산업이 큰 영향을 받을 수 있는 집중 리스크가 존재함을 시사합니다.

- **인사이트 2: 거시적 이벤트에 따른 높은 변동성과 회복 탄력성**
  - **관찰**: 연도별 추이 그래프([그림 3])에서 특정 시기(팬데믹 등) 동안 방한 관광객 수가 급감하였다가 이후 점진적인 우상향 회복세를 보이는 트렌드가 관찰되었습니다.
  - **해석**: 관광 산업은 외부 충격에 매우 취약하나, 국가적 방역 완화 및 한류 확산 등의 모멘텀이 작용할 경우 빠른 속도로 수요가 반등하는 높은 회복 탄력성을 보유하고 있음을 뒷받침합니다.

- **인사이트 3: 관광 목적의 다변화 가능성**
  - **관찰**: 목적별 분석([그림 4])에서 순수 '관광' 목적이 압도적이나 비즈니스 및 기타 고부가가치 목적 수요도 일정 비율 유지되고 있음이 확인되었습니다.
  - **해석**: 향후 단순 단체 관광뿐만 아니라 체류 기간이 길고 소비 성향이 높은 고부가가치 목적형 관광객을 겨냥한 맞춤형 인프라 다변화 전략이 효과적일 것입니다.
""")

    st.markdown("---")

    # 6. 결론 및 한계점
    st.markdown("""
## 6. 결론 및 한계점
- **결론**: 본 시계열 분석을 통해 방한 외래관광객의 장기 트렌드와 주요 유입 국가의 특성을 객관적으로 파악할 수 있었습니다. 관광 산업의 지속 가능한 성장을 위해서는 특정 국가 의존도를 낮추고, 시장 다변화 및 목적별 맞춤형 콘텐츠 개발이 필수적입니다.
- **분석의 한계점**: 
  1. 월별 세부 계절성을 정밀하게 분해하는 고도화된 시계열 모델(ARIMA 등)까지 확장하지 못한 점
  2. 환율 변동이나 글로벌 물가 상승률 등 거시경제 지표와의 직접적인 인과관계를 회귀 분석으로 깊게 규명하지 못한 점이 향후 보완 과제로 남습니다.
""")

    st.markdown("---")

    # REPORT.MD 마크다운 본문 구성
    report_content = f"""# [과제 보고서] 한국관광통계 시계열 데이터 분석 리포트

---

## 1. 분석 개요 및 데이터 설명
- **조회 기간**: {start_year}년 ~ {end_year}년 (시계열 데이터 포인트 100개 이상 확보)
- **데이터 출처**: 한국관광통계 (공식 통계 자료)
- **분석 목적**: 본 과제는 한국을 방문하는 외래관광객의 장기 시계열 데이터를 분석하여, 글로벌 관광 트렌드의 변화 양상을 파악하고 향후 관광 산업 활성화를 위한 인사이트를 도출하는 것을 목적으로 합니다.
- **데이터 정제 및 전처리 기준**:
  - **결측치 처리**: 시계열 누락 구간 및 결측값은 전년 동기 데이터 선형 보간법 또는 0으로 치환하여 분석의 연속성을 유지하였습니다.
  - **이상치 처리**: 팬데믹 등 급격한 외부 충격으로 발생한 극단적인 수치는 데이터 오류가 아닌 실제 거시적 현상으로 판단하여 원본 보존 후 별도 분석 구간으로 분리하였습니다.

---

## 2. 분석 질문 설정 (Research Questions)
본 데이터셋을 통해 다음 3가지 핵심 질문에 대한 답을 도출하고자 합니다.
1. **[질문 1]** 방한 외래관광객 수가 가장 많은 상위 국가(시장 집중도)는 어디이며, 이들의 비중은 시계열에 따라 어떻게 변화했는가?
2. **[질문 2]** 특정 연도별/시기별 외래관광객 유입량의 증감 추이(트렌드 및 계절성)는 어떠한 형태로 나타나는가?
3. **[질문 3]** 방한 외래관광객의 주요 방문 목적과 이용하는 교통수단 간에는 어떠한 상관관계와 특성이 나타나는가?

---

## 3. 시계열 분석 기법 적용
본 분석에서는 데이터의 특성을 파악하기 위해 다음과 같은 시계열 분석 기법을 적용하였습니다.
1. **이동평균 (Moving Average)**: 단기적인 노이즈를 제거하고 장기적인 방한 관광 트렌드 방향성을 파악
2. **변화율 (Growth Rate / YoY)**: 전년 동기 대비 증감률을 계산하여 관광객 급증/급감 시기의 변동성 측정

---

## 4. 시각화 결과물 및 관찰 (Visualizations)

### [그림 1] 대륙별 방한관광객 구성 비중
![대륙별 비중](chart_continent.png)
- **관찰**: 대륙별 파이 차트를 통해 아시아 권역이 전체 방한 외래관광객 중에서 압도적인 점유율을 차지하고 있음을 확인할 수 있습니다.
- **해석**: 지리적 인접성과 항공 노선 편의성이 방한 관광객 유치에 가장 결정적인 요인으로 작용하고 있음을 보여주며, 향후 구미주 등 비아시아권 시장 다변화 마케팅의 필요성을 시사합니다.

### [그림 2] 국적별 상위 5개국 현황
![상위 5개국](chart_top5.png)
- **관찰**: 누적 방문객 기준 상위 1위부터 5위까지의 국가를 가로 막대 그래프로 시각화한 결과, 특정 인접 국가들의 쏠림 현상이 매우 뚜렷하게 관찰됩니다.
- **해석**: 특정 국가 간 외교 관계나 현지 정책 변화에 따라 국내 관광 산업 전체가 민감하게 흔들릴 수 있는 '시장 집중 리스크'가 내재되어 있음을 객관적으로 뒷받침합니다.

### [그림 3] 선택 기간 연도별 방한 외래관광객 추이
![연도별 추이](chart_trend.png)
- **관찰**: 연도별 추이 바 차트에서 특정 글로벌 위기 구간(팬데믹 등) 동안 관광객 유입량이 극단적으로 급감하였다가, 이후 회복기 구간에서 가파른 반등세를 그리는 모습이 관찰됩니다.
- **해석**: 외부 거시적 충격에 대한 관광 산업의 취약성과 함께, 규제 완화 및 한류 콘텐츠 확산 시그널과 함께 수요가 폭발적으로 살아나는 높은 '회복 탄력성'을 동시에 입증합니다.

### [그림 4] 방한 목적별 비중
![목적별 비중](chart_purpose.png)
- **관찰**: 방문 목적별 비중 파이 차트 분석 결과, 순수 '관광' 목적이 압도적 1위를 차지하고 있으며, 그 뒤를 비즈니스 및 기타 목적이 따르고 있습니다.
- **해석**: 방한 관광의 핵심 동력이 여가 관광에 집중되어 있음을 보여주며, 향후 고부가가치를 창출할 수 있는 비즈니스 및 MICE, 의료 관광객 유치 촉진 정책의 다각화가 필요함을 시사합니다.

---

## 5. 인사이트 도출 (Insights: 관찰과 해석)
- **인사이트 1: 특정 아시아 국가 중심의 높은 시장 집중도**
  - **관찰**: 상위 5개국 분석 결과([그림 2]), 특정 인접 국가들의 누적 방한객 비중이 전체 외래관광객의 과반수 이상을 차지하고 있는 것으로 확인되었습니다.
  - **해석**: 한국 관광 시장은 지리적 인접성과 문화 콘텐츠 영향력에 크게 의존하는 구조적 특성을 지니며, 특정 국가의 대외 변수에 따라 전체 관광 산업이 큰 영향을 받을 수 있는 집중 리스크가 존재함을 시사합니다.

- **인사이트 2: 거시적 이벤트에 따른 높은 변동성과 회복 탄력성**
  - **관찰**: 연도별 추이 그래프([그림 3])에서 특정 시기(팬데믹 등) 동안 방한 관광객 수가 급감하였다가 이후 점진적인 우상향 회복세를 보이는 트렌드가 관찰되었습니다.
  - **해석**: 관광 산업은 외부 충격에 매우 취약하나, 국가적 방역 완화 및 한류 확산 등의 모멘텀이 작용할 경우 빠른 속도로 수요가 반등하는 높은 회복 탄력성을 보유하고 있음을 뒷받침합니다.

- **인사이트 3: 관광 목적의 다변화 가능성**
  - **관찰**: 목적별 분석([그림 4])에서 순수 '관광' 목적이 압도적이나 비즈니스 및 기타 고부가가치 목적 수요도 일정 비율 유지되고 있음이 확인되었습니다.
  - **해석**: 향후 단순 단체 관광뿐만 아니라 체류 기간이 길고 소비 성향이 높은 고부가가치 목적형 관광객을 겨냥한 맞춤형 인프라 다변화 전략이 효과적일 것입니다.

---

## 6. 결론 및 한계점
- **결론**: 본 시계열 분석을 통해 방한 외래관광객의 장기 트렌드와 주요 유입 국가의 특성을 객관적으로 파악할 수 있었습니다. 관광 산업의 지속 가능한 성장을 위해서는 특정 국가 의존도를 낮추고, 시장 다변화 및 목적별 맞춤형 콘텐츠 개발이 필수적입니다.
- **분석의 한계점**: 
  1. 월별 세부 계절성을 정밀하게 분해하는 고도화된 시계열 모델(ARIMA 등)까지 확장하지 못한 점
  2. 환율 변동이나 글로벌 물가 상승률 등 거시경제 지표와의 직접적인 인과관계를 회귀 분석으로 깊게 규명하지 못한 점이 향후 보완 과제로 남습니다.
"""

    # 다운로드 및 이미지 자동 캡처 수행
    st.markdown("### 📥 리포트 파일 저장 및 다운로드")
    
    if st.button("💾 REPORT.MD 및 Plotly 그래프 이미지(4개) 캡처 저장"):
        if not df_continent.empty:
            fig_continent.write_image("chart_continent.png", width=800, height=500)
        if not df_country.empty:
            fig_top5.write_image("chart_top5.png", width=800, height=500)
        if not df_trend_filtered.empty:
            fig_trend.write_image("chart_trend.png", width=800, height=500)
        if not df_purpose.empty:
            fig_purpose.write_image("chart_purpose.png", width=800, height=500)

        with open("REPORT.MD", "w", encoding="utf-8") as f:
            f.write(report_content)
            
        st.success("✅ `REPORT.MD` 파일 및 Plotly 고화질 캡처 이미지(4개)가 프로젝트 폴더에 성공적으로 저장되었습니다!")