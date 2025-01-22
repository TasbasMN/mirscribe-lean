import logging
import os
import numpy as np
from scripts.utils import * 
def validate_ref_nucleotides(df, report_path):
    logger = logging.getLogger('pipeline.validation')
    
    # Add ref_len and alt_len columns
    df["ref_len"] = df["ref"].str.len()
    df["alt_len"] = df["alt"].str.len()

    logger.debug(f"Processing {len(df)} variants")
    
    # Fetch reference nucleotides
    df['nuc_at_pos'] = np.where(
        df['ref_len'] > 1,
        df.apply(lambda x: get_nucleotides_in_interval(
            x['chr'], x['pos'], x["pos"] + x["ref_len"] - 1), axis=1),
        np.where(
            df['ref_len'] == 1,
            df.apply(lambda x: get_nucleotide_at_position(
                x['chr'], x['pos']), axis=1),
            ""
        )
    )

    # Check if ref matches nucleotide_at_position
    mask = df['ref'] != df['nuc_at_pos']
    invalid_rows = df[mask]
    
    n_invalid = len(invalid_rows)
    n_total = len(df)
    logger.debug(f"Found {n_invalid}/{n_total} mismatching reference alleles")

    if not invalid_rows.empty:
        file_exists = os.path.isfile(report_path)
        mode = 'a' if file_exists else 'w'
        
        logger.debug(f"Writing invalid variants to {report_path}")
        with open(report_path, mode) as f:
            if not file_exists:
                f.write("id\n")
            for _, row in invalid_rows.iterrows():
                f.write(f"{row['id']}\n")

    valid_df = df[~mask].drop("nuc_at_pos", axis=1)
    valid_df.drop(["ref_len", "alt_len"], axis=1, inplace=True)
    
    logger.info(f"validated={len(valid_df)} invalid={n_invalid}")
    return valid_df

