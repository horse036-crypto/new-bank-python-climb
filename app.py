import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import requests
import time
import urllib3
import competitor_analysis as ca
import chips_analysis as chips # 👈 新增這一行
import report_generator as rg # 👈 新增這個
# === 匯入模組 ===
import company_info as ci
import financial_data as fd
import news_analyzer as news # 確保已匯入
import chips_analysis as chips
# 忽略 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. 設定網頁
# ==========================================
st.set_page_config(page_title="超級財報狗 (新聞雷達版)", layout="wide")
st.title("🐶 超級財報狗 Pro+ : 深度個股分析")

# ... (中間的 fetch_stock_history, 股票搜尋, 基本資料, 股價圖, 財報分析 都不用動) ...
# ... (為了節省篇幅，請保留您原本中間這一段程式碼) ...

# 這裡我把 fetch_stock_history 補上以免您複製貼上時漏掉
@st.cache_data(ttl=3600)
def fetch_stock_history(stock_code):
    all_data = []
    date_list = pd.date_range(end=pd.Timestamp.now(), periods=6, freq='MS')
    for date_item in date_list:
        date_str = date_item.strftime("%Y%m%d")
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_code}"
        try:
            res = requests.get(url, verify=False)
            data = res.json()
            if data['stat'] == 'OK':
                df = pd.DataFrame(data['data'], columns=data['fields'])
                df['日期'] = df['日期'].apply(lambda x: str(int(x.split('/')[0]) + 1911) + '-' + x.split('/')[1] + '-' + x.split('/')[2])
                for col in ['收盤價', '開盤價', '最高價', '最低價', '成交股數']:
                    if col in df.columns: df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
                all_data.append(df)
            time.sleep(0.5)
        except: pass
    return pd.concat(all_data, ignore_index=True) if all_data else None

# ==========================================

# ==========================================
# 2. 股價爬蟲 (這個比較單純，暫時留在主程式)
# ==========================================
@st.cache_data(ttl=3600)
def fetch_stock_history(stock_code):
    all_data = []
    # 抓取最近 6 個月
    date_list = pd.date_range(end=pd.Timestamp.now(), periods=6, freq='MS')
    for date_item in date_list:
        date_str = date_item.strftime("%Y%m%d")
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_code}"
        try:
            res = requests.get(url, verify=False)
            data = res.json()
            if data['stat'] == 'OK':
                df = pd.DataFrame(data['data'], columns=data['fields'])
                df['日期'] = df['日期'].apply(lambda x: str(int(x.split('/')[0]) + 1911) + '-' + x.split('/')[1] + '-' + x.split('/')[2])
                for col in ['收盤價', '開盤價', '最高價', '最低價', '成交股數']:
                    if col in df.columns: df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
                all_data.append(df)
            time.sleep(0.5)
        except: pass
    return pd.concat(all_data, ignore_index=True) if all_data else None

# ==========================================
# 3. 主介面邏輯
# ==========================================
with st.sidebar:
    st.header("🔍 股票搜尋")
    stock_id = st.text_input("輸入股票代號", value="2330")
    st.markdown("---")
    st.markdown("### 📥 輸出報告")
    
    # 只有當所有資料都跑完，且 score_data 存在時才顯示按鈕
    # 注意：這裡的變數名稱要跟下面主程式對應，我們通常放在最下面執行，
    # 但 Streamlit 的 Sidebar 可以在任何地方定義。
    # 為了簡單起見，我們把按鈕放在「主程式邏輯」的最後面，但顯示位置設在 Sidebar。
    st.caption("模組化版本：基本資料與財報分離")

if stock_id:
    # 1. 載入資料 (分別呼叫不同模組)
    with st.spinner('正在挖掘公司資料... 🕵️'):
        # 呼叫基本資料模組 (company_info)
        info = ci.get_company_basic_info(stock_id)
        
        # 呼叫財報分析模組 (financial_data)
        df_ratios, insights, score_data = fd.get_comprehensive_analysis(stock_id)
        
        # 呼叫股價爬蟲
        df_price = fetch_stock_history(stock_id)

    # 2. 顯示詳細基本資料
    if info and '公司名稱' in info:
        with st.expander(f"🏢 {info['公司名稱']} ({stock_id}) - 詳細基本資料", expanded=True):
            
            st.markdown("#### 👤 經營團隊")
            c1, c2, c3, c4 = st.columns(4)
            c1.write(f"**董事長**：\n{info.get('董事長', 'N/A')}")
            c2.write(f"**總經理**：\n{info.get('總經理', 'N/A')}")
            c3.write(f"**發言人**：\n{info.get('發言人', 'N/A')}")
            c4.write(f"**代理發言人**：\n{info.get('代理發言人', 'N/A')}")
            
            st.markdown("---")
            
            st.markdown("#### 📈 市場與股本資訊")
            k1, k2, k3, k4 = st.columns(4)
            k1.write(f"**成立日期**：\n{info.get('成立日期', 'N/A')}")
            k2.write(f"**上市日期**：\n{info.get('上市日期', 'N/A')}")
            k3.write(f"**實收資本額**：\n{info.get('實收資本額', 'N/A')}")
            k4.write(f"**已發行股數**：\n{info.get('已發行股數', 'N/A')}")
            
            st.markdown("---")

            st.markdown("#### 📞 聯絡與股務資訊")
            L1, L2, L3, L4 = st.columns(4)
            L1.write(f"**總機電話**：\n{info.get('總機電話', 'N/A')}")
            L2.write(f"**電子郵件**：\n{info.get('電子郵件', 'N/A')}")
            L3.write(f"**統一編號**：\n{info.get('統一編號', 'N/A')}")
            L4.write(f"**股務代理**：\n{info.get('股務代理', 'N/A')}") 
            
            st.markdown(f"**公司地址**：{info.get('公司地址', 'N/A')}")
            st.markdown(f"**公司網址**：[{info.get('公司網址', '#')}]({info.get('公司網址', '#')})")

            st.markdown("---")
            
            st.markdown("#### 📝 公司簡介")
            st.info(info.get('公司簡介', '無簡介'))

    else:
        st.error(f"找不到 {stock_id} 的基本資料")

    # ... (前面的程式碼不用動) ...

    # 3. 顯示股價圖 (專業 K 線版)
    if df_price is not None:
        st.markdown("### 📈 股價走勢 (K線圖)")
        
        # 資料整理
        df_price['日期'] = pd.to_datetime(df_price['日期'])
        df_plot = df_price.sort_values('日期')
        
        # 計算移動平均線 (MA)
        df_plot['MA5'] = df_plot['收盤價'].rolling(5).mean()
        df_plot['MA20'] = df_plot['收盤價'].rolling(20).mean()

        # 引入高階繪圖套件
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # 建立雙軸圖表 (上面是 K 線，下面是成交量)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3])

        # --- 第一層：K 線圖 ---
        # 繪製蠟燭圖 (漲紅跌綠)
        fig.add_trace(go.Candlestick(
            x=df_plot['日期'],
            open=df_plot['開盤價'],
            high=df_plot['最高價'],
            low=df_plot['最低價'],
            close=df_plot['收盤價'],
            name='K線',
            increasing_line_color='red',  # 台股習慣：漲是紅色
            decreasing_line_color='green' # 台股習慣：跌是綠色
        ), row=1, col=1)

        # 繪製 MA5 (黃線)
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['MA5'], 
                                 mode='lines', name='MA5 (週線)', line=dict(color='orange', width=1)), row=1, col=1)
        
        # 繪製 MA20 (藍線)
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['MA20'], 
                                 mode='lines', name='MA20 (月線)', line=dict(color='blue', width=1)), row=1, col=1)

        # --- 第二層：成交量 ---
        # 設定顏色：漲紅跌綠
        colors = ['red' if row['收盤價'] >= row['開盤價'] else 'green' for index, row in df_plot.iterrows()]
        
        fig.add_trace(go.Bar(
            x=df_plot['日期'], 
            y=df_plot['成交股數'],
            name='成交量',
            marker_color=colors
        ), row=2, col=1)

        # --- 版面設定 ---
        fig.update_layout(
            title=f"{stock_id} 股價走勢與成交量",
            xaxis_rangeslider_visible=False, # 隱藏下方預設的滑桿
            height=600, # 設定圖表高度
            showlegend=True,
            hovermode="x unified" # 滑鼠移過去顯示所有資訊
        )
        
        # 顯示圖表
        st.plotly_chart(fig, use_container_width=True)
# ==========================================
    # 3. 顯示技術面 + 籌碼面 (更新版)
    # ==========================================
    if df_price is not None:
        st.markdown("### 📈 技術籌碼分析 (K線 + 成交量 + 三大法人)")
        
        # 1. 補抓籌碼資料 (原本沒有這行)
        with st.spinner('正在分析法人動向...'):
            df_chips = chips.get_chips_data(stock_id, days=10) # 抓最近 10 天
        
        df_price['日期'] = pd.to_datetime(df_price['日期'])
        df_plot = df_price.sort_values('日期')
        
        # 計算均線
        df_plot['MA5'] = df_plot['收盤價'].rolling(5).mean()
        df_plot['MA20'] = df_plot['收盤價'].rolling(20).mean()

        # --- 設定 3 層樓圖表 ---
        fig = make_subplots(
            rows=3, cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.05, 
            row_heights=[0.5, 0.25, 0.25], # K線佔一半，剩下給成交量和籌碼
            subplot_titles=("股價走勢", "成交量", "三大法人買賣超 (近10日)")
        )

        # (1) K線圖
        fig.add_trace(go.Candlestick(
            x=df_plot['日期'],
            open=df_plot['開盤價'], high=df_plot['最高價'],
            low=df_plot['最低價'], close=df_plot['收盤價'],
            name='K線', increasing_line_color='red', decreasing_line_color='green'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['MA5'], mode='lines', name='MA5', line=dict(color='orange', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_plot['日期'], y=df_plot['MA20'], mode='lines', name='MA20', line=dict(color='blue', width=1)), row=1, col=1)

        # (2) 成交量
        colors_vol = ['red' if row['收盤價'] >= row['開盤價'] else 'green' for index, row in df_plot.iterrows()]
        fig.add_trace(go.Bar(x=df_plot['日期'], y=df_plot['成交股數'], name='成交量', marker_color=colors_vol), row=2, col=1)

        # (3) 籌碼圖 (新增的部分!)
        if df_chips is not None and not df_chips.empty:
            # 買超顯示紅色，賣超顯示綠色
            colors_chip = ['red' if val > 0 else 'green' for val in df_chips['合計']]
            
            fig.add_trace(go.Bar(
                x=df_chips['日期'], 
                y=df_chips['合計'], 
                name='法人買賣超',
                marker_color=colors_chip,
                # 滑鼠移上去可以看到細節
                customdata=df_chips[['外資', '投信', '自營商']],
                hovertemplate="<br>日期: %{x}<br>合計: %{y}<br>外資: %{customdata[0]}<br>投信: %{customdata[1]}<br>自營商: %{customdata[2]}"
            ), row=3, col=1)

        # 版面設定
        fig.update_layout(height=800, xaxis_rangeslider_visible=False, hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    # ... (後面的財報分析也不用動) ...

    # 4. 顯示財報分析
    st.markdown("---")
    st.markdown("### 📊 深度財務分析")
    
    if df_ratios is not None and not df_ratios.empty:
        col_text, col_table = st.columns([1, 1.5])
        
        with col_text:
            st.markdown("#### 💡 AI 財報診斷")
            if insights:
                for point in insights:
                    st.write(point)
            else:
                st.write("資料不足，無法產生解讀。")
                
        with col_table:
            st.markdown("#### 📅 關鍵財務比率表")
            st.dataframe(
                df_ratios,
                column_config={"資料來源": st.column_config.LinkColumn("財報連結")},
                hide_index=True
            )
    # ... (前面的 股價圖、財報分析 都保持原樣) ...
    # ==========================================
    # 5. 銀行級徵信報告 (儀表板版)
    # ==========================================
    st.markdown("---")
    st.subheader("🏦 企業財務徵信與風險評估報告")
    
    if score_data and df_ratios is not None:
        
        # --- A. 核心風險儀表板 (三欄位) ---
        c1, c2, c3 = st.columns(3)
        
        # 1. 綜合信用評分
        with c1:
            score = score_data.get('總分', 0)
            color = "green" if score >= 80 else "orange" if score >= 60 else "red"
            st.markdown(f"#### 🏆 綜合信用評分")
            st.markdown(f"<h1 style='color:{color}'>{score} 分</h1>", unsafe_allow_html=True)
            st.caption(f"評級：{score_data.get('評級', 'N/A')}")
        
        # 2. Z-Score 破產預測 (新增!)
        with c2:
            z_val = score_data.get('Z-Score', 0)
            z_stat = score_data.get('Z-Status', 'N/A')
            # 綠色安全，紅色危險
            z_color = "green" if z_val > 2.99 else "red" if z_val < 1.81 else "orange"
            st.markdown(f"#### 📉 破產風險 (Z-Score)")
            st.markdown(f"<h1 style='color:{z_color}'>{z_val}</h1>", unsafe_allow_html=True)
            st.caption(f"狀態：{z_stat}")

        # 3. 自由現金流 (新增!)
        with c3:
            # 抓取最新一期的 FCF
            fcf = df_ratios.iloc[0]['自由現金流 (億)']
            fcf_color = "green" if fcf > 0 else "red"
            st.markdown(f"#### 💰 自由現金流 (FCF)")
            st.markdown(f"<h1 style='color:{fcf_color}'>{fcf} 億</h1>", unsafe_allow_html=True)
            st.caption("真正落袋的現金 (營運現金 - 資本支出)")

        st.markdown("---")

        # --- B. 詳細結構分析 (五力 + 杜邦) ---
        col_detail, col_dupont = st.columns([1.2, 1])
        
        with col_detail:
            st.markdown("##### 📊 五力評分明細")
            st.dataframe(
                pd.DataFrame(score_data['細項']), 
                column_config={
                    "得分": st.column_config.ProgressColumn(
                        "得分 (滿分20)", format="%d", min_value=0, max_value=20
                    ),
                },
                hide_index=True, use_container_width=True
            )

        with col_dupont:
            st.markdown("##### 🧬 杜邦分析 (ROE 拆解)")
            latest = df_ratios.iloc[0]
            # 使用 Metric 顯示
            d1, d2, d3 = st.columns(3)
            d1.metric("淨利率", f"{latest['淨利率 (%)']}%", "獲利能力")
            d2.metric("周轉率", f"{latest['資產周轉率 (次)']}", "管理效率")
            d3.metric("權益乘數", f"{latest['權益乘數 (倍)']}", "財務槓桿", delta_color="inverse")
            st.info(f"💡 **ROE = {latest['ROE (%)']}%**")

        # --- C. 完整數據表格 ---
        with st.expander("📄 查看完整財務三表數據"):
            st.dataframe(df_ratios, use_container_width=True)
            
    else:
        st.error("⚠️ 資料不足，無法產生徵信報告。")

    # ==========================================
    # ==========================================
    # 5. 新聞雷達 (修正版：對應新欄位)
    # ==========================================
    st.markdown("---")
    st.subheader("📰 市場消息雷達")
    
    # 取得公司名稱
    # 這裡多做一個防呆：如果 info 沒抓到，就用股票代號
    target_name = info.get('公司名稱', stock_id) if 'info' in locals() and info else stock_id
    
    if target_name:
        with st.expander(f"查看 「{target_name}」 的多空消息面", expanded=False):
            
            # 分成左右兩欄
            col_good, col_bad = st.columns(2)
            
            # --- 左邊：正面利多 ---
            with col_good:
                st.markdown("### 🎉 正面利多")
                with st.spinner('搜尋好消息...'):
                    # 呼叫 news.search_news (V8.0 新函式)
                    good_news = news.search_news(target_name, news_type='positive')
                
                if good_news:
                    for n in good_news:
                        st.markdown(f"🟢 **[{n['標題']}]({n['連結']})**")
                        # 【修正點】這裡改成抓 '日期' 和 '來源'
                        st.caption(f"{n.get('日期', '')} | {n.get('來源', 'Google News')}")
                        st.markdown("---")
                else:
                    st.info("近期無重大正面新聞。")

            # --- 右邊：負面風險 ---
            with col_bad:
                st.markdown("### 💣 負面風險")
                with st.spinner('搜尋壞消息...'):
                    # 呼叫 news.search_news (V8.0 新函式)
                    bad_news = news.search_news(target_name, news_type='negative')
                
                if bad_news:
                    for n in bad_news:
                        st.markdown(f"🔴 **[{n['標題']}]({n['連結']})**")
                        # 【修正點】這裡改成抓 '日期' 和 '來源'
                        st.caption(f"{n.get('日期', '')} | {n.get('來源', 'Google News')}")
                        st.markdown("---")
                else:
                    st.success("✅ 近期無重大負面新聞。")
                    
            st.caption("資料來源：Google News RSS (AI 自動過濾篩選)")
    else:
        st.warning("無法取得公司名稱，無法搜尋新聞。")
    # ==========================================
    # 5. 同業比較 (新功能!)
    # ==========================================
    st.markdown("---")
    st.subheader("⚖️ 同業估值比較")
    
    # 取得這家公司的產業
    industry = info.get('產業別', '')
    
    if industry:
        st.caption(f"目前所屬產業：**{industry}** (資料來源：台灣證交所)")
        
        with st.spinner(f'正在召集 {industry} 的各路好手...'):
            df_peers = ca.get_peers_comparison(stock_id, industry)
        
        if df_peers is not None and not df_peers.empty:
            
            # 為了讓圖表好看，我們只取跟目標股票 本益比 最接近的 5 檔，或是全產業平均
            # 這裡簡單處理：取本益比最接近目標股票的前後各 4 檔 (共 9 檔)
            
            # 找到目標股票的位置
            try:
                target_idx = df_peers[df_peers['證券代號'] == stock_id].index[0]
                current_loc = df_peers.index.get_loc(target_idx)
                
                # 取前後範圍
                start = max(0, current_loc - 4)
                end = min(len(df_peers), current_loc + 5)
                df_chart = df_peers.iloc[start:end]
            except:
                df_chart = df_peers.head(10) # 如果出錯就取前 10 檔
            
            # 準備畫圖
            tab1, tab2 = st.tabs(["📊 本益比 (PE) PK", "💰 殖利率 (Yield) PK"])
            
            with tab1:
                st.markdown("##### 誰比較貴？ (本益比越低越便宜)")
                # 設定顏色：目標股票顯示紅色，其他顯示灰色
                colors_pe = ['red' if x == stock_id else 'lightgray' for x in df_chart['證券代號']]
                
                fig_pe = px.bar(
                    df_chart, 
                    x='公司名稱', 
                    y='本益比', 
                    text='本益比',
                    title=f"{industry} - 本益比比較",
                    color='證券代號', # 為了讓 color_discrete_map 生效
                    color_discrete_map={code: 'red' if code == stock_id else 'gray' for code in df_chart['證券代號']}
                )
                fig_pe.update_traces(showlegend=False) # 隱藏圖例比較清爽
                st.plotly_chart(fig_pe, use_container_width=True)
                
            with tab2:
                st.markdown("##### 誰配息最大方？ (殖利率越高越好)")
                fig_yield = px.bar(
                    df_chart, 
                    x='公司名稱', 
                    y='殖利率(%)', 
                    text='殖利率(%)',
                    title=f"{industry} - 殖利率比較",
                    color='證券代號',
                    color_discrete_map={code: 'red' if code == stock_id else 'gray' for code in df_chart['證券代號']}
                )
                fig_yield.update_traces(showlegend=False)
                st.plotly_chart(fig_yield, use_container_width=True)
            
            # 顯示詳細表格
            with st.expander("查看完整同業數據表"):
                st.dataframe(df_peers, hide_index=True)
                
        else:
            st.info("該產業資料不足或無同業可比較。")
    else:
        st.warning("無法識別產業類別，無法進行比較。")
    # ==========================================
    # 5. 銀行級徵信報告 (信用評分 + 杜邦分析)
    # ==========================================
    st.markdown("---")
    st.subheader("📑 財務體質徵信報告")
    
    if score_data and df_ratios is not None:
        
        # --- 區塊 A: 信用評分卡 (Credit Scorecard) ---
        # 模仿銀行內部報告的摘要欄
        score = score_data['總分']
        grade = score_data['評級']
        
        # 設定顏色：高分綠色，低分紅色
        score_color = "green" if score >= 80 else "orange" if score >= 60 else "red"
        
        with st.container():
            # 畫出類似證書的邊框效果
            st.markdown(f"""
            <div style="border: 2px solid #f0f2f6; border-radius: 10px; padding: 20px; background-color: #f9f9f9;">
                <h3 style="text-align: center; margin: 0;">綜合財務信用評分</h3>
                <h1 style="text-align: center; color: {score_color}; font-size: 50px; margin: 0;">{score} 分</h1>
                <p style="text-align: center; font-size: 20px; font-weight: bold;">評級：{grade}</p>
                <hr>
                <p style="text-align: center; color: gray;">根據您設定的 5 大指標進行加權評分 (滿分 100)</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("") # 空一行

        # --- 區塊 B: 評分細項 (Risk Details) ---
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.markdown("##### 📊 五力分析評分表")
            score_df = pd.DataFrame(score_data['細項'])
            st.dataframe(score_df, hide_index=True, use_container_width=True)

        with c2:
            st.markdown("##### 🧬 杜邦分析 (ROE 拆解)")
            if not df_ratios.empty:
                latest = df_ratios.iloc[0]
                roe = latest['ROE (%)']
                net_m = latest['淨利率 (%)']
                asset_t = latest['資產周轉率 (次)']
                lev = latest['權益乘數 (倍)']
                
                # 用 Metric 顯示杜邦公式
                m1, m2, m3 = st.columns(3)
                m1.metric("淨利率 (獲利)", f"{net_m}%")
                m2.metric("周轉率 (管理)", f"{asset_t}次")
                m3.metric("權益乘數 (槓桿)", f"{lev}倍")
                
                st.info(f"💡 **ROE 分析**：本期 ROE 為 **{roe}%**。\n\n"
                        f"是由 **{net_m}%** 的獲利能力 × **{asset_t}** 次的資產運用效率 × **{lev}** 倍的財務槓桿所組成。")

        # --- 區塊 C: 完整財報數據 ---
        with st.expander("查看近三年詳細財報數據 (含趨勢)"):
            st.dataframe(df_ratios, hide_index=True)
            if insights:
                st.markdown("**趨勢解讀：**")
                for i in insights: st.write(i)
                
    else:
        st.error("資料不足，無法產生徵信報告。")
    # ==========================================
    # 7. 下載 Excel 報告 (放在最下面執行，顯示在左邊)一定放在最後面!!!!!!!!!!!!!
    # ==========================================
    if stock_id and 'score_data' in locals() and score_data:
        with st.sidebar:
            st.success("✅ 分析完成！")
            
            # 產生 Excel 檔案
            excel_data = rg.generate_excel_report(
                stock_id, info, df_price, df_ratios, 
                df_chips if 'df_chips' in locals() else None, 
                score_data
            )
            
            file_name = f"{stock_id}_{info.get('公司名稱','股票')}_徵信報告.xlsx"
            
            st.download_button(
                label="📥 下載完整 Excel 報告",
                data=excel_data,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )