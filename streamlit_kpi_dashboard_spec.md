
# Streamlit Dashboard for Employee KPI Analysis

## Objective
Build a single-page Streamlit dashboard with Plotly visualizations to simulate and analyze employee data from a multi-location, multi-department company. Users should be able to explore performance, salary, and bonus data interactively, and monitor KPI targets.

## Features

### 1. Simulated Employee Dataset
- Locations: 城市1–城市4
- Departments: 單位1–單位10 (repeat across cities)
- Fields:
  - 員工姓名: 隨機中文姓名
  - 年薪: 100,000–300,000
  - 獎金: 10,000–30,000
  - 考績 (Performance): 1–10
- Derived:
  - 總薪資 = 年薪 + 獎金
  - 重要程度 = 年薪 * 考績

### 2. Filters
- Location
- Department
- Name keyword
- Performance score range
- Settings are saved/restored from `filter_config.json`

### 3. KPI Monitoring
- User-defined KPI targets:
  - Average Salary
  - Average Bonus
  - Average Performance Score
- Actual averages are compared to targets
- Color-coded delta values using `st.metric`

### 4. Visualizations
- **Treemap** (hierarchical view using `plotly.express.treemap`)
- **Sunburst** (radial hierarchy using `plotly.express.sunburst`)
- Based on path levels (City > Department > Person), using 重要程度 as value
- Custom color encoding

### 5. Department KPI Table
- Aggregation by Department:
  - 平均年薪, 平均獎金, 平均考績, 人數
  - % of target for each KPI
- Conditional formatting:
  - Green gradient for high performance
  - Red for low performance
- Auto flag:
  - "最強單位" if all KPIs ≥ 100%
  - "需改善" if all KPIs < 90%
- Flag color overlay (green/pink background)
- CSV export option

### 6. Code Readability
- Every major block annotated with:
  - WHAT: explains what the block does
  - WHY: explains why it's written that way
