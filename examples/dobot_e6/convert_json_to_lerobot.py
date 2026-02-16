"""
JSON 형식의 Dobot E6 데이터를 DROID 스타일 LeRobot 형식으로 변환하는 스크립트.

이 스크립트는 convert_to_json.py로 생성한 JSON 파일을 읽어서
openpi 학습용 LeRobot 데이터셋으로 변환합니다.

주요 변환:
- State: 6 joint + 1 dummy + 1 gripper = 8D (DROID 호환)
- Actions: 6 Δjoint + 1 dummy + 1 Δgripper = 8D (DROID 호환)
- 단위 변환: deg → rad, mm → m
- robot_mode 필터링 (기본값: mode==7만 사용)
- DROID 스타일 키로 저장

사용법:
    uv run examples/dobot_e6/convert_json_to_lerobot.py \
        --json_dir /path/to/json_output \
        --images_base_dir /path/to/vla_dataset \
        --output_repo_id your_hf_username/dobot_e6_dataset \
        --fps 10 \
        --filter_mode 7
"""

import json
import pathlib
from typing import Any

import numpy as np
from PIL import Image
import tyro
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# 단위 변환 상수
DEG_TO_RAD = np.pi / 180.0
MM_TO_M = 0.001

# DROID 호환을 위한 차원
STATE_DIM = 8  # 6 joint + 1 dummy + 1 gripper
ACTION_DIM = 8  # 6 Δjoint + 1 dummy + 1 Δgripper


def deg_to_rad(deg: float) -> float:
    """도(degree)를 라디안(radian)으로 변환."""
    return deg * DEG_TO_RAD


def mm_to_m(mm: float) -> float:
    """밀리미터를 미터로 변환."""
    return mm * MM_TO_M


def load_image(image_path: pathlib.Path) -> np.ndarray:
    """이미지를 로드하고 224x224로 리사이즈합니다."""
    if not image_path.exists():
        print(f"  Warning: Image not found: {image_path}, using dummy image")
        return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    try:
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        return np.array(img, dtype=np.uint8)
    except Exception as e:
        print(f"  Error loading image {image_path}: {e}")
        return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)


def pad_state(joint_angles: list[float], gripper: float) -> np.ndarray:
    """State를 8D로 패딩: [j1..j6, j_dummy=0, gripper]."""
    joints_rad = [deg_to_rad(j) for j in joint_angles]
    return np.array(joints_rad + [0.0, gripper], dtype=np.float32)


def pad_actions(actions: list[float]) -> np.ndarray:
    """Actions를 8D로 패딩: [Δj1..Δj6, Δj_dummy=0, Δgripper].
    
    입력 actions는 7D (6 Δjoint + 1 Δgripper)를 가정.
    deg → rad 변환도 함께 수행.
    """
    if len(actions) == 7:
        # 6개 joint delta를 rad로 변환
        joint_deltas_rad = [deg_to_rad(actions[i]) for i in range(6)]
        gripper_delta = actions[6]  # gripper는 이미 0/1이므로 변환 불필요
        return np.array(joint_deltas_rad + [0.0, gripper_delta], dtype=np.float32)
    elif len(actions) == 8:
        # 이미 8D인 경우 (joint만 rad 변환)
        joint_deltas_rad = [deg_to_rad(actions[i]) for i in range(6)]
        return np.array(joint_deltas_rad + [0.0, actions[7]], dtype=np.float32)
    else:
        raise ValueError(f"Unexpected actions dimension: {len(actions)}")


def load_json_episode(
    json_path: pathlib.Path,
    images_base_dir: pathlib.Path,
    filter_mode: int | None = 7,
) -> tuple[list[dict[str, Any]], str]:
    """
    JSON 파일에서 에피소드 데이터를 로드합니다.
    
    Args:
        json_path: JSON 파일 경로
        images_base_dir: 이미지가 있는 base 디렉토리 (vla_dataset)
        filter_mode: robot_mode 필터 (None이면 필터링 안 함)
    
    Returns:
        (frames, prompt) 튜플
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    episode_name = data['episode_name']
    prompt = data.get('prompt', 'pick and place')
    frames = data['frames']
    
    # robot_mode 필터링
    if filter_mode is not None:
        original_count = len(frames)
        frames = [f for f in frames if f.get('robot_mode') == filter_mode]
        print(f"  Filtered: {original_count} → {len(frames)} frames (mode=={filter_mode})")
    
    # 이미지 경로 구성
    episode_dir = images_base_dir / episode_name
    
    # 각 프레임에 이미지 경로 추가
    for frame in frames:
        image_path = episode_dir / "images" / frame['image_path']
        frame['_image_path'] = image_path
    
    return frames, prompt


def main(
    json_dir: str,
    images_base_dir: str,
    output_repo_id: str = "your_hf_username/dobot_e6_dataset",
    fps: int = 10,
    filter_mode: int | None = 7,
    robot_type: str = "dobot_e6",
):
    """
    JSON 파일들을 DROID 스타일 LeRobot 형식으로 변환합니다.
    
    Args:
        json_dir: JSON 파일들이 있는 디렉토리
        images_base_dir: 이미지가 있는 base 디렉토리 (vla_dataset)
        output_repo_id: 출력 데이터셋의 HuggingFace repo ID
        fps: 데이터셋의 프레임레이트
        filter_mode: robot_mode 필터 (None이면 필터링 안 함, 기본값: 7)
        robot_type: 로봇 타입 (기본값: dobot_e6)
    """
    json_path = pathlib.Path(json_dir)
    images_base = pathlib.Path(images_base_dir)
    
    if not json_path.exists():
        raise ValueError(f"JSON directory not found: {json_dir}")
    
    # JSON 파일 찾기
    json_files = sorted(json_path.glob("*.json"))
    
    if len(json_files) == 0:
        raise ValueError(f"No JSON files found in {json_dir}")
    
    print(f"Found {len(json_files)} JSON files")
    print(f"Filter mode: {filter_mode}")
    print(f"Output repo: {output_repo_id}")
    
    # LeRobot 데이터셋 생성 (DROID 스타일)
    dataset = LeRobotDataset.create(
        repo_id=output_repo_id,
        robot_type=robot_type,
        fps=fps,
        features={
            "exterior_image_1_left": {
                "dtype": "image",
                "shape": (224, 224, 3),
                "names": ["height", "width", "channel"],
            },
            "wrist_image_left": {
                "dtype": "image",
                "shape": (224, 224, 3),
                "names": ["height", "width", "channel"],
            },
            "joint_position": {
                "dtype": "float32",
                "shape": (STATE_DIM,),  # 8D (6 joint + 1 dummy + 1 gripper)
                "names": ["joint"],
            },
            "gripper_position": {
                "dtype": "float32",
                "shape": (1,),
                "names": ["gripper"],
            },
            "actions": {
                "dtype": "float32",
                "shape": (ACTION_DIM,),  # 8D (6 Δjoint + 1 dummy + 1 Δgripper)
                "names": ["actions"],
            },
        },
        image_writer_threads=10,
        image_writer_processes=5,
    )
    
    total_frames = 0
    
    # 각 JSON 파일 처리
    for json_file in json_files:
        print(f"\nProcessing {json_file.name}...")
        
        try:
            frames, prompt = load_json_episode(json_file, images_base, filter_mode=filter_mode)
            
            if len(frames) == 0:
                print(f"  Skipping (no frames after filtering)")
                continue
            
            # 각 프레임을 LeRobot 형식으로 변환하여 추가
            for frame in frames:
                # 이미지 로드
                base_image = load_image(frame['_image_path'])
                wrist_image = base_image  # 동일 이미지 사용 (wrist 카메라 없음)
                
                # State: 8D로 패딩 (deg → rad 변환)
                joint_position = pad_state(frame['joint_angles'], frame['gripper'])
                
                # Gripper position (별도 필드)
                gripper_position = np.array([frame['gripper']], dtype=np.float32)
                
                # Actions: 8D로 패딩 (deg → rad 변환)
                actions = pad_actions(frame['actions'])
                
                # LeRobot에 추가 (DROID 스타일 키 사용)
                dataset.add_frame(
                    {
                        "exterior_image_1_left": base_image,
                        "wrist_image_left": wrist_image,
                        "joint_position": joint_position,
                        "gripper_position": gripper_position,
                        "actions": actions,
                        "task": prompt,  # LeRobot은 'task' 키 사용
                    }
                )
                total_frames += 1
            
            # 에피소드 저장
            dataset.save_episode()
            print(f"  ✓ Saved episode with {len(frames)} frames")
            
        except Exception as e:
            print(f"  Error processing {json_file.name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n✅ Dataset conversion complete!")
    print(f"Total frames: {total_frames}")
    print(f"Dataset repo: {output_repo_id}")
    print(f"Dataset saved to: ~/.cache/lerobot/{output_repo_id}/")
    print(f"\nTo push to HuggingFace Hub, run:")
    print(f"  from lerobot.common.datasets.lerobot_dataset import LeRobotDataset")
    print(f"  dataset = LeRobotDataset('{output_repo_id}')")
    print(f"  dataset.push_to_hub(tags=['dobot', 'e6', 'robot'], private=False)")


if __name__ == "__main__":
    tyro.cli(main)
