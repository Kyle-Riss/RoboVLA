"""
LeRobot 변환 상태 확인 스크립트
"""

import pathlib
import time

def check_status():
    log_file = pathlib.Path("/tmp/lerobot_conversion.log")
    dataset_path = pathlib.Path("/home/billy/.cache/huggingface/lerobot/billy/dobot_e6_vla_dataset")
    
    if not log_file.exists():
        print("로그 파일이 없습니다.")
        return
    
    # 로그 파일의 마지막 몇 줄 읽기
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print("=" * 80)
    print("LeRobot 변환 상태")
    print("=" * 80)
    print(f"\n로그 파일: {log_file}")
    print(f"데이터셋 경로: {dataset_path}")
    print(f"데이터셋 존재: {dataset_path.exists()}")
    
    if dataset_path.exists():
        # 에피소드 수 확인
        episode_dirs = [d for d in dataset_path.iterdir() if d.is_dir() and d.name.startswith("episode_")]
        print(f"변환된 에피소드 수: {len(episode_dirs)}")
    
    print("\n[최근 로그 (마지막 20줄)]")
    for line in lines[-20:]:
        print(line.rstrip())
    
    # 완료 여부 확인
    if lines:
        last_line = lines[-1].strip()
        if "✅ Dataset conversion complete!" in last_line or "Total frames:" in last_line:
            print("\n✅ 변환 완료!")
        elif "Error" in last_line or "Traceback" in last_line:
            print("\n❌ 오류 발생!")
        else:
            print("\n⏳ 변환 진행 중...")


if __name__ == "__main__":
    check_status()
