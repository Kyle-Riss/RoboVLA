"""
RoboVLA Config Module

This module provides config registration for RoboVLA without modifying openpi source.
"""

# Lazy import to avoid requiring openpi at import time
from .robot_config import (
    RobotConfig,
    GripperConfig,
    get_robot_config,
    create_custom_config,
    ROBOT_CONFIGS,
)

# Lazy import for openpi-dependent config
def get_pi0_e6_freeze_vlm_config():
    """Lazy import of pi0_e6_freeze_vlm config."""
    from .pi0_e6_freeze_vlm import get_pi0_e6_freeze_vlm_config as _get_config
    return _get_config()

def register_config():
    """Lazy import and registration of config."""
    from .pi0_e6_freeze_vlm import register_config as _register
    return _register()

__all__ = [
    "get_pi0_e6_freeze_vlm_config",
    "register_config",
    "RobotConfig",
    "GripperConfig",
    "get_robot_config",
    "create_custom_config",
    "ROBOT_CONFIGS",
]
