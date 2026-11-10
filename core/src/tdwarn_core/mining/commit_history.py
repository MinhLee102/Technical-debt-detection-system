from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from pydriller import Repository

def mine_commit_history(
        repo_path: str | Path, 
        extensions: tuple[str, ...] = (".java",), 
        until: datetime | None = None,
) -> pd.DataFrame:
    
    repo = Repository(
        str(repo_path),
        only_no_merge=True,                              
        to=until,                                        
        only_modifications_with_file_types=list(extensions),
    )
    rows = []
    for commit in repo.traverse_commits():               
        num_files = len(commit.modified_files)             
        for mf in commit.modified_files:
            old_path, new_path = _posix(mf.old_path), _posix(mf.new_path)
            path = new_path or old_path            
            if not path or not path.endswith(extensions):
                continue
            rows.append({
                "commit_hash": commit.hash,
                "author_email": (commit.author.email or "").lower(),
                "author_date": commit.author_date,
                "change_type": mf.change_type.name,      
                "old_path": mf.old_path,
                "new_path": mf.new_path,
                "path": path,
                "added_lines": mf.added_lines,
                "deleted_lines": mf.deleted_lines,
                "num_files_in_commit": num_files,
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["author_date"] = pd.to_datetime(df["author_date"], utc=True)   # (5)
    return df


def resolve_renames(df: pd.DataFrame) -> pd.DataFrame:
    renames = df[df["change_type"] == "RENAME"]
    mapping = dict(zip(renames["old_path"], renames["new_path"]))

    def final_name(p: str) -> str:
        seen = set()
        while p in mapping and p not in seen:            
            seen.add(p)
            p = mapping[p]
        return p

    out = df.copy()
    out["canonical_path"] = out["path"].map(final_name)
    return out

def _posix(p: str | None) -> str | None:
    return p.replace("\\", "/") if p else p