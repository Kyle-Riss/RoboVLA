#!/usr/bin/env python3
"""
체크포인트(1k/2k/5k/10k/20k) 자동 평가 후 베스트 선택.

- policy_config.create_trained_policy + infer 파이프라인 사용
- 동일한 고정 테스트 세트로 각 ckpt 추론
- action mean, std, max 로그
- 베스트: act_max 낮은 순 (안정성 우선), act_std 적당한 것

사용법:
    python scripts/pick_best_checkpoint.py

    # 경로/체크포인트 지정
    python scripts/pick_best_checkpoint.py --checkpoint_base checkpoints/.../dobot_e6_run_20k \\
        --checkpoints 1000 2000 5000 10000 20000
"""

import sys
from pathlib import Path

import numpy as np
import tyro

import openpi.training.config as _config
import openpi.policies.policy_config as _policy_config
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset

# 기본 평가 체크포인트 (상한 20k, 중간 2k~5k 포함)
DEFAULT_CHECKPOINTS = [1000, 2000, 5000, 10000, 20000]


def eval_checkpoint(checkpoint_dir: str, config_name: str, num_samples: int) -> dict:
    """단일 체크포인트에서 추론 action 통계 계산."""
    config = _config.get_config(config_name)
    policy = _policy_config.create_trained_policy(config, checkpoint_dir, pytorch_device="cuda")

    repo_id = config.data.repo_id
    dataset = LeRobotDataset(repo_id)

    all_actions = []
    step = max(1, len(dataset) // num_samples)
    indices = list(range(0, min(len(dataset), num_samples * step), step))[:num_samples]

    for idx in indices:
        sample = dataset[idx]
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
        act = out["actions"][:, :8]
        all_actions.append(act)

    all_actions = np.concatenate(all_actions, axis=0)
    return {
        "mean": float(np.abs(all_actions).mean()),
        "std": float(all_actions.std()),
        "max": float(np.abs(all_actions).max()),
    }


def pick_best(results: dict) -> str:
    """
    베스트 체크포인트 선택.
    - act_max 낮을수록 안정적 (과격한 action 회피)
    - act_max 동률이면 act_std 낮은 쪽
    """
    valid = {k: v for k, v in results.items() if "max" in v}
    if not valid:
        return ""
    # act_max 오름차순, 같으면 act_std 오름차순
    best = min(valid.items(), key=lambda x: (x[1]["max"], x[1]["std"]))
    return best[0]


def main(
    checkpoint_base: str = "checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_20k",
    checkpoints: list[int] = DEFAULT_CHECKPOINTS,
    config_name: str = "pi0_e6_freeze_vlm",
    num_samples: int = 50,
    pick_best_ckpt: bool = True,
):
    """체크포인트 자동 평가 후 베스트 출력."""
    base = Path(checkpoint_base).resolve()
    if not base.exists():
        print(f"Error: checkpoint_base not found: {base}")
        sys.exit(1)

    dirs = [(base / str(ckpt)) for ckpt in checkpoints]
    dirs = [d for d in dirs if d.exists()]
    if not dirs:
        print(f"Error: no checkpoints found in {base} for {checkpoints}")
        sys.exit(1)

    print("=" * 60)
    print("Checkpoint Action Stats (create_trained_policy + infer)")
    print("=" * 60)
    print(f"Config: {config_name}")
    print(f"Test samples: {num_samples}")
    print("-" * 60)
    print(f"{'Checkpoint':<12} {'act_mean':>10} {'act_std':>10} {'act_max':>10}")
    print("-" * 60)

    results = {}
    for d in sorted(dirs, key=lambda x: int(x.name) if x.name.isdigit() else 0):
        try:
            stats = eval_checkpoint(str(d), config_name, num_samples)
            results[d.name] = stats
            print(f"{d.name:<12} {stats['mean']:>10.4f} {stats['std']:>10.4f} {stats['max']:>10.4f}")
        except Exception as e:
            print(f"{d.name:<12} (error: {e})")

    if pick_best_ckpt and results:
        best_name = pick_best(results)
        if best_name:
            best_path = base / best_name
            print("-" * 60)
            print(f">>> Best (act_max 낮음 = 안정성 우선): {best_name}")
            print(f"    Path: {best_path}")
            print("=" * 60)


if __name__ == "__main__":
    tyro.cli(main)
