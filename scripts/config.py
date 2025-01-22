import argparse
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Process a VCF file in chunks using concurrent futures.')
    
    
    parser.add_argument('--file_path', default="data/sample_vcfs/sample.vcf",
                    type=str, help='Path to the VCF file')
    parser.add_argument("-c", '--ARG_CHUNKSIZE', default=200,
                        type=int, help='Number of lines to process per chunk')
    parser.add_argument("-o", '--output_dir', type=str,
                        default='./results', help='Path to the output directory')
    parser.add_argument('-v', '--ARG_VERBOSE', action='store_true',
                        help='Enable ARG_VERBOSE logging')
    parser.add_argument('-w', '--ARG_WORKERS', default=os.cpu_count(),
                        type=int, help='Number of concurrent ARG_WORKERS')
    parser.add_argument('-t', '--threshold', default=0.2, type=float,
                        help='Threshold for filtering out pairs that have less prediction difference than the threshold')
    parser.add_argument('--profile', action='store_true',
                        help='Enable memory profiling')

    return parser.parse_args()


args = parse_arguments()

ARG_VCF_FULL_PATH = args.file_path
ARG_CHUNKSIZE = args.ARG_CHUNKSIZE
ARG_VERBOSE = args.ARG_VERBOSE
ARG_WORKERS = args.ARG_WORKERS
ARG_FILTER_THRESHOLD = args.threshold
ARG_PROFILER = args.profile

VCF_ID = os.path.basename(ARG_VCF_FULL_PATH).split(".")[0]
OUTPUT_DIR = os.path.join(args.output_dir, f"{VCF_ID}_{ARG_CHUNKSIZE}")


G37_FASTAS_DIR = "data/fasta/grch37"
MIRNA_COORDS_DIR = "data/mirna_coordinates"
NUCLEOTIDE_OFFSET = 30
VCF_COLNAMES = ["chr", "pos", "id", "ref", "alt"]
