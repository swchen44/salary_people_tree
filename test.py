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
df["人員要重程度"] = df["人員年薪"] * df["人員考績"]

st.title("公司員工結構視覺化")
st.caption("可篩選公司地點、單位、人員姓名與考績分數，依要重程度呈現")

# 搜尋與篩選
selected_city = st.multiselect("選擇公司地點:", options=sorted(df["公司地點"].unique()), default=sorted(df["公司地點"].unique()))
selected_unit = st.multiselect("選擇單位:", options=sorted(df["單位"].unique()), default=sorted(df["單位"].unique()))
search_name = st.text_input("輸入人員姓名關鍵字（可選）")
performance_range = st.slider("選擇考績分數範圍:", 1, 10, (1, 10))
top_n = st.slider("顯示 Top N 要重程度最高人員（可選）:", 1, 100, 100)

filtered_df = df[
    df["公司地點"].isin(selected_city) &
    df["單位"].isin(selected_unit) &
    df["人員考績"].between(performance_range[0], performance_range[1])
]

if search_name:
    filtered_df = filtered_df[filtered_df["人員名字"].str.contains(search_name)]

# 依要重程度排序顯示前 N 名（避免圖太大）
filtered_df = filtered_df.sort_values("人員要重程度", ascending=False).head(top_n)

# Treemap 顯示（依人員要重程度）
st.subheader("Treemap（依人員要重程度）")
fig = px.treemap(
    filtered_df,
    path=["公司地點", "單位", "人員名字"],
    values="人員要重程度",
    color="人員年薪",
    color_continuous_scale="RdBu",
    hover_data={"人員年薪": True, "人員獎金": True, "人員考績": True, "人員要重程度": True}
)
st.plotly_chart(fig, use_container_width=True)

# Sunburst 顯示（可選）
st.subheader("Sunburst（依人員要重程度）")
fig2 = px.sunburst(
    filtered_df,
    path=["公司地點", "單位", "人員名字"],
    values="人員要重程度",
    color="人員考績",
    color_continuous_scale="Bluered_r",
    hover_data={"人員年薪": True, "人員獎金": True, "人員考績": True, "人員要重程度": True}
)
st.plotly_chart(fig2, use_container_width=True)

