# RoboVLA Git Clone Checklist

This document outlines the checklist for using RoboVLA after cloning it in a new local environment.

## ✅ No Source Modification Required

**RoboVLA does not modify openpi's source code at all.**

- ✅ Config is dynamically registered at runtime (`config/pi0_e6_freeze_vlm.py`)
- ✅ openpi can be used as-is
- ✅ All changes exist only within RoboVLA

## 📋 Pre-Use Checklist for New Environment

### 1. Install Required Dependencies

```bash
# Install openpi (do not modify!)
git clone https://github.com/26kp/openpi.git
cd openpi
pip install -e .
cd ..

# Clone RoboVLA
git clone <your-repo>/RoboVLA.git
cd RoboVLA
```

### 2. Verify Directory Structure

```
your_workspace/
├── openpi/                    # ✅ Original as-is (not modified)
├── Dobot-Arm-DataCollect/     # Data collection (optional)
└── RoboVLA/                   # ✅ This project
```

### 3. Set Environment Variables (Optional)

```bash
# If openpi is not a sibling directory, set this
export OPENPI_PATH=/path/to/openpi

# Or add to PYTHONPATH
export PYTHONPATH=/path/to/openpi:$PYTHONPATH
```

### 4. Verify Config Registration

Config is automatically registered, but to verify manually:

```python
python -c "from config import register_config; register_config(); print('✅ Config registered')"
```

### 5. Verify Script Paths

- `scripts/data/convert_all_episodes_to_json.py`: Check Dobot-Arm-DataCollect path
- `scripts/training/run_dobot_e6_training.sh`: Check OPENPI_PATH or sibling directory

## 🚫 Things You Must Never Do

- ❌ Modify openpi's `src/openpi/training/config.py`
- ❌ Modify other openpi source files
- ❌ Use a fork or modified version of openpi

## ✅ Correct Usage

1. **Config Registration**: `config/pi0_e6_freeze_vlm.py` automatically registers at runtime
2. **Use Wrapper**: `train_pytorch_wrapper.py` automatically registers config
3. **Environment Variables**: Specify openpi location with OPENPI_PATH

## 📚 More Information

- **Usage**: `docs/USAGE.md`
- **Setup**: `docs/SETUP.md`
- **Config**: `config/pi0_e6_freeze_vlm.py`

## 🔍 Troubleshooting

### Config Not Found

```python
# Manual registration
from config import register_config
register_config()
```

### openpi Not Found

```bash
export OPENPI_PATH=/path/to/openpi
export PYTHONPATH=/path/to/openpi:$PYTHONPATH
```

### Script Path Error

Check the path in `scripts/data/convert_all_episodes_to_json.py` and modify if necessary.
