"""
Environment configuration for RoboVLA.

Handles paths, dependencies, and environment setup.
"""

import os
from pathlib import Path
from typing import Optional


class EnvConfig:
    """Environment configuration."""
    
    def __init__(self):
        self.robo_vla_root = self._find_robo_vla_root()
        self.openpi_path = self._find_openpi_path()
        self.data_collector_path = self._find_data_collector_path()
    
    def _find_robo_vla_root(self) -> Path:
        """Find RoboVLA root directory."""
        # Check if ROBOVLA_ROOT is set
        if "ROBOVLA_ROOT" in os.environ:
            return Path(os.environ["ROBOVLA_ROOT"]).resolve()
        
        # Try to find from current file location
        current_file = Path(__file__).resolve()
        # config/env_config.py -> RoboVLA root
        if current_file.parent.name == "config":
            return current_file.parent.parent.resolve()
        
        # Fallback: current working directory
        return Path.cwd()
    
    def _find_openpi_path(self) -> Optional[Path]:
        """Find openpi installation."""
        # Check environment variable
        if "OPENPI_PATH" in os.environ:
            path = Path(os.environ["OPENPI_PATH"]).resolve()
            if path.exists():
                return path
        
        # Check sibling directory
        sibling = self.robo_vla_root.parent / "openpi"
        if sibling.exists():
            return sibling.resolve()
        
        # Check if openpi is installed as package
        try:
            import openpi
            if hasattr(openpi, "__file__"):
                return Path(openpi.__file__).parent.parent.resolve()
        except ImportError:
            pass
        
        return None
    
    def _find_data_collector_path(self) -> Optional[Path]:
        """Find data collector (e.g., Dobot-Arm-DataCollect)."""
        # Check environment variable
        if "DATA_COLLECTOR_PATH" in os.environ:
            path = Path(os.environ["DATA_COLLECTOR_PATH"]).resolve()
            if path.exists():
                return path
        
        # Check common names
        for name in ["Dobot-Arm-DataCollect", "dobot-arm-datacollect"]:
            sibling = self.robo_vla_root.parent / name
            if sibling.exists():
                return sibling.resolve()
        
        return None
    
    def setup_pythonpath(self):
        """Setup PYTHONPATH for RoboVLA and openpi."""
        paths = [str(self.robo_vla_root)]
        
        if self.openpi_path:
            paths.insert(0, str(self.openpi_path))
        
        current_path = os.environ.get("PYTHONPATH", "")
        if current_path:
            paths.append(current_path)
        
        os.environ["PYTHONPATH"] = ":".join(paths)
        return paths
    
    def verify_setup(self) -> dict[str, bool]:
        """Verify environment setup."""
        results = {
            "robo_vla_root": self.robo_vla_root.exists(),
            "openpi": self.openpi_path is not None and self.openpi_path.exists() if self.openpi_path else False,
            "data_collector": self.data_collector_path is not None and self.data_collector_path.exists() if self.data_collector_path else False,
        }
        
        # Check openpi import
        try:
            import openpi
            results["openpi_import"] = True
        except ImportError:
            results["openpi_import"] = False
        
        return results


# Global instance
_env_config = EnvConfig()


def get_env_config() -> EnvConfig:
    """Get global environment configuration."""
    return _env_config
