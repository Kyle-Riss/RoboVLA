"""
Robot Configuration Schema

This module defines the robot configuration structure for RoboVLA.
Supports different DOF, gripper formats, and action spaces.
"""

from dataclasses import dataclass
from typing import Literal, Optional
from pathlib import Path


@dataclass
class GripperConfig:
    """Gripper configuration."""
    # Gripper field name in JSON/CSV
    field_name: str = "gripper"
    
    # Gripper source fields (for CSV conversion)
    source_fields: list[str] = None  # e.g., ["gripper_tooldo1", "gripper_tooldo2"]
    
    # Gripper extraction method
    extraction_method: Literal["direct", "threshold", "max"] = "direct"
    
    # Threshold for binary gripper (if extraction_method == "threshold")
    threshold: float = 0.5
    
    # Gripper value range
    value_range: tuple[float, float] = (0.0, 1.0)  # (min, max)
    
    # Is gripper discrete (0/1) or continuous?
    discrete: bool = True
    
    def __post_init__(self):
        if self.source_fields is None:
            self.source_fields = [self.field_name]


@dataclass
class RobotConfig:
    """Robot configuration for RoboVLA."""
    
    # Robot name
    name: str
    
    # Number of joints (DOF)
    num_joints: int = 6
    
    # Gripper configuration
    gripper: Optional[GripperConfig] = None
    
    # Action space configuration
    use_dummy_dim: bool = True  # Add dummy dimension for DROID compatibility
    action_dim: int = None  # Auto-calculated if None
    
    # State space configuration
    state_dim: int = None  # Auto-calculated if None
    
    # Unit conversions
    joint_units: Literal["deg", "rad"] = "deg"  # Input joint units
    joint_output_units: Literal["deg", "rad"] = "rad"  # Output joint units
    
    # Position units (for TCP pose, if used)
    position_units: Literal["mm", "m"] = "mm"
    position_output_units: Literal["mm", "m"] = "m"
    
    # Data collection format
    data_collector: Optional[str] = None  # e.g., "Dobot-Arm-DataCollect"
    json_converter_path: Optional[str] = None  # Path to convert_to_json.py
    
    # Filter settings
    filter_robot_mode: Optional[int] = None  # Filter by robot_mode (None = no filter)
    
    # Dataset settings
    default_fps: int = 10
    image_size: tuple[int, int] = (224, 224)
    
    def __post_init__(self):
        """Calculate dimensions if not specified."""
        # Calculate state dim
        if self.state_dim is None:
            self.state_dim = self.num_joints
            if self.use_dummy_dim:
                self.state_dim += 1
            if self.gripper is not None:
                self.state_dim += 1
        
        # Calculate action dim
        if self.action_dim is None:
            self.action_dim = self.num_joints
            if self.use_dummy_dim:
                self.action_dim += 1
            if self.gripper is not None:
                self.action_dim += 1


# Predefined robot configurations
ROBOT_CONFIGS = {
    "dobot_e6": RobotConfig(
        name="dobot_e6",
        num_joints=6,
        gripper=GripperConfig(
            field_name="gripper",
            source_fields=["gripper_tooldo1"],
            extraction_method="threshold",
            threshold=0.5,
            discrete=True,
        ),
        use_dummy_dim=True,
        joint_units="deg",
        joint_output_units="rad",
        data_collector="Dobot-Arm-DataCollect",
        filter_robot_mode=7,
        default_fps=10,
    ),
    
    # Example: 7DOF robot
    "7dof_robot": RobotConfig(
        name="7dof_robot",
        num_joints=7,
        gripper=GripperConfig(
            field_name="gripper",
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
    ),
    
    # Example: Robot without gripper
    "6dof_no_gripper": RobotConfig(
        name="6dof_no_gripper",
        num_joints=6,
        gripper=None,
        use_dummy_dim=True,
        joint_units="deg",
        joint_output_units="rad",
        filter_robot_mode=None,
        default_fps=10,
    ),
}


def get_robot_config(robot_name: str) -> RobotConfig:
    """Get robot configuration by name."""
    if robot_name not in ROBOT_CONFIGS:
        raise ValueError(
            f"Unknown robot: {robot_name}. "
            f"Available: {list(ROBOT_CONFIGS.keys())}"
        )
    return ROBOT_CONFIGS[robot_name]


def create_custom_config(
    name: str,
    num_joints: int,
    gripper: Optional[GripperConfig] = None,
    **kwargs
) -> RobotConfig:
    """Create a custom robot configuration."""
    config = RobotConfig(name=name, num_joints=num_joints, gripper=gripper, **kwargs)
    ROBOT_CONFIGS[name] = config
    return config
