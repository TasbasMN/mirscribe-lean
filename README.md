This is the lean version of mirscribe pipeline's vcf analysis branch, until the xgboost step.

how to install:

clone repo

install env (install poetry through pipx if you don't have it already)

pyensembl install --release 75


## Pipeline Architecture

The pipeline follows a parallel processing architecture with retry mechanisms and streaming data handling.

### Function Call Graph

```
🚀 run_pipeline
│
├──➡️ yield_chunks
│   └──📊 pd.read_csv
│
├──🔄 ThreadPoolExecutor
│   └──📦 submit_chunk (nested function)
│      └──🔁 process_chunk_with_retry
│         └──⚙️ process_chunk
│            └──🛠️ transform_chunk
│
└──✅ as_completed
```

### Component Roles
- 🚀 run_pipeline: Main orchestrator
- ➡️ yield_chunks: Data stream generator
- 🔄 ThreadPoolExecutor: Parallel processing manager
- 🔁 process_chunk_with_retry: Retry wrapper
- ⚙️ process_chunk: Core processing logic
- 🛠️ transform_chunk: Data transformation

### Processing Flow
1. run_pipeline initiates the process
2. yield_chunks streams data
3. ThreadPoolExecutor manages parallel processing
4. Each chunk goes through retry wrapper
5. Process and transform functions handle the data
6. Results are collected via as_completed