import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PREFIX = "data/"

trials = pd.read_csv(f"{PREFIX}results.csv")

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




# Define metrics
metrics = [
    ("throughput_normalized", "Throughput (higher = better)"),
    ("plr_normalized", "PLR (lower = better)"),
    ("submovement_count_normalized", "Submovement Count (lower = better)"),
    ("hit_rate_normalized", "Hit Rate (higher = better)"),
]

# Draw plots
for metric, label in metrics:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), sharey=True)
    fig.suptitle(label)
    
    for ax, task in zip(axes, ["clicking", "dragging", "slider"]):
        task_data = agg[agg["task_type"] == task]
        sns.lineplot(data=task_data, x="slot", y=metric, hue="group", ax=ax, marker="o",
                     palette={"control": "steelblue", "experimental": "tomato"})
        sns.regplot(data=task_data[task_data["group"] == "control"], x="slot", y=metric,
            ax=ax, scatter=False, color="steelblue", line_kws={"linestyle": "--", "alpha": 0.5})
        sns.regplot(data=task_data[task_data["group"] == "experimental"], x="slot", y=metric,
            ax=ax, scatter=False, color="tomato", line_kws={"linestyle": "--", "alpha": 0.5})

        
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
        ax.set_title(task)
        ax.set_xlabel("Slot")
        ax.set_ylabel(label if ax == axes[0] else "")
        
    plt.tight_layout()
    os.makedirs(f"{PREFIX}plots", exist_ok=True)
    plt.savefig(f"{PREFIX}plots/{metric}.png", dpi=150)
    plt.show()