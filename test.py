import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import random

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

# 選單介面
st.title("公司員工結構視覺化")
st.caption("可篩選公司地點、單位、人員姓名與考績分數，依重要程度呈現")

selected_city = st.multiselect("選擇公司地點:", sorted(df["公司地點"].unique()), default=sorted(df["公司地點"].unique()))
selected_unit = st.multiselect("選擇單位:", sorted(df["單位"].unique()), default=sorted(df["單位"].unique()))
search_name = st.text_input("輸入人員姓名關鍵字（可選）")
performance_range = st.slider("選擇考績分數範圍:", 1, 10, (1, 10))

path_options = ["公司地點", "單位", "人員名字"]
treemap_path = st.multiselect("Treemap 顯示層級:", options=path_options, default=path_options)
color_field = st.selectbox("選擇顏色依據欄位:", ["人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度"])
color_scale = st.selectbox("選擇顏色樣式:", ["RdBu", "Viridis", "Cividis", "Blues", "Inferno"])

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

# Treemap
st.subheader("Treemap（依重要程度）")
fig = px.treemap(
    filtered_df,
    path=treemap_path,
    values="重要程度",
    color=color_field,
    color_continuous_scale=color_scale,
    hover_data={col: True for col in [
        "人員年薪", "人員獎金", "人員考績", "總薪資", "重要程度",
        "單位總年薪", "單位總獎金", "單位平均年薪", "單位平均獎金", "單位人數",
        "城市總年薪", "城市總獎金", "城市平均年薪", "城市平均獎金", "城市人數"] if col in filtered_df.columns}
)
st.plotly_chart(fig, use_container_width=True)

# 其他圖表恢復
st.subheader("Sunburst（依重要程度）")
fig2 = px.sunburst(
    filtered_df,
    path=["公司地點", "單位", "人員名字"],
    values="重要程度",
    color="人員考績",
    color_continuous_scale="Bluered_r"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("單位總年薪佔比（圓餅圖）")
unit_sum = filtered_df.groupby("單位")["人員年薪"].sum().reset_index()
fig3 = px.pie(unit_sum, names="單位", values="人員年薪", title="單位總年薪佔比")
st.plotly_chart(fig3, use_container_width=True)

st.subheader("城市人數比例")
city_count = df.groupby("公司地點")["人員名字"].count().reset_index(name="人數")
fig4 = px.pie(city_count, names="公司地點", values="人數", title="城市人數比例")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("單位人數排行")
unit_count = df.groupby("單位")["人員名字"].count().reset_index(name="人數")
fig5 = px.bar(unit_count.sort_values("人數", ascending=False), x="單位", y="人數", title="各單位人數排行")
st.plotly_chart(fig5, use_container_width=True)

st.subheader("篩選後資料表格")
st.dataframe(filtered_df)
st.download_button(
    label="下載篩選後資料（CSV）",
    data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="filtered_employees.csv",
    mime="text/csv"
)
