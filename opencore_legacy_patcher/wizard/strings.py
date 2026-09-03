"""
strings.py: 한국어 사용자 문자열
"""

APP_NAME = "26x86"

STEPS = [
    {
        "id": "detect",
        "title": "1. 내 Mac 확인",
        "tooltip": "현재 Mac 모델과 하드웨어 정보를 자동으로 확인합니다.",
    },
    {
        "id": "macos",
        "title": "2. macOS 버전 선택",
        "tooltip": "설치하려는 macOS 버전을 선택합니다. Mac에 맞는 버전을 고르세요.",
    },
    {
        "id": "build",
        "title": "3. 패치 생성",
        "tooltip": "선택한 Mac과 macOS에 맞는 부팅 파일(EFI)을 만듭니다.",
    },
    {
        "id": "install",
        "title": "4. EFI 설치",
        "tooltip": "만든 EFI를 USB 또는 디스크에 설치합니다.",
    },
    {
        "id": "root_patch",
        "title": "5. 루트 패치",
        "tooltip": "macOS 설치 후 Wi-Fi, 그래픽 등 추가 패치를 적용합니다.",
    },
]

# Step 1
STEP_DETECT_HEADING = "내 Mac 정보"
STEP_DETECT_DESC = "아래 정보가 맞는지 확인하세요. 다른 Mac용으로 작업하려면 모델을 변경할 수 있습니다."
STEP_DETECT_BUTTON = "다시 확인"
STEP_DETECT_CHANGE_MODEL = "모델 변경"
STEP_DETECT_MODEL_LABEL = "Mac 모델"
STEP_DETECT_NAME_LABEL = "제품명"
STEP_DETECT_CPU_LABEL = "프로세서"
STEP_DETECT_OS_LABEL = "현재 macOS"

# Step 2
STEP_MACOS_HEADING = "설치할 macOS 선택"
STEP_MACOS_DESC = "이 Mac에서 사용할 macOS 버전을 선택하세요."
STEP_MACOS_CURRENT = "현재 실행 중"
STEP_MACOS_RECOMMENDED = "권장"

# Step 3
STEP_BUILD_HEADING = "패치(EFI) 생성"
STEP_BUILD_DESC = "선택한 설정으로 부팅 파일을 만듭니다. 완료까지 1~3분 정도 걸릴 수 있습니다."
STEP_BUILD_BUTTON = "패치 생성 시작"
STEP_BUILD_DONE = "패치 생성이 완료되었습니다."
STEP_BUILD_RUNNING = "패치를 생성하는 중…"

# Step 4
STEP_INSTALL_HEADING = "EFI 설치"
STEP_INSTALL_DESC = "USB 메모리 또는 디스크에 EFI를 설치합니다. 설치 전 데이터를 백업하세요."
STEP_INSTALL_BUTTON = "EFI 설치 시작"
STEP_INSTALL_NEED_BUILD = "먼저 3단계에서 패치를 생성해 주세요."

# Step 5
STEP_ROOT_HEADING = "루트 패치"
STEP_ROOT_DESC = "macOS를 설치한 뒤, Wi-Fi·그래픽·오디오 등을 사용하려면 루트 패치가 필요할 수 있습니다."
STEP_ROOT_APPLY = "루트 패치 적용"
STEP_ROOT_REVERT = "루트 패치 되돌리기"
STEP_ROOT_STATUS = "패치 상태"
STEP_ROOT_NONE = "적용할 패치가 없습니다."
STEP_ROOT_LAST = "마지막 패치"

# Navigation
BTN_PREV = "← 이전"
BTN_NEXT = "다음 →"
BTN_ADVANCED = "고급 모드"
BTN_SETTINGS = "설정"
BTN_HELP = "도움말"
BTN_ABOUT = "정보"

# Status bar defaults
STATUS_READY = "준비됨"
STATUS_WORKING = "작업 중…"

# Settings (simplified)
SETTINGS_TITLE = "설정"
SETTINGS_GENERAL = "일반"
SETTINGS_UPDATES = "업데이트 확인"
SETTINGS_ANALYTICS = "익명 사용 통계 보내기"
SETTINGS_SAVE = "저장"
SETTINGS_CANCEL = "닫기"

# About
ABOUT_TITLE = "26x86 정보"
ABOUT_DESC = "오래된 Mac에서 최신 macOS를 사용할 수 있도록 돕는 도구입니다."
ABOUT_DOCS = "사용 설명서 열기"
ABOUT_VERSION = "버전"

# Errors (plain Korean)
ERR_GENERIC = "작업을 완료하지 못했습니다. 잠시 후 다시 시도해 주세요."
ERR_BUILD_FAILED = "패치 생성에 실패했습니다. Mac 모델과 macOS 버전을 확인해 주세요."
ERR_INSTALL_FAILED = "EFI 설치에 실패했습니다. USB 또는 디스크 연결을 확인해 주세요."
ERR_PATCH_FAILED = "루트 패치에 실패했습니다. macOS를 재시작한 뒤 다시 시도해 주세요."
ERR_UNSUPPORTED = "이 Mac에서는 해당 작업을 지원하지 않습니다."
ERR_PERMISSION = "관리자 권한이 필요합니다. 비밀번호를 입력해 주세요."
