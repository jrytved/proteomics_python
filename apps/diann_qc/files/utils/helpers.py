import pandas as pd
import re


def count_missed_cleavages(peptide: str) -> int:
    """
    Count missed cleavages in a peptide sequence.
    A missed cleavage is an internal R or K NOT followed by P.
    'Internal' means we exclude the last amino acid of the peptide.
    """
    # Strip any modification brackets or common prefixes (e.g. leading underscore in DIA-NN)
    # DIA-NN stripped sequences look like: PEPTIDER or _PEPTIDER_
    seq = re.sub(r'[^A-Z]', '', peptide.upper())

    missed = 0
    # Check every R/K except the very last residue (C-terminal cleavage site)
    for i, aa in enumerate(seq[:-1]):
        if aa in ('R', 'K'):
            next_aa = seq[i + 1]
            if next_aa != 'P':
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
        'by_missed_cleavages' : DataFrame — overall counts & percentages per MC category.
        'by_identifier'       : DataFrame — counts & percentages per sample and MC category.
    """
    # --- Validate columns ------------------------------------------------
    for col in (peptide_col, identifier_col):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame. "
                             f"Available columns: {df.columns.tolist()}")

    # --- Deduplicate peptides per sample (precursor-level → peptide-level) -
    # DIA-NN reports can have multiple rows per peptide (different charge states,
    # modifications, etc.). Deduplicate on (Identifier, stripped sequence).
    peptides = (
        df[[identifier_col, peptide_col]]
        .drop_duplicates()
        .copy()
    )

    # --- Count missed cleavages ------------------------------------------
    peptides["missed_cleavages"] = peptides[peptide_col].apply(count_missed_cleavages)

    # Bin into categories: 0, 1, 2, …, max_mc, f'{max_mc}+'
    def mc_category(n: int) -> str:
        return str(n) if n <= max_mc else f"{max_mc}+"

    peptides["mc_category"] = peptides["missed_cleavages"].apply(mc_category)

    # Define ordered categories for nice sorting
    categories = [str(i) for i in range(max_mc + 1)] + [f"{max_mc}+"]

    # --- (a) Grouped by number of missed cleavages -----------------------
    mc_counts = (
        peptides["mc_category"]
        .value_counts()
        .reindex(categories, fill_value=0)
        .rename_axis("missed_cleavages")
        .reset_index(name="peptide_count")
    )
    total = mc_counts["peptide_count"].sum()
    mc_counts["percent"] = (mc_counts["peptide_count"] / total * 100).round(2)

    # --- (b) Grouped by Identifier × missed cleavages --------------------
    id_mc_counts = (
        peptides.groupby([identifier_col, "mc_category"])
        .size()
        .unstack(fill_value=0)
        # Ensure all MC categories exist as columns
        .reindex(columns=categories, fill_value=0)
    )
    id_mc_counts.columns.name = "missed_cleavages"

    # Add total and percentage columns per sample
    id_mc_counts["total_peptides"] = id_mc_counts.sum(axis=1)
    for cat in categories:
        id_mc_counts[f"pct_{cat}mc"] = (
            id_mc_counts[cat] / id_mc_counts["total_peptides"] * 100
        ).round(2)

    id_mc_counts = id_mc_counts.reset_index()

    return {
        "by_missed_cleavages": mc_counts,
        "by_identifier": id_mc_counts,
    }

