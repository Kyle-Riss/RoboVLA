#!/usr/bin/env python3
"""
체크포인트별 추론 action 통계를 비교합니다.

검증 없이 학습할 때, 베스트 체크포인트 선택을 위해:
- 동일한 테스트 세트로 각 체크포인트 추론
- action mean, std, max(abs) 로그 → action 스케일 비교
- 값이 과도하게 커지면(과격/편향) 위험 신호

사용법:
    # 단일 체크포인트
    python scripts/eval_checkpoint_actions.py --checkpoint_dir checkpoints/.../1000

    # 여러 체크포인트 비교
    python scripts/eval_checkpoint_actions.py --checkpoint_dirs 1000 2000 5000 10000 15000 20000 \\
        --checkpoint_base checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_20k
"""

import argparse
from pathlib import Path

import numpy as np
import tyro

import openpi.training.config as _config
import openpi.policies.policy_config as _policy_config
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset


def eval_checkpoint(checkpoint_dir: str, config_name: str = "pi0_e6_freeze_vlm", num_samples: int = 50):
    """단일 체크포인트에서 추론 action 통계를 계산합니다."""
    config = _config.get_config(config_name)
    policy = _policy_config.create_trained_policy(config, checkpoint_dir, pytorch_device="cuda")

    # 고정 테스트 세트: 데이터셋 앞부분
    repo_id = config.data.repo_id
    dataset = LeRobotDataset(repo_id)

    all_actions = []
    step = max(1, len(dataset) // num_samples)
    indices = list(range(0, min(len(dataset), num_samples * step), step))[:num_samples]

    for idx in indices:
        sample = dataset[idx]
        # LeRobot -> DROID 형식 obs (policy 입력)
        task = sample.get("task", "pick and place") or "pick and place"
        if isinstance(task, bytes):
            task = task.decode("utf-8", errors="replace")
        obs = {
            "observation/exterior_image_1_left": np.array(sample["exterior_image_1_left"]),
            "observation/wrist_image_left": np.array(sample["wrist_image_left"]),
            "observation/joint_position": np.array(sample["joint_position"]),
            "observation/gripper_position": np.array(sample["gripper_position"]).reshape(-1),
            "prompt": task,
        }
        out = policy.infer(obs)
        act = out["actions"]  # (action_horizon, action_dim)
        all_actions.append(act[:, :8])  # 8D만 사용 (Dobot)

    all_actions = np.concatenate(all_actions, axis=0)
    return {
        "mean": float(np.abs(all_actions).mean()),
        "std": float(all_actions.std()),
        "max": float(np.abs(all_actions).max()),
        "mean_per_dim": all_actions.mean(axis=0).tolist(),
        "std_per_dim": all_actions.std(axis=0).tolist(),
    }


def main(
    checkpoint_dir: str | None = None,
    checkpoint_base: str = "checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_20k",
    checkpoint_dirs: list[str] | None = None,
    config_name: str = "pi0_e6_freeze_vlm",
    num_samples: int = 50,
):
    """체크포인트별 action 통계를 출력합니다."""
    if checkpoint_dir:
        dirs = [Path(checkpoint_dir).resolve()]
    elif checkpoint_dirs:
        base = Path(checkpoint_base).resolve()
        dirs = [base / d for d in checkpoint_dirs if (base / d).exists()]
    else:
        raise ValueError("--checkpoint_dir 또는 --checkpoint_dirs 필요")

    print("Checkpoint\tact_mean\tact_std\tact_max")
    print("-" * 55)
    results = {}
    for d in sorted(dirs):
        if not d.exists():
            print(f"{d.name}\t(skip: not found)")
            continue
        try:
            stats = eval_checkpoint(str(d), config_name, num_samples)
            results[d.name] = stats
            print(f"{d.name}\t{stats['mean']:.4f}\t{stats['std']:.4f}\t{stats['max']:.4f}")
        except Exception as e:
            print(f"{d.name}\t(error: {e})")

    return results


if __name__ == "__main__":
    tyro.cli(main)
