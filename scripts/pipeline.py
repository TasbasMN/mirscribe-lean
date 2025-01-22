import logging
from typing import Generator, Tuple
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from scripts.config import *


def configure_pipeline_logging(log_file_path=None, log_level=logging.INFO):
    """Configure logging for the entire pipeline

    Args:
        log_file_path (str, optional): Path to log file. If None, logs only to console
        log_level (int, optional): Logging level. Defaults to logging.INFO
    """
    global logger

    # Create logger
    logger = logging.getLogger('pipeline')
    logger.setLevel(log_level)

    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(message)s')
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # Show only WARNING+ on console

    logger.addHandler(console_handler)

    # File handler if path provided
    if log_file_path:
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent logging from propagating to the root logger
    logger.propagate = False

    return logger


def yield_chunks(filepath: str, chunksize: int) -> Generator[pd.DataFrame, None, None]:
    """Reads VCF file in chunks"""
    logger.info(f"Reading: {os.path.basename(filepath)} | Chunk size: {chunksize}")
    
    try:
        yield from pd.read_csv(
            filepath,
            chunksize=chunksize,
            sep="\t",
            header=None,
            names=VCF_COLNAMES,
        )
    except Exception as e:
        logger.error(f"Read failed: {str(e)}")
        raise


def process_chunk(
    chunk: pd.DataFrame,
    start_index: int,
    end_index: int,
    output_dir: str,
    vcf_id: str
) -> Tuple[int, int]:
    """
    Applies transformations, writes the chunk to a CSV file.
    Returns (start_index, end_index) so we know which rows were processed.
    """
    logger.info(f"Processing chunk {start_index}–{end_index} ...")

    try:
        # 1) Transform the chunk
        chunk = transform_chunk(chunk)

        # 2) Write out results
        result_file = os.path.join(output_dir, f"result_{start_index}_{end_index}.csv")
        chunk.to_csv(result_file, index=False)

        logger.info(f"Finished chunk {start_index}–{end_index}, wrote: {result_file}")
        return start_index, end_index

    except Exception as e:
        logger.error(f"Error processing chunk {start_index}–{end_index}: {str(e)}")
        raise


def process_chunk_with_retry(
    chunk: pd.DataFrame,
    start_index: int,
    end_index: int,
    output_dir: str,
    vcf_id: str,
    retry_count: int,
    max_retries: int
) -> Tuple[int, int]:
    """
    Wraps process_chunk with a simple retry mechanism.
    """
    try:
        return process_chunk(chunk, start_index, end_index, output_dir, vcf_id)
    except Exception as e:
        logger.warning(
            f"Retry {retry_count +1} of {max_retries} for chunk {start_index}-{end_index}. "
            f"Exception: {e}"
        )
        if retry_count >= max_retries:
            logger.error(f"Max retries ({max_retries}) reached for chunk {start_index}-{end_index}")
            raise
        return process_chunk_with_retry(
            chunk,
            start_index,
            end_index,
            output_dir,
            vcf_id,
            retry_count + 1,
            max_retries
        )


def transform_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """Transform chunk"""
    logger.debug(f"Transform start | Rows: {len(chunk)}")
    try:

        # Convert chromosome column to string
        chunk["chr"] = chunk["chr"].astype(str)

        # Append variant details to the 'id' column
        chunk["id"] = (
            chunk["id"].astype(str)
            + "_" + chunk["chr"]
            + "_" + chunk["pos"].astype(str)
            + "_" + chunk["ref"]
            + "_" + chunk["alt"]
        )

        logger.debug("Transform complete")
        return chunk
    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
        raise


def run_pipeline(
    vcf_full_path: str,
    chunksize: int,
    output_dir: str,
    vcf_id: str,
    max_workers: int = ARG_WORKERS,
    max_retries: int = 3
) -> None:
    """
    Main pipeline function.
    """
    logger.info(f"Starting pipeline for {vcf_id}")
    logger.info(f"Parameters: chunksize={chunksize}, max_workers={max_workers}, max_retries={max_retries}")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    futures = []
    processed_chunks = []
    start_idx = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Schedule each chunk
        for chunk in yield_chunks(vcf_full_path, chunksize):
            end_idx = start_idx + len(chunk) - 1

            def submit_chunk(retry_count=0):
                future = executor.submit(
                    process_chunk_with_retry,
                    chunk,
                    start_idx,
                    end_idx,
                    output_dir,
                    vcf_id,
                    retry_count,
                    max_retries
                )
                futures.append(future)

            submit_chunk()
            start_idx = end_idx + 1

        # Gather results
        for future in as_completed(futures):
            try:
                s_idx, e_idx = future.result()
                processed_chunks.append((s_idx, e_idx))
            except Exception as e:
                logger.error(f"Chunk failed after retries. Exception: {e}")

    logger.info(f"Processed {len(processed_chunks)} chunk(s) successfully.")
