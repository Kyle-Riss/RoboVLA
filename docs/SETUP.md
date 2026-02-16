# RoboVLA Setup Guide

## Prerequisites

1. **openpi**: Core training framework
   ```bash
   git clone https://github.com/26kp/openpi.git
   cd openpi
   pip install -e .
   ```

2. **Dobot-Arm-DataCollect**: Data collection (sibling directory)
   ```bash
   # Should be at: ../Dobot-Arm-DataCollect/
   git clone https://github.com/Kyle-Riss/Dobot-Arm-DataCollect.git
   ```

3. **Python Dependencies**:
   - PyTorch
   - LeRobot
   - HuggingFace datasets
   - (See openpi requirements)

## Directory Structure

```
26kp/
├── openpi/                    # Training framework
├── Dobot-Arm-DataCollect/     # Data collection
└── RoboVLA/                  # This project
```

## Configuration

### 1. Config Registration (Automatic)

The `pi0_e6_freeze_vlm` config is automatically registered at runtime. No modification to openpi source code is required.

The config is defined in `config/pi0_e6_freeze_vlm.py` and registered via:
- `scripts/training/train_universal.py` (universal training script)
- `scripts/training/train_pytorch_wrapper.py` (wrapper for openpi's train_pytorch)

### 2. Environment Detection

Paths are automatically detected via `config/env_config.py`:
- `openpi` path: Checks sibling directory or `OPENPI_PATH` environment variable
- `Dobot-Arm-DataCollect` path: Checks sibling directory or configured path

You can verify the setup:
```bash
python scripts/setup_env.py
```

### 3. Manual Path Configuration (Optional)

If automatic detection fails, set environment variables:
```bash
export OPENPI_PATH=/path/to/openpi
export PYTHONPATH=/path/to/openpi:$PYTHONPATH
```

## Usage

See main README.md for usage examples.
