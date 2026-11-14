"""Matplotlib charts shared by run_analysis.py and the Streamlit app."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GREEN, RED, BLUE, GREY = "#2e7d32", "#c62828", "#1565c0", "#9e9e9e"


def waterfall(items, title="Profit Waterfall"):
    """items = [(label, value), ...]; first = start, last = final total."""
    labels = [n for n, _ in items]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    running = 0
    for i, (name, val) in enumerate(items):
        if i == 0:                       # starting bar
            ax.bar(i, val, color=BLUE)
            running = val
            ax.text(i, val, f"{val:,.0f}", ha="center", va="bottom", fontsize=8)
        elif i == len(items) - 1:        # final total
            ax.bar(i, val, color=GREEN if val >= 0 else RED)
            ax.text(i, val, f"{val:,.0f}", ha="center",
                    va="bottom" if val >= 0 else "top", fontsize=9, fontweight="bold")
        else:                            # a leak (negative step)
            ax.bar(i, val, bottom=running, color=RED if val < 0 else GREEN)
            ax.text(i, running + val, f"{val:,.0f}", ha="center", va="top",
                    fontsize=8, color="black")
            running += val
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Amount (Rs)")
    ax.set_title(title)
    fig.tight_layout()
    return fig


def monthly_trend(monthly):
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    ax1.plot(monthly.index, monthly["net_profit"], marker="o", color=GREEN, label="Net profit (Rs)")
    ax1.set_ylabel("Net profit (Rs)")
    ax1.axhline(0, color=GREY, linewidth=0.8)
    ax2 = ax1.twinx()
    ax2.plot(monthly.index, monthly["discount_rate_pct"], marker="s", color=RED,
             linestyle="--", label="Discount rate (%)")
    ax2.set_ylabel("Discount rate (% of gross sales)")
    ax1.set_title("Profit falls as discounts rise")
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="center left")
    fig.tight_layout()
    return fig


def leakage_bar(table):
    t = table.sort_values("pct_of_gross_sales")
    colors = {"High Risk": RED, "Medium Risk": "#ef6c00", "Low Risk": GREEN}
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(t.index, t["pct_of_gross_sales"], color=[colors[r] for r in t["risk"]])
    ax.set_xlabel("Leak as % of gross sales")
    ax.set_title("Leakage Score by category")
    fig.tight_layout()
    return fig


def product_margin_bar(pm):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(pm.index, pm["margin_pct"], color=[RED if x < 0 else BLUE for x in pm["margin_pct"]])
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Margin after discount (%)")
    ax.set_title("Product margins (red = loss-making)")
    fig.tight_layout()
    return fig
