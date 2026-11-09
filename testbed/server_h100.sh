#!/usr/bin/env bash
# Chạy trên server H100 80GB, từ thư mục gốc repo (xem testbed/RUNBOOK_B.md).
#   bash testbed/server_h100.sh check   kiểm phần cứng, không cài gì
#   bash testbed/server_h100.sh setup   tạo venv vLLM 0.11.0, tải Qwen2.5-VL-7B đúng revision và kiểm từng file
#   bash testbed/server_h100.sh serve   chạy model ở 127.0.0.1:8101 (chạy trong tmux; Ctrl-C để dừng)
set -euo pipefail
cd "$(dirname "$0")/.."
VENV=runtime/serve-venv
PY=$VENV/bin/python
STAMP=$(date +%m%d-%H%M)
mkdir -p testbed/runs

case "${1:-}" in
check)
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo "CPU: $(nproc) nhân"
    free -g | sed -n '1,2p'
    df -h . | tail -1
    if [ -r /dev/kvm ] && [ -w /dev/kvm ]; then echo "KVM: có"; else echo "KVM: không (AVD chạy ở máy local)"; fi
    python3 --version
    ;;
setup)
    [ -d "$VENV" ] || python3 -m venv "$VENV"
    "$PY" -m pip install -q --upgrade pip
    "$PY" -m pip install -q vllm==0.11.0 huggingface_hub
    "$PY" -c "import importlib.metadata as m; print('vllm', m.version('vllm'))"
    if [ -f runtime/models/qwen/cc594898137f460bfe9f0759e9844b3ce807cfb5/SNAPSHOT.json ]; then
        echo "Qwen đã tải và kiểm xong trước đó"
    else
        "$PY" testbed/setup_models.py --only qwen --download --output "testbed/runs/models-$STAMP"
    fi
    ;;
serve)
    "$PY" testbed/serve_model.py --model qwen --allocation singleton --port 8101 --output "testbed/runs/serve-$STAMP"
    ;;
*)
    echo "dùng: bash testbed/server_h100.sh check|setup|serve" >&2
    exit 2
    ;;
esac
