"""
Example: Adding a 7DOF robot configuration

This shows how to add a custom robot configuration.
"""

from config.robot_config import RobotConfig, GripperConfig, create_custom_config

# Example 1: 7DOF with continuous gripper
robot_7dof_continuous = create_custom_config(
    name="7dof_continuous_gripper",
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
    default_fps=10,
)

# Example 2: 7DOF with binary gripper
robot_7dof_binary = create_custom_config(
    name="7dof_binary_gripper",
    num_joints=7,
    gripper=GripperConfig(
        field_name="gripper",
        source_fields=["gripper_open", "gripper_close"],
        extraction_method="max",  # Use max of open/close
        discrete=True,
    ),
    use_dummy_dim=True,
    joint_units="deg",
    joint_output_units="rad",
    filter_robot_mode=None,
)

# Example 3: 7DOF without gripper
robot_7dof_no_gripper = create_custom_config(
    name="7dof_no_gripper",
    num_joints=7,
    gripper=None,
    use_dummy_dim=True,
    joint_units="deg",
    joint_output_units="rad",
)

# To use these configs:
# python scripts/data/convert_json_to_lerobot_universal.py \
#     --robot_name 7dof_continuous_gripper \
#     ...
