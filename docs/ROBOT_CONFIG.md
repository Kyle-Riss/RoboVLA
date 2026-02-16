# Robot Configuration Guide

RoboVLA supports any robot with configurable DOF and gripper formats.

## Quick Example: 7DOF Robot

```python
from config.robot_config import create_custom_config, GripperConfig

# Add to config/robot_config.py or create new file
my_7dof = create_custom_config(
    name="my_7dof_robot",
    num_joints=7,
    gripper=GripperConfig(
        field_name="gripper_position",
        source_fields=["gripper_position"],
        extraction_method="direct",
        discrete=False,  # Continuous gripper
    ),
    use_dummy_dim=True,
    joint_units="deg",
    joint_output_units="rad",
)
```

Then use:
```bash
python scripts/data/convert_json_to_lerobot_universal.py \
    --robot_name my_7dof_robot \
    ...
```

## Configuration Options

### DOF (Degrees of Freedom)

```python
num_joints=6   # 6DOF robot
num_joints=7   # 7DOF robot
num_joints=8   # 8DOF robot
```

### Gripper Formats

**Binary Gripper (0/1):**
```python
gripper=GripperConfig(
    field_name="gripper",
    source_fields=["gripper_open"],
    extraction_method="threshold",
    threshold=0.5,
    discrete=True,
)
```

**Continuous Gripper (0.0-1.0):**
```python
gripper=GripperConfig(
    field_name="gripper_position",
    source_fields=["gripper_position"],
    extraction_method="direct",
    discrete=False,
    value_range=(0.0, 1.0),
)
```

**No Gripper:**
```python
gripper=None
```

### Extraction Methods

- `"direct"`: Use field value directly
- `"threshold"`: Convert to binary (0/1) based on threshold
- `"max"`: Use maximum value from source_fields

### Units

- `joint_units`: Input units ("deg" or "rad")
- `joint_output_units`: Output units ("deg" or "rad")
- Automatic conversion handled by scripts

## Data Format Requirements

Your JSON/CSV data should have:
- `joint_angles`: List of joint angles (length = num_joints)
- Gripper field(s): As specified in GripperConfig
- `actions`: List of action deltas (optional, auto-calculated if missing)

## Examples

See:
- `config/robot_config.py`: Predefined configs (dobot_e6, 7dof_robot, etc.)
- `config/example_7dof.py`: 7DOF examples
- `examples/dobot_e6/`: Dobot E6 specific example
