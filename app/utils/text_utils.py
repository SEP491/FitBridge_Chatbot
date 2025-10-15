# app/utils/text_utils.py - Text processing and normalization utilities

import json
import re
from difflib import SequenceMatcher
from typing import List

def build_conversation_context(conversation_history: List[dict]) -> str:
    """Xây dựng ngữ cảnh từ lịch sử hội thoại"""
    if not conversation_history:
        return ""
    
    context_parts = []
    for msg in conversation_history[-10:]:  # Lấy 10 tin nhắn gần nhất làm ngữ cảnh
        role_label = "Người dùng" if msg.get("role") == "user" else "FitBridge"
        content = sanitize_text_for_json(msg.get('content', ''))
        context_parts.append(f"{role_label}: {content}")
    
    return "\n".join(context_parts)

def sanitize_text_for_json(text: str) -> str:
    """Làm sạch text để tránh lỗi JSON parsing"""
    if not text:
        return ""
    
    # Thay thế các ký tự điều khiển có thể gây lỗi JSON
    try:
        # Loại bỏ các ký tự điều khiển không mong muốn
        cleaned_text = text.replace('\x00', '').replace('\x08', '').replace('\x0c', '')
        cleaned_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned_text)
        
        # Đảm bảo text có thể được encode thành JSON
        json.dumps(cleaned_text)
        return cleaned_text
    except (UnicodeDecodeError, json.JSONDecodeError):
        # Nếu vẫn có lỗi, encode/decode để loại bỏ ký tự không hợp lệ
        return text.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

def normalize_vietnamese_text(text):
    """Chuẩn hóa văn bản tiếng Việt để tìm kiếm tốt hơn"""
    if not text:
        return ""
    
    text = text.lower()
    
    # Bản đồ chuyển đổi ký tự tiếng Việt sang Latin
    char_map = {
        'à': 'a', 'á': 'a', 'ạ': 'a', 'ả': 'a', 'ã': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ậ': 'a', 'ẩ': 'a', 'ẫ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ặ': 'a', 'ẳ': 'a', 'ẵ': 'a',
        'è': 'e', 'é': 'e', 'ẹ': 'e', 'ẻ': 'e', 'ẽ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ệ': 'e', 'ể': 'e', 'ễ': 'e',
        'ì': 'i', 'í': 'i', 'ị': 'i', 'ỉ': 'i', 'ĩ': 'i',
        'ò': 'o', 'ó': 'o', 'ọ': 'o', 'ỏ': 'o', 'õ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ộ': 'o', 'ổ': 'o', 'ỗ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ợ': 'o', 'ở': 'o', 'ỡ': 'o',
        'ù': 'u', 'ú': 'u', 'ụ': 'u', 'ủ': 'u', 'ũ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ự': 'u', 'ử': 'u', 'ữ': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỵ': 'y', 'ỷ': 'y', 'ỹ': 'y',
        'đ': 'd'
    }
    
    # Thay thế ký tự tiếng Việt
    for viet_char, latin_char in char_map.items():
        text = text.replace(viet_char, latin_char)
    
    # Loại bỏ ký tự đặc biệt, chỉ giữ chữ cái và số
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = ' '.join(text.split())
    
    return text


def extract_search_keywords(user_input):
    """Trích xuất từ khóa tìm kiếm từ đầu vào của người dùng"""
    stop_words = {
        'tìm', 'tìm kiếm', 'find', 'search', 'có', 'không', 'gym', 'phòng gym', 
        'nào', 'đâu', 'where', 'what', 'gì', 'là', 'ở', 'tại', 'trong', 'của',
        'một', 'vài', 'những', 'các', 'the', 'a', 'an', 'and', 'or', 'for'
    }
    
    normalized = normalize_vietnamese_text(user_input)
    words = normalized.split()
    keywords = [word for word in words if word not in stop_words and len(word) >= 2]
    
    return keywords