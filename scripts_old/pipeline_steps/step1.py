import logging
import numpy as np
import os
from scripts.utils.sequence_utils import *
from scripts.globals import *
import pandas as pd



def validate_ref_nucleotides(df, report_path):

    # Add ref_len and alt_len columns
    df["ref_len"] = df["ref"].str.len()
    df["alt_len"] = df["alt"].str.len()

    # For rows where the reference length (ref_len) is greater than 1:
    # - Use the get_nucleotides_in_interval function to fetch the nucleotides
    #   in the interval [pos, pos + ref_len - 1] for the given chromosome (chr)
    df['nuc_at_pos'] = np.where(
        df['ref_len'] > 1,
        df.apply(lambda x: get_nucleotides_in_interval(
            x['chr'], x['pos'], x["pos"] + x["ref_len"] - 1), axis=1),
        # For rows where the reference length (ref_len) is 1:
        # - Use the get_nucleotide_at_position function to fetch the nucleotide
        #   at the given position (pos) for the given chromosome (chr)
        np.where(
            df['ref_len'] == 1,
            df.apply(lambda x: get_nucleotide_at_position(
                x['chr'], x['pos']), axis=1),
            # For all other cases, set the value to an empty string
            ""
        )
    )

    # Check if ref matches nucleotide_at_position
    mask = df['ref'] != df['nuc_at_pos']

    # Isolate invalid rows
    invalid_rows = df[mask]

    if not invalid_rows.empty:
        # Check if the file exists
        file_exists = os.path.isfile(report_path)

        # Open the file in append mode ('a') or write mode ('w')
        mode = 'a' if file_exists else 'w'
        with open(report_path, mode) as f:
            # If the file is new, write the header
            if not file_exists:
                f.write("id\n")

            # Write each invalid row to the file
            for _, row in invalid_rows.iterrows():
                f.write(f"{row['id']}\n")

    return df[~mask].drop("nuc_at_pos", axis=1)

def generate_is_mirna_column(df, grch):
    """
    Adds two columns to the input DataFrame:
    'is_mirna': 1 if the mutation falls within a miRNA region, 0 otherwise
    'mirna_accession': the accession number of the miRNA if 'is_mirna' is 1, None otherwise

    Args:
        df (pandas.DataFrame): The input DataFrame containing mutation data
        grch (int): The genome reference coordinate system version (e.g., 37, 38)

    Returns:
        pandas.DataFrame: The input DataFrame with two additional columns ('is_mirna' and 'mirna_accession')
    """
    # Construct the miRNA coordinates file path
    mirna_coords_file = os.path.join(
        MIRNA_COORDS_DIR, f"grch{grch}_coordinates.csv")

    # Load miRNA coordinates
    coords = pd.read_csv(mirna_coords_file)

    # Initialize new columns
    df['is_mirna'] = 0
    df['mirna_accession'] = None
    df["pos"] = df["pos"].astype(int)
    

    # Iterate over each mutation in the mutations dataframe
    for index, row in df.iterrows():
        mutation_chr = row['chr']
        mutation_start = row['pos']

        # Find matching miRNAs
        matching_rnas = coords.loc[(coords['chr'] == mutation_chr) &
                                   (coords['start'] <= mutation_start) &
                                   (coords['end'] >= mutation_start)]

        if not matching_rnas.empty:
            # Update the 'is_mirna' and 'mirna_accession' columns
            df.at[index, 'is_mirna'] = 1
            df.at[index, 'mirna_accession'] = matching_rnas['mirna_accession'].values[0]

    return df


def add_sequence_columns(df):  # sourcery skip: avoid-builtin-shadow
    """Add sequence context columns to DataFrame"""
    logging.info("Starting sequence column addition for %d variants", len(df))
    
    grouped = df.groupby(['chr', 'pos'])
    logging.debug("Grouped into %d chromosome/position groups", len(grouped))

    def apply_func(group):
        try:
            chr = group['chr'].iloc[0]
            pos = group['pos'].iloc[0]
            ref = group['ref'].iloc[0]
            
            logging.debug("Processing group: %s:%s (ref: %s)", chr, pos, ref)
            
            # Original sequence processing
            group['upstream_seq'] = get_upstream_sequence(chr, pos, NUCLEOTIDE_OFFSET)
            group['downstream_seq'] = get_downstream_sequence(chr, pos, ref, NUCLEOTIDE_OFFSET)
            group['wt_seq'] = group['upstream_seq'] + group['ref'] + group['downstream_seq']
            group['mut_seq'] = group['upstream_seq'] + group['alt'] + group['downstream_seq']
            
            logging.debug("Processed group: %s:%s (seq length: %d)", 
                        chr, pos, len(group['wt_seq'].iloc[0]))
            
            return group
            
        except Exception as e:
            logging.error("Failed processing group %s:%s: %s", chr, pos, str(e))
            raise

    logging.info("Starting sequence generation for %d groups", len(grouped))
    df = grouped.apply(apply_func)
    logging.info("Completed sequence generation")
    
    df = df.reset_index(drop=True)
    logging.info("Final DataFrame contains %d rows", len(df))
    
    return df