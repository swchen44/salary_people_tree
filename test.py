# 📊 Streamlit 員工視覺化分析 Dashboard
# --------------------------------------------
# 💡 使用情境與需求假設：
# - 給定一間多城市跨部門公司的人事資料，希望：
#   - 快速掌握每個部門的人力結構與獎酬水準
#   - 評估 KPI 是否達標，並視覺化呈現達標率
#   - 具備互動性（可切換篩選條件）、即時資料彙總與匯出報表
#   - 適合中大型企業 HR、主管、財務等使用者日常追蹤
# - 本工具也可延伸用於模擬資料測試資料分析技巧與前端儀表板設計
# --------------------------------------------
# 本應用程式設計目的：
# - 利用 Plotly 與 Streamlit 結合，呈現企業員工的年薪、獎金、考績等關鍵指標
# - 支援 KPI 設定、達標率視覺化、各單位績效比較、可互動式資料探索
# - 可作為部門績效盤點、管理報表、決策參考之用
# 設計理念：
# - 模擬真實部門結構與人事資料，透過簡單控制介面達成靈活篩選與視覺展示
# - 鼓勵即時互動與 KPI 驅動式文化推動，並保有資料下載與設定儲存的可擴充性

import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import random
import json
import os

# 🔧 1. 產生模擬員工資料
# WHY: 使用隨機資料模擬真實場景，便於展示互動功能與 KPI 分析
random.seed(42)
np.random.seed(42)
cities = [f"城市{i}" for i in range(1, 5)]
units = [f"單位{i}" for i in range(1, 11)]
first_names = ["小明", "小華", "小美", "小強", "小麗", "小王", "小李", "小陳", "小黃", "小吳"]
last_names = ["陳", "李", "王", "林", "張", "黃", "吳", "周", "徐", "賴"]

records = []
# WHAT: 依據每城市/單位隨機建立 3~50 名員工紀錄
# WHY: 模擬跨城市的單位員工組織，提供後續分析依據
for city in cities:
    for unit in units:
        for _ in range(random.randint(3, 50)):
            name = f"{random.choice(last_names)}{random.choice(first_names)}"
            salary = np.random.randint(100000, 300001)
            bonus = np.random.randint(10000, 30001)
            perf = np.random.randint(1, 11)
            records.append({
                "公司地點": city,
                "單位": unit,
                "人員名字": name,
                "人員年薪": salary,
                "人員獎金": bonus,
                "人員考績": perf
            })

# 🧮 2. 建立主要資料表 df 並計算欄位
# WHAT: 加總、加權產出「總薪資」「重要程度」等分析用欄位
# WHY: 這些欄位供後續視覺化、KPI 統計使用
df = pd.DataFrame(records)
df["總薪資"] = df["人員年薪"] + df["人員獎金"]
df["重要程度"] = df["人員年薪"] * df["人員考績"]
total_count = len(df)

# 🗂️ 3. 載入（或建立）過往儲存的篩選條件
# WHAT: 讀取使用者上次選擇的篩選器參數（地點、單位、考績...）
# WHY: 提供更連續、個人化的使用體驗
CONFIG_FILE = "filter_config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        saved_filters = json.load(f)
else:
    saved_filters = {}

# 🖼️ 4. 建立頁面標題與初始選單介面
# WHAT: 顯示標題，後續將加入互動式選單與圖表
# WHY: 使用者介面邏輯的起點，呼應設計目標與操作流程
st.title("公司員工視覺化分析 Dashboard")

# 🎛️ 5. 篩選器與控制面板建立
# WHAT: 提供地點、單位、姓名關鍵字、考績等欄位過濾器
# WHY: 讓使用者聚焦於目標分析區域，提高圖表與 KPI 表現的針對性
selected_city = st.multiselect("選擇公司地點:", sorted(df["公司地點"].unique()), default=saved_filters.get("selected_city", sorted(df["公司地點"].unique())))
selected_unit = st.multiselect("選擇單位:", sorted(df["單位"].unique()), default=saved_filters.get("selected_unit", sorted(df["單位"].unique())))
search_name = st.text_input("輸入人員姓名關鍵字（可選）", value=saved_filters.get("search_name", ""))
performance_range = st.slider("選擇考績分數範圍:", 1, 10, tuple(saved_filters.get("performance_range", (1, 10))))

# 🎯 6. KPI 目標設定介面
# WHAT: 使用者輸入 KPI 評量標準（年薪、獎金、考績）
# WHY: 提供對照基準，後續用於顯示各部門績效達標程度
with st.expander("🎯 設定 KPI 目標值", expanded=True):
    goal_salary = st.number_input("目標平均年薪", value=200000, step=10000)
    goal_bonus = st.number_input("目標平均獎金", value=20000, step=1000)
    goal_perf = st.number_input("目標平均考績", value=7.0, step=0.1)

# 📊 7. 資料篩選處理（依據使用者選單）
# WHAT: 根據城市、單位、姓名、考績範圍過濾資料集
# WHY: 篩選出關心的資料子集，供後續 KPI 計算與圖表視覺化使用
df_filtered = df[
    df["公司地點"].isin(selected_city) &
    df["單位"].isin(selected_unit) &
    df["人員考績"].between(performance_range[0], performance_range[1])
]
if search_name:
    df_filtered = df_filtered[df_filtered["人員名字"].str.contains(search_name)]

# 📈 8. KPI 實際值計算與視覺化達標率顯示
# WHAT: 計算當前篩選子集的平均年薪、獎金、考績並與目標值比較
# WHY: 視覺化達標程度，有助於管理層快速判斷部門績效

def get_delta_color(value, goal):
    return "normal" if pd.isna(value) else ("inverse" if value < goal else "off")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 平均年薪", f"{df_filtered['人員年薪'].mean():,.0f} 元", delta=f"達標率 {(df_filtered['人員年薪'].mean() / goal_salary * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員年薪'].mean(), goal_salary))
col2.metric("🎯 平均獎金", f"{df_filtered['人員獎金'].mean():,.0f} 元", delta=f"達標率 {(df_filtered['人員獎金'].mean() / goal_bonus * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員獎金'].mean(), goal_bonus))
col3.metric("🎯 平均考績", f"{df_filtered['人員考績'].mean():.2f} 分", delta=f"達標率 {(df_filtered['人員考績'].mean() / goal_perf * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員考績'].mean(), goal_perf))
col4.metric("👥 人數", f"{len(df_filtered)} / {total_count}")

# 🌳 9. Treemap 圖表產生
# WHAT: 依據使用者定義的層級與欄位生成樹狀圖視覺化結構
# WHY: 快速觀察不同城市 / 單位 / 員工在重要程度上的分佈與貢獻度
st.subheader("🌳 Treemap")
treemap_path = st.multiselect("Treemap 層級:", ["公司地點", "單位", "人員名字"], default=["公司地點", "單位", "人員名字"])
color_field = st.selectbox("Treemap 顏色依據欄位:", ["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"])
color_scale = st.selectbox("顏色樣式:", ["RdBu", "Viridis", "Cividis", "Blues", "Inferno"])

fig_treemap = px.treemap(
    df_filtered,
    path=treemap_path,
    values="重要程度",
    color=color_field,
    color_continuous_scale=color_scale,
    hover_data={"人員年薪": True, "人員獎金": True, "人員考績": True, "總薪資": True, "重要程度": True}
)
st.plotly_chart(fig_treemap, use_container_width=True)

# 🔆 10. Sunburst 圖表產生
# WHAT: 類似 Treemap 的層級結構視覺化，但以放射狀呈現
# WHY: 更直觀展示層級關係與比例結構，適合展示城市 → 單位 → 人員的階層貢獻
st.subheader("🔆 Sunburst")
fig_sunburst = px.sunburst(
    df_filtered,
    path=["公司地點", "單位", "人員名字"],
    values="重要程度",
    color="人員考績",
    color_continuous_scale="Bluered_r"
)
st.plotly_chart(fig_sunburst, use_container_width=True)

# 📋 11. 各單位 KPI 表格 + 條件色彩顯示
# WHAT: 顯示各部門平均 KPI 值與達標率，加入色彩提示利於辨識
# WHY: 管理者可快速判斷部門間表現差異
unit_kpi = df.groupby("單位").agg({
    "人員年薪": "mean",
    "人員獎金": "mean",
    "人員考績": "mean",
    "人員名字": "count"
}).reset_index()
unit_kpi.columns = ["單位", "平均年薪", "平均獎金", "平均考績", "人數"]
unit_kpi["年薪達標率"] = (unit_kpi["平均年薪"] / goal_salary * 100).round(1)
unit_kpi["獎金達標率"] = (unit_kpi["平均獎金"] / goal_bonus * 100).round(1)
unit_kpi["考績達標率"] = (unit_kpi["平均考績"] / goal_perf * 100).round(1)

# 🏳️ 自動標記：最強單位與需改善單位
unit_kpi["旗標"] = ""
unit_kpi.loc[unit_kpi[["年薪達標率", "獎金達標率", "考績達標率"]].min(axis=1) >= 100, "旗標"] = "🏅 最強單位"
unit_kpi.loc[unit_kpi[["年薪達標率", "獎金達標率", "考績達標率"]].max(axis=1) < 90, "旗標"] = "⚠️ 需改善"
