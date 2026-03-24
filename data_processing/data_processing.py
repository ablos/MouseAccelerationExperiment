import pandas as pd


PREFIX = "data/"
MOUSE_COORDINATES = "mouse_coordinates"
PARTICIPANTS = "participants"
SESSIONS = "sessions"
TASKS = "tasks"
TRIALS = "trials"

filenames = [MOUSE_COORDINATES, PARTICIPANTS, SESSIONS, TASKS, TRIALS]

dfs = {name: pd.read_csv(f"{PREFIX}{name}.csv") for name in filenames}


result = dfs[MOUSE_COORDINATES] \
    .merge(dfs[TRIALS], left_on="trial_id", right_on="id", suffixes=("", "_trial")) \
    .merge(dfs[TASKS], left_on="task_id", right_on="id", suffixes=("", "_task")) \
    .merge(dfs[SESSIONS], left_on="session_id", right_on="id", suffixes=("", "_session")) \
    .merge(dfs[PARTICIPANTS], left_on="participant_id", right_on="id", suffixes=("", "_participant"))


print(result[result['group'] == 'experimental']['x'].mean())