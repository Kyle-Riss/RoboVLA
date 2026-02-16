"""
Wrapper for train_pytorch.py that registers RoboVLA config before training.

This allows using pi0_e6_freeze_vlm config without modifying openpi source.
"""

import sys
from pathlib import Path

# Add RoboVLA config to path
robo_vla_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(robo_vla_root))

# Register config before importing openpi training code
try:
    from config import register_config
    register_config()
    print("✅ Registered pi0_e6_freeze_vlm config")
except Exception as e:
    print(f"⚠️  Warning: Failed to register config: {e}")
    print("   Make sure config/pi0_e6_freeze_vlm.py exists")

# Now import and run the original train_pytorch
# This assumes openpi is installed or in PYTHONPATH
from openpi.scripts.train_pytorch import main

if __name__ == "__main__":
    main()
