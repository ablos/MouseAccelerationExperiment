import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

SHOW_FIGS = False
PREFIX = "data/"

trials = pd.read_csv(f"{PREFIX}results.csv")
model_results = pd.read_csv(f"{PREFIX}model_results.csv")
effect_sizes = pd.read_csv(f"{PREFIX}effect_sizes.csv")

# Aggregate (average each metric per participant per session per task type)
agg = trials.groupby(["participant_id", "slot", "task_type", "group"]).agg(
    throughput=("throughput", "mean"),
    plr=("plr", "mean"),
    submovement_count=("submovement_count", "mean"),
    hit_rate=("hit", "mean"),
).reset_index()

baseline = agg[agg["slot"] == 1].set_index(["participant_id", "task_type"])

# 1.0 = baseline, < 1.0 = worse than baseline, > 1.0 = better than baseline
for metric in ["throughput", "plr", "submovement_count", "hit_rate"]:
    agg[f"{metric}_normalized"] = agg.apply(
        lambda row: row[metric] / baseline.loc[(row["participant_id"], row["task_type"]), metric],
        axis=1
    )

# =====================================
# NORMALIZED LEARNING CURVES
# =====================================

# Define metrics
metrics = [
    ("throughput_normalized", "Throughput (higher = better)"),
    ("plr_normalized", "Path Length Ratio (lower = better)"),
    ("submovement_count_normalized", "Submovement Count (lower = better)"),
    ("hit_rate_normalized", "Hit Rate (higher = better)"),
]

# Draw plots for each metric
for metric, label in metrics:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    fig.suptitle(label)
    
    for ax, task in zip(axes, ["clicking", "dragging", "slider"]):
        task_data = agg[agg["task_type"] == task]
    
        # Individual participant lines on the background
        for pid in task_data["participant_id"].unique():
            for group, color in [("control", "steelblue"), ("experimental", "tomato")]:
                pdata = task_data[(task_data["participant_id"] == pid) & (task_data["group"] == group)]
                ax.plot(pdata["slot"], pdata[metric], color=color, alpha=0.1, linewidth=0.8)
                
        # Mean + CI on foreground
        sns.lineplot(data=task_data, x="slot", y=metric, hue="group", ax=ax, marker="o", palette={"control": "steelblue", "experimental": "tomato"}, errorbar="ci")
        
        # Trend lines
        for group, color in [("control", "steelblue"), ("experimental", "tomato")]:
            sns.regplot(data=task_data[task_data["group"] == group], x="slot", y=metric, ax=ax, scatter=False, color=color, line_kws={"linestyle": "--", "alpha": 0.5}, ci=None)

        # Baseline
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
        
        ax.set_title(task)
        ax.set_xlabel("Slot")
        ax.set_ylabel(label if ax == axes[0] else "")
        
    plt.tight_layout()
    os.makedirs(f"{PREFIX}plots", exist_ok=True)
    plt.savefig(f"{PREFIX}plots/{metric}.png", dpi=150, bbox_inches="tight")
    
    if SHOW_FIGS:
        plt.show()
        
# =====================================
# RAW LEARNING CURVES
# =====================================
raw_metrics = [
    ("throughput", "Throughput (higher = better)"),
    ("plr", "Path Length Ratio (lower = better)"),
    ("submovement_count", "Submovement count (lower = better)"),
    ("hit_rate", "Hit Rate (higher = better)"),
]

for metric, label in raw_metrics:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    fig.suptitle(label)
    
    for ax, task in zip(axes, ["clicking", "dragging", "slider"]):
        task_data = agg[agg["task_type"] == task]
        
        for pid in task_data["participant_id"].unique():
            for group, color in [("control", "steelblue"), ("experimental", "tomato")]:
                pdata = task_data[(task_data["participant_id"] == pid) & (task_data["group"] == group)]
                ax.plot(pdata["slot"], pdata[metric], color=color, alpha=0.1, linewidth=0.8)
                
        sns.lineplot(data=task_data, x="slot", y=metric, hue="group", ax=ax, marker="o", palette={"control": "steelblue", "experimental": "tomato"}, errorbar="ci")
        
        for group, color in [("control", "steelblue"), ("experimental", "tomato")]:
            sns.regplot(data=task_data[task_data["group"] == group], x="slot", y=metric, ax=ax, scatter=False, color=color, line_kws={"linestyle": "--", "alpha": 0.5}, ci=None)
            
        ax.set_title(task)
        ax.set_xlabel("Slot")
        ax.set_ylabel(label if ax == axes[0] else "")
        
    plt.tight_layout()
    plt.savefig(f"{PREFIX}plots/raw_{metric}.png", dpi=150, bbox_inches="tight")
    
    if SHOW_FIGS:
        plt.show()

# =====================================
# MODEL RESULTS AND EFFECT SIZES
# =====================================

interaction = model_results[model_results["term"] == "group[T.experimental]:slot_scaled"].copy()
interaction["label"] = interaction.apply(lambda r: f"β={r['coef']:.3f}\np={r['p']:.3f}", axis=1)

# Pivot for heatmap
pval_pivot = interaction.pivot(index="metric", columns="task", values="p")
label_pivot = interaction.pivot(index="metric", columns="task", values="label")

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# p-value heatmap
sns.heatmap(pval_pivot, annot=label_pivot, fmt="", cmap="RdYlGn_r", vmin=0, vmax=0.1, ax=axes[0], linewidths=0.5)
axes[0].set_title("Interaction effect (group × slot)\np-value + coefficient")

# Add significance threshold to p-value colorbar
cbar_pval = axes[0].collections[0].colorbar
cbar_pval.set_ticks([0, 0.05, 0.1])
cbar_pval.set_ticklabels(["0", "0.05 ← sig", "0.1"])

# Effect size heatmap
f2_pivot = effect_sizes.pivot(index="metric", columns="task", values="cohens_f2")
sns.heatmap(f2_pivot, annot=True, fmt=".3f", cmap="Blues", ax=axes[1], linewidths=0.5)
axes[1].set_title("Effect size (Cohen's f²)")

# Add effect size thresholds to f² colorbar
cbar_f2 = axes[1].collections[0].colorbar
cbar_f2.set_ticks([0, 0.02, 0.15, 0.35])
cbar_f2.set_ticklabels(["0", "0.02 small", "0.15 medium", "0.35 large"])

plt.tight_layout()
fig.text(0.5, -0.02, "Note: All values are rounded to 3 decimal places. Very small p-values therefore display as 0.000.", ha="center", fontsize=8, style="italic")
plt.savefig(f"{PREFIX}plots/summary_heatmap.png", dpi=150, bbox_inches="tight")

if SHOW_FIGS:
    plt.show()
    
# =====================================
# DESCRIPTIVE STATISTICS
# =====================================

desc = trials.groupby(["group", "task_type"]).agg(
    throughput_mean=("throughput", "mean"),
    throughput_sd=("throughput", "std"),
    plr_mean=("plr", "mean"),
    plr_sd=("plr", "std"),
    submovement_mean=("submovement_count", "mean"),
    submovement_sd=("submovement_count", "std"),
    hit_rate_mean=("hit", "mean"),
    hit_rate_sd=("hit", "std"),
).reset_index()

desc.to_csv(f"{PREFIX}plots/descriptive_stats.csv", index=False)

fig, ax = plt.subplots(figsize=(14, 4))
ax.axis("off")

table_data = []
for _, row in desc.iterrows():
    table_data.append([
        row["group"], row["task_type"],
        f"{row['throughput_mean']:.3f} ± {row['throughput_sd']:.2f}",
        f"{row['plr_mean']:.3f} ± {row['plr_sd']:.3f}",
        f"{row['submovement_mean']:.3f} ± {row['submovement_mean']:.3f}",
        f"{row['hit_rate_mean']:.3f} ± {row['hit_rate_sd']:.3f}"
    ])
    
table = ax.table(
    cellText=table_data,
    colLabels=["Group", "Task", "Throughput (bits/s)", "Path Length Ratio", "Submovements", "Hit Rate"],
    loc="center",
    cellLoc="center",
)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.5)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold")
    elif row % 2 == 0:
        cell.set_facecolor("#e8e8e8")

plt.tight_layout()
plt.savefig(f"{PREFIX}plots/descriptive_stats.png", dpi=150, bbox_inches="tight")

if SHOW_FIGS:
    plt.show()
    
# =====================================
# BASELINE EQUIVALENCE (SLOT 1)
# =====================================

baseline_data = agg[agg["slot"] == 1]

fig, axes = plt.subplots(1, 4, figsize=(18, 4))
fig.suptitle("Baseline equivalence (slot 1)")

for ax, (metric, label) in zip(axes, [
    ("throughput", "Throughput (bits/s)"),
    ("plr", "Path Length Ratio"),
    ("submovement_count", "Submovement Count"),
    ("hit_rate", "Hit Rate"),
]):
    sns.boxplot(data=baseline_data, x="task_type", y=metric, hue="group", palette={"control": "steelblue", "experimental": "tomato"}, ax=ax)
    ax.set_title(label)
    ax.set_xlabel("")
    ax.set_ylabel("")
    
plt.tight_layout()
plt.savefig(f"{PREFIX}plots/baseline_equivalence.png", dpi=150, bbox_inches="tight")

if SHOW_FIGS:
    plt.show()
    
# =====================================
# DEMOGRAPHICS TABLE
# =====================================

participants = pd.read_csv(f"{PREFIX}participants.csv")
valid_participants = participants[participants["id"].isin(trials["participant_id"].unique())]

demo = valid_participants.groupby("group").agg(
    n=("id", "count"),
    age_mean=("age", "mean"),
    age_sd=("age", "std"),
    hours_per_week_mean=("hours_per_week", "mean"),
    hours_per_week_sd=("hours_per_week", "std"),
).reset_index()

# Categorical counts per group
sex_counts = valid_participants.groupby(["group", "sex"]).size().unstack(fill_value=0)
hand_counts = valid_participants.groupby(["group", "handedness"]).size().unstack(fill_value=0)
gaming_counts = valid_participants.groupby(["group", "gaming_experience"]).size().unstack(fill_value=0)

# Table: continuous variables
fig, ax = plt.subplots(figsize=(8, 2))
ax.axis("off")

table1_data = []
for _, row in demo.iterrows():
    table1_data.append([
        row["group"], int(row["n"]),
        f"{row['age_mean']:.1f} ± {row['age_sd']:.1f}",
        f"{row['hours_per_week_mean']:.1f} ± {row['hours_per_week_sd']:.1f}",
    ])

t1 = ax.table(
    cellText=table1_data,
    colLabels=["Group", "N", "Age (mean ± SD)", "Hours/week (mean ± SD)"],
    loc="center", cellLoc="center",
)
t1.auto_set_font_size(False)
t1.set_fontsize(9)
t1.scale(1, 2)

for (row, col), cell in t1.get_celld().items():
    cell.PAD = 0.05
    if row == 0:
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold")
    elif row % 2 == 0:
        cell.set_facecolor("#e8e8e8")

plt.tight_layout()
plt.savefig(f"{PREFIX}plots/demographics_continuous.png", dpi=150, bbox_inches="tight")

if SHOW_FIGS:
    plt.show()

# Bar charts: categorical variables
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.suptitle("Participant Demographics by Group")

for ax, (col, label) in zip(axes, [
    ("sex", "Sex"),
    ("handedness", "Handedness"),
    ("gaming_experience", "Gaming Experience"),
]):
    counts = valid_participants.groupby(["group", col]).size().reset_index(name="count")
    sns.barplot(data=counts, x=col, y="count", hue="group",
                palette={"control": "steelblue", "experimental": "tomato"}, ax=ax)
    ax.set_title(label)
    ax.set_xlabel("")
    ax.set_ylabel("Count")
        
plt.tight_layout()
plt.savefig(f"{PREFIX}plots/demographics_categorical.png", dpi=150, bbox_inches="tight")

if SHOW_FIGS:
    plt.show()