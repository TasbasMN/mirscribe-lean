from socket import gethostname





















def get_pyensembl_cache_location():
    hostname = gethostname()
    if hostname == "nazo":
        return "/home/nazif/thesis/data"
    elif hostname == "Minerva":
        return "/home/yamak/Code/nazif/data"
    else:
        return "/truba/home/mtasbas/data"

def get_rnaduplex_location():
    hostname = gethostname()
    if hostname == "nazo":
        return "/usr/local/bin/RNAduplex"
    elif hostname == "Minerva":
        return "/usr/bin/RNAduplex"
    else:
        return "/truba/home/mtasbas/miniconda3/envs/venv/bin/RNAduplex"
    
PYENSEMBL_CACHE_DIR = get_pyensembl_cache_location()
RNADUPLEX_LOCATION = get_rnaduplex_location()

TA_SPS_CSV = "data/ta_sps/ta_sps.csv"
MIRNA_CSV = "data/mirna/mirna.csv"
XGB_MODEL = "misc/models/model_with_no_close_proximity.json"

NUCLEOTIDE_OFFSET = 30


AWK_SCRIPT_PATH = "scripts/rnaduplex_to_csv.awk"
AWK_SCRIPT_PATH_NEW = "scripts/rnaduplex_to_csv_new.awk"

MUTSIG_PROBABILITIES = "data/mutsig_probabilities/probabilities.csv"
MUTSIG_PROBABILITIES_560 = "data/mutsig_probabilities/probabilities_560.csv"

