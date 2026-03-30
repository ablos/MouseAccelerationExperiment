import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu
import statsmodels.formula.api as smf

PREFIX = "data/"

trials = pd.read_csv(f"{PREFIX}results.csv")

# Standardize predictors to mean=0, std=1 so the optimizer works in a comparable scale space
# It improves convergence and makes coefficients comparable across predictors
trials["slot_scaled"] = (trials["slot"] - trials["slot"].mean()) / trials["slot"].std()
trials["hours_scaled"] = (trials["hours_since_last_session"] - trials["hours_since_last_session"].mean()) / trials["hours_since_last_session"].std()
trials["hit"] = trials["hit"].astype(int)

results = []
effect_sizes = []

# Helper function for R² of a mixed effects model
def r2(fit):
    var_fixed = fit.fittedvalues.var()
    var_random = fit.cov_re.values[0][0] if fit.cov_re is not None else 0
    var_resid = fit.scale
    return var_fixed / (var_fixed + var_random + var_resid)

# Incremental Cohen's f² for the interaction term:
# how much variance does group×slot explain above the reduced model?
def incremental_cohens_f2(r2_full, r2_reduced):
    delta = max(r2_full - r2_reduced, 0)  # clamp: negative means ~0 effect (convergence noise)
    return delta / (1 - r2_full)

# Run the mixed-effects model for each metric per task type
for metric, formula in [
    ("throughput", "throughput ~ group * slot_scaled + hours_scaled"),
    ("plr", "plr ~ group * slot_scaled + hours_scaled"),
    ("submovement_count", "submovement_count ~ group * slot_scaled + hours_scaled"),
    ("hit", "hit ~ group * slot_scaled + hours_scaled")
]:
    for task in ["clicking", "dragging", "slider"]:
        data = trials[trials["task_type"] == task].dropna(subset=[metric, "slot_scaled", "hours_scaled"]).reset_index(drop=True)

        full_model = smf.mixedlm(formula, data=data, groups=data["participant_id"])
        fit = full_model.fit(disp=False)

        reduced_formula = formula.replace(f"{metric} ~ group * slot_scaled", f"{metric} ~ group + slot_scaled")
        reduced_model = smf.mixedlm(reduced_formula, data=data, groups=data["participant_id"])
        fit_reduced = reduced_model.fit(disp=False)

        for term in fit.params.index:
            results.append({
                "metric": metric,
                "task": task,
                "term": term,
                "coef": fit.params[term],
                "se": fit.bse[term],
                "z": fit.tvalues[term],
                "p": fit.pvalues[term],
                "ci_low": fit.conf_int().loc[term, 0],
                "ci_high": fit.conf_int().loc[term, 1],
            })

        effect_sizes.append({
            "metric": metric,
            "task": task,
            "cohens_f2": incremental_cohens_f2(r2(fit), r2(fit_reduced)),
        })
            
results_df = pd.DataFrame(results)
effect_df = pd.DataFrame(effect_sizes)

print("Significance results:")
print(results_df)

print("\nEffect sizes:")
print(effect_df)

results_df.to_csv(f"{PREFIX}model_results.csv", index=False)
effect_df.to_csv(f"{PREFIX}effect_sizes.csv", index=False)

# =============================================
# MANN-WHITNEY U ON IMPROVEMENT PERCENTAGES
# =============================================

# Compute per-participant improvement % (last 2 sessions vs slot 1)
agg = trials.groupby(["participant_id", "slot", "task_type", "group"]).agg(
    throughput=("throughput", "mean"),
    plr=("plr", "mean"),
    submovement_count=("submovement_count", "mean"),
    hit_rate=("hit", "mean"),
).reset_index()

max_slot = agg.groupby(["participant_id", "task_type"])["slot"].max().reset_index()
max_slot["slot_cutoff"] = max_slot["slot"] - 1
last_two = agg.merge(max_slot[["participant_id", "task_type", "slot_cutoff"]], on=["participant_id", "task_type"])
last_two = last_two[last_two["slot"] >= last_two["slot_cutoff"]]
final_perf = last_two.groupby(["participant_id", "task_type", "group"])[["throughput", "plr", "submovement_count", "hit_rate"]].mean().reset_index()
baseline_perf = agg[agg["slot"] == 1][["participant_id", "task_type", "throughput", "plr", "submovement_count", "hit_rate"]].rename(
    columns={"throughput": "throughput_base", "plr": "plr_base", "submovement_count": "submovement_base", "hit_rate": "hit_rate_base"}
)
merged = final_perf.merge(baseline_perf, on=["participant_id", "task_type"])
merged["throughput_pct"]  = (merged["throughput"]       - merged["throughput_base"])  / merged["throughput_base"]  * 100
merged["plr_pct"]         = (merged["plr_base"]         - merged["plr"])              / merged["plr_base"]         * 100
merged["submovement_pct"] = (merged["submovement_base"] - merged["submovement_count"]) / merged["submovement_base"] * 100
merged["hit_rate_pct"]    = (merged["hit_rate"]         - merged["hit_rate_base"])    / merged["hit_rate_base"]    * 100

def cohens_d(a, b):
    n1, n2 = len(a), len(b)
    pooled_std = np.sqrt(((n1 - 1) * a.std(ddof=1)**2 + (n2 - 1) * b.std(ddof=1)**2) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / pooled_std if pooled_std > 0 else 0

improvement_tests = []
groups = merged.groupby(["task_type", "group"])
for metric, col in [("throughput", "throughput_pct"), ("plr", "plr_pct"), ("submovement_count", "submovement_pct"), ("hit", "hit_rate_pct")]:
    for task in ["clicking", "dragging", "slider"]:
        exp  = groups.get_group((task, "experimental"))[col].dropna()
        ctrl = groups.get_group((task, "control"))[col].dropna()
        stat, p = mannwhitneyu(exp, ctrl, alternative="two-sided")
        improvement_tests.append({
            "metric": metric,
            "task": task,
            "p": p,
            "cohens_d": cohens_d(exp, ctrl),
        })

improvement_tests_df = pd.DataFrame(improvement_tests)
print("\nMann-Whitney U on improvement percentages (Bonferroni α ≈ .004):")
print(improvement_tests_df.to_string(index=False))
improvement_tests_df.to_csv(f"{PREFIX}improvement_tests.csv", index=False)