import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import random
import json
import os

# 產生測試資料
random.seed(42)
np.random.seed(42)
cities = [f"城市{i}" for i in range(1, 5)]
units = [f"單位{i}" for i in range(1, 11)]
first_names = ["小明", "小華", "小美", "小強", "小麗", "小王", "小李", "小陳", "小黃", "小吳"]
last_names = ["陳", "李", "王", "林", "張", "黃", "吳", "周", "徐", "賴"]

records = []
for city in cities:
    for unit in units:
        for _ in range(random.randint(3, 50)):
            name = f"{random.choice(last_names)}{random.choice(first_names)}"
            salary = np.random.randint(100000, 300001)
            bonus = np.random.randint(10000, 30001)
            perf = np.random.randint(1, 11)
            records.append({"公司地點": city, "單位": unit, "人員名字": name, "人員年薪": salary, "人員獎金": bonus, "人員考績": perf})

df = pd.DataFrame(records)
df["總薪資"] = df["人員年薪"] + df["人員獎金"]
df["重要程度"] = df["人員年薪"] * df["人員考績"]
total_count = len(df)

# 設定檔案名稱
CONFIG_FILE = "filter_config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        saved_filters = json.load(f)
else:
    saved_filters = {}

st.title("公司員工視覺化分析 Dashboard")

# 篩選區塊
selected_city = st.multiselect("選擇公司地點:", sorted(df["公司地點"].unique()), default=saved_filters.get("selected_city", sorted(df["公司地點"].unique())))
selected_unit = st.multiselect("選擇單位:", sorted(df["單位"].unique()), default=saved_filters.get("selected_unit", sorted(df["單位"].unique())))
search_name = st.text_input("輸入人員姓名關鍵字（可選）", value=saved_filters.get("search_name", ""))
performance_range = st.slider("選擇考績分數範圍:", 1, 10, tuple(saved_filters.get("performance_range", (1, 10))))
treemap_path = st.multiselect("Treemap 顯示層級:", ["公司地點", "單位", "人員名字"], default=saved_filters.get("treemap_path", ["公司地點", "單位", "人員名字"]))
color_field = st.selectbox("顏色依據欄位:", ["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"], index=["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"].index(saved_filters.get("color_field", "人員年薪")))
color_scale = st.selectbox("顏色樣式:", ["RdBu", "Viridis", "Cividis", "Blues", "Inferno"], index=["RdBu", "Viridis", "Cividis", "Blues", "Inferno"].index(saved_filters.get("color_scale", "RdBu")))

# 儲存設定
if st.button("💾 儲存目前篩選設定"):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "selected_city": selected_city,
            "selected_unit": selected_unit,
            "search_name": search_name,
            "performance_range": performance_range,
            "treemap_path": treemap_path,
            "color_field": color_field,
            "color_scale": color_scale
        }, f, ensure_ascii=False, indent=2)
    st.success("✅ 設定已儲存！")

# KPI 設定區
st.subheader("📈 KPI 目標與達標率")
with st.expander("🎯 設定 KPI 目標值", expanded=True):
    goal_salary = st.number_input("目標平均年薪", value=200000, step=10000)
    goal_bonus = st.number_input("目標平均獎金", value=20000, step=1000)
    goal_perf = st.number_input("目標平均考績", value=7.0, step=0.1)

# 篩選資料
df_filtered = df[
    df["公司地點"].isin(selected_city) &
    df["單位"].isin(selected_unit) &
    df["人員考績"].between(performance_range[0], performance_range[1])
]
if search_name:
    df_filtered = df_filtered[df_filtered["人員名字"].str.contains(search_name)]

# KPI 計算
def get_delta_color(value, goal):
    return "normal" if pd.isna(value) else ("inverse" if value < goal else "off")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 平均年薪", f"{df_filtered['人員年薪'].mean():,.0f} 元", delta=f"達標率 {(df_filtered['人員年薪'].mean() / goal_salary * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員年薪'].mean(), goal_salary))
col2.metric("🎯 平均獎金", f"{df_filtered['人員獎金'].mean():,.0f} 元", delta=f"達標率 {(df_filtered['人員獎金'].mean() / goal_bonus * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員獎金'].mean(), goal_bonus))
col3.metric("🎯 平均考績", f"{df_filtered['人員考績'].mean():.2f} 分", delta=f"達標率 {(df_filtered['人員考績'].mean() / goal_perf * 100):.1f}%", delta_color=get_delta_color(df_filtered['人員考績'].mean(), goal_perf))
col4.metric("👥 人數", f"{len(df_filtered)} / {total_count}")

# Treemap 圖表
st.subheader("🌳 Treemap")
fig = px.treemap(
    df_filtered,
    path=treemap_path,
    values="重要程度",
    color=color_field,
    color_continuous_scale=color_scale,
    hover_data={"人員年薪": True, "人員獎金": True, "人員考績": True, "總薪資": True, "重要程度": True}
)
st.plotly_chart(fig, use_container_width=True)

# Sunburst 圖表
st.subheader("🔆 Sunburst")
fig2 = px.sunburst(
    df_filtered,
    path=["公司地點", "單位", "人員名字"],
    values="重要程度",
    color="人員考績",
    color_continuous_scale="Bluered_r"
)
st.plotly_chart(fig2, use_container_width=True)

# KPI 表格（單位達標率）
df_kpi = df.groupby("單位").agg({
    "人員年薪": "mean",
    "人員獎金": "mean",
    "人員考績": "mean",
    "人員名字": "count"
}).reset_index()
df_kpi.columns = ["單位", "平均年薪", "平均獎金", "平均考績", "人數"]
df_kpi["年薪達標率"] = (df_kpi["平均年薪"] / goal_salary * 100).round(1).astype(str) + "%"
df_kpi["獎金達標率"] = (df_kpi["平均獎金"] / goal_bonus * 100).round(1).astype(str) + "%"
df_kpi["考績達標率"] = (df_kpi["平均考績"] / goal_perf * 100).round(1).astype(str) + "%"

st.subheader("📋 各單位 KPI 達標率表")
st.dataframe(df_kpi)
st.download_button("下載 KPI 表格 (CSV)", data=df_kpi.to_csv(index=False).encode("utf-8-sig"), file_name="unit_kpi_report.csv", mime="text/csv")
