# PaperPilot

논문 PDF의 제목을 자동으로 추출하여 파일명을 정리해주는 Windows 유틸리티 프로그램입니다.  
사용자는 PDF를 드래그 앤 드롭하면, 프로그램이 논문의 제목을 분석하여 파일명을 자동으로 변경합니다.

---

## 1. exe 파일 실행 방법 (가장 쉬운 방법)

배포된 exe 파일이 있으면 **Python이나 추가 라이브러리 설치 없이 바로 실행 가능**합니다.

### 1) exe 파일 위치
PyInstaller로 빌드하면 exe파일은 결과물은 보통 아래 경로에 생성됩니다.

```text
C:\Users\user\Downloads\PaperPilot_Package\PaperPilot_Package\dist
```

빌드 옵션에 따라 결과 형태는 두 가지입니다.

#### 경우 A. `--onefile`로 빌드한 경우
```text
...\dist\PaperPilot.exe
```

이 경우 **`PaperPilot.exe` 하나만 실행**하면 됩니다.

#### 경우 B. `--onefile` 없이 빌드한 경우
```text
...\dist\PaperPilot\PaperPilot.exe
```

이 경우 **`PaperPilot` 폴더 안의 `PaperPilot.exe`를 실행**해야 하며,  
폴더 안의 다른 파일들도 함께 유지해야 정상 실행됩니다.

### 2) exe 실행 방법
1. `dist` 폴더로 이동
2. `PaperPilot.exe` 더블클릭
3. 프로그램 창이 열리면 PDF 파일을 드래그 앤 드롭
4. `파일명 변경 실행` 클릭

### 3) exe 실행에 필요한 추가 라이브러리
**없습니다.**  
배포된 exe 파일은 일반적으로 **추가 Python 라이브러리 설치 없이 실행**할 수 있습니다.

즉, exe 사용자에게는 아래 항목이 **필요 없습니다.**
- Python 설치
- PyMuPDF 설치
- tkinterdnd2 설치
- PyInstaller 설치

### 4) exe가 실행되지 않을 때 확인할 점
- 압축 파일에서 바로 실행하지 말고 **압축 해제 후 실행**
- `--onefile` 없이 빌드한 경우 **exe만 따로 꺼내지 말고 전체 폴더 유지**
- Windows 보안 또는 백신이 exe 실행을 차단했는지 확인
- 파일을 `다운로드` 폴더 대신 바탕화면 등 다른 폴더로 옮겨 실행해보기

---

## 2. 개발 목적

논문을 다운로드할 때 파일명이 `download.pdf`, `paper123.pdf` 등으로 저장되는 경우가 많습니다.  
이 프로그램은 PDF 내용을 분석하여 **논문 제목 기반으로 파일명을 자동 정리**함으로써  
논문 관리 효율을 높이기 위해 제작되었습니다.

---

## 3. 실행 환경

- OS: Windows 10 / Windows 11 (64-bit)
- Python: 3.10 이상 권장 (개발 기준: 3.13)
- 인터넷 연결: 최초 패키지 설치 시 필요

---

## 4. 소스코드 직접 실행 방법

exe가 아니라 `paperpilot_app.py`를 직접 실행하려면 아래 환경이 필요합니다.

### 1) Python 설치
Python: 3.10 이상 권장 (개발 기준: 3.13)

공식 사이트:
```text
https://www.python.org/downloads/
```

설치 시 반드시 아래 옵션 체크:
- Add Python to PATH

설치 확인:
```bash
python --version
```
또는
```bash
py --version
```

### 2) 필수 패키지 설치
```bash
python -m pip install pymupdf tkinterdnd2
```

또는

```bash
py -m pip install pymupdf tkinterdnd2
```

### 3) 사용 라이브러리 설명
- **PyMuPDF**: PDF에서 제목 텍스트 추출
- **tkinter**: GUI 창 구성
- **tkinterdnd2**: 드래그 앤 드롭 기능

참고: `tkinter`는 일반적인 Python Windows 설치본에 기본 포함되는 경우가 많아 별도 설치가 필요 없는 경우가 많습니다.

---

## 5. 프로그램 실행 방법 (소스코드 직접 실행)

1. 다운받은 파일 내 `paperpilot_app.py`를 PC에 저장
2. `paperpilot_app.py`의 저장 경로를 기준으로 PowerShell 또는 명령프롬프트에서 실행

실행 예시:

```bash
python C:\paperpilot_app.py
```

또는

```bash
py C:\paperpilot_app.py
```

---

## 6. 사용 방법

1. 프로그램 실행
2. PDF 파일을 드래그 앤 드롭
3. 제목 자동 분석
4. `파일명 변경 실행` 클릭

---

## 7. 주요 기능

- PDF 제목 자동 추출
- 드래그 앤 드롭 지원
- 파일명 자동 변경
- 중복 파일명 처리

---

## 8. 관리자 권한

일반 폴더에서는 필요 없습니다.

단, 시스템 보호 폴더나 권한 제한이 있는 위치의 파일명을 변경할 때는 권한 문제가 발생할 수 있습니다.

---

## 9. 주의사항

- 스캔 PDF는 제목 인식 정확도가 낮을 수 있습니다.
- 일부 논문은 제목 인식에 실패할 수 있습니다.
- 이미 같은 이름의 파일이 있으면 자동으로 중복 파일명 처리됩니다.

---

## 10. 오류 해결

### Python 명령이 안 될 경우
- Python 재설치
- 설치 시 `Add Python to PATH` 체크 여부 확인

### exe가 안 열릴 경우
- 압축 해제 후 실행
- 백신 또는 SmartScreen 차단 여부 확인
- `dist` 폴더 구조가 유지되어 있는지 확인

### 드래그 앤 드롭이 안 될 경우
- 소스코드 실행 환경에서는 `tkinterdnd2` 설치 여부 확인
- exe 버전에서는 파일 손상 여부 또는 보안 프로그램 차단 여부 확인

---

## 11. 개발/배포 시 참고

exe 파일을 직접 만들려면 예를 들어 아래와 같이 빌드할 수 있습니다.

```bash
python -m PyInstaller --onefile --windowed paperpilot_app.py
```

또는

```bash
py -m PyInstaller --onefile --windowed paperpilot_app.py
```

빌드 완료 후 결과물은 보통 `dist` 폴더에 생성됩니다.
