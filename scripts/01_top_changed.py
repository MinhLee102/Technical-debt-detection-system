import sys

from tdwarn_core.mining.commit_history import resolve_renames, mine_commit_history

repo = sys.argv[1]
df = resolve_renames(mine_commit_history(repo))
df.to_csv("data/processed/changes.csv", index=False)     

print(f"{df['commit_hash'].nunique()} commit, {len(df)} dòng")
top = df.groupby("canonical_path")["commit_hash"].nunique().nlargest(10)
print(top.to_string())