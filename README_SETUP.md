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

5) Ingest PDF bằng HTTP endpoint (mới)

Sau khi app chạy (docker compose up hoặc uvicorn), bạn có thể gửi request POST tới `/ingest`:

Curl (Git Bash / Linux / macOS):

```bash
curl -X POST http://localhost:8000/ingest \
	-H "Content-Type: application/json" \
	-d '{"pdf_path":"/app/test.pdf","source_id":"my-doc"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/ingest -Method Post -Body (@{pdf_path="C:\\path\\to\\test.pdf"; source_id="my-doc"} | ConvertTo-Json) -ContentType "application/json"
```

Lưu ý: nếu bạn chạy app trong Docker Compose (cài repo vào `/app` trong container), dùng đường dẫn `/app/<file>` hoặc copy file vào repo trước khi gọi endpoint.

6) Truy vấn (RAG) bằng `/query`

Gửi truy vấn văn bản để lấy các đoạn ngữ cảnh từ Qdrant:

```bash
curl -X POST http://localhost:8000/query \
	-H "Content-Type: application/json" \
	-d '{"query":"What is the purpose of the document?","top_k":5}'
```

Response trả về các contexts và nguồn tương ứng.



Ghi chú:
- Nếu bạn dùng Windows CMD/PowerShell, thay `source` bằng `.venv\\Scripts\\Activate.ps1` hoặc `.
venv\\Scripts\\activate`.
- `pyproject.toml` chứa cùng danh sách dependencies; tôi đã tạo `requirements.txt` cho pip.
