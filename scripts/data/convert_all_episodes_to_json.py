"""
VLA_DATASET의 모든 에피소드를 JSON으로 변환하는 스크립트.

사용법:
    python scripts/convert_all_episodes_to_json.py \
        --vla_dataset_dir VLA_DATASET \
        --output_dir json_output \
        --use_csv
"""

import argparse
import pathlib
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description="Convert all episodes in VLA_DATASET to JSON")
    parser.add_argument(
        '--vla_dataset_dir',
        type=str,
        default='VLA_DATASET',
        help='VLA_DATASET directory path (default: VLA_DATASET)'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        default='json_output',
        help='Output directory for JSON files (default: json_output)'
    )
    parser.add_argument(
        '--use_csv',
        action='store_true',
        help='Use CSV instead of NPY'
    )
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Do not include images in JSON'
    )
    parser.add_argument(
        '--start_episode',
        type=int,
        default=1,
        help='Start episode number (default: 1)'
    )
    parser.add_argument(
        '--end_episode',
        type=int,
        default=138,
        help='End episode number (default: 138)'
    )
    
    args = parser.parse_args()
    
    vla_dataset_dir = pathlib.Path(args.vla_dataset_dir)
    output_dir = pathlib.Path(args.output_dir)
    
    if not vla_dataset_dir.exists():
        print(f"Error: VLA_DATASET directory not found: {vla_dataset_dir}")
        sys.exit(1)
    
    # convert_to_json.py 경로 찾기
    import sys
    robo_vla_root = pathlib.Path(__file__).parent.parent.parent
    sys.path.insert(0, str(robo_vla_root))
    
    from config.env_config import get_env_config
    env_config = get_env_config()
    
    # Try to find data collector
    if env_config.data_collector_path:
        convert_script = env_config.data_collector_path / "convert_to_json.py"
    else:
        # Fallback: check common locations
        convert_script = pathlib.Path(__file__).parent.parent.parent.parent / "Dobot-Arm-DataCollect" / "convert_to_json.py"
    
    if not convert_script.exists():
        print(f"Error: convert_to_json.py not found at {convert_script}")
        print(f"Set DATA_COLLECTOR_PATH environment variable or place data collector as sibling directory.")
        sys.exit(1)
    
    # 에피소드 디렉토리 찾기
    episode_dirs = []
    for i in range(args.start_episode, args.end_episode + 1):
        episode_dir = vla_dataset_dir / str(i)
        if episode_dir.exists():
            episode_dirs.append(episode_dir)
        else:
            print(f"Warning: Episode {i} directory not found: {episode_dir}")
    
    print(f"Found {len(episode_dirs)} episodes to convert")
    print(f"Output directory: {output_dir}")
    print(f"Use CSV: {args.use_csv}")
    print(f"Include images: {not args.no_images}")
    
    # 변환 명령어 구성
    cmd = [
        sys.executable,
        str(convert_script),
        '--episode_dirs',
    ] + [str(d) for d in episode_dirs] + [
        '--output_dir',
        str(output_dir),
    ]
    
    if args.use_csv:
        cmd.append('--use-csv')
    
    if args.no_images:
        cmd.append('--no-images')
    
    print(f"\nRunning conversion command...")
    print(f"Command: {' '.join(cmd)}")
    
    # 변환 실행
    try:
        result = subprocess.run(cmd, check=True, cwd=vla_dataset_dir.parent)
        print(f"\n✅ Conversion complete!")
        print(f"JSON files saved to: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Conversion failed with exit code {e.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
