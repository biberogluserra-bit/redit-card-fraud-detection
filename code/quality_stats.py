"""Exploratory AP ranks across five overlapping splits. No test predictions used."""
from pathlib import Path
from itertools import combinations
import json
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, studentized_range

root = Path(__file__).resolve().parents[1]
out = root / "results"
scores = pd.read_csv(out / "cv_repeated_results.csv").pivot(index="seed", columns="model", values="ap")
assert scores.shape == (5, 6) and scores.notna().all().all()
n, k = scores.shape
ranks = scores.rank(axis=1, ascending=False, method="average").mean()
stat = friedmanchisquare(*scores.T.to_numpy())
se = np.sqrt(k * (k + 1) / (6 * n))
cd = studentized_range.ppf(.95, k, np.inf) * se / np.sqrt(2)
pairs = []
for a, b in combinations(scores, 2):
    x, y = scores[a].to_numpy(), scores[b].to_numpy()
    delta = np.sign(x[:, None] - y[None, :]).mean()
    q = np.sqrt(2) * abs(ranks[a] - ranks[b]) / se
    pairs.append(dict(a=a, b=b, rank_a=ranks[a], rank_b=ranks[b],
                      nemenyi_p=studentized_range.sf(q, k, np.inf),
                      cliffs_delta_a_vs_b=delta, mean_paired_delta_ap=(x-y).mean()))
pd.DataFrame(pairs).to_csv(out / "quality_pairwise.csv",index=False)
(out / "quality_omnibus.json").write_text(json.dumps(dict(metric="AP", blocks=n,
    methods=k, friedman_chi2=stat.statistic, df=k-1, asymptotic_p=stat.pvalue,
    critical_distance_05=cd, average_rank=ranks.to_dict(),
    scope="Exploratory: overlapping splits of one dataset; tied ranks averaged. Cliff compares marginal scores."),indent=2))
print(stat, cd, pd.DataFrame(pairs).query('nemenyi_p < .05').to_string(index=False))
