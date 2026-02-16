# Git Push 전 파일 검토 결과

## ❌ 제거해야 할 파일 (Git에 포함하지 않음)

### 1. 원본과 동일한 파일 (openpi에서 그대로 복사)
- ❌ `scripts/training/train_pytorch.py` 
  - **이유**: openpi 원본과 완전히 동일 (diff 없음)
  - **대안**: `train_universal.py` 또는 `train_pytorch_wrapper.py` 사용
  - **조치**: 삭제 또는 .gitignore에 추가

### 2. 구버전/중복 스크립트
- ❌ `examples/dobot_e6/convert_dobot_data_to_lerobot.py`
  - **이유**: `gripper_tooldo2` 사용 (구버전), 범용 스크립트 `convert_json_to_lerobot_universal.py` 있음
  - **조치**: 삭제 또는 examples/dobot_e6/README.md에만 참조

- ❌ `examples/dobot_e6/config_reference.py`
  - **이유**: 참조용이지만 실제로는 `config/pi0_e6_freeze_vlm.py`가 있음
  - **조치**: 삭제 (config/pi0_e6_freeze_vlm.py가 더 완전함)

### 3. 임시/모니터링 스크립트 (선택적 제거)
- ⚠️ `scripts/data/check_lerobot_conversion_status.py`
  - **이유**: 하드코딩된 경로 (`/home/billy`, `/tmp/lerobot_conversion.log`)
  - **조치**: 경로를 환경변수로 변경하거나 제거

- ⚠️ `scripts/data/check_norm_stats_status.py`
  - **이유**: 하드코딩된 경로 (`/tmp/norm_stats.log`)
  - **조치**: 경로를 환경변수로 변경하거나 제거

### 4. 임시 문서
- ❌ `SUMMARY.md`
  - **이유**: 임시 요약 문서 (내부용)
  - **조치**: 삭제 (README.md에 요약 포함)

## ⚠️ 수정이 필요한 파일 (하드코딩된 경로/값)

### 1. 하드코딩된 사용자명/경로
- ⚠️ `config/pi0_e6_freeze_vlm.py`
  - `repo_id="billy/dobot_e6_vla_dataset"` → 환경변수 또는 기본값으로 변경
  - `asset_id="billy/dobot_e6_vla_dataset"` → 동일

- ⚠️ `scripts/data/check_lerobot_conversion_status.py`
  - `/home/billy/.cache/...` → `pathlib.Path.home() / ".cache/..."`
  - `/tmp/lerobot_conversion.log` → 환경변수 또는 기본값

- ⚠️ `scripts/training/run_dobot_e6_training.sh`
  - `--exp-name dobot_e6_run_10k_gripper` → 기본값으로 변경 (선택 가능하게)

- ⚠️ `scripts/training/eval_checkpoint_actions.py`
  - `checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_20k` → 기본값만 (예시)

- ⚠️ `scripts/training/pick_best_checkpoint.py`
  - `checkpoints/pi0_e6_freeze_vlm/dobot_e6_run_20k` → 기본값만 (예시)

## ✅ 유지해야 할 파일 (Git에 포함)

### 핵심 스크립트
- ✅ `scripts/data/convert_all_episodes_to_json.py` - 데이터 변환
- ✅ `scripts/data/convert_json_to_lerobot_universal.py` - 범용 변환
- ✅ `scripts/data/compute_norm_stats.py` - norm stats 계산
- ✅ `scripts/data/verify_gripper_in_json.py` - 검증
- ✅ `scripts/training/run_training_universal.sh` - 범용 학습
- ✅ `scripts/training/train_universal.py` - 범용 학습 래퍼
- ✅ `scripts/training/train_pytorch_wrapper.py` - Config 등록 래퍼
- ✅ `scripts/training/pick_best_checkpoint.py` - 체크포인트 선택
- ✅ `scripts/training/eval_checkpoint_actions.py` - 체크포인트 평가
- ✅ `scripts/deployment/convert_checkpoint_for_jetson.py` - Jetson 변환
- ✅ `scripts/deployment/serve_policy.py` - 정책 서버
- ✅ `scripts/setup_env.py` - 환경 설정

### 설정 파일
- ✅ `config/robot_config.py` - 로봇 설정 시스템
- ✅ `config/env_config.py` - 환경 자동 감지
- ✅ `config/pi0_e6_freeze_vlm.py` - Config 등록 (하드코딩 수정 필요)
- ✅ `config/example_7dof.py` - 7DOF 예제
- ✅ `config/__init__.py`

### 문서
- ✅ `README.md` - 메인 문서
- ✅ `QUICKSTART.md` - 빠른 시작
- ✅ `CHECKLIST.md` - 체크리스트 (한국어, 유지할지 결정)
- ✅ `docs/USAGE.md` - 사용법
- ✅ `docs/SETUP.md` - 설정 가이드
- ✅ `docs/ROBOT_CONFIG.md` - 로봇 설정 가이드
- ✅ `examples/README.md` - 예제 가이드
- ✅ `examples/dobot_e6/README.md` - Dobot E6 가이드
- ✅ `examples/dobot_e6/convert_json_to_lerobot.py` - Dobot E6 변환 (레거시, 참조용)

### 기타
- ✅ `.gitignore` - Git 제외 파일

## 📋 권장 조치사항

### 즉시 제거
1. `scripts/training/train_pytorch.py` (원본과 동일)
2. `examples/dobot_e6/config_reference.py` (중복)
3. `SUMMARY.md` (임시 문서)

### 선택적 제거/수정
4. `examples/dobot_e6/convert_dobot_data_to_lerobot.py` (구버전, 범용 스크립트 있음)
5. `scripts/data/check_*_status.py` (임시 모니터링, 경로 하드코딩)

### 수정 필요
6. 하드코딩된 경로/사용자명을 환경변수 또는 기본값으로 변경
