"""Streamlit dashboard: Small Business Profit Leakage Detector.

Run:  streamlit run app.py
Needs: pip install streamlit pandas matplotlib
"""
import streamlit as st
import analysis as a
import charts as c

st.set_page_config(page_title="Profit Leakage Detector", page_icon="🕵️", layout="wide")


@st.cache_data
def load(sales_file, exp_file):
    return a.load_and_clean(sales_file, exp_file)


st.title("🕵️ Small Business Profit Leakage Detector")
st.caption("Finds where a small business loses money: discounts, wastage, expenses and wrong pricing.")

# ---------------- sidebar: data + month ----------------
st.sidebar.header("Data")
up_sales = st.sidebar.file_uploader("Sales CSV", type="csv")
up_exp = st.sidebar.file_uploader("Expenses CSV", type="csv")
sales, exp, report = load(up_sales or "sales.csv", up_exp or "expenses.csv")
monthly = a.monthly_summary(sales, exp)

months = ["All"] + list(monthly.index)
month = st.sidebar.selectbox("Month", months, index=len(months) - 1)

with st.sidebar.expander("Data cleaning report"):
    st.write(f"Rows loaded: {report['rows_before']}")
    st.write(f"Blank cells filled: {report['blank_cells']}")
    st.write(f"Duplicates removed: {report['duplicates_removed']}")
    st.write(f"Rows after cleaning: {report['rows_after']}")

# ---------------- KPI row ----------------
items = a.waterfall_items(sales, exp, month)
gross = items[0][1]
net = items[-1][1]
disc = -items[1][1]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Gross sales", f"Rs {gross:,.0f}")
k2.metric("Discounts given", f"Rs {disc:,.0f}", f"{100 * disc / gross:.1f}% of sales", delta_color="inverse")
k3.metric("Net profit", f"Rs {net:,.0f}")
k4.metric("Net margin", f"{100 * net / (gross - disc):.1f}%")

# ---------------- insights ----------------
st.subheader("Auto-generated insights")
for line in a.generate_insights(monthly, sales, exp):
    (st.error if line.startswith("ALERT") else st.warning)(line)

# ---------------- waterfall + trend ----------------
left, right = st.columns([3, 2])
with left:
    st.subheader("Profit waterfall")
    st.pyplot(c.waterfall(items, f"Where did the money go? ({month})"))
with right:
    st.subheader("Monthly trend")
    st.pyplot(c.monthly_trend(monthly))

# ---------------- leakage score + product margins ----------------
l2, r2 = st.columns(2)
leak = a.leakage_table(sales, exp, month)
with l2:
    st.subheader("Leakage score")
    st.dataframe(leak, use_container_width=True)
    st.pyplot(c.leakage_bar(leak))
with r2:
    st.subheader("Product margins")
    pm = a.product_margins(sales, month)
    st.dataframe(pm[["revenue", "gross_profit", "margin_pct", "status"]], use_container_width=True)
    st.pyplot(c.product_margin_bar(pm))

# ---------------- what-if simulator ----------------
st.subheader("What-if simulator")
s1, s2, s3 = st.columns(3)
dc = s1.slider("Cut discounts by (%)", 0, 100, 0)
wc = s2.slider("Cut wastage by (%)", 0, 100, 0)
pr = s3.slider("Raise prices by (%)", 0, 15, 0)
w = a.what_if(sales, exp, month, dc, wc, pr)
m1, m2 = st.columns(2)
m1.metric("Profit today", f"Rs {w['base_profit']:,.0f}")
m2.metric("Profit with changes", f"Rs {w['new_profit']:,.0f}", f"Rs {w['gain']:,.0f}")

with st.expander("Raw cleaned sales data"):
    st.dataframe(sales)
