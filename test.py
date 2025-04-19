import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import random
import json
import os

# 產生測試資料（與前面一致）
random.seed(42)
np.random.seed(42)

cities = [f"城市{i}" for i in range(1, 5)]
units = [f"單位{i}" for i in range(1, 11)]
first_names = ["小明", "小華", "小美", "小強", "小麗", "小王", "小李", "小陳", "小黃", "小吳"]
last_names = ["陳", "李", "王", "林", "張", "黃", "吳", "周", "徐", "賴"]

records = []
for city in cities:
    for unit in units:
        num_people = random.randint(3, 50)
        for _ in range(num_people):
            name = f"{random.choice(last_names)}{random.choice(first_names)}"
            salary = np.random.randint(100000, 300001)
            bonus = np.random.randint(10000, 30001)
            performance = np.random.randint(1, 11)
            records.append({
                "公司地點": city,
                "單位": unit,
                "人員名字": name,
                "人員年薪": salary,
                "人員獎金": bonus,
                "人員考績": performance
            })

# 建立 DataFrame
df = pd.DataFrame(records)
df["總薪資"] = df["人員年薪"] + df["人員獎金"]
df["重要程度"] = df["人員年薪"] * df["人員考績"]

# 單位與城市統計欄位
grouped_unit = df.groupby(["公司地點", "單位"]).agg({
    "人員年薪": ["sum", "mean"],
    "人員獎金": ["sum", "mean"],
    "人員名字": "count"
}).reset_index()
grouped_unit.columns = ["公司地點", "單位", "單位總年薪", "單位平均年薪", "單位總獎金", "單位平均獎金", "單位人數"]
df = df.merge(grouped_unit, on=["公司地點", "單位"], how="left")

city_summary = df.groupby("公司地點").agg({
    "人員年薪": ["sum", "mean"],
    "人員獎金": ["sum", "mean"],
    "人員名字": "count"
}).reset_index()
city_summary.columns = ["公司地點", "城市總年薪", "城市平均年薪", "城市總獎金", "城市平均獎金", "城市人數"]
df = df.merge(city_summary, on="公司地點", how="left")

# 儲存與讀取預設設定檔
CONFIG_FILE = "filter_config.json"
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        saved_filters = json.load(f)
else:
    saved_filters = {}

# UI 控制項
st.title("公司員工結構視覺化")
st.caption("可篩選公司地點、單位、人員姓名與考績分數，依重要程度呈現")

selected_city = st.multiselect("選擇公司地點:", sorted(df["公司地點"].unique()), default=saved_filters.get("selected_city", sorted(df["公司地點"].unique())))
selected_unit = st.multiselect("選擇單位:", sorted(df["單位"].unique()), default=saved_filters.get("selected_unit", sorted(df["單位"].unique())))
search_name = st.text_input("輸入人員姓名關鍵字（可選）", value=saved_filters.get("search_name", ""))
performance_range = st.slider("選擇考績分數範圍:", 1, 10, tuple(saved_filters.get("performance_range", (1, 10))))

path_options = ["公司地點", "單位", "人員名字"]
treemap_path = st.multiselect("Treemap 顯示層級:", options=path_options, default=saved_filters.get("treemap_path", path_options))
color_field = st.selectbox("選擇顏色依據欄位:", ["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"], index=["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"].index(saved_filters.get("color_field", "人員年薪")))
color_scale = st.selectbox("選擇顏色樣式:", ["RdBu", "Viridis", "Cividis", "Blues", "Inferno"], index=["RdBu", "Viridis", "Cividis", "Blues", "Inferno"].index(saved_filters.get("color_scale", "RdBu")))

# 儲存設定按鈕
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
    st.success("設定已儲存！")

# KPI 報表區塊
st.subheader("📈 KPI 報表")

# 使用者輸入 KPI 目標
with st.expander("🎯 設定 KPI 目標值", expanded=True):
    goal_salary = st.number_input("目標平均年薪", value=200000, step=10000)
    goal_bonus = st.number_input("目標平均獎金", value=20000, step=1000)
    goal_perf = st.number_input("目標平均考績", value=7.0, step=0.1)

col1, col2, col3, col4 = st.columns(4)

# KPI 計算
total_count = len(df)
avg_salary = df["人員年薪"].mean()
avg_bonus = df["人員獎金"].mean()
avg_perf = df["人員考績"].mean()

# 實際值（篩選前 KPI 還沒用到）
# filtered_df 尚未定義，延後處理於後面正確位置
actual_count = len(filtered_df)
actual_salary = filtered_df["人員年薪"].mean()
actual_bonus = filtered_df["人員獎金"].mean()
actual_perf = filtered_df["人員考績"].mean()

# KPI 顯示 + 達標率（含顏色）
def get_delta_color(value, goal):
    return "normal" if pd.isna(value) else ("inverse" if value < goal else "off")

col1.metric("🎯 平均年薪", f"{actual_salary:,.0f} 元", delta=f"達標率 {(actual_salary / goal_salary * 100):.1f}%", delta_color=get_delta_color(actual_salary, goal_salary))
col2.metric("🎯 平均獎金", f"{actual_bonus:,.0f} 元", delta=f"達標率 {(actual_bonus / goal_bonus * 100):.1f}%", delta_color=get_delta_color(actual_bonus, goal_bonus))
col3.metric("🎯 平均考績", f"{actual_perf:.2f} 分", delta=f"達標率 {(actual_perf / goal_perf * 100):.1f}%", delta_color=get_delta_color(actual_perf, goal_perf))
col4.metric("👥 人數", f"{actual_count} / {total_count}")

# 篩選與顯示
filtered_df = df[
    df["公司地點"].isin(selected_city) &
    df["單位"].isin(selected_unit) &
    df["人員考績"].between(performance_range[0], performance_range[1])
]
if search_name:
    filtered_df = filtered_df[filtered_df["人員名字"].str.contains(search_name)]

# 實際值（篩選後）
actual_count = len(filtered_df)
actual_salary = filtered_df["人員年薪"].mean()
actual_bonus = filtered_df["人員獎金"].mean()
actual_perf = filtered_df["人員考績"].mean()

# KPI 顯示 + 達標率（含顏色）
def get_delta_color(value, goal):
    return "normal" if pd.isna(value) else ("inverse" if value < goal else "off")

col1.metric("🎯 平均年薪", f"{actual_salary:,.0f} 元", delta=f"達標率 {(actual_salary / goal_salary * 100):.1f}%", delta_color=get_delta_color(actual_salary, goal_salary))
col2.metric("🎯 平均獎金", f"{actual_bonus:,.0f} 元", delta=f"達標率 {(actual_bonus / goal_bonus * 100):.1f}%", delta_color=get_delta_color(actual_bonus, goal_bonus))
col3.metric("🎯 平均考績", f"{actual_perf:.2f} 分", delta=f"達標率 {(actual_perf / goal_perf * 100):.1f}%", delta_color=get_delta_color(actual_perf, goal_perf))
col4.metric("👥 人數", f"{actual_count} / {total_count}")
filtered_df = df[
    df["公司地點"].isin(selected_city) &
    df["單位"].isin(selected_unit) &
    df["人員考績"].between(performance_range[0], performance_range[1])
]
if search_name:
    filtered_df = filtered_df[filtered_df["人員名字"].str.contains(search_name)]

max_n = len(filtered_df)
top_n = st.slider("顯示 Top N 重要程度最高人員（可選）:", 1, max_n, min(100, max_n))
filtered_df = filtered_df.sort_values("重要程度", ascending=False).head(top_n)

# Treemap 顯示（保留原樣）......
