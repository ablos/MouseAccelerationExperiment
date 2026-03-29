"""
Demo animation of clicking, slider, and dragging trials.
Visual style matches the experiment web app exactly.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Polygon
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter

PREFIX = "data/"
N_TRIALS        = 9  # N_EARLY + N_LATE
FRAMES_PER_TRIAL = 55
PAUSE_FRAMES     = 15

# ── colours (directly from the Svelte source) ─────────────────────────────────
BG       = "#F1F1F1"
CARD_BG  = "#ffffff"
BORDER   = "#c4c4c4"
TEXT     = "#111111"
BLUE     = "#0000ff"
RED      = "#ff0000"
TRACK    = "#a3a3a3"
HANDLE   = "#f0f0f0"
HANDLE_RING = "#0d0d10"
HANDLE_DRAG = "#e8ff5a"
FOLDER   = "#808080"    # gray
GREEN    = "#22c55e"
TRAIL    = "#555555"
# ─────────────────────────────────────────────────────────────────────────────

coords   = pd.read_csv(f"{PREFIX}mouse_coordinates.csv")
trials   = pd.read_csv(f"{PREFIX}trials.csv")
tasks    = pd.read_csv(f"{PREFIX}tasks.csv")
sessions = pd.read_csv(f"{PREFIX}sessions.csv")

trials = trials.merge(tasks[["id", "task_type", "session_id"]], left_on="task_id", right_on="id", suffixes=("", "_task"))
trials = trials.merge(sessions[["id", "slot", "participant_id"]], left_on="session_id", right_on="id", suffixes=("", "_session"))
trials["n_coords"] = trials["id"].map(coords.groupby("trial_id").size())
trials = trials.dropna(subset=["n_coords"])

# Participants with clear improvement in clicking throughput (good for visual story)
GOOD_PARTICIPANTS = [1, 23, 13, 22, 18, 10]

def pick_trials(task_type, n, slots, participants=None):
    """Pick n clean trials from given slots, optionally filtered by participants."""
    subset = trials[
        (trials["task_type"] == task_type) &
        (trials["slot"].isin(slots))
    ].copy()
    if participants:
        subset = subset[subset["participant_id"].isin(participants)]
    med = subset["n_coords"].median()
    subset["coord_dist"] = (subset["n_coords"] - med).abs()
    return subset.nsmallest(n * 4, "coord_dist").head(n)["id"].tolist()

# Alternate: baseline trial, late trial, baseline, late, baseline
EARLY_SLOTS = [1]
LATE_SLOTS  = [9, 10]
N_EARLY = 5
N_LATE  = 4

early_clicking = pick_trials("clicking", N_EARLY, EARLY_SLOTS, GOOD_PARTICIPANTS)
late_clicking  = pick_trials("clicking", N_LATE,  LATE_SLOTS,  GOOD_PARTICIPANTS)
early_slider   = pick_trials("slider",   N_EARLY, EARLY_SLOTS, GOOD_PARTICIPANTS)
late_slider    = pick_trials("slider",   N_LATE,  LATE_SLOTS,  GOOD_PARTICIPANTS)
early_dragging = pick_trials("dragging", N_EARLY, EARLY_SLOTS, GOOD_PARTICIPANTS)
late_dragging  = pick_trials("dragging", N_LATE,  LATE_SLOTS,  GOOD_PARTICIPANTS)

# Interleave: early, late, early, late, early
def interleave(early, late):
    result = []
    ei, li = iter(early), iter(late)
    for i in range(N_EARLY + N_LATE):
        result.append(next(ei) if i % 2 == 0 else next(li))
    return result

clicking_ids = interleave(early_clicking, late_clicking)
slider_ids   = interleave(early_slider,   late_slider)
dragging_ids = interleave(early_dragging, late_dragging)

def get_trial_data(trial_id):
    row  = trials[trials["id"] == trial_id].iloc[0]
    path = coords[coords["trial_id"] == trial_id].sort_values("timestamp")
    return row, path

def normalize(path, row):
    xs = path["x"].values.astype(float)
    ys = path["y"].values.astype(float)
    tr = row["target_size"]  # physical radius/size in pixels
    # include target extent in bounding box so it is never clipped
    pts_x = list(xs) + [row["start_x"], row["target_x"] - tr, row["target_x"] + tr]
    pts_y = list(ys) + [row["start_y"], row["target_y"] - tr, row["target_y"] + tr]
    xmin, xmax = min(pts_x), max(pts_x)
    ymin, ymax = min(pts_y), max(pts_y)
    span = max(xmax - xmin, ymax - ymin, 1)
    pad  = span * 0.2
    def nx(v): return (v - xmin + pad) / (span + 2 * pad)
    def ny(v): return 1 - (v - ymin + pad) / (span + 2 * pad)
    return (
        nx(xs), ny(ys),
        nx(row["start_x"]), ny(row["start_y"]),
        nx(row["target_x"]), ny(row["target_y"]),
        tr / (span + 2 * pad),  # properly normalized target size
    )

TASK_LABEL = {"clicking": "Clicking", "slider": "Slider", "dragging": "Dragging"}
task_order = [("clicking", clicking_ids), ("slider", slider_ids), ("dragging", dragging_ids)]

def make_figure(vertical=False):
    if vertical:
        fig = plt.figure(figsize=(5, 13), facecolor=BG)
        fig.text(0.5, 0.98, "Task Reconstructions from Recorded Data",
                 ha="center", va="top", color=TEXT, fontsize=13, fontweight="bold",
                 fontfamily="sans-serif")
        axes = []
        for i, (task_type, _) in enumerate(task_order):
            ax = fig.add_axes([0.08, 0.03 + (2 - i) * 0.315, 0.84, 0.27])
            ax.set_facecolor(CARD_BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal")
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color(BORDER)
                spine.set_linewidth(1)
            ax.set_title(TASK_LABEL[task_type], color=TEXT, fontsize=12,
                         fontweight="bold", pad=8, loc="center", fontfamily="sans-serif")
            axes.append(ax)
    else:
        fig = plt.figure(figsize=(13, 4.8), facecolor=BG)
        fig.text(0.5, 0.97, "Task Reconstructions from Recorded Data",
                 ha="center", va="top", color=TEXT, fontsize=15, fontweight="bold",
                 fontfamily="sans-serif")
        axes = []
        for i, (task_type, _) in enumerate(task_order):
            ax = fig.add_axes([0.03 + i * 0.325, 0.06, 0.30, 0.80])
            ax.set_facecolor(CARD_BG)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal")
            ax.axis("off")
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_color(BORDER)
                spine.set_linewidth(1)
            ax.set_title(TASK_LABEL[task_type], color=TEXT, fontsize=12,
                         fontweight="bold", pad=8, loc="center", fontfamily="sans-serif")
            axes.append(ax)
    return fig, axes

# ── precompute ────────────────────────────────────────────────────────────────
all_data = {}
for task_type, trial_ids in task_order:
    all_data[task_type] = []
    for tid in trial_ids:
        row, path = get_trial_data(tid)
        slot = int(trials[trials["id"] == tid]["slot"].iloc[0])
        label = "Session 1 (baseline)" if slot == 1 else f"Session {slot} (late)"
        all_data[task_type].append((row, path, normalize(path, row), label))


def draw_file_icon(ax, cx, cy, size, color=BLUE, alpha=1.0):
    """Draw a simple file icon (rectangle with folded top-right corner)."""
    w, h = size * 0.6, size * 0.75
    fold = w * 0.3
    # main body (clipped at top-right)
    body = Polygon([
        [cx - w/2, cy - h/2],
        [cx - w/2, cy + h/2],
        [cx + w/2 - fold, cy + h/2],
        [cx + w/2, cy + h/2 - fold],
        [cx + w/2, cy - h/2],
    ], closed=True, facecolor=color, edgecolor=color, alpha=alpha, zorder=4)
    ax.add_patch(body)
    # fold triangle
    fold_tri = Polygon([
        [cx + w/2 - fold, cy + h/2],
        [cx + w/2 - fold, cy + h/2 - fold],
        [cx + w/2,        cy + h/2 - fold],
    ], closed=True, facecolor="white", edgecolor=color, alpha=alpha, zorder=4)
    ax.add_patch(fold_tri)


def draw_folder_icon(ax, cx, cy, size, color=FOLDER, glow=False):
    """Draw a simple folder icon (body + tab on top)."""
    w, h = size * 1.1, size * 0.75
    tab_w, tab_h = w * 0.4, h * 0.2
    edge_col = GREEN if glow else color
    alpha = 1.0
    # tab
    tab = FancyBboxPatch((cx - w/2, cy + h/2 - tab_h), tab_w, tab_h,
                          boxstyle="round,pad=0.005",
                          facecolor=edge_col, edgecolor=edge_col, alpha=alpha, zorder=3)
    ax.add_patch(tab)
    # body
    body = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                           boxstyle="round,pad=0.01",
                           facecolor=edge_col, edgecolor=edge_col, alpha=alpha, zorder=3)
    ax.add_patch(body)
    if glow:
        # green outer glow ring
        glow_patch = FancyBboxPatch((cx - w/2 - 0.015, cy - h/2 - 0.015),
                                     w + 0.03, h + 0.03,
                                     boxstyle="round,pad=0.015",
                                     facecolor="none", edgecolor=GREEN,
                                     linewidth=3, alpha=0.6, zorder=2)
        ax.add_patch(glow_patch)


def clear_patches(ax):
    for p in list(ax.patches):
        p.remove()
    for c in list(ax.collections):
        c.remove()
    for l in list(ax.lines):
        if l not in (trail_lines.get(None), cursor_dots.get(None)):
            pass  # keep trail_lines and cursor_dots — they're managed separately


def draw_scene(ax, task_type, xs, ys, sx, sy, tx, ty, radius, progress):
    # Remove only patches (not the persistent line/dot artists)
    for p in list(ax.patches):
        p.remove()
    for l in list(ax.lines):
        if l is not trail_lines[task_type] and l is not cursor_dots[task_type]:
            l.remove()
    for c in list(ax.collections):
        c.remove()

    r = radius
    idx = max(0, int(progress * len(xs)) - 1)
    cx = xs[idx] if len(xs) > 0 else sx
    cy = ys[idx] if len(ys) > 0 else sy

    if task_type == "clicking":
        # Outer blue filled circle
        ax.add_patch(plt.Circle((tx, ty), r, color=BLUE, zorder=1))
        # Inner red filled circle (20% of diameter = 10% of radius... actually 20% of outer diameter)
        inner_r = r * 0.2
        ax.add_patch(plt.Circle((tx, ty), inner_r, color=RED, zorder=2))

    elif task_type == "slider":
        # Track y is the start y (handle starts on the track)
        track_y = sy
        handle_r = 0.032  # handle radius in normalized coords
        # Track: full width gray line
        ax.plot([0.05, 0.95], [track_y, track_y], color=TRACK, lw=4,
                solid_capstyle="round", zorder=1)
        # Zone: blue left + right border lines, with inner blue bar and red accuracy line
        zone_half = r
        zone_l = tx - zone_half
        zone_r = tx + zone_half
        bar_h  = 0.025
        acc_w  = handle_r * 2  # red line = same width as handle diameter
        # Blue horizontal bar (zone-target-line, 70% opacity)
        ax.add_patch(patches.Rectangle((zone_l, track_y - bar_h / 2),
                                        zone_half * 2, bar_h,
                                        color=BLUE, alpha=0.7, zorder=2, linewidth=0))
        # Red center accuracy line (same width as handle)
        ax.add_patch(patches.Rectangle((tx - acc_w / 2, track_y - bar_h / 2),
                                        acc_w, bar_h,
                                        color=RED, zorder=3, linewidth=0))
        # Left blue border
        ax.plot([zone_l, zone_l], [track_y - 0.06, track_y + 0.06],
                color=BLUE, lw=3, zorder=2)
        # Right blue border
        ax.plot([zone_r, zone_r], [track_y - 0.06, track_y + 0.06],
                color=BLUE, lw=3, zorder=2)
        # Handle follows cursor x but stays locked to track_y
        is_dragging = 0.05 < progress < 0.95
        handle_col = HANDLE_DRAG if is_dragging else HANDLE
        ax.add_patch(plt.Circle((cx, track_y), handle_r + 0.006, color=HANDLE_RING, zorder=4))
        ax.add_patch(plt.Circle((cx, track_y), handle_r, color=handle_col, zorder=5))

    elif task_type == "dragging":
        is_over = progress > 0.85
        # Folder at target position
        draw_folder_icon(ax, tx, ty, r, glow=is_over)
        # File icon follows cursor
        file_alpha = 0.5 if is_over else 1.0
        draw_file_icon(ax, cx, cy, r, color=BLUE, alpha=file_alpha)


TOTAL_FRAMES = N_TRIALS * (FRAMES_PER_TRIAL + PAUSE_FRAMES)


def animate(frame):
    trial_idx   = frame // (FRAMES_PER_TRIAL + PAUSE_FRAMES)
    local_frame = frame  % (FRAMES_PER_TRIAL + PAUSE_FRAMES)
    is_pause    = local_frame >= FRAMES_PER_TRIAL
    progress    = 1.0 if is_pause else local_frame / FRAMES_PER_TRIAL

    for ax, (task_type, _) in zip(axes, task_order):
        row, path, (xs, ys, sx, sy, tx, ty, radius), slot_label = all_data[task_type][trial_idx]
        n   = len(xs)
        idx = max(1, int(progress * n))

        draw_scene(ax, task_type, xs, ys, sx, sy, tx, ty, radius, progress)

        if task_type == "slider":
            trail_lines[task_type].set_data(xs[:idx], np.full(idx, sy))
        else:
            trail_lines[task_type].set_data(xs[:idx], ys[:idx])

        # Slider: dot locked to track y; dragging: file icon used instead; clicking: normal dot
        if task_type == "slider":
            cursor_dots[task_type].set_data([], [])  # handle is drawn as patch
        elif task_type == "dragging":
            cursor_dots[task_type].set_data([], [])
        else:
            cursor_dots[task_type].set_data([xs[idx - 1]], [ys[idx - 1]])

    return list(trail_lines.values()) + list(cursor_dots.values())


def build_and_save(vertical):
    global fig, axes, trail_lines, cursor_dots, session_labels

    fig, axes = make_figure(vertical=vertical)

    trail_lines    = {}
    cursor_dots    = {}
    session_labels = {}
    for ax, (task_type, _) in zip(axes, task_order):
        line, = ax.plot([], [], color=TRAIL, lw=1.5, alpha=0.5, zorder=2)
        dot,  = ax.plot([], [], "o", color=TEXT, ms=4, zorder=5)
        lbl   = ax.text(0.5, 0.04, "", ha="center", va="bottom", fontsize=8,
                        color="#666666", transform=ax.transAxes, visible=False)
        trail_lines[task_type]    = line
        cursor_dots[task_type]    = dot
        session_labels[task_type] = lbl

    anim = FuncAnimation(fig, animate, frames=TOTAL_FRAMES, interval=40, blit=False)

    suffix = "_vertical" if vertical else ""
    print(f"Saving GIF{suffix}...")
    anim.save(f"{PREFIX}plots/demo_animation{suffix}.gif", writer=PillowWriter(fps=25))
    print(f"Saved demo_animation{suffix}.gif")
    try:
        anim.save(f"{PREFIX}plots/demo_animation{suffix}.mp4", writer=FFMpegWriter(fps=25))
        print(f"Saved demo_animation{suffix}.mp4")
    except Exception as e:
        print(f"MP4 skipped: {e}")
    plt.close(fig)

build_and_save(vertical=False)
build_and_save(vertical=True)
