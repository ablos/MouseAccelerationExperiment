import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PREFIX = "data/"
OUTPUT_DIR = "data/participant_reports/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MOUSE_COORDINATES = "mouse_coordinates"
PARTICIPANTS = "participants"
SESSIONS = "sessions"
TASKS = "tasks"
TRIALS = "trials"

dfs = { name: pd.read_csv(f"{PREFIX}{name}.csv") for name in [MOUSE_COORDINATES, PARTICIPANTS, SESSIONS, TASKS, TRIALS] }

# Apply same data quality fixes as data_processing.py
dfs[TASKS] = dfs[TASKS].sort_values("id").drop_duplicates(subset=["session_id", "task_type"], keep="first")
complete_sessions = dfs[TASKS].groupby("session_id")["task_type"].nunique()
complete_sids = set(complete_sessions[complete_sessions == 3].index)
dfs[SESSIONS] = dfs[SESSIONS][dfs[SESSIONS]["id"].isin(complete_sids) & dfs[SESSIONS]["end_time"].notna()]

# Filter: >= 1 session, no monitor group
session_counts = dfs[SESSIONS].groupby("participant_id").size()
all_pids = set(session_counts[session_counts >= 1].index)
all_pids -= set(dfs[PARTICIPANTS].loc[dfs[PARTICIPANTS]["group"] == "monitor", "id"])

dfs[SESSIONS] = dfs[SESSIONS][dfs[SESSIONS]["participant_id"].isin(all_pids)]
valid_sids = set(dfs[SESSIONS]["id"])
dfs[TASKS] = dfs[TASKS][dfs[TASKS]["session_id"].isin(valid_sids)]
valid_tids = set(dfs[TASKS]["id"])
dfs[TRIALS] = dfs[TRIALS][dfs[TRIALS]["task_id"].isin(valid_tids)]
valid_trids = set(dfs[TRIALS]["id"])
dfs[MOUSE_COORDINATES] = dfs[MOUSE_COORDINATES][dfs[MOUSE_COORDINATES]["trial_id"].isin(valid_trids)]

# Slot correction for participants who missed slot 1
missing_slot1 = all_pids - set(dfs[SESSIONS].loc[dfs[SESSIONS]["slot"] == 1, "participant_id"])
def shift_slots(row):
    if row["participant_id"] in missing_slot1 and row["slot"] in [2, 3, 4, 5]:
        return row["slot"] - 1
    return row["slot"]
dfs[SESSIONS]["slot"] = dfs[SESSIONS].apply(shift_slots, axis=1)

# Build trials
trials = dfs[TRIALS].copy()
trials = trials.merge(dfs[TASKS][["id", "task_type", "session_id"]], left_on="task_id", right_on="id", suffixes=("", "_task"))
trials = trials.merge(dfs[SESSIONS][["id", "participant_id", "screen_px_per_mm", "slot", "hours_since_last_session"]], left_on="session_id", right_on="id", suffixes=("", "_session"))
trials = trials.merge(dfs[PARTICIPANTS][["id", "group"]], left_on="participant_id", right_on="id", suffixes=("", "_participant"))

trials["start_time"] = pd.to_datetime(trials["start_time"], format="ISO8601")
trials["end_time"] = pd.to_datetime(trials["end_time"], format="ISO8601")
trials["completion_time_ms"] = (trials["end_time"] - trials["start_time"]).dt.total_seconds() * 1000

slider_mask = trials["task_type"] == "slider"
dist_2d = np.sqrt((trials["end_x"] - trials["target_x"]) ** 2 + (trials["end_y"] - trials["target_y"]) ** 2)
dist_1d = (trials["end_x"] - trials["target_x"]).abs()
trials["accuracy_px"] = np.where(slider_mask, dist_1d, dist_2d)
trials["accuracy_mm"] = trials["accuracy_px"] / trials["screen_px_per_mm"]
trials["hit"] = np.where(slider_mask, dist_1d <= trials["target_size"] / 2, dist_2d <= trials["target_size"])

coords = dfs[MOUSE_COORDINATES].sort_values(["trial_id", "timestamp"])
coords_by_trial = { tid: grp for tid, grp in coords.groupby("trial_id") }

def compute_plr(row):
    trial_coords = coords_by_trial.get(row["id"])
    if trial_coords is None or len(trial_coords) < 2:
        return np.nan
    xs = trial_coords["x"].to_numpy()
    ys = trial_coords["y"].to_numpy()
    if row["task_type"] == "slider":
        path = np.sum(np.abs(np.diff(xs)))
        straight = abs(row["start_x"] - row["end_x"])
    else:
        path = np.sum(np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2))
        straight = np.sqrt((row["start_x"] - row["end_x"]) ** 2 + (row["start_y"] - row["end_y"]) ** 2)
    return np.nan if straight == 0 else path / straight

def compute_submovements(row):
    trial_coords = coords_by_trial.get(row["id"])
    if trial_coords is None or len(trial_coords) < 2:
        return np.nan
    xs = trial_coords["x"].to_numpy()
    ys = trial_coords["y"].to_numpy()
    ts = trial_coords["timestamp"].to_numpy().astype(float)
    dt = np.diff(ts)
    dt[dt == 0] = np.nan
    speed = np.abs(np.diff(xs)) / dt if row["task_type"] == "slider" else np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2) / dt
    speed = np.nan_to_num(speed, nan=0.0)
    speed = gaussian_filter1d(speed, sigma=1.5)
    median_dt = np.median(dt[~np.isnan(dt)])
    min_distance_samples = int(100 / median_dt)
    min_speed = 0.05 * np.nanmax(speed)
    peaks, _ = find_peaks(speed, height=min_speed, prominence=min_speed, distance=min_distance_samples)
    return len(peaks)

trials["plr"] = trials.apply(compute_plr, axis=1)
trials["submovement_count"] = trials.apply(compute_submovements, axis=1)

D = np.where(slider_mask, np.abs(trials["start_x"] - trials["target_x"]),
             np.sqrt((trials["start_x"] - trials["target_x"]) ** 2 + (trials["start_y"] - trials["target_y"]) ** 2))
trials["id_bits"] = np.log2(2 * D / trials["target_size"])
trials["throughput"] = trials["id_bits"] / (trials["completion_time_ms"] / 1000)

# MAD-based trial-level outlier filtering (same as data_processing.py)
mask = pd.Series(True, index=trials.index)
for (pid, task), group in trials.groupby(["participant_id", "task_type"]):
    median = group["throughput"].median()
    mad = np.median(np.abs(group["throughput"] - median))
    if mad == 0:
        continue
    modified_z = 0.6745 * (group["throughput"] - median) / mad
    mask[group.index[np.abs(modified_z) > 3.5]] = False
trials = trials[mask]

# Aggregate per participant per slot per task type
agg = trials.groupby(["participant_id", "slot", "task_type", "group"]).agg(
    throughput=("throughput", "mean"),
    plr=("plr", "mean"),
    submovement_count=("submovement_count", "mean"),
    hit_rate=("hit", "mean"),
).reset_index()

# Load valid participant agg for group means (from main analysis)
valid_trials = pd.read_csv(f"{PREFIX}results.csv")
valid_agg = valid_trials.groupby(["participant_id", "slot", "task_type", "group"]).agg(
    throughput=("throughput", "mean"),
    plr=("plr", "mean"),
    submovement_count=("submovement_count", "mean"),
    hit_rate=("hit", "mean"),
).reset_index()

metrics = [
    ("throughput", "Throughput (bits/s)", "higher = better"),
    ("plr", "Path Length Ratio", "lower = better"),
    ("submovement_count", "Submovement Count", "lower = better"),
    ("hit_rate", "Hit Rate", "higher = better"),
]

pid_to_code = dfs[PARTICIPANTS].set_index("id")["code"].to_dict()

for pid in sorted(trials["participant_id"].unique()):
    pdata = agg[agg["participant_id"] == pid]
    group = pdata["group"].iloc[0]
    other_group = "control" if group == "experimental" else "experimental"
    code = pid_to_code.get(pid, str(pid))

    fig, axes = plt.subplots(len(metrics), 3, figsize=(15, 3 * len(metrics)), sharey="row")
    fig.suptitle(f"Participant {code} ({group} group) — Performance over sessions", fontsize=14)

    for row, (metric, label, direction) in enumerate(metrics):
        for col, task in enumerate(["clicking", "dragging", "slider"]):
            ax = axes[row][col]
            task_data = pdata[pdata["task_type"] == task]

            group_data = valid_agg[(valid_agg["group"] == group) & (valid_agg["task_type"] == task)]
            other_data = valid_agg[(valid_agg["group"] == other_group) & (valid_agg["task_type"] == task)]
            group_mean = group_data.groupby("slot")[metric].mean()
            other_mean = other_data.groupby("slot")[metric].mean()

            ax.plot(other_mean.index, other_mean.values,
                    color="steelblue" if other_group == "control" else "tomato",
                    linewidth=1, linestyle="--", alpha=0.5, label=f"{other_group} mean")
            ax.plot(group_mean.index, group_mean.values,
                    color="steelblue" if group == "control" else "tomato",
                    linewidth=1, linestyle=":", alpha=0.7, label=f"{group} mean")
            ax.plot(task_data["slot"], task_data[metric],
                    color="steelblue" if group == "control" else "tomato",
                    marker="o", linewidth=2, label="you")

            baseline_rows = task_data[task_data["slot"] == 1]
            if not baseline_rows.empty:
                baseline_val = baseline_rows[metric].iloc[0]
                if pd.notna(baseline_val):
                    ax.axhline(baseline_val, color="gray", linewidth=1,
                               linestyle="--", alpha=0.6, label="your baseline")

            if row == 0:
                ax.set_title(task)
            if col == 0:
                ax.set_ylabel(f"{label}\n({direction})", fontsize=8)
            ax.set_xlabel("Session" if row == len(metrics) - 1 else "")

    axes[0][2].legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}participant_{pid}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved report for participant {pid}")

print(f"\nDone. Reports saved to {OUTPUT_DIR}")
