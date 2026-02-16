# RoboVLA

**Robot Vision-Language-Action (VLA) Training Pipeline**

> Freeze VLM (PaliGemma-3B) and train action head only for 6DOF + gripper manipulation tasks.

## Overview

RoboVLA provides a complete pipeline for training VLA models on manipulation robots:
- **VLM Freeze Strategy**: PaliGemma-3B encoder frozen, only action head trained
- **Universal Structure**: 6DOF joint + gripper action space (easily adaptable to other robots)
- **PyTorch Training**: Full PyTorch implementation for edge deployment (Jetson)

## Supported Robots

- ✅ **Dobot E6**: Full pipeline (data collection → training → deployment)
- 🔄 **Other 6DOF robots**: Easy to add (just change action mapping)

## Key Features

- **VLM Freeze**: Efficient training by freezing vision-language encoder
- **Action Head Only**: Train only the action prediction head
- **8D Action Space**: 6 joint deltas + dummy + gripper delta
- **PyTorch Native**: Ready for Jetson deployment (.pth format)
- **Extensible**: Easy to add new robots by modifying action config

## Pipeline

```
Data Collection (Dobot-Arm-DataCollect)
    ↓
CSV/NPY → JSON (convert_all_episodes_to_json.py)
    ↓
JSON → LeRobot Format (convert_json_to_lerobot.py)
    ↓
Compute Norm Stats (compute_norm_stats.py)
    ↓
Training (train_universal.py or train_pytorch_wrapper.py with frozen VLM)
    ↓
Deployment (convert_checkpoint_for_jetson.py)
```

## Project Structure

```
RoboVLA/
├── scripts/
│   ├── data/              # Data conversion scripts
│   │   ├── convert_all_episodes_to_json.py
│   │   ├── convert_json_to_lerobot.py
│   │   ├── compute_norm_stats.py
│   │   └── verify_gripper_in_json.py
│   ├── training/          # Training scripts
│   │   ├── run_training_universal.sh
│   │   ├── run_dobot_e6_training.sh
│   │   ├── train_universal.py
│   │   ├── train_pytorch_wrapper.py
│   │   ├── eval_checkpoint_actions.py
│   │   └── pick_best_checkpoint.py
│   └── deployment/        # Deployment scripts
│       └── convert_checkpoint_for_jetson.py
├── examples/
│   └── dobot_e6/          # Dobot E6 example
│       ├── convert_json_to_lerobot.py
│       ├── config_reference.py
│       └── README.md
└── docs/                  # Documentation
```

## Dependencies

- **openpi**: Core training framework (required, but **NOT modified**)
- **Dobot-Arm-DataCollect**: Data collection (sibling directory)
- **LeRobot**: Dataset format
- **PyTorch**: Training framework

## ⚠️ Important: No Modification to openpi Source

**RoboVLA does NOT require modifying openpi source code.** 

Config registration happens at runtime using `config/pi0_e6_freeze_vlm.py`. 
See `docs/USAGE.md` for details.

## Quick Start

### 1. Setup (Standalone - No openpi modification)

```bash
# Clone RoboVLA
git clone <your-repo>/RoboVLA.git
cd RoboVLA

# Install openpi (don't modify it!)
git clone https://github.com/26kp/openpi.git ../openpi
cd ../openpi && pip install -e . && cd ../RoboVLA

# Verify setup
python scripts/setup_env.py
```

### 2. Data Pipeline

```bash
# Step 1: Convert VLA_DATASET to JSON
python scripts/data/convert_all_episodes_to_json.py \
    --vla_dataset_dir /path/to/VLA_DATASET \
    --output_dir json_output \
    --use_csv

# Step 2: Convert JSON to LeRobot format
python examples/dobot_e6/convert_json_to_lerobot.py \
    --json_dir json_output \
    --images_base_dir /path/to/VLA_DATASET \
    --output_repo_id your_hf_username/dobot_e6_vla_dataset

# Step 3: Compute normalization statistics
python scripts/data/compute_norm_stats.py \
    --repo_id your_hf_username/dobot_e6_vla_dataset \
    --asset_id your_hf_username/dobot_e6_vla_dataset
```

### 3. Training

**Universal training (recommended):**

```bash
cd RoboVLA

# Universal script (auto-detects paths)
bash scripts/training/run_training_universal.sh \
    --config pi0_e6_freeze_vlm \
    --exp-name my_experiment \
    --num-steps 10000

# Or set paths manually
export OPENPI_PATH=/path/to/openpi
bash scripts/training/run_training_universal.sh
```

**Dobot E6 specific (legacy):**

```bash
bash scripts/training/run_dobot_e6_training.sh
```

### 4. Deployment

```bash
# Convert checkpoint for Jetson
python scripts/deployment/convert_checkpoint_for_jetson.py \
    --checkpoint_dir checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_10k_gripper/10000 \
    --output_dir checkpoints/jetson_deploy
```

## Configuration

**No openpi modification needed!** 

The config `pi0_e6_freeze_vlm` is registered dynamically at runtime.
See `config/pi0_e6_freeze_vlm.py` and `docs/USAGE.md` for details.

## Adding New Robots

RoboVLA supports any robot with configurable DOF and gripper format:

### Step 1: Add Robot Config

Edit `config/robot_config.py` or create a new config file:

```python
from config.robot_config import create_custom_config, GripperConfig

my_robot = create_custom_config(
    name="my_robot",
    num_joints=7,  # 6, 7, 8, etc.
    gripper=GripperConfig(
        field_name="gripper",
        source_fields=["gripper_field"],
        extraction_method="direct",  # or "threshold", "max"
        discrete=False,  # True for 0/1, False for continuous
    ),
    use_dummy_dim=True,
    joint_units="deg",
    joint_output_units="rad",
)
```

### Step 2: Use Universal Scripts

```bash
# Convert data (automatically uses your robot config)
python scripts/data/convert_json_to_lerobot_universal.py \
    --robot_name my_robot \
    --json_dir json_output \
    --images_base_dir VLA_DATASET \
    --output_repo_id your_hf_username/my_robot_dataset

# Train (same pipeline works for all robots)
bash scripts/training/run_training_universal.sh \
    --config pi0_e6_freeze_vlm \
    --exp-name my_robot_training
```

See `examples/README.md` and `config/example_7dof.py` for more examples.

## Documentation

- **Usage Guide**: `docs/USAGE.md` - How to use without modifying openpi
- **Setup Guide**: `docs/SETUP.md` - Initial setup instructions
- **Dobot E6 Guide**: `examples/dobot_e6/README.md`
- **Config Reference**: `config/pi0_e6_freeze_vlm.py` - Runtime config registration

## License

MIT License (same as openpi)

## References

- **openpi**: https://github.com/26kp/openpi
- **Dobot-Arm-DataCollect**: https://github.com/Kyle-Riss/Dobot-Arm-DataCollect
- **LeRobot**: https://github.com/huggingface/lerobot
