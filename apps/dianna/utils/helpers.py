import pandas as pd
import re


def count_missed_cleavages(peptide: str) -> int:
    """
    Count missed cleavages in a peptide sequence.
    A missed cleavage is an internal R or K NOT followed by P.
    'Internal' means we exclude the last amino acid of the peptide.
    """
    seq = re.sub(r'[^A-Z]', '', peptide.upper())

    missed = 0
    for i, aa in enumerate(seq[:-1]):
        if aa in ('R', 'K'):
            if seq[i + 1] != 'P':
                missed += 1
    return missed


def analyze_missed_cleavages(
    df: pd.DataFrame,
    peptide_col: str = "Stripped.Sequence",
    identifier_col: str = "Identifier",
    max_mc: int = 3,
) -> dict[str, pd.DataFrame]:
    """
    Analyze missed cleavage rates in a DIA-NN parquet report DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DIA-NN report loaded from a parquet file.
    peptide_col : str
        Column containing the peptide sequence (stripped). Default: 'Stripped.Sequence'.
    identifier_col : str
        Column representing sample IDs. Default: 'Identifier'.
    max_mc : int
        Maximum number of missed cleavages to report individually;
        anything above is grouped as f'{max_mc}+'. Default: 3.

    Returns
    -------
    dict with two keys:
        'by_missed_cleavages' : DataFrame — long-format overall counts & percentages per MC category.
        'by_identifier'       : DataFrame — long-format counts & percentages per sample and MC category.

    Both DataFrames have columns:
        mc_category   : str  — missed cleavage label e.g. '0', '1', '2', '3+'
        mc_label      : str  — metric label e.g. 'pct_mc0', 'pct_mc1', 'pct_mc2', 'pct_mc3+'
        peptide_count : int  — number of peptides in that category
        percent       : float — percentage of total peptides

    'by_identifier' additionally has:
        {identifier_col} : str — sample ID
        total_peptides   : int — total peptides for that sample
    """
    for col in (peptide_col, identifier_col):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame. "
                             f"Available columns: {df.columns.tolist()}")

    peptides = (
        df[[identifier_col, peptide_col]]
        .drop_duplicates()
        .copy()
    )

    peptides["missed_cleavages"] = peptides[peptide_col].apply(count_missed_cleavages)

    def mc_category(n: int) -> str:
        return str(n) if n <= max_mc else f"{max_mc}+"

    peptides["mc_category"] = peptides["missed_cleavages"].apply(mc_category)
    categories = [str(i) for i in range(max_mc + 1)] + [f"{max_mc}+"]

    def make_mc_label(cat: str) -> str:
        """Turn category string like '2' or '3+' into 'pct_mc2' or 'pct_mc3+'."""
        return f"pct_mc{cat}"

    # --- (a) Overall: grouped by missed cleavage count only --------------
    mc_counts = (
        peptides["mc_category"]
        .value_counts()
        .reindex(categories, fill_value=0)
        .rename_axis("mc_category")
        .reset_index(name="peptide_count")
    )
    total = mc_counts["peptide_count"].sum()
    mc_counts["percent"] = (mc_counts["peptide_count"] / total * 100).round(2)
    mc_counts["mc_label"] = mc_counts["mc_category"].apply(make_mc_label)
    mc_counts = mc_counts[["mc_category", "mc_label", "peptide_count", "percent"]]

    # --- (b) Per sample: grouped by Identifier × missed cleavage count ---
    id_totals = peptides.groupby(identifier_col).size().rename("total_peptides")

    id_mc_counts = (
        peptides.groupby([identifier_col, "mc_category"])
        .size()
        .reindex(
            pd.MultiIndex.from_product(
                [peptides[identifier_col].unique(), categories],
                names=[identifier_col, "mc_category"]
            ),
            fill_value=0
        )
        .reset_index(name="peptide_count")
    )

    id_mc_counts = id_mc_counts.merge(id_totals, on=identifier_col)
    id_mc_counts["percent"] = (
        id_mc_counts["peptide_count"] / id_mc_counts["total_peptides"] * 100
    ).round(2)
    id_mc_counts["mc_label"] = id_mc_counts["mc_category"].apply(make_mc_label)
    id_mc_counts = id_mc_counts[
        [identifier_col, "total_peptides", "mc_category", "mc_label", "peptide_count", "percent"]
    ]

    # Preserve logical ordering of MC categories in both outputs
    cat_order = pd.CategoricalDtype(categories, ordered=True)
    mc_counts["mc_category"] = mc_counts["mc_category"].astype(cat_order)
    id_mc_counts["mc_category"] = id_mc_counts["mc_category"].astype(cat_order)
    mc_counts = mc_counts.sort_values("mc_category").reset_index(drop=True)
    id_mc_counts = id_mc_counts.sort_values([identifier_col, "mc_category"]).reset_index(drop=True)

    return {
        "by_missed_cleavages": mc_counts,
        "by_identifier": id_mc_counts,
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    report = pd.read_parquet("report.parquet")

    results = analyze_missed_cleavages(report)

    print("=== Missed cleavages (overall) ===")
    print(results["by_missed_cleavages"].to_string(index=False))

    print("\n=== Missed cleavages by sample ===")
    print(results["by_identifier"].to_string(index=False))