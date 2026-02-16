"""
Dobot E6 VLM Freeze Config for RoboVLA

This config can be dynamically registered to openpi without modifying the original config.py.
Use this by setting OPENPI_CONFIG_EXTRA_PATH or importing before using openpi.training.config
"""

import os
from pathlib import Path

# Try to import openpi config classes
try:
    import openpi.models.pi0_config as pi0_config
    import openpi.training.config as _config
    from openpi.training.config import (
        TrainConfig,
        DataConfig,
        AssetsConfig,
        LeRobotE6DataConfig,
    )
    from openpi.training import weight_loaders
except ImportError:
    raise ImportError(
        "openpi is required. Install with: pip install -e <path-to-openpi>"
    )


def get_pi0_e6_freeze_vlm_config():
    """Get the pi0_e6_freeze_vlm config."""
    return TrainConfig(
        name="pi0_e6_freeze_vlm",
        model=pi0_config.Pi0Config(
            pi05=True,  # Compatible with pi05_droid checkpoint
            action_dim=32,  # pi05_droid uses 32D (8D data is padded)
            action_horizon=10,
        ),
        data=LeRobotE6DataConfig(
            repo_id="billy/dobot_e6_vla_dataset",  # Change to your dataset
            base_config=DataConfig(prompt_from_task=True),
            assets=AssetsConfig(
                assets_dir=None,  # Use config assets_dirs
                asset_id="billy/dobot_e6_vla_dataset",  # Change to your asset_id
            ),
        ),
        weight_loader=weight_loaders.CheckpointWeightLoader(
            "gs://openpi-assets/checkpoints/pi05_droid/params"
        ),
        pytorch_weight_path=os.path.expanduser(
            "~/.cache/openpi/openpi-assets/checkpoints/pi05_droid_pytorch"
        ),
        # Freeze VLM (PaliGemma) parameters, only train action head
        freeze_filter=pi0_config.Pi0Config(
            pi05=True,
            action_dim=32,
            action_horizon=10,
        ).get_freeze_filter(freeze_vlm=True),
        num_train_steps=20_000,
        batch_size=32,
    )


# Register config dynamically
def register_config():
    """Register pi0_e6_freeze_vlm config to openpi's config registry."""
    config = get_pi0_e6_freeze_vlm_config()
    
    # Add to _CONFIGS if it exists
    if hasattr(_config, "_CONFIGS"):
        _config._CONFIGS[config.name] = config
    else:
        # Try to add to the config dict
        if hasattr(_config, "get_config"):
            # Monkey patch get_config to include our config
            original_get_config = _config.get_config
            
            def patched_get_config(name: str):
                if name == "pi0_e6_freeze_vlm":
                    return config
                return original_get_config(name)
            
            _config.get_config = patched_get_config
    
    return config


# Auto-register when imported
if __name__ != "__main__":
    try:
        register_config()
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to auto-register config: {e}. You may need to register manually.")
