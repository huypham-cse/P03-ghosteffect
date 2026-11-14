#!/usr/bin/env bash
# Run on the GPU server from the repo root (see testbed/RUNBOOK_B.md).
#   bash testbed/server_gpu.sh check   hardware and Python only, installs nothing
#   bash testbed/server_gpu.sh setup   venv with vLLM 0.11.0, Qwen2.5-VL-7B at the pinned revision, every file checked
#   bash testbed/server_gpu.sh serve   model on 127.0.0.1:8101 (run inside tmux; Ctrl-C stops it)
# GPU profile from nvidia-smi: A10G (AWS g5), L40S (AWS g6e) or H100. Memory settings per profile are in serve_model.py.
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=runtime/serve-venv
PY=$VENV/bin/python
STAMP=$(date +%m%d-%H%M)
mkdir -p testbed/runs

gpu_profile() {
    local name
    name=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    case "$name" in
        *A10G*) echo a10g ;;
        *L40S*) echo l40s ;;
        *H100*) echo h100 ;;
        *) echo "no profile for GPU '$name' (serve_model.py GPUS)" >&2; return 1 ;;
    esac
}

python_ok() {   # vLLM 0.11.0 and torch 2.8.0 have wheels for Python 3.9 to 3.13 only (Ubuntu 26.04 ships 3.14)
    python3 -c 'import sys; v=sys.version_info[:2]; sys.exit(0 if (3, 9) <= v < (3, 14) else 1)' ||
        { echo "python3 is $(python3 --version); vLLM 0.11.0 needs 3.9 to 3.13 (use Ubuntu 24.04)" >&2; return 1; }
}

case "${1:-}" in
check)
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo "profile: $(gpu_profile)"
    echo "CPU: $(nproc) cores"
    free -g | sed -n '1,2p'
    df -h . | tail -1
    python3 --version
    python_ok && echo "Python: OK for vLLM 0.11.0"
    ;;
setup)
    python_ok
    if ! python3 -c 'import ensurepip' 2>/dev/null; then   # Ubuntu leaves venv support out of the base image
        SUDO=; [ "$(id -u)" = 0 ] || SUDO=sudo
        $SUDO apt-get -o DPkg::Lock::Timeout=600 update -q
        $SUDO apt-get -o DPkg::Lock::Timeout=600 install -y -q python3-venv
    fi
    [ -d "$VENV" ] || python3 -m venv "$VENV"
    "$PY" -m pip install -q --upgrade pip
    # vllm 0.11.0 only asks for transformers>=4.55.2, so pip would take transformers 5; pin what its CI tested
    "$PY" -m pip install -q vllm==0.11.0 transformers==4.55.2 huggingface_hub==0.34.3
    "$PY" -c "import vllm, transformers, importlib.metadata as m; print('vllm', m.version('vllm'), 'transformers', transformers.__version__)"
    if [ -f runtime/models/qwen/cc594898137f460bfe9f0759e9844b3ce807cfb5/SNAPSHOT.json ]; then
        echo "Qwen already downloaded and checked"
    else
        "$PY" testbed/setup_models.py --only qwen --download --output "testbed/runs/models-$STAMP"
    fi
    ;;
serve)
    "$PY" testbed/serve_model.py --model qwen --allocation singleton --gpu "$(gpu_profile)" --port 8101 \
        --output "testbed/runs/serve-$STAMP"
    ;;
*)
    echo "usage: bash testbed/server_gpu.sh check|setup|serve" >&2
    exit 2
    ;;
esac
