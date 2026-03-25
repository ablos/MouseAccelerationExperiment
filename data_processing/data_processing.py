import time
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

t_start = time.time()

PREFIX = "data/"
MOUSE_COORDINATES = "mouse_coordinates"
PARTICIPANTS = "participants"
SESSIONS = "sessions"
TASKS = "tasks"
TRIALS = "trials"

filenames = [MOUSE_COORDINATES, PARTICIPANTS, SESSIONS, TASKS, TRIALS]

dfs = { name: pd.read_csv(f"{PREFIX}{name}.csv") for name in filenames }

print(f"Loaded {sum(len(dfs[name]) for name in filenames)} rows across {len(filenames)} tables")
print(f"  {len(dfs[PARTICIPANTS])} participants | {len(dfs[SESSIONS])} sessions | {len(dfs[TASKS])} tasks | {len(dfs[TRIALS])} trials | {len(dfs[MOUSE_COORDINATES])} coordinates")

# -- Filter for valid entries

# Find participant IDs who have done at least 7 session
session_counts = dfs[SESSIONS].groupby("participant_id").size()
valid_pids = set(session_counts[session_counts >= 7].index)
valid_pids -= set(dfs[PARTICIPANTS].loc[dfs[PARTICIPANTS]["group"] == "monitor", "id"])

# Filter out all invalid entries
dfs[SESSIONS] = dfs[SESSIONS][dfs[SESSIONS]["participant_id"].isin(valid_pids)]
valid_sids = set(dfs[SESSIONS]["id"])

dfs[TASKS] = dfs[TASKS][dfs[TASKS]["session_id"].isin(valid_sids)]
valid_tids = set(dfs[TASKS]["id"])

dfs[TRIALS] = dfs[TRIALS][dfs[TRIALS]["task_id"].isin(valid_tids)]
valid_trids = set(dfs[TRIALS]["id"])

dfs[MOUSE_COORDINATES] = dfs[MOUSE_COORDINATES][dfs[MOUSE_COORDINATES]["trial_id"].isin(valid_trids)]


print(f"\nAfter filtering (>= 7 sessions, excluding researchers):")
print(f"  {len(valid_pids)} participants | {len(dfs[SESSIONS])} sessions | {len(dfs[TRIALS])} trials | {len(dfs[MOUSE_COORDINATES])} coordinates")



# -- Number sessions
dfs[SESSIONS] = dfs[SESSIONS].sort_values(["participant_id", "start_time"])
dfs[SESSIONS]["session_number"] = dfs[SESSIONS].groupby("participant_id").cumcount() + 1



# -- Build trial metrics
trials = dfs[TRIALS].copy()

# Merge in task type from tasks
trials = trials.merge(
    dfs[TASKS][["id", "task_type", "session_id"]],
    left_on="task_id", right_on="id",
    suffixes=("", "_task")
)

# Merge in participant_id, screen_px_per_mm and session_number from sessions
trials = trials.merge(
    dfs[SESSIONS][["id", "participant_id", "screen_px_per_mm", "session_number", "slot", "hours_since_last_session"]],
    left_on="session_id", right_on= "id",
    suffixes=("", "_session")
)

# Merge in group from participants
trials = trials.merge(
    dfs[PARTICIPANTS][["id", "group"]],
    left_on="participant_id", right_on="id",
    suffixes=("", "_participant")
)

# Completion time
trials["start_time"] = pd.to_datetime(trials["start_time"], format="ISO8601")
trials["end_time"] = pd.to_datetime(trials["end_time"], format="ISO8601")
trials["completion_time_ms"] = (trials["end_time"] - trials["start_time"]).dt.total_seconds() * 1000


# Accuracy
slider_mask = trials["task_type"] == "slider"

dist_2d = np.sqrt((trials["end_x"] - trials["target_x"]) ** 2 + (trials["end_y"] - trials["target_y"]) ** 2)
dist_1d = (trials["end_x"] - trials["target_x"]).abs()

trials["accuracy_px"] = np.where(slider_mask, dist_1d, dist_2d)
trials["accuracy_mm"] = trials["accuracy_px"] / trials["screen_px_per_mm"]
trials["hit"] = np.where(
    slider_mask,
    dist_1d <= trials["target_size"] / 2,
    dist_2d <= trials["target_size"],
)

# Path Length Ratio
coords = dfs[MOUSE_COORDINATES].sort_values(["trial_id", "timestamp"])
# --- Outlier filtering per trial using IQR. Coordinate level outlier ---
def filter_coordinate_outliers(group):
    for col in ["x", "y"]:
        Q1 = group[col].quantile(0.25)
        Q3 = group[col].quantile(0.75)
        IQR = Q3 - Q1
        group = group[(group[col] >= Q1 - 1.5 * IQR) & (group[col] <= Q3 + 1.5 * IQR)]
    return group

coords_before = len(coords)
coords = coords.groupby("trial_id", group_keys=False).apply(filter_coordinate_outliers)
print(f"\nOutlier filtering: removed {coords_before - len(coords)} coordinate points ({(coords_before - len(coords)) / coords_before * 100:.1f}%)")

coords_by_trial = { tid: grp for tid, grp in coords.groupby("trial_id") }



def compute_plr(row):
    trial_coords = coords_by_trial.get(row["id"])
    if trial_coords is None or len(trial_coords) < 2:
        return np.nan
    
    xs = trial_coords["x"].to_numpy()
    ys = trial_coords["y"].to_numpy()
    x_only = row["task_type"] == "slider"
    
    if x_only:
        path = np.sum(np.abs(np.diff(xs)))
        straight = abs(row["start_x"] - row["end_x"])
    else:
        path = np.sum(np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2))
        straight = np.sqrt((row["start_x"] - row["end_x"]) ** 2 + (row["start_y"] - row["end_y"]) ** 2)
        
    if straight == 0:
        return np.nan
    
    return path / straight

trials["plr"] = trials.apply(compute_plr, axis=1)

# Submovement count
def compute_submovements(row):
    trial_coords = coords_by_trial.get(row["id"])
    if trial_coords is None or len(trial_coords) < 2:
        return np.nan
    
    xs = trial_coords["x"].to_numpy()
    ys = trial_coords["y"].to_numpy()
    ts = trial_coords["timestamp"].to_numpy().astype(float)
    x_only = row["task_type"] == "slider"
    
    # Compute speed at each sample
    dt = np.diff(ts)
    dt[dt == 0] = np.nan
    
    if x_only:
        speed = np.abs(np.diff(xs)) / dt
    else:
        speed = np.sqrt(np.diff(xs) ** 2 + np.diff(ys) ** 2) / dt
        
    # Smooth using Gaussian filter, since 60 fps samples are noisy
    speed = np.nan_to_num(speed, nan=0.0)
    speed = gaussian_filter1d(speed, sigma=1.5)
    
    # Find peaks
    median_dt = np.median(dt[~np.isnan(dt)])    # ms per sample
    min_distance_samples = int(100 / median_dt) # 100ms in samples
    min_speed = 0.05 * np.nanmax(speed)
    peaks, _ = find_peaks(speed, height=min_speed, prominence=min_speed, distance=min_distance_samples)
    
    return len(peaks)

trials["submovement_count"] = trials.apply(compute_submovements, axis=1)

# Fitts Throughput
D = np.where(
    slider_mask,
    np.abs(trials["start_x"] - trials["target_x"]),
    np.sqrt((trials["start_x"] - trials["target_x"]) ** 2 + (trials["start_y"] - trials["target_y"]) ** 2)
)
W = trials["target_size"]
trials["id_bits"] = np.log2(2 * D / W)
trials["throughput"] = trials["id_bits"] / (trials["completion_time_ms"] / 1000)

# filter trials based on completion time
# --- Trial-level outlier filtering  ---
def filter_trial_outliers(group):
    col = "throughput"
    Q1 = group[col].quantile(0.25)
    Q3 = group[col].quantile(0.75)
    IQR = Q3 - Q1
    group = group[
        (group[col] >= Q1 - 1.5 * IQR) &
        (group[col] <= Q3 + 1.5 * IQR)
    ]
    return group

trials_before = len(trials)
print(trials_before)
trials = trials.groupby("task_type", group_keys=False).apply(filter_trial_outliers)
print(f"\nTrial outlier filtering: removed {trials_before - len(trials)} trials ({(trials_before - len(trials)) / trials_before * 100:.1f}%)")


trials.to_csv(f"{PREFIX}/results.csv", index=False)

print(f"\nDone in {time.time() - t_start:.1f}s")
print(f"\n{len(trials)} trials | {trials['participant_id'].nunique()} participants | {trials['session_id'].nunique()} sessions")
print(f"\nHit rate:")
print(trials.groupby("task_type")["hit"].mean().map(lambda x: f"  {x*100:.1f}%"))
print(f"\nMedian completion time:")
print(trials.groupby("task_type")["completion_time_ms"].median().map(lambda x: f"  {x:.0f}ms"))
print(f"\nMean PLR:")
print(trials.groupby("task_type")["plr"].mean().map(lambda x: f"  {x:.3f}"))
print(f"\nMean submovements:")
print(trials.groupby("task_type")["submovement_count"].mean().map(lambda x: f"  {x:.2f}"))
print(f"\nNegative ID trials (target larger than distance): {(trials['id_bits'] < 0).sum()}")
print(f"\nMean throughput (bits/s):")
print(trials.groupby("task_type")["throughput"].mean().map(lambda x: f"  {x:.2f}"))

from scipy.stats import shapiro, normaltest

for task in ["clicking", "slider", "dragging"]:
    data = trials[trials["task_type"] == task]["completion_time_ms"]
    stat, p = shapiro(data)
    print(f"{task}: p={p:.4f} → {'normal ✅' if p > 0.05 else 'not normal ❌'}")