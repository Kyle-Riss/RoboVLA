#!/bin/bash
# Universal training script for RoboVLA
#
# This script works with any robot configuration and automatically sets up environment.
#
# Usage:
#   bash scripts/training/run_training_universal.sh \
#     --config pi0_e6_freeze_vlm \
#     --exp-name my_experiment \
#     --num-steps 10000 \
#     [--openpi-path /path/to/openpi]
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROBOVLA_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Default values
CONFIG_NAME="pi0_e6_freeze_vlm"
EXP_NAME="robovla_training"
NUM_STEPS=10000
OPENPI_PATH=""
BATCH_SIZE=4
SAVE_INTERVAL=10000

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_NAME="$2"
            shift 2
            ;;
        --exp-name)
            EXP_NAME="$2"
            shift 2
            ;;
        --num-steps)
            NUM_STEPS="$2"
            shift 2
            ;;
        --openpi-path)
            OPENPI_PATH="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --save-interval)
            SAVE_INTERVAL="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--config CONFIG] [--exp-name NAME] [--num-steps N] [--openpi-path PATH]"
            exit 1
            ;;
    esac
done

echo "RoboVLA Universal Training"
echo "=========================="
echo "Config: $CONFIG_NAME"
echo "Experiment: $EXP_NAME"
echo "Steps: $NUM_STEPS"
echo ""

# Setup environment
cd "$ROBOVLA_ROOT"

# Setup Python path and register config
export ROBOVLA_ROOT="$ROBOVLA_ROOT"
if [ -n "$OPENPI_PATH" ]; then
    export OPENPI_PATH="$OPENPI_PATH"
fi

# Run environment setup
python scripts/setup_env.py

# Activate venv if exists
if [ -f "$ROBOVLA_ROOT/.venv/bin/activate" ]; then
    source "$ROBOVLA_ROOT/.venv/bin/activate"
elif [ -n "$OPENPI_PATH" ] && [ -f "$OPENPI_PATH/.venv/bin/activate" ]; then
    source "$OPENPI_PATH/.venv/bin/activate"
fi

# Run training using universal script
echo ""
echo "Starting training..."
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python scripts/training/train_universal.py "$CONFIG_NAME" \
    --exp-name "$EXP_NAME" \
    --no-wandb-enabled \
    --num-train-steps "$NUM_STEPS" \
    --save-interval "$SAVE_INTERVAL" \
    --log-interval 100 \
    --batch-size "$BATCH_SIZE" \
    --num-workers 0 \
    --overwrite

echo ""
echo "✅ Training complete!"
