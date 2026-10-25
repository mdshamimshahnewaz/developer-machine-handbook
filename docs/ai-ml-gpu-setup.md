# AI/ML & GPU Acceleration Reference

Guidance for developers doing machine learning and local LLM inference.

## 1. Hardware Inspection
```bash
# Check GPU presence
lspci | grep -i nvidia

# Check driver and CUDA capability (if NVIDIA GPU installed)
nvidia-smi
```

## 2. PyTorch with CUDA or CPU
Using Astral `uv`:
```bash
# CPU-only installation (standard laptops/workstations)
uv pip install torch --index-url https://download.pytorch.org/whl/cpu

# NVIDIA GPU (CUDA 12.4+)
uv pip install torch --index-url https://download.pytorch.org/whl/cu124
```

## 3. Local LLM Runner (Ollama)
Run models locally with zero Docker overhead:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull lightweight models
ollama run llama3.2:1b
ollama run qwen2.5-coder:1.5b
```

## 4. Cache Management
Hugging Face and PyTorch cache models in `~/.cache/huggingface`. Prune specific model caches rather than deleting the entire `~/.cache` directory:
```bash
# Check model cache size
du -sh ~/.cache/huggingface/hub/*
```
