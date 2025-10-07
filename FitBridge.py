# Import các thư viện cốt lõi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import từ cấu trúc module mới
from app.models.chat_models import ChatRequest, ChatResponse
from app.services.response_service import get_response_with_history
from config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, CORS_ORIGINS

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints
@app.post("/chat", summary="Chat với lịch sử hội thoại", response_description="Trả về phản hồi với lịch sử hội thoại")
async def chat_with_history(request: ChatRequest):
    return get_response_with_history(
        user_input=request.prompt,
        conversation_history=request.conversation_history,
        longitude=request.longitude,
        latitude=request.latitude
    )

# Chạy ứng dụng
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
