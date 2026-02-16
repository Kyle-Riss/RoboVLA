#!/bin/bash
# Dobot E6 PyTorch 학습 실행 스크립트
#
# 전략: 20k는 상한선. 2k~5k까지 먼저 가보고, eval로 베스트 확인.
#       개선 없으면 조기 종료, 있으면 10k/20k까지 확장.
#
# 사용법:
#   1. 다른 GPU 프로세스 종료 후 실행 (nvidia-smi)
#   2. 5k 먼저: NUM_STEPS=5000 ./scripts/run_dobot_e6_training.sh
#   3. 20k 완주: ./scripts/run_dobot_e6_training.sh (기본)
#   4. 학습 후: python scripts/pick_best_checkpoint.py
#
# GPU 메모리: 최소 16GB (batch_size=4)

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROBOVLA_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if openpi is available
if [ -z "$OPENPI_PATH" ]; then
    # Try to find openpi as sibling directory
    if [ -d "$ROBOVLA_ROOT/../openpi" ]; then
        OPENPI_PATH="$ROBOVLA_ROOT/../openpi"
    elif [ -d "$ROBOVLA_ROOT/openpi" ]; then
        OPENPI_PATH="$ROBOVLA_ROOT/openpi"
    else
        echo "Error: openpi not found. Set OPENPI_PATH environment variable."
        echo "  Example: export OPENPI_PATH=/path/to/openpi"
        exit 1
    fi
fi

echo "Using openpi at: $OPENPI_PATH"

# Activate venv if exists
if [ -f "$OPENPI_PATH/.venv/bin/activate" ]; then
    source "$OPENPI_PATH/.venv/bin/activate"
elif [ -f "$ROBOVLA_ROOT/.venv/bin/activate" ]; then
    source "$ROBOVLA_ROOT/.venv/bin/activate"
fi

# Register RoboVLA config before training
export PYTHONPATH="$ROBOVLA_ROOT:$OPENPI_PATH:$PYTHONPATH"

NUM_STEPS=${NUM_STEPS:-10000}  # 10k step 학습

# Use wrapper that registers config, or use openpi's train_pytorch directly
# Option 1: Use wrapper (registers config automatically)
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True python "$ROBOVLA_ROOT/scripts/training/train_pytorch_wrapper.py" pi0_e6_freeze_vlm \
  --exp-name dobot_e6_run_10k_gripper \
  --no-wandb-enabled \
  --num-train-steps "$NUM_STEPS" \
  --save-interval 10000 \
  --log-interval 100 \
  --batch-size 4 \
  --num-workers 0 \
  --overwrite
