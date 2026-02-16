"""
변환된 JSON 파일에서 그리퍼 값이 제대로 변환되었는지 확인하는 스크립트.
"""

import json
import pathlib
from collections import Counter

def check_gripper_values(json_dir: str, num_samples: int = 5):
    """JSON 파일들에서 그리퍼 값 확인"""
    json_path = pathlib.Path(json_dir)
    
    json_files = sorted(json_path.glob("*.json"))
    print(f"Found {len(json_files)} JSON files")
    
    # 샘플 몇 개 확인
    print(f"\n[샘플 {num_samples}개 파일 확인]")
    for json_file in json_files[:num_samples]:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        frames = data['frames']
        
        # 그리퍼 값 통계
        gripper_values = [f['gripper'] for f in frames]
        gripper_tooldo1_values = [f['gripper_tooldo1'] for f in frames]
        actions_gripper = [f['actions'][6] for f in frames]
        
        print(f"\n{json_file.name}:")
        print(f"  총 프레임: {len(frames)}")
        print(f"  gripper 값: min={min(gripper_values)}, max={max(gripper_values)}, "
              f"unique={sorted(set(gripper_values))}")
        print(f"  gripper_tooldo1 값: min={min(gripper_tooldo1_values)}, max={max(gripper_tooldo1_values)}, "
              f"unique={sorted(set(gripper_tooldo1_values))}")
        print(f"  actions[6] (그리퍼 델타): min={min(actions_gripper):.6f}, max={max(actions_gripper):.6f}, "
              f"unique={sorted(set([round(x, 6) for x in actions_gripper]))}")
        
        # 그리퍼 상태 변경 확인
        gripper_changes = []
        prev_g = None
        for i, f in enumerate(frames):
            g = f['gripper']
            if g != prev_g:
                gripper_changes.append((i, f['gripper_tooldo1'], f['gripper_tooldo2'], g))
                prev_g = g
        
        if gripper_changes:
            print(f"  그리퍼 상태 변경: {len(gripper_changes)}회")
            print(f"    처음 5개: {gripper_changes[:5]}")
        else:
            print(f"  그리퍼 상태 변경: 없음 (모두 동일)")
    
    # 전체 통계
    print(f"\n[전체 통계]")
    all_gripper_values = []
    all_actions_gripper = []
    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)
        for frame in data['frames']:
            all_gripper_values.append(frame['gripper'])
            all_actions_gripper.append(frame['actions'][6])
    
    print(f"전체 프레임 수: {len(all_gripper_values)}")
    print(f"gripper 값 분포: {Counter(all_gripper_values)}")
    print(f"actions[6] 값 범위: min={min(all_actions_gripper):.6f}, max={max(all_actions_gripper):.6f}")
    print(f"actions[6] != 0인 프레임: {sum(1 for x in all_actions_gripper if abs(x) > 1e-6)}개")


if __name__ == "__main__":
    import sys
    json_dir = sys.argv[1] if len(sys.argv) > 1 else "json_output"
    check_gripper_values(json_dir)
