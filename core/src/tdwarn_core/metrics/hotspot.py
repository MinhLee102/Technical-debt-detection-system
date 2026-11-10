from __future__ import annotations

from pathlib import Path

import lizard
import pandas as pd


def file_complexity(repo_path: str | Path, rel_paths: list[str]) -> pd.DataFrame:
    repo_path = Path(repo_path)
    rows = []
    for rel in rel_paths:
        full = repo_path / rel
        if not full.is_file():                     
            continue
        info = lizard.analyze_file(str(full))
        ccns = [f.cyclomatic_complexity for f in info.function_list]
        rows.append({
            "canonical_path": rel,
            "nloc": info.nloc,
            "total_ccn": sum(ccns),                
            "max_ccn": max(ccns, default=0),
        })
    return pd.DataFrame(rows)


def churn(changes: pd.DataFrame, window_months: int | None = 12) -> pd.DataFrame:
    end = changes["author_date"].max()             
    df = changes
    if window_months:
        df = df[df["author_date"] > end - pd.DateOffset(months=window_months)]
    g = df.groupby("canonical_path")
    return pd.DataFrame({
        "revisions": g["commit_hash"].nunique(),
        "n_authors": g["author_email"].nunique(),
    }).reset_index()


def hotspots(changes: pd.DataFrame, repo_path, window_months=12) -> pd.DataFrame:
    churn_df = churn(changes, window_months)
    complexity_df = file_complexity(repo_path, churn_df["canonical_path"].tolist())
    df = churn_df.merge(complexity_df, on="canonical_path", how="inner")
    df["hotspot_score"] = df["total_ccn"].rank(pct=True) * df["revisions"].rank(pct=True)  
    df["hotspot_raw"] = df["total_ccn"] * df["revisions"]
    return df.sort_values("hotspot_score", ascending=False)