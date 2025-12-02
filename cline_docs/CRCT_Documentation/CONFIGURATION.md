# Configuration Reference

> [!TIP]
> This is a comprehensive reference for all configuration options in v8.0. Most users can use the defaults, but this guide helps fine-tune CRCT for specific needs.

## Configuration File

**Location**: `.clinerules.config.json` (project root)

**Format**: JSON

**Auto-Created**: If missing, defaults are used

---

## Quick Start

### Minimal Configuration

```json
{
  "code_roots": ["src/", "lib/"],
  "excluded_dirs": ["node_modules", "__pycache__"]
}
```

### Recommended Configuration

```json
{
  "code_roots": ["src/", "lib/"],
  "excluded_dirs": ["node_modules", "__pycache__", "venv", "build"],
  "thresholds": {
    "reranker_promotion_threshold": 0.92,
    "reranker_strong_semantic_threshold": 0.78
  },
  "analysis": {
    "max_reranker_scans": 20,
    "reranker_enabled": true
  },
  "embedding": {
    "auto_select_model": true,
    "batch_size": "auto"
  }
}
```

---

## Core Settings

### code_roots

**Type**: `Array<string>`  
**Default**: Auto-detected from project structure  
**Description**: Directories containing source code to analyze

```json
{
  "code_roots": [
    "src/",
    "lib/",
    "app/core/"
  ]
}
```

**Notes**:
- Paths relative to project root
- Only files in these directories are analyzed
- Subdirectories automatically included

### excluded_dirs

**Type**: `Array<string>`  
**Default**: See below  
**Description**: Directory names to skip during analysis

```json
{
  "excluded_dirs": [
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "build",
    "dist",
    ".pytest_cache"
  ]
}
```

### excluded_extensions

**Type**: `Array<string>`  
**Default**: Binary and compiled file extensions  
**Description**: File extensions to skip

```json
{
  "excluded_extensions": [
    ".pyc",
    ".exe",
    ".dll",
    ".so",
    ".o",
    ".jpg",
    ".png"
  ]
}
```

### excluded_file_patterns

**Type**: `Array<string>`  
**Default**: `[]`  
**Description**: Glob patterns for files to exclude

```json
{
  "excluded_file_patterns": [
    "*_test.py",
    "test_*.py",
    "*debug.txt",
    "*/migrations/*"
  ]
}
```

---

## Threshold Settings

### reranker_promotion_threshold

**Type**: `float` (0.0-1.0)  
**Default**: `0.92`  
**Description**: Score threshold for promoting to structural dependency (`<`)

**Usage**:
```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.95  // Stricter
  }
}
```

**Recommendations**:
- **Strict** (fewer deps): `0.95-0.98`
- **Balanced**: `0.90-0.94` (default)
- **Permissive** (more deps): `0.85-0.89`

### reranker_strong_semantic_threshold

**Type**: `float` (0.0-1.0)  
**Default**: `0.78`  
**Description**: Threshold for strong semantic dependency (`S`)

**Recommendations**:
- **Strict**: `0.85+`
- **Balanced**: `0.75-0.82` (default)
- **Permissive**: `0.65-0.74`

### reranker_weak_semantic_threshold

**Type**: `float` (0.0-1.0)  
**Default**: `0.65`  
**Description**: Threshold for weak semantic dependency (`s`)

**Recommendations**:
- **Strict**: `0.75+`
- **Balanced**: `0.60-0.70` (default)
- **Permissive**: `0.50-0.59`

---

## Analysis Settings

### max_reranker_scans

**Type**: `integer`  
**Default**: `20`  
**Description**: Maximum file pairs to rerank per file

```json
{
  "analysis": {
    "max_reranker_scans": 10  // Faster, less thorough
  }
}
```

**Impact**:
- Higher = More accurate, slower
- Lower = Faster, may miss dependencies

### reranker_enabled

**Type**: `boolean`  
**Default**: `true`  
**Description**: Enable/disable reranker

```json
{
  "analysis": {
    "reranker_enabled": false  // Disable for speed
  }
}
```

### runtime_inspection_enabled

**Type**: `boolean`  
**Default**: `true`  
**Description**: Enable runtime symbol inspection

```json
{
  "analysis": {
    "runtime_inspection_enabled": true
  }
}
```

### runtime_inspection_timeout

**Type**: `integer` (seconds)  
**Default**: `30`  
**Description**: Max time per module for runtime inspection

```json
{
  "analysis": {
    "runtime_inspection_timeout": 10  // Stricter timeout
  }
}
```

---

## Embedding Settings

### auto_select_model

**Type**: `boolean`  
**Default**: `true`  
**Description**: Automatically select best embedding model

```json
{
  "embedding": {
    "auto_select_model": true  // Recommended
  }
}
```

### batch_size

**Type**: `integer | "auto"`  
**Default**: `"auto"`  
**Description**: Batch size for embedding generation

```json
{
  "embedding": {
    "batch_size": 128  // Fixed size
  }
}
```

**Auto-sizing** (recommended):
- 6GB+ VRAM: 256
- 4GB+ VRAM: 128
- 2GB+ VRAM: 64
- CPU/low VRAM: 32

### max_context_length

**Type**: `integer`  
**Default**: `32768`  
**Description**: Maximum tokens for embeddings

```json
{
  "embedding": {
    "max_context_length": 16384  // Shorter for speed
  }
}
```

### ses_max_chars

**Type**: `integer`  
**Default**: `4000`  
**Description**: Maximum characters for Symbol Essence Strings

```json
{
  "embedding": {
    "ses_max_chars": 8000  // Larger for very detailed symbols
  }
}
```

---

## Compute Settings

### embedding_device

**Type**: `"auto" | "cuda" | "mps" | "cpu"`  
**Default**: `"auto"`  
**Description**: Device for embedding computations

```json
{
  "compute": {
    "embedding_device": "cuda"  // Force CUDA
  }
}
```

**Options**:
- `"auto"`: Detect best available
- `"cuda"`: NVIDIA GPU
- `"mps"`: Apple Silicon GPU
- `"cpu"`: CPU only

---

## Resource Settings

### min_memory_mb

**Type**: `integer`  
**Default**: `512`  
**Description**: Minimum RAM required (warnings if below)

```json
{
  "resources": {
    "min_memory_mb": 1024
  }
}
```

### recommended_memory_mb

**Type**: `integer`  
**Default**: `2048`  
**Description**: Recommended RAM for optimal performance

### max_workers

**Type**: `integer | "auto"`  
**Default**: `"auto"` (cpu_count * 4, max 64)  
**Description**: Maximum parallel workers

```json
{
  "resources": {
    "max_workers": 8  // Limit parallelism
  }
}
```

---

## Output Settings

### auto_generate_diagrams

**Type**: `boolean`  
**Default**: `true`  
**Description**: Auto-generate dependency diagrams

```json
{
  "output": {
    "auto_generate_diagrams": true
  }
}
```

### diagram_output_dir

**Type**: `string`  
**Default**: `"dependency_diagrams"`  
**Description**: Directory for generated diagrams

```json
{
  "output": {
    "diagram_output_dir": "docs/diagrams"
  }
}
```

### max_diagram_nodes

**Type**: `integer`  
**Default**: `100`  
**Description**: Maximum nodes in generated diagrams

```json
{
  "output": {
    "max_diagram_nodes": 50  // Simpler diagrams
  }
}
```

---

## Path Settings

### doc_dir

**Type**: `string`  
**Default**: `"docs"`  
**Description**: Documentation directory

### memory_dir

**Type**: `string`  
**Default**: `"cline_docs"`  
**Description**: System memory/state directory

### embeddings_dir

**Type**: `string`  
**Default**: `"cline_utils/dependency_system/analysis/embeddings"`  
**Description**: Embeddings storage directory

---

## Visualization Settings

### auto_diagram_output_dir

**Type**: `string | null`  
**Default**: `null`  
**Description**: Auto-diagram output location

```json
{
  "visualization": {
    "auto_diagram_output_dir": "cline_docs/dependency_diagrams"
  }
}
```

### max_edges_for_visualization

**Type**: `integer`  
**Default**: `1500`  
** Description**: Maximum edges before warning

```json
{
  "visualization": {
    "max_edges_for_visualization": 1000
  }
}
```

---

## Cache Settings

### cache_ttl_seconds

**Type**: `integer`  
**Default**: `300` (5 minutes)  
**Description**: Default cache time-to-live

```json
{
  "caching": {
    "cache_ttl_seconds": 600  // 10 minutes
  }
}
```

### enable_compression

**Type**: `boolean`  
**Default**: `true`  
**Description**: Enable cache compression

### compression_threshold

**Type**: `integer`  
**Default**: `1024` (1KB)  
**Description**: Minimum size for compression

---

## Environment Variables

CRCT also supports configuration via environment variables:

### EMBEDDING_MODEL

Override automatic model selection:
```bash
export EMBEDDING_MODEL="all-mpnet-base-v2"
```

### EMBEDDING_DEVICE

Force specific device:
```bash
export EMBEDDING_DEVICE="cuda"
```

### MAX_WORKERS

Set worker count:
```bash
export MAX_WORKERS=16
```

### USE_STREAMING

Enable streaming mode:
```bash
export USE_STREAMING=true
```

### DEBUG

Enable debug logging:
```bash
export DEBUG=true
```

---

## Complete Example

```json
{
  "code_roots": ["src/", "lib/", "app/"],
  
  "excluded_dirs": [
    "__pycache__",
    ".git",
    "node_modules",
    "venv",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache"
  ],
  
  "excluded_file_patterns": [
    "*_test.py",
    "test_*.py",
    "*debug.txt",
    "*/migrations/*"
  ],
  
  "thresholds": {
    "reranker_promotion_threshold": 0.92,
    "reranker_strong_semantic_threshold": 0.78,
    "reranker_weak_semantic_threshold": 0.65
  },
  
  "analysis": {
    "max_reranker_scans": 20,
    "reranker_enabled": true,
    "runtime_inspection_enabled": true,
    "runtime_inspection_timeout": 30,
    "strict_binary_detection": true
  },
  
  "embedding": {
    "auto_select_model": true,
    "batch_size": "auto",
    "max_context_length": 32768,
    "ses_max_chars": 4000
  },
  
  "compute": {
    "embedding_device": "auto"
  },
  
  "resources": {
    "min_memory_mb": 512,
    "recommended_memory_mb": 2048,
    "max_workers": "auto",
    "resource_check_enabled": true
  },
  
  "output": {
    "auto_generate_diagrams": true,
    "diagram_output_dir": "dependency_diagrams",
    "max_diagram_nodes": 100
  },
  
  "caching": {
    "cache_ttl_seconds": 300,
    "enable_compression": true,
    "compression_threshold": 1024
  }
}
```

---

## Configuration Tips

### 1. Start with Defaults

Defaults work well for most projects. Only customize if needed.

### 2. Exclude Aggressively

Exclude test files, migrations, generated code:
```json
{
  "excluded_file_patterns": [
    "test_*.py",
    "*_test.py",
    "*/migrations/*",
    "*/generated/*"
  ]
}
```

### 3. Tune Thresholds Gradually

Adjust in small increments (±0.05) and test:
```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.90  // Was 0.92
  }
}
```

### 4. Monitor Resource Usage

Check logs to see if limits are being hit:
```bash
grep "memory" cline_docs/debug.txt
grep "workers" cline_docs/debug.txt
```

### 5. Use Environment Variables for Testing

```bash
# Test with different settings
DEBUG=true MAX_WORKERS=4 python -m cline_utils.dependency_system.dependency_processor analyze-project
```

---

## Validation

CRCT validates configuration on startup:

```
INFO: Loading configuration from .clinerules.config.json
INFO: Validating settings...
WARNING: max_reranker_scans > 50 may be slow
ERROR: Invalid embedding_device: 'invalid'
INFO: Configuration loaded successfully
```

Fix errors before proceeding.

---

## References

- [Default Configuration](cline_utils/dependency_system/utils/config_manager.py#L20)
- [Migration Guide](MIGRATION_v7.x_to_v8.0.md)
- [Hardware Optimization](HARDWARE_OPTIMIZATION.md)

---

**Proper configuration ensures CRCT performs optimally for your specific project and hardware.** Start with defaults and tune as needed based on analysis results.
