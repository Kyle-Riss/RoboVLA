"""
Universal JSON to LeRobot converter for any robot configuration.

This script uses robot_config.py to support different DOF, gripper formats, etc.
"""

import json
import pathlib
from typing import Any

import numpy as np
from PIL import Image
import tyro
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

import sys
from pathlib import Path

# Add RoboVLA root to path
robo_vla_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(robo_vla_root))

from config.robot_config import get_robot_config, RobotConfig


def deg_to_rad(deg: float) -> float:
    """Convert degrees to radians."""
    return deg * np.pi / 180.0


def mm_to_m(mm: float) -> float:
    """Convert millimeters to meters."""
    return mm * 0.001


def load_image(image_path: pathlib.Path, target_size: tuple[int, int] = (224, 224)) -> np.ndarray:
    """Load and resize image."""
    if not image_path.exists():
        print(f"  Warning: Image not found: {image_path}, using dummy image")
        return np.random.randint(0, 255, (*target_size, 3), dtype=np.uint8)
    
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        return np.array(img, dtype=np.uint8)
    except Exception as e:
        print(f"  Error loading image {image_path}: {e}")
        return np.random.randint(0, 255, (*target_size, 3), dtype=np.uint8)


def pad_state(
    joint_angles: list[float],
    gripper: float | None,
    config: RobotConfig
) -> np.ndarray:
    """Pad state to configured dimensions."""
    # Convert joint units
    if config.joint_units == "deg" and config.joint_output_units == "rad":
        joints = [deg_to_rad(j) for j in joint_angles]
    else:
        joints = joint_angles[:config.num_joints]
    
    state = joints.copy()
    
    # Add dummy dimension if needed
    if config.use_dummy_dim:
        state.append(0.0)
    
    # Add gripper if present
    if config.gripper is not None and gripper is not None:
        state.append(float(gripper))
    
    return np.array(state, dtype=np.float32)


def pad_actions(
    actions: list[float],
    config: RobotConfig
) -> np.ndarray:
    """Pad actions to configured dimensions."""
    # Extract joint deltas
    joint_deltas = actions[:config.num_joints]
    
    # Convert units
    if config.joint_units == "deg" and config.joint_output_units == "rad":
        joint_deltas = [deg_to_rad(d) for d in joint_deltas]
    
    action = joint_deltas.copy()
    
    # Add dummy dimension if needed
    if config.use_dummy_dim:
        action.append(0.0)
    
    # Extract gripper delta
    if config.gripper is not None:
        gripper_idx = config.num_joints
        if len(actions) > gripper_idx:
            gripper_delta = actions[gripper_idx]
        else:
            gripper_delta = 0.0
        action.append(gripper_delta)
    
    return np.array(action, dtype=np.float32)


def load_json_episode(
    json_path: pathlib.Path,
    images_base_dir: pathlib.Path,
    config: RobotConfig,
) -> tuple[list[dict[str, Any]], str]:
    """Load episode data from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episode_name = data['episode_name']
    prompt = data.get('prompt', 'manipulation task')
    frames = data['frames']
    
    # Filter by robot_mode if configured
    if config.filter_robot_mode is not None:
        original_count = len(frames)
        frames = [f for f in frames if f.get('robot_mode') == config.filter_robot_mode]
        print(f"  Filtered: {original_count} → {len(frames)} frames (mode=={config.filter_robot_mode})")
    
    # Extract gripper values
    for frame in frames:
        gripper_value = None
        if config.gripper is not None:
            # Try to get gripper from configured field
            if config.gripper.field_name in frame:
                gripper_value = frame[config.gripper.field_name]
            else:
                # Try source fields
                for source_field in config.gripper.source_fields:
                    if source_field in frame:
                        raw_value = frame[source_field]
                        # Apply extraction method
                        if config.gripper.extraction_method == "threshold":
                            gripper_value = 1.0 if float(raw_value) > config.gripper.threshold else 0.0
                        elif config.gripper.extraction_method == "direct":
                            gripper_value = float(raw_value)
                        elif config.gripper.extraction_method == "max":
                            gripper_value = max([float(frame.get(f, 0)) for f in config.gripper.source_fields])
                        break
        
        frame['_gripper'] = gripper_value
        
        # Add image path
        episode_dir = images_base_dir / episode_name
        image_path = episode_dir / "images" / frame.get('image_path', f"frame_{frame['frame_id']:06d}.jpg")
        frame['_image_path'] = image_path
    
    return frames, prompt


def convert_episode(
    json_path: pathlib.Path,
    images_base_dir: pathlib.Path,
    config: RobotConfig,
) -> dict[str, Any]:
    """Convert a single JSON episode to LeRobot format."""
    frames, prompt = load_json_episode(json_path, images_base_dir, config)
    
    if len(frames) == 0:
        return None
    
    # Prepare data arrays
    images = []
    states = []
    actions = []
    tasks = []
    
    prev_gripper = None
    for i, frame in enumerate(frames):
        # Load image
        img = load_image(frame['_image_path'], config.image_size)
        images.append(img)
        
        # Extract joint angles
        joint_angles = frame.get('joint_angles', [])
        if len(joint_angles) < config.num_joints:
            print(f"  Warning: Frame {i} has {len(joint_angles)} joints, expected {config.num_joints}")
            joint_angles.extend([0.0] * (config.num_joints - len(joint_angles)))
        
        # Extract gripper
        gripper = frame.get('_gripper')
        if gripper is None and config.gripper is not None:
            gripper = 0.0
        
        # Pad state
        state = pad_state(joint_angles, gripper, config)
        states.append(state)
        
        # Extract actions
        frame_actions = frame.get('actions', [])
        if len(frame_actions) == 0:
            # Calculate delta from previous frame
            if i > 0:
                prev_joints = frames[i-1].get('joint_angles', [])
                frame_actions = [joint_angles[j] - prev_joints[j] if j < len(prev_joints) else 0.0 
                                for j in range(config.num_joints)]
                if config.gripper is not None:
                    prev_gripper_val = frames[i-1].get('_gripper', 0.0) or 0.0
                    gripper_delta = (gripper or 0.0) - prev_gripper_val
                    frame_actions.append(gripper_delta)
            else:
                frame_actions = [0.0] * config.num_joints
                if config.gripper is not None:
                    frame_actions.append(0.0)
        
        # Pad actions
        action = pad_actions(frame_actions, config)
        actions.append(action)
        
        tasks.append(prompt)
        prev_gripper = gripper
    
    return {
        "image": np.array(images),
        "state": np.array(states),
        "action": np.array(actions),
        "task": tasks,
    }


@tyro.cli
def main(
    json_dir: str,
    images_base_dir: str,
    output_repo_id: str,
    robot_name: str = "dobot_e6",
    fps: int = 10,
    start_episode: int = 1,
    end_episode: int = 138,
):
    """Convert JSON episodes to LeRobot format using robot configuration."""
    json_path = Path(json_dir)
    images_base = Path(images_base_dir)
    
    # Get robot configuration
    config = get_robot_config(robot_name)
    print(f"Using robot config: {config.name}")
    print(f"  Joints: {config.num_joints}DOF")
    print(f"  State dim: {config.state_dim}")
    print(f"  Action dim: {config.action_dim}")
    print(f"  Gripper: {config.gripper.field_name if config.gripper else 'None'}")
    
    # Find JSON files
    json_files = sorted(json_path.glob("*.json"))
    if start_episode > 1 or end_episode < len(json_files):
        json_files = [f for f in json_files 
                     if start_episode <= int(f.stem) <= end_episode]
    
    print(f"Found {len(json_files)} JSON files")
    
    # Convert episodes
    episodes = []
    for json_file in json_files:
        print(f"Converting {json_file.name}...")
        episode_data = convert_episode(json_file, images_base, config)
        if episode_data is not None:
            episodes.append(episode_data)
    
    if len(episodes) == 0:
        print("No episodes to convert!")
        return
    
    # Create LeRobot dataset
    print(f"\nCreating LeRobot dataset: {output_repo_id}")
    dataset = LeRobotDataset(output_repo_id)
    
    # Add episodes
    for i, episode_data in enumerate(episodes):
        dataset.add_episode(episode_data)
        if (i + 1) % 10 == 0:
            print(f"  Added {i + 1}/{len(episodes)} episodes")
    
    print(f"\n✅ Conversion complete!")
    print(f"  Total episodes: {len(episodes)}")
    print(f"  Dataset: {output_repo_id}")


if __name__ == "__main__":
    main()
