#!/usr/bin/env python3
"""
Setup and verify RoboVLA environment.

This script checks dependencies and sets up paths.
"""

import sys
from pathlib import Path

robo_vla_root = Path(__file__).parent.parent
sys.path.insert(0, str(robo_vla_root))

from config.env_config import get_env_config


def main():
    """Setup and verify environment."""
    env_config = get_env_config()
    
    print("RoboVLA Environment Setup")
    print("=" * 50)
    print(f"RoboVLA root: {env_config.robo_vla_root}")
    print(f"OpenPI path: {env_config.openpi_path or 'Not found'}")
    print(f"Data collector: {env_config.data_collector_path or 'Not found'}")
    print()
    
    # Setup PYTHONPATH
    paths = env_config.setup_pythonpath()
    print("PYTHONPATH setup:")
    for p in paths:
        print(f"  - {p}")
    print()
    
    # Verify setup
    print("Verification:")
    results = env_config.verify_setup()
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    # Check config registration (only if openpi is available)
    print()
    print("Config registration:")
    if results.get("openpi_import", False):
        try:
            from config import register_config
            register_config()
            print("  ✅ Config registered")
            
            import openpi.training.config as _config
            config = _config.get_config("pi0_e6_freeze_vlm")
            print(f"  ✅ Config found: {config.name}")
        except Exception as e:
            print(f"  ❌ Config error: {e}")
    else:
        print("  ⚠️  Skipped (openpi not available)")
        print("     Install openpi to enable config registration")
    
    print()
    if all(results.values()):
        print("✅ Environment setup complete!")
    else:
        print("⚠️  Some dependencies missing. See docs/SETUP.md for details.")


if __name__ == "__main__":
    main()
