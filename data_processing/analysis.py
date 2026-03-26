import pandas as pd
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

# Helper function of Cohens' f^2
def cohens_f2(fit):
    var_fixed = fit.fittedvalues.var()
    var_random = fit.cov_re.values[0][0] if fit.cov_re is not None else 0
    var_resid = fit.scale
    
    r2 = var_fixed / (var_fixed + var_random + var_resid)
    return r2 / (1 - r2)

# Run the mixed-effects model for each metric per task type
for metric, formula in [
    ("throughput", "throughput ~ group * slot_scaled + hours_scaled"),
    ("plr", "plr ~ group * slot_scaled + hours_scaled"),
    ("submovement_count", "submovement_count ~ group * slot_scaled + hours_scaled"),
    ("hit", "hit ~ group * slot_scaled + hours_scaled")
]:
    for task in ["clicking", "dragging", "slider"]:
        data = trials[trials["task_type"] == task].dropna(subset=[metric, "slot_scaled", "hours_scaled"]).reset_index(drop=True)
        model = smf.mixedlm(formula, data=data, groups=data["participant_id"])
        fit = model.fit(disp=False)
        
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
            "cohens_f2": cohens_f2(fit),
        })
            
results_df = pd.DataFrame(results)
effect_df = pd.DataFrame(effect_sizes)

print("Significance results:")
print(results_df)

print("\nEffect sizes:")
print(effect_df)

results_df.to_csv(f"{PREFIX}model_results.csv", index=False)
effect_df.to_csv(f"{PREFIX}effect_sizes.csv", index=False)