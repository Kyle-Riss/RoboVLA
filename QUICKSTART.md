# RoboVLA Quick Start

## 1. Clone & Setup

```bash
# Clone RoboVLA
git clone <your-repo>/RoboVLA.git
cd RoboVLA

# Install openpi (don't modify it!)
git clone https://github.com/26kp/openpi.git ../openpi
cd ../openpi && pip install -e . && cd ../RoboVLA
```

## 2. Verify Setup

```bash
# Check config registration
python -c "from config import register_config; register_config(); print('✅ OK')"

# Check openpi import
python -c "import openpi; print('✅ openpi found')"
```

## 3. Run Training

```bash
# Set paths (if needed)
export OPENPI_PATH=$(pwd)/../openpi

# Run training
bash scripts/training/run_dobot_e6_training.sh
```

## ✅ That's it!

**No modification to openpi source required!**

See `docs/USAGE.md` for detailed usage.
