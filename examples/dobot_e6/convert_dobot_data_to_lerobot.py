"""
Dobot-Arm-DataCollect 형식의 데이터를 LeRobot 형식으로 변환하는 스크립트.

Dobot-Arm-DataCollect 저장소에서 생성된 VLA 데이터셋을 openpi 학습용 LeRobot 형식으로 변환합니다.

사용법:
    uv run examples/dobot_e6/convert_dobot_data_to_lerobot.py \
        --data_dir /path/to/Dobot-Arm-DataCollect/vla_dataset \
        --output_repo_id your_hf_username/dobot_e6_dataset \
        --fps 10

데이터 형식:
    Dobot-Arm-DataCollect는 다음 구조로 데이터를 저장합니다:
    vla_dataset/
        vla_auto_YYYYMMDD_HHMMSS/
            images/
                frame_000000.jpg
                frame_000001.jpg
                ...
            robot_data.csv
            dataset.npy
            metadata.txt
"""

import json
import pathlib
from typing import Any

import numpy as np
from PIL import Image
import tyro
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# E6 로봇은 7DOF (6개 관절 + 1개 gripper)
# Dobot-Arm-DataCollect는 gripper_tooldo1, gripper_tooldo2를 사용
E6_ACTION_DIM = 7
E6_STATE_DIM = 7


def load_dobot_csv(csv_path: pathlib.Path) -> list[dict[str, Any]]:
    """Dobot-Arm-DataCollect의 CSV 파일을 로드합니다.
    
    CSV 형식:
        frame_id,timestamp,image_path,j1,j2,j3,j4,j5,j6,x,y,z,rx,ry,rz,
        gripper_tooldo1,gripper_tooldo2,robot_mode
    """
    import csv
    
    data = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 관절 각도 (j1-j6)
            joints = [float(row[f'j{i}']) for i in range(1, 7)]
            
            # Gripper: gripper_tooldo2는 석션 그리퍼로 0,1로만 작동
            # gripper_tooldo2를 그대로 사용 (이미 0 또는 1)
            gripper2 = float(row.get('gripper_tooldo2', 0))
            gripper = 1.0 if gripper2 > 0.5 else 0.0
            
            # Action: 관절 각도 + gripper (7DOF)
            action = np.array(joints + [gripper], dtype=np.float32)
            
            # State: 관절 각도 + gripper (7DOF)
            state = np.array(joints + [gripper], dtype=np.float32)
            
            data.append({
                'action': action,
                'state': state,
                'image_path': row['image_path'],
                'timestamp': float(row['timestamp']),
                'frame_id': int(row['frame_id']),
            })
    
    return data


def load_dobot_npy(npy_path: pathlib.Path) -> list[dict[str, Any]]:
    """Dobot-Arm-DataCollect의 NPY 파일을 로드합니다.
    
    NPY 형식:
        각 항목은 dict:
        {
            'frame_id': int,
            'timestamp': float,
            'image_path': str,
            'joint_angles': [j1, j2, j3, j4, j5, j6],
            'tcp_pose': [x, y, z, rx, ry, rz],
            'gripper_tooldo1': int,
            'gripper_tooldo2': int,
            'robot_mode': int
        }
    """
    data = np.load(npy_path, allow_pickle=True)
    
    episodes = []
    for item in data:
        joints = item['joint_angles'][:6]  # 6개 관절
        
        # Gripper 처리: gripper_tooldo2는 석션 그리퍼로 0,1로만 작동
        gripper2 = float(item.get('gripper_tooldo2', 0))
        gripper = 1.0 if gripper2 > 0.5 else 0.0
        
        # Action과 State
        action = np.array(list(joints) + [gripper], dtype=np.float32)
        state = np.array(list(joints) + [gripper], dtype=np.float32)
        
        episodes.append({
            'action': action,
            'state': state,
            'image_path': item['image_path'],
            'timestamp': float(item['timestamp']),
            'frame_id': int(item['frame_id']),
        })
    
    return episodes


def load_image(image_path: pathlib.Path, images_dir: pathlib.Path) -> np.ndarray:
    """이미지를 로드하고 224x224로 리사이즈합니다."""
    full_path = images_dir / image_path
    
    if not full_path.exists():
        # 이미지가 없으면 더미 이미지 생성
        print(f"  Warning: Image not found: {full_path}, using dummy image")
        return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    try:
        img = Image.open(full_path)
        # RGB로 변환
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # 224x224로 리사이즈
        img = img.resize((224, 224), Image.Resampling.LANCZOS)
        return np.array(img, dtype=np.uint8)
    except Exception as e:
        print(f"  Error loading image {full_path}: {e}")
        return np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)


def main(
    data_dir: str,
    output_repo_id: str = "your_hf_username/dobot_e6_dataset",
    fps: int = 10,
    task_description: str = "pick and place",
    use_npy: bool = True,  # True면 dataset.npy 사용, False면 robot_data.csv 사용
):
    """
    Dobot-Arm-DataCollect 형식의 데이터를 LeRobot 형식으로 변환합니다.
    
    Args:
        data_dir: Dobot-Arm-DataCollect의 vla_dataset 디렉토리 경로
        output_repo_id: 출력 데이터셋의 HuggingFace repo ID
        fps: 데이터셋의 프레임레이트
        task_description: 작업 설명 (프롬프트로 사용)
        use_npy: True면 dataset.npy 사용, False면 robot_data.csv 사용
    """
    data_path = pathlib.Path(data_dir)
    
    if not data_path.exists():
        raise ValueError(f"Data directory not found: {data_dir}")
    
    # LeRobot 데이터셋 생성
    dataset = LeRobotDataset.create(
        repo_id=output_repo_id,
        robot_type="dobot_e6",
        fps=fps,
        features={
            "image": {
                "dtype": "image",
                "shape": (224, 224, 3),
                "names": ["height", "width", "channel"],
            },
            "state": {
                "dtype": "float32",
                "shape": (E6_STATE_DIM,),
                "names": ["state"],
            },
            "actions": {
                "dtype": "float32",
                "shape": (E6_ACTION_DIM,),
                "names": ["actions"],
            },
        },
        image_writer_threads=10,
        image_writer_processes=5,
    )
    
    # vla_auto_* 디렉토리 찾기
    episode_dirs = sorted([d for d in data_path.iterdir() if d.is_dir() and d.name.startswith("vla_auto_")])
    
    if len(episode_dirs) == 0:
        raise ValueError(f"No episode directories found in {data_dir}")
    
    print(f"Found {len(episode_dirs)} episodes")
    
    # 각 에피소드 처리
    for episode_dir in episode_dirs:
        print(f"\nProcessing {episode_dir.name}...")
        
        images_dir = episode_dir / "images"
        
        # 데이터 로드
        if use_npy:
            npy_path = episode_dir / "dataset.npy"
            if npy_path.exists():
                try:
                    episode_data = load_dobot_npy(npy_path)
                    print(f"  Loaded {len(episode_data)} frames from dataset.npy")
                except Exception as e:
                    print(f"  Error loading NPY: {e}, trying CSV...")
                    use_npy = False
        
        if not use_npy:
            csv_path = episode_dir / "robot_data.csv"
            if csv_path.exists():
                try:
                    episode_data = load_dobot_csv(csv_path)
                    print(f"  Loaded {len(episode_data)} frames from robot_data.csv")
                except Exception as e:
                    print(f"  Error loading CSV: {e}, skipping episode")
                    continue
            else:
                print(f"  No robot_data.csv found, skipping episode")
                continue
        
        if len(episode_data) == 0:
            print(f"  Skipping empty episode")
            continue
        
        # 각 프레임 추가
        for frame_data in episode_data:
            # 이미지 로드
            image = load_image(frame_data['image_path'], images_dir)
            
            # LeRobot 데이터셋에 추가
            dataset.add_frame(
                {
                    "image": image,
                    "state": frame_data["state"],
                    "actions": frame_data["action"],
                    "task": task_description,
                }
            )
        
        # 에피소드 저장
        dataset.save_episode()
        print(f"  Saved episode with {len(episode_data)} frames")
    
    print(f"\n✅ Dataset conversion complete!")
    print(f"Dataset saved to: {dataset.repo_path}")
    print(f"\nTo push to HuggingFace Hub, run:")
    print(f"  from lerobot.common.datasets.lerobot_dataset import LeRobotDataset")
    print(f"  dataset = LeRobotDataset('{output_repo_id}')")
    print(f"  dataset.push_to_hub(tags=['dobot', 'e6', 'robot'], private=False)")


if __name__ == "__main__":
    tyro.cli(main)
