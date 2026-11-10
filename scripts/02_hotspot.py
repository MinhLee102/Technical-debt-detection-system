import sys

import pandas as pd

from tdwarn_core.metrics.hotspot import hotspots

repo, window = sys.argv[1], int(sys.argv[2])
changes = pd.read_csv("data/processed/changes.csv", parse_dates=["author_date"])
df = hotspots(changes, repo, window_months=window or None)
df.to_csv(f"data/processed/hotspots_w{window}.csv", index=False)
print(df.head(10)[["canonical_path", "revisions", "total_ccn", "hotspot_score"]].to_string(index=False))