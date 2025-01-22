from scripts.pipeline import *
from memory_profiler import profile

logger = None


def main():
    global logger
    
    try:        
        # Configure logging
        logger = configure_pipeline_logging(log_file_path='logs/pipeline.log',log_level=logging.INFO)

        # Test logging levels
        logger.debug("Debug message - Pipeline starting")
        logger.info("Info message - Pipeline configuration complete")
        logger.warning("Warning message - This is a test warning")

        # Run pipeline
        run_pipeline(
            vcf_full_path=ARG_VCF_FULL_PATH,
            chunksize=ARG_CHUNKSIZE,
            output_dir=OUTPUT_DIR,
            vcf_id=VCF_ID
        )

        logger.info("Pipeline completed successfully")

    except Exception as e:
        if logger:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        else:
            print(f"Fatal error (logger not initialized): {str(e)}")
        raise


if __name__ == '__main__':
    if ARG_PROFILER:
        profile(main)()
    else:
        main()