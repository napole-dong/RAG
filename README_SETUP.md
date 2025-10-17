# Thiết lập môi trường để chạy dự án

Yêu cầu:
- Python 3.13+ (hoặc cài Python 3.13 và đảm bảo gọi bằng `python` trong bash)
- Git
- (Tuỳ chọn) Docker nếu muốn chạy Qdrant local

1) Tạo virtualenv và cài dependencies (bash):

```bash
./scripts/setup_venv.sh .venv
source .venv/bin/activate
```

Nếu hệ thống của bạn có nhiều python, gọi rõ:

```bash
PYTHON=python3.13 ./scripts/setup_venv.sh .venv
```

Nếu bạn chưa cài Python (thông báo `Python was not found`), trên Windows bạn có thể cài bằng:

- Winget (Windows 10/11):

```powershell
winget install --id=Python.Python.3.13 -e --source winget
```

- Chocolatey (nếu bạn dùng choco):

```powershell
choco install python --version=3.13.0
```

Sau khi cài, mở lại Git Bash và kiểm tra:

```bash
python --version
```

2) Biến môi trường
- Tạo file `.env` theo mẫu (nếu cần) và thêm biến như GOOGLE_API_KEY hoặc QDRANT_URL, QDRANT_API_KEY tuỳ cấu hình.

3) (Tuỳ chọn) Chạy Qdrant bằng Docker (nếu cần):

```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage -d qdrant/qdrant
```

4) Chạy app (FastAPI + Inngest):

```bash
# Với uvicorn
uvicorn main:app --reload

# Hoặc theo hướng dẫn trong main.py nếu dùng Inngest integration
```

Ghi chú:
- Nếu bạn dùng Windows CMD/PowerShell, thay `source` bằng `.venv\\Scripts\\Activate.ps1` hoặc `.
venv\\Scripts\\activate`.
- `pyproject.toml` chứa cùng danh sách dependencies; tôi đã tạo `requirements.txt` cho pip.
