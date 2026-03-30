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

# Capitalize categorical labels for display
for df in [trials, model_results, effect_sizes]:
    for col in ["group", "task", "task_type", "metric"]:
        if col in df.columns:
            df[col] = df[col].str.capitalize()

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

GROUP_PALETTE = {"Control": "steelblue", "Experimental": "tomato"}

os.makedirs(f"{PREFIX}plots", exist_ok=True)
os.makedirs(f"{PREFIX}plots_transparent", exist_ok=True)

def savefig(filename):
    plt.savefig(f"{PREFIX}plots/{filename}", dpi=150, bbox_inches="tight")
    plt.savefig(f"{PREFIX}plots_transparent/{filename}", dpi=150, bbox_inches="tight", transparent=True)

def set_ci_ylim(ax, task_data, metric, floor=None):
    ci_bounds = []
    for group in task_data["group"].unique():
        for slot in task_data["slot"].unique():
            vals = task_data[(task_data["group"] == group) & (task_data["slot"] == slot)][metric].dropna()
            if len(vals) > 1:
                se = vals.std() / np.sqrt(len(vals))
                ci_bounds.append(vals.mean() - 1.96 * se)
                ci_bounds.append(vals.mean() + 1.96 * se)
    lo, hi = min(ci_bounds), max(ci_bounds)
    pad = max((hi - lo) * 0.1, 0.05)
    lo_final = max(floor, lo - pad) if floor is not None else lo - pad
    ax.set_ylim(lo_final, hi + pad)

def remove_inner_legends(axes):
    for ax in axes:
        legend = ax.get_legend()
        if legend:
            legend.remove()

def add_shared_legend(fig, axes):
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(1.0, 1.0), frameon=True)

# =====================================
# NORMALIZED LEARNING CURVES
# =====================================

metrics = [
    ("throughput_normalized", "Throughput (relative to baseline)", "higher = better"),
    ("plr_normalized", "Path Length Ratio (relative to baseline)", "lower = better"),
    ("submovement_count_normalized", "Submovement Count (relative to baseline)", "lower = better"),
    ("hit_rate_normalized", "Hit Rate (relative to baseline)", "higher = better"),
]

for metric, title, subtitle in metrics:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
    fig.suptitle(title, fontsize=13, y=1.02)
    fig.text(0.5, 0.95, subtitle, ha="center", fontsize=10, color="gray")

    for ax, task in zip(axes, ["Clicking", "Dragging", "Slider"]):
        task_data = agg[agg["task_type"] == task]

        sns.lineplot(data=task_data, x="slot", y=metric, hue="group", ax=ax, marker="o", palette=GROUP_PALETTE, errorbar="ci", n_boot=2000, err_kws={"alpha": 0.15})

        for group, color in GROUP_PALETTE.items():
            sns.regplot(data=task_data[task_data["group"] == group], x="slot", y=metric, ax=ax, scatter=False, color=color, line_kws={"linestyle": "--", "alpha": 0.5}, ci=None)

        ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
        set_ci_ylim(ax, task_data, metric)

        ax.set_title(task)
        ax.set_xlabel("Slot")
        ax.set_ylabel(title if ax == axes[0] else "")

    remove_inner_legends(axes)
    add_shared_legend(fig, axes)

    plt.tight_layout()
    os.makedirs(f"{PREFIX}plots", exist_ok=True)
    savefig(f"{metric}.png")

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
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=False)
    fig.suptitle(label)

    for ax, task in zip(axes, ["Clicking", "Dragging", "Slider"]):
        task_data = agg[agg["task_type"] == task]

        sns.lineplot(data=task_data, x="slot", y=metric, hue="group", ax=ax, marker="o", palette=GROUP_PALETTE, errorbar="ci", n_boot=2000, err_kws={"alpha": 0.15})

        for group, color in GROUP_PALETTE.items():
            sns.regplot(data=task_data[task_data["group"] == group], x="slot", y=metric, ax=ax, scatter=False, color=color, line_kws={"linestyle": "--", "alpha": 0.5}, ci=None)

        set_ci_ylim(ax, task_data, metric, floor=0)

        ax.set_title(task)
        ax.set_xlabel("Slot")
        ax.set_ylabel(label if ax == axes[0] else "")

    remove_inner_legends(axes)
    add_shared_legend(fig, axes)

    plt.tight_layout()
    savefig(f"raw_{metric}.png")

    if SHOW_FIGS:
        plt.show()

# =====================================
# MODEL RESULTS AND EFFECT SIZES
# =====================================

METRIC_LABELS = {"Plr": "Path Length Ratio", "Submovement_count": "Submovement Count", "Hit": "Hit Rate"}

def make_term_pivots(term):
    df = model_results[model_results["term"] == term].copy()
    df["label"] = df.apply(lambda r: f"β={r['coef']:.3f}\np={r['p']:.3f}" + (" *" if r['p'] < 0.004 else ""), axis=1)
    p = df.pivot(index="metric", columns="task", values="p").rename(index=METRIC_LABELS)
    l = df.pivot(index="metric", columns="task", values="label").rename(index=METRIC_LABELS)
    return p, l

interaction_p, interaction_l = make_term_pivots("group[T.experimental]:slot_scaled")
group_p, group_l = make_term_pivots("group[T.experimental]")

fig, axes = plt.subplots(1, 3, figsize=(18, 4))

sns.heatmap(group_p, annot=group_l, fmt="", cmap="RdYlGn_r", vmin=0, vmax=0.1, ax=axes[0], linewidths=0.5)
axes[0].set_title("Main effect of group\np-value + coefficient")
cbar = axes[0].collections[0].colorbar
cbar.set_ticks([0, 0.004, 0.05, 0.1])
cbar.set_ticklabels(["0", "0.004*", "0.05", "0.1"])

sns.heatmap(interaction_p, annot=interaction_l, fmt="", cmap="RdYlGn_r", vmin=0, vmax=0.1, ax=axes[1], linewidths=0.5)
axes[1].set_title("Interaction effect (group x slot)\np-value + coefficient")
cbar = axes[1].collections[0].colorbar
cbar.set_ticks([0, 0.004, 0.05, 0.1])
cbar.set_ticklabels(["0", "0.004*", "0.05", "0.1"])

f2_pivot = effect_sizes.pivot(index="metric", columns="task", values="cohens_f2").rename(index=METRIC_LABELS)
sns.heatmap(f2_pivot, annot=True, fmt=".3f", cmap="Blues", ax=axes[2], linewidths=0.5)
axes[2].set_title("Interaction effect size\n(incremental Cohen's f²)")
axes[2].collections[0].colorbar.set_label("f²", fontsize=9)

plt.tight_layout()
fig.text(0.5, -0.05, "Note: All values are rounded to 3 decimal places. Very small p-values therefore display as 0.000.\n* p < .004 (Bonferroni correction across 12 tests)", ha="center", fontsize=8, style="italic")
savefig("summary_heatmap.png")

if SHOW_FIGS:
    plt.show()

# =====================================
# IMPROVEMENT HEATMAP (Mann-Whitney + Cohen's d)
# =====================================

improvement_tests = pd.read_csv(f"{PREFIX}improvement_tests.csv")
METRIC_LABELS_IMP = {"throughput": "Throughput", "plr": "Path Length Ratio", "submovement_count": "Submovement Count", "hit": "Hit Rate"}

imp_p = improvement_tests.pivot(index="metric", columns="task", values="p").rename(index=METRIC_LABELS_IMP)
imp_d = improvement_tests.pivot(index="metric", columns="task", values="cohens_d").rename(index=METRIC_LABELS_IMP)

imp_p_label = improvement_tests.copy()
imp_p_label["label"] = imp_p_label.apply(lambda r: f"p={r['p']:.3f}" + (" *" if r["p"] < 0.004 else ""), axis=1)
imp_p_label = imp_p_label.pivot(index="metric", columns="task", values="label").rename(index=METRIC_LABELS_IMP)

imp_d_label = improvement_tests.copy()
imp_d_label["label"] = imp_d_label["cohens_d"].apply(lambda d: f"d={d:.2f}")
imp_d_label = imp_d_label.pivot(index="metric", columns="task", values="label").rename(index=METRIC_LABELS_IMP)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

sns.heatmap(imp_p, annot=imp_p_label, fmt="", cmap="RdYlGn_r", vmin=0, vmax=0.1, ax=axes[0], linewidths=0.5)
axes[0].set_title("Mann-Whitney U: group difference in % improvement\np-value")
cbar = axes[0].collections[0].colorbar
cbar.set_ticks([0, 0.004, 0.05, 0.1])
cbar.set_ticklabels(["0", "0.004*", "0.05", "0.1"])

sns.heatmap(imp_d, annot=imp_d_label, fmt="", cmap="RdYlGn", vmin=-1, vmax=2, ax=axes[1], linewidths=0.5)
axes[1].set_title("Effect size (Cohen's d)\n% improvement: experimental vs control")
axes[1].collections[0].colorbar.set_label("d", fontsize=9)

plt.tight_layout()
fig.text(0.5, -0.05, "Note: * p < .004 (Bonferroni correction across 12 tests). Positive d = experimental improved more.", ha="center", fontsize=8, style="italic")
savefig("improvement_heatmap.png")

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

desc_overall = trials.groupby("group").agg(
    throughput_mean=("throughput", "mean"),
    throughput_sd=("throughput", "std"),
    plr_mean=("plr", "mean"),
    plr_sd=("plr", "std"),
    submovement_mean=("submovement_count", "mean"),
    submovement_sd=("submovement_count", "std"),
    hit_rate_mean=("hit", "mean"),
    hit_rate_sd=("hit", "std"),
).reset_index()
desc_overall["task_type"] = "All tasks"

desc.to_csv(f"{PREFIX}plots/descriptive_stats.csv", index=False)

fig, ax = plt.subplots(figsize=(14, 5))
ax.axis("off")

table_data = []
for _, row in desc.iterrows():
    table_data.append([
        row["group"], row["task_type"],
        f"{row['throughput_mean']:.3f} ± {row['throughput_sd']:.2f}",
        f"{row['plr_mean']:.3f} ± {row['plr_sd']:.3f}",
        f"{row['submovement_mean']:.3f} ± {row['submovement_sd']:.3f}",
        f"{row['hit_rate_mean']:.3f} ± {row['hit_rate_sd']:.3f}"
    ])
for _, row in desc_overall.iterrows():
    table_data.append([
        row["group"], "All tasks",
        f"{row['throughput_mean']:.3f} ± {row['throughput_sd']:.2f}",
        f"{row['plr_mean']:.3f} ± {row['plr_sd']:.3f}",
        f"{row['submovement_mean']:.3f} ± {row['submovement_sd']:.3f}",
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
savefig("descriptive_stats.png")

if SHOW_FIGS:
    plt.show()

# =====================================
# MEAN % IMPROVEMENT FROM BASELINE
# =====================================

# Last two sessions per participant per task
max_slot = agg.groupby(["participant_id", "task_type"])["slot"].max().reset_index()
max_slot["slot_cutoff"] = max_slot["slot"] - 1
last_two = agg.merge(max_slot[["participant_id", "task_type", "slot_cutoff"]], on=["participant_id", "task_type"])
last_two = last_two[last_two["slot"] >= last_two["slot_cutoff"]]

# Mean of last two sessions per participant per task
final_perf = last_two.groupby(["participant_id", "task_type", "group"])[["throughput", "plr", "submovement_count", "hit_rate"]].mean().reset_index()
baseline_perf = agg[agg["slot"] == 1][["participant_id", "task_type", "throughput", "plr", "submovement_count", "hit_rate"]].rename(columns={
    "throughput": "throughput_base", "plr": "plr_base", "submovement_count": "submovement_base", "hit_rate": "hit_rate_base"
})

merged = final_perf.merge(baseline_perf, on=["participant_id", "task_type"])
merged["throughput_pct"]  = (merged["throughput"]        - merged["throughput_base"])        / merged["throughput_base"]        * 100
merged["plr_pct"]         = (merged["plr_base"]          - merged["plr"])                    / merged["plr_base"]                * 100
merged["submovement_pct"] = (merged["submovement_base"]  - merged["submovement_count"])       / merged["submovement_base"]        * 100
merged["hit_rate_pct"]    = (merged["hit_rate"]          - merged["hit_rate_base"])           / merged["hit_rate_base"]           * 100

improvement_df = merged[["participant_id", "task_type", "group", "throughput_pct", "plr_pct", "submovement_pct", "hit_rate_pct"]]
pct_summary = improvement_df.groupby(["group", "task_type"])[["throughput_pct", "plr_pct", "submovement_pct", "hit_rate_pct"]].agg(["mean", "std"]).reset_index()
pct_summary.columns = ["_".join(c).strip("_") for c in pct_summary.columns]

pct_overall = improvement_df.groupby("group")[["throughput_pct", "plr_pct", "submovement_pct", "hit_rate_pct"]].agg(["mean", "std"]).reset_index()
pct_overall.columns = ["_".join(c).strip("_") for c in pct_overall.columns]
pct_overall["task_type"] = "All tasks"

pct_summary.to_csv(f"{PREFIX}plots/improvement_pct.csv", index=False)

# Cohen's d on improvement percentages
def cohens_d(a, b):
    n1, n2 = len(a), len(b)
    pooled_std = np.sqrt(((n1 - 1) * a.std(ddof=1)**2 + (n2 - 1) * b.std(ddof=1)**2) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / pooled_std if pooled_std > 0 else 0

cohens_d_rows = []
_groups = improvement_df.groupby(["task_type", "group"])
_groups_overall = improvement_df.groupby("group")
for metric in ["throughput_pct", "plr_pct", "submovement_pct", "hit_rate_pct"]:
    for task in ["Clicking", "Dragging", "Slider"]:
        exp = _groups.get_group((task, "Experimental"))[metric].dropna() if (task, "Experimental") in _groups.groups else pd.Series(dtype=float)
        ctrl = _groups.get_group((task, "Control"))[metric].dropna() if (task, "Control") in _groups.groups else pd.Series(dtype=float)
        cohens_d_rows.append({"metric": metric, "task": task.lower(), "cohens_d": cohens_d(exp, ctrl)})
    exp = _groups_overall.get_group("Experimental")[metric].dropna() if "Experimental" in _groups_overall.groups else pd.Series(dtype=float)
    ctrl = _groups_overall.get_group("Control")[metric].dropna() if "Control" in _groups_overall.groups else pd.Series(dtype=float)
    cohens_d_rows.append({"metric": metric, "task": "all", "cohens_d": cohens_d(exp, ctrl)})

cohens_d_df = pd.DataFrame(cohens_d_rows)
print("\nCohen's d on improvement percentages:")
print(cohens_d_df.to_string(index=False))
cohens_d_df.to_csv(f"{PREFIX}plots/cohens_d_improvement.csv", index=False)

fig, ax = plt.subplots(figsize=(16, 5))
ax.axis("off")

table_data = []
for _, row in pct_summary.iterrows():
    table_data.append([
        row["group"], row["task_type"],
        f"{row['throughput_pct_mean']:+.1f}% ± {row['throughput_pct_std']:.1f}%",
        f"{row['plr_pct_mean']:+.1f}% ± {row['plr_pct_std']:.1f}%",
        f"{row['submovement_pct_mean']:+.1f}% ± {row['submovement_pct_std']:.1f}%",
        f"{row['hit_rate_pct_mean']:+.1f}% ± {row['hit_rate_pct_std']:.1f}%",
    ])
for _, row in pct_overall.iterrows():
    table_data.append([
        row["group"], "All tasks",
        f"{row['throughput_pct_mean']:+.1f}% ± {row['throughput_pct_std']:.1f}%",
        f"{row['plr_pct_mean']:+.1f}% ± {row['plr_pct_std']:.1f}%",
        f"{row['submovement_pct_mean']:+.1f}% ± {row['submovement_pct_std']:.1f}%",
        f"{row['hit_rate_pct_mean']:+.1f}% ± {row['hit_rate_pct_std']:.1f}%",
    ])

table = ax.table(
    cellText=table_data,
    colLabels=["Group", "Task", "Throughput", "Path Length Ratio", "Submovements", "Hit Rate"],
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

ax.set_title("Mean % improvement from baseline (last 2 sessions vs slot 1)\nPositive = better for all metrics", fontsize=10, pad=12)
plt.tight_layout()
savefig("improvement_pct.png")

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
    sns.boxplot(data=baseline_data, x="task_type", y=metric, hue="group", palette=GROUP_PALETTE, ax=ax)
    ax.set_title(label)
    ax.set_xlabel("")
    ax.set_ylabel("")

remove_inner_legends(axes)
add_shared_legend(fig, axes)

plt.tight_layout()
savefig("baseline_equivalence.png")

if SHOW_FIGS:
    plt.show()

# =====================================
# DEMOGRAPHICS TABLE
# =====================================

participants = pd.read_csv(f"{PREFIX}participants.csv")
participants["group"] = participants["group"].str.capitalize()
valid_participants = participants[participants["id"].isin(trials["participant_id"].unique())]

demo = valid_participants.groupby("group").agg(
    n=("id", "count"),
    age_mean=("age", "mean"),
    age_sd=("age", "std"),
    hours_per_week_mean=("hours_per_week", "mean"),
    hours_per_week_sd=("hours_per_week", "std"),
).reset_index()

sex_counts = valid_participants.groupby(["group", "sex"]).size().unstack(fill_value=0)
hand_counts = valid_participants.groupby(["group", "handedness"]).size().unstack(fill_value=0)
gaming_counts = valid_participants.groupby(["group", "gaming_experience"]).size().unstack(fill_value=0)

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
savefig("demographics_continuous.png")

if SHOW_FIGS:
    plt.show()

fig, axes = plt.subplots(1, 3, figsize=(14, 4))
fig.suptitle("Participant Demographics by Group")

for ax, (col, label) in zip(axes, [
    ("sex", "Sex"),
    ("handedness", "Handedness"),
    ("gaming_experience", "Gaming Experience"),
]):
    counts = valid_participants.groupby(["group", col]).size().reset_index(name="count")
    sns.barplot(data=counts, x=col, y="count", hue="group", palette=GROUP_PALETTE, ax=ax)
    ax.set_title(label)
    ax.set_xlabel("")
    ax.set_ylabel("Count")

remove_inner_legends(axes)
add_shared_legend(fig, axes)

plt.tight_layout()
savefig("demographics_categorical.png")

if SHOW_FIGS:
    plt.show()
