## MirScribe Pipeline - VCF Analysis Module

This repository contains the streamlined version of MirScribe pipeline's VCF analysis branch, focusing on pre-processing steps before XGBoost modeling.

### Prerequisites

- Python 3.8+
- Poetry (package manager)
- Git

### Installation

1. Install Poetry if not already installed:
```bash
pipx install poetry
```

2. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

3. Install dependencies:
```bash
poetry install
```

4. Install Pyensembl data:
```bash
poetry run pyensembl install --release 75
```

The pipeline is now ready to use. See [Pipeline Architecture](#pipeline-architecture) section for details about the components and data flow.

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