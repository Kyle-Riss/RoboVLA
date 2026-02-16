"""
norm_stats 계산 상태 확인 스크립트
"""

import pathlib
import json

def check_status():
    log_file = pathlib.Path("/tmp/norm_stats.log")
    
    print("=" * 80)
    print("norm_stats 계산 상태")
    print("=" * 80)
    
    if not log_file.exists():
        print("로그 파일이 없습니다.")
        return
    
    # 로그 파일의 마지막 몇 줄 읽기
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    print(f"\n로그 파일: {log_file}")
    print(f"로그 라인 수: {len(lines)}")
    
    # 진행률 확인
    progress_lines = [l for l in lines if "Computing stats:" in l]
    if progress_lines:
        last_progress = progress_lines[-1]
        print(f"\n[최근 진행 상황]")
        print(last_progress.strip())
    
    print("\n[최근 로그 (마지막 15줄)]")
    for line in lines[-15:]:
        print(line.rstrip())
    
    # 완료 여부 확인
    if lines:
        last_lines = ''.join(lines[-10:])
        if "Saved norm_stats" in last_lines or "norm_stats.json" in last_lines:
            print("\n✅ 계산 완료!")
            
            # norm_stats.json 위치 확인
            config_name = "pi0_e6_freeze_vlm"
            possible_paths = [
                pathlib.Path.home() / ".cache" / "openpi" / "openpi-assets" / "checkpoints" / config_name / "assets" / "norm_stats.json",
                pathlib.Path("checkpoints") / config_name / "assets" / "norm_stats.json",
            ]
            
            for p in possible_paths:
                if p.exists():
                    print(f"\n✅ norm_stats.json 발견: {p}")
                    # 그리퍼 통계 확인
                    with open(p, 'r') as f:
                        stats = json.load(f)
                    if 'norm_stats' in stats and 'actions' in stats['norm_stats']:
                        actions_stats = stats['norm_stats']['actions']
                        if 'mean' in actions_stats and len(actions_stats['mean']) >= 8:
                            print(f"\n[그리퍼 통계 확인]")
                            print(f"  actions[6] (dummy): mean={actions_stats['mean'][6]:.6f}, std={actions_stats['std'][6]:.6f}")
                            print(f"  actions[7] (gripper): mean={actions_stats['mean'][7]:.6f}, std={actions_stats['std'][7]:.6f}")
                            if abs(actions_stats['mean'][7]) > 1e-6 or abs(actions_stats['std'][7]) > 1e-6:
                                print("  ✅ 그리퍼 값이 정상적으로 계산되었습니다!")
                            else:
                                print("  ⚠️  그리퍼 값이 여전히 0입니다.")
                    break
        elif "Error" in last_lines or "Traceback" in last_lines:
            print("\n❌ 오류 발생!")
        else:
            print("\n⏳ 계산 진행 중...")


if __name__ == "__main__":
    check_status()
