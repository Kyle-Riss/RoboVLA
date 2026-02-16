# Converting Dobot E6 Data to openpi Format

This guide explains how to convert data collected from the [Dobot-Arm-DataCollect](https://github.com/Kyle-Riss/Dobot-Arm-DataCollect) repository to LeRobot format for openpi training.

## Data Format

Dobot-Arm-DataCollect stores data in the following structure:

```
vla_dataset/
└── vla_auto_YYYYMMDD_HHMMSS/
    ├── images/
    │   ├── frame_000000.jpg    # 640x480 RGB image
    │   ├── frame_000001.jpg
    │   └── ...
    ├── robot_data.csv          # Robot state data
    ├── dataset.npy             # NumPy array format data
    └── metadata.txt            # Metadata
```

### robot_data.csv Format

```csv
frame_id,timestamp,image_path,j1,j2,j3,j4,j5,j6,x,y,z,rx,ry,rz,gripper_tooldo1,gripper_tooldo2,robot_mode
0,1769415506.1058023,frame_000000.jpg,-76.4,4.89,-13.1,2.53,83.28,108.06,...,0,0,7
```

- `j1-j6`: 6 joint angles (in degrees)
- `x,y,z,rx,ry,rz`: TCP pose (Cartesian coordinates)
- `gripper_tooldo1`, `gripper_tooldo2`: Gripper state (0 or 1)

### dataset.npy Format

Each item is a dict:
```python
{
    'frame_id': 0,
    'timestamp': 1769415506.1058023,
    'image_path': 'frame_000000.jpg',
    'joint_angles': [j1, j2, j3, j4, j5, j6],
    'tcp_pose': [x, y, z, rx, ry, rz],
    'gripper_tooldo1': 0,
    'gripper_tooldo2': 0,
    'robot_mode': 7
}
```

## Conversion Method

### Step 1: Data Conversion

```bash
cd /path/to/RoboVLA

python examples/dobot_e6/convert_json_to_lerobot.py \
    --json_dir /path/to/json_output \
    --images_base_dir /path/to/VLA_DATASET \
    --output_repo_id your_hf_username/dobot_e6_dataset \
    --fps 10
```

**Parameter Description:**
- `--json_dir`: Path to JSON output directory
- `--images_base_dir`: Base directory containing episode image folders
- `--output_repo_id`: HuggingFace repo ID for output dataset
- `--fps`: Dataset framerate (default: 10)

**Note:** For universal conversion that works with any robot configuration, use:
```bash
python scripts/data/convert_json_to_lerobot_universal.py \
    --robot_name dobot_e6 \
    --json_dir /path/to/json_output \
    --images_base_dir /path/to/VLA_DATASET \
    --output_repo_id your_hf_username/dobot_e6_dataset \
    --fps 10
```

### Step 2: Upload to HuggingFace Hub (Optional)

```python
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

dataset = LeRobotDataset("your_hf_username/dobot_e6_dataset")
dataset.push_to_hub(
    tags=["dobot", "e6", "robot", "manipulation"],
    private=False,
    push_videos=True,
    license="apache-2.0",
)
```

## Converted Data Format

The converted LeRobot dataset follows this format:

- **image**: 224x224x3 RGB image
- **state**: 7-dimensional array [j1, j2, j3, j4, j5, j6, gripper]
- **actions**: 8-dimensional array [Δj1, Δj2, Δj3, Δj4, Δj5, Δj6, dummy=0, Δgripper]
- **task**: Task description string

## Notes

1. **Image Path**: Image files must be in the `images/` directory
2. **Gripper Processing**: Uses `gripper_tooldo1` (if > 0.5, gripper=1.0, else 0.0)
3. **Image Resize**: 640x480 images are automatically resized to 224x224
4. **Unit Conversion**: Joint angles are stored in degrees and automatically converted to radians for actions

## Next Steps

After data conversion, to proceed with openpi training:

1. Add VLM freeze configuration (if needed)
2. Create training config
3. Compute normalization statistics
4. Start training

For more details, refer to the main README.
