#!/usr/bin/env python3
"""
PyTorch 체크포인트를 젯슨 배포용으로 변환합니다.

- model.safetensors → model.pth
- assets/norm_stats.json 유지
- 불필요한 optimizer.pt, metadata.pt 제외한 배포용 폴더 생성

사용법:
    python scripts/convert_checkpoint_for_jetson.py \
        --checkpoint_dir checkpoints/pi0_e6_freeze_vlm/dobot_e6_run/100 \
        --output_dir checkpoints/pi0_e6_freeze_vlm/dobot_e6_run/100_jetson
"""

import argparse
import shutil
from pathlib import Path

import safetensors.torch
import torch
import tyro

import openpi.training.config as _config


def main(
    checkpoint_dir: str,
    output_dir: str | None = None,
    config_name: str = "pi0_e6_freeze_vlm",
):
    """Convert checkpoint for Jetson deployment."""
    ckpt_path = Path(checkpoint_dir).resolve()
    if not ckpt_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

    out_path = Path(output_dir) if output_dir else ckpt_path.parent / f"{ckpt_path.name}_jetson"
    out_path = out_path.resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    # Load config and model
    config = _config.get_config(config_name)
    safetensors_file = ckpt_path / "model.safetensors"
    if not safetensors_file.exists():
        raise FileNotFoundError(f"model.safetensors not found in {ckpt_path}")

    print(f"Loading model from {safetensors_file}...")
    model = config.model.load_pytorch(config, str(safetensors_file))

    # Save as .pth (Jetson 권장)
    pth_file = out_path / "model.pth"
    torch.save(model.state_dict(), pth_file)
    print(f"Saved {pth_file}")

    # Copy assets (norm_stats)
    assets_src = ckpt_path / "assets"
    assets_dst = out_path / "assets"
    if assets_src.exists():
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)
        print(f"Copied assets to {assets_dst}")
    else:
        print(f"Warning: No assets found at {assets_src}")

    # Also keep safetensors for flexibility
    shutil.copy2(safetensors_file, out_path / "model.safetensors")
    print(f"Copied model.safetensors to {out_path}")

    print(f"\n젯슨 배포용 체크포인트: {out_path}")
    print("  - model.pth          (젯슨 권장)")
    print("  - model.safetensors")
    print("  - assets/.../norm_stats.json")


if __name__ == "__main__":
    tyro.cli(main)
