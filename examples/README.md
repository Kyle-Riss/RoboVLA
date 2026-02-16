# Robot Examples

This directory contains robot-specific examples and configurations.

## Adding a New Robot

### 1. Create Robot Config

Add your robot configuration to `config/robot_config.py`:

```python
from config.robot_config import RobotConfig, GripperConfig, create_custom_config

# Example: 7DOF robot with continuous gripper
my_robot = create_custom_config(
    name="my_7dof_robot",
    num_joints=7,
    gripper=GripperConfig(
        field_name="gripper_position",
        source_fields=["gripper_position"],
        extraction_method="direct",
        discrete=False,
        value_range=(0.0, 1.0),
    ),
    use_dummy_dim=True,
    joint_units="deg",
    joint_output_units="rad",
    filter_robot_mode=None,
)
```

### 2. Use Universal Scripts

```bash
# Convert JSON to LeRobot (uses robot config)
python scripts/data/convert_json_to_lerobot_universal.py \
    --json_dir json_output \
    --images_base_dir VLA_DATASET \
    --output_repo_id your_hf_username/my_robot_dataset \
    --robot_name my_7dof_robot
```

### 3. Training

The training config (`pi0_e6_freeze_vlm`) is robot-agnostic - it works with any 6DOF+ robot.
For different action dimensions, modify `config/pi0_e6_freeze_vlm.py`.

## Existing Examples

- **dobot_e6**: 6DOF + binary gripper (gripper_tooldo1)
  - See `dobot_e6/README.md` for details

## Robot Configuration Options

### DOF
- `num_joints`: Number of joints (6, 7, etc.)

### Gripper
- `gripper=None`: No gripper
- `gripper=GripperConfig(...)`: Configure gripper format
  - `discrete=True`: Binary (0/1)
  - `discrete=False`: Continuous (0.0-1.0)
  - `extraction_method`: How to extract from source data

### Units
- `joint_units`: Input units ("deg" or "rad")
- `joint_output_units`: Output units ("deg" or "rad")
- `position_units`: Position input units ("mm" or "m")

### Filtering
- `filter_robot_mode`: Filter by robot_mode value (None = no filter)
