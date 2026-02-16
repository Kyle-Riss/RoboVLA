# RoboVLA Usage Guide

## Prerequisites

### 1. Install openpi (without modifying source)

```bash
# Clone openpi
git clone https://github.com/26kp/openpi.git
cd openpi
pip install -e .

# OR use existing openpi installation
# Just ensure openpi is in your PYTHONPATH
```

### 2. Register Config (Without Modifying openpi)

RoboVLA provides a config registration system that doesn't require modifying openpi source.

**Option A: Auto-register (Recommended)**

```python
# Before using any openpi.training.config functions:
from config import register_config
register_config()

# Now you can use:
from openpi.training.config import get_config
config = get_config("pi0_e6_freeze_vlm")  # ✅ Works!
```

**Option B: Manual registration**

```python
import sys
from pathlib import Path

robo_vla_root = Path("/path/to/RoboVLA")
sys.path.insert(0, str(robo_vla_root))

from config import register_config
register_config()
```

**Option C: Use wrapper scripts**

The training scripts use `train_pytorch_wrapper.py` which auto-registers config.

## Directory Structure

```
your_workspace/
├── openpi/                    # Original openpi (untouched)
├── Dobot-Arm-DataCollect/     # Data collection
└── RoboVLA/                   # This project
    ├── config/                # Config registration (no openpi modification)
    ├── scripts/
    └── examples/
```

## Usage Examples

### 1. Data Pipeline

```bash
cd RoboVLA

# Convert VLA_DATASET to JSON
python scripts/data/convert_all_episodes_to_json.py \
    --vla_dataset_dir /path/to/VLA_DATASET \
    --output_dir json_output \
    --use_csv

# Convert JSON to LeRobot
python examples/dobot_e6/convert_json_to_lerobot.py \
    --json_dir json_output \
    --images_base_dir /path/to/VLA_DATASET \
    --output_repo_id your_hf_username/dobot_e6_vla_dataset
```

### 2. Training

```bash
cd RoboVLA

# Set openpi path (if not sibling directory)
export OPENPI_PATH=/path/to/openpi

# Run training (config auto-registered)
bash scripts/training/run_dobot_e6_training.sh
```

### 3. Using Config in Python

```python
import sys
from pathlib import Path

# Add RoboVLA to path
robo_vla_root = Path("/path/to/RoboVLA")
sys.path.insert(0, str(robo_vla_root))

# Register config
from config import register_config
register_config()

# Now use openpi normally
from openpi.training.config import get_config
config = get_config("pi0_e6_freeze_vlm")
```

## Important Notes

1. **openpi is NOT modified**: All config registration happens at runtime
2. **Config registration**: Must happen before calling `get_config()`
3. **Path dependencies**: 
   - `convert_all_episodes_to_json.py` expects Dobot-Arm-DataCollect as sibling
   - Training scripts expect openpi in OPENPI_PATH or as sibling

## Troubleshooting

### Config not found

```
KeyError: 'pi0_e6_freeze_vlm'
```

**Solution**: Make sure to register config before using:
```python
from config import register_config
register_config()
```

### openpi not found

```
ModuleNotFoundError: No module named 'openpi'
```

**Solution**: Install openpi or set PYTHONPATH:
```bash
export PYTHONPATH=/path/to/openpi:$PYTHONPATH
```

### Dobot-Arm-DataCollect not found

```
Error: convert_to_json.py not found
```

**Solution**: Ensure Dobot-Arm-DataCollect is sibling directory or adjust path in script.
