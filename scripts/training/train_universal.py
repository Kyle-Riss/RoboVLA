"""
Universal training script that works with any robot configuration.

This script automatically registers config and handles different robot setups.
"""

import sys
import os
from pathlib import Path

# Add RoboVLA root to path
robo_vla_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(robo_vla_root))

# Register RoboVLA config before importing openpi
try:
    from config import register_config
    register_config()
    print("✅ Registered RoboVLA config")
except Exception as e:
    print(f"⚠️  Warning: Failed to register config: {e}")

# Now import openpi training code
try:
    import openpi.training.config as _config
    import openpi.scripts.train_pytorch as train_pytorch
except ImportError:
    print("Error: openpi not found. Install with: pip install -e <path-to-openpi>")
    print("Or set PYTHONPATH: export PYTHONPATH=/path/to/openpi:$PYTHONPATH")
    sys.exit(1)


def main():
    """Main training entry point."""
    # Check if config is registered
    try:
        config = _config.get_config("pi0_e6_freeze_vlm")
        print(f"✅ Config found: {config.name}")
    except KeyError:
        print("❌ Config 'pi0_e6_freeze_vlm' not found!")
        print("   Make sure config/pi0_e6_freeze_vlm.py exists and is registered.")
        sys.exit(1)
    
    # Run training using openpi's train_pytorch
    # This will use command line arguments
    train_pytorch.main()


if __name__ == "__main__":
    main()
