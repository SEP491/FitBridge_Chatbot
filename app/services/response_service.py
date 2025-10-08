# app/services/response_service.py - Response generation and handling functions

from datetime import datetime
import google.generativeai as genai
from app.utils.text_utils import sanitize_text_for_json, build_conversation_context
from app.utils.format_utils import format_distance_friendly
from app.services.search_service import classify_query_with_context, build_nearby_gym_query, get_nearby_distance_preference
from app.services.pt_search_service import classify_trainer_query, build_nearby_trainer_query, get_trainer_distance_preference
from app.services.pt_recommendation_service import create_trainer_response
from app.database.connection import query_database
from app.models.gym_models import safe_get_row_data
from app.models.trainer_models import safe_get_trainer_data
from config import GEMINI_API_KEY

# Cấu hình Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo mô hình Gemini
model = genai.GenerativeModel("gemini-2.0-flash")

def create_simple_response(gyms, user_input, is_nearby=False):
    """Tạo phản hồi đơn giản cho kết quả tìm kiếm gym"""
    if not gyms:
        return "Không tìm thấy gym nào phù hợp với tiêu chí của bạn."

    if len(gyms) == 1:
        gym = gyms[0]
        response = f"**{gym['gymName']}**"
        if gym.get('distance_km'):
            response += f" - {format_distance_friendly(gym['distance_km'])}"
        if gym['address']:
            response += f"\nĐịa chỉ: {gym['address']}"
        if gym['hotResearch']:
            response += "\nĐây là phòng gym rất được yêu thích!"
        return response
    
    elif len(gyms) <= 3:
        response = f"**Tìm thấy {len(gyms)} phòng gym:**\n"
        for i, gym in enumerate(gyms, 1):
            name = gym['gymName']
            if gym['hotResearch']:
                name += " (Hot)"
            if gym.get('distance_km'):
                name += f" ({format_distance_friendly(gym['distance_km'])})"
            response += f"{i}. **{name}**\n"
        return response
    
    else:
        hot_gyms = [g for g in gyms if g['hotResearch']]
        response = f"**Tìm thấy {len(gyms)} phòng gym!**\n"

        if hot_gyms:
            response += "**Các phòng gym phổ biến:**\n"
            for i, gym in enumerate(hot_gyms, 1):
                name = gym['gymName']
                if gym.get('distance_km'):
                    name += f" ({format_distance_friendly(gym['distance_km'])})"
                response += f"{i}. **{name}**\n"
                
            # Hiển thị các gym còn lại
            other_gyms = [g for g in gyms if not g['hotResearch']]
            if other_gyms:
                response += "\n**Các phòng gym khác:**\n"
                for i, gym in enumerate(other_gyms, len(hot_gyms) + 1):
                    name = gym['gymName']
                    if gym.get('distance_km'):
                        name += f" ({format_distance_friendly(gym['distance_km'])})"
                    response += f"{i}. **{name}**\n"
        else:
            response += "**Tất cả phòng gym:**\n"
            for i, gym in enumerate(gyms, 1):
                name = gym['gymName']
                if gym.get('distance_km'):
                    name += f" ({format_distance_friendly(gym['distance_km'])})"
                response += f"{i}. **{name}**\n"
        
        return response

def get_response_with_history(user_input, conversation_history=None, longitude=None, latitude=None):
    """Hàm chính để xử lý yêu cầu của người dùng với lịch sử hội thoại"""
    try:
        if conversation_history is None:
            conversation_history = []
        
        conversation_context = build_conversation_context(conversation_history)
        
        # Thêm tin nhắn của người dùng vào lịch sử
        current_conversation = conversation_history.copy()
        current_conversation.append({
            "role": "user",
            "content": sanitize_text_for_json(user_input),
            "timestamp": datetime.now().isoformat()
        })
        
        # PRIORITY 1: Xử lý tìm kiếm Personal Trainer
        is_trainer_query, trainer_sql = classify_trainer_query(user_input, longitude, latitude)

        if is_trainer_query:
            print(f"🏋️ TRAINER_SEARCH: Detected trainer search request")

            # Xử lý tìm kiếm PT gần với tọa độ
            if longitude and latitude and any(keyword in user_input.lower() for keyword in ["gần", "near", "nearby", "xung quanh", "lân cận"]):
                max_distance = get_trainer_distance_preference(user_input)
                print(f"🎯 TRAINER SMART RADIUS: Bán kính được chọn: {max_distance}km")
                trainer_sql = build_nearby_trainer_query(longitude, latitude, max_distance)

            results = query_database(trainer_sql)

            if isinstance(results, str) or not results:
                response_text = "Không tìm thấy huấn luyện viên nào phù hợp với yêu cầu của bạn. Hãy thử mở rộng tiêu chí tìm kiếm!"
                current_conversation.append({
                    "role": "assistant",
                    "content": sanitize_text_for_json(response_text),
                    "timestamp": datetime.now().isoformat()
                })
                return {
                    "promptResponse": sanitize_text_for_json(response_text),
                    "conversation_history": current_conversation
                }

            trainers = [safe_get_trainer_data(row) for row in results]
            print(f"🎯 TRAINER_RESULT: Tìm thấy {len(trainers)} huấn luyện viên")

            is_nearby = longitude and latitude and any(kw in user_input.lower() for kw in ["gần", "near", "nearby"])
            prompt_response = create_trainer_response(trainers, user_input, is_nearby)

            current_conversation.append({
                "role": "assistant",
                "content": sanitize_text_for_json(prompt_response),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "trainers": trainers,
                "promptResponse": sanitize_text_for_json(prompt_response),
                "conversation_history": current_conversation
            }

        # PRIORITY 2: Xử lý tìm kiếm gym gần với tọa độ
        if longitude and latitude and any(keyword in user_input.lower() for keyword in ["gần", "near", "nearby", "xung quanh", "lân cận", "gần đây", "quanh đây"]):
            max_distance = get_nearby_distance_preference(user_input)
            print(f"🎯 SMART RADIUS: User input '{user_input}' → Bán kính được chọn: {max_distance}km")
            
            sql_query = build_nearby_gym_query(longitude, latitude, max_distance)
            results = query_database(sql_query)

            if isinstance(results, str) or not results:
                response_text = f"Không tìm thấy gym nào trong bán kính {max_distance}km. Hãy thử mở rộng khu vực tìm kiếm!"
                current_conversation.append({
                    "role": "assistant",
                    "content": sanitize_text_for_json(response_text),
                    "timestamp": datetime.now().isoformat()
                })
                return {
                    "promptResponse": sanitize_text_for_json(response_text),
                    "conversation_history": current_conversation
                }

            gyms = [safe_get_row_data(row) for row in results]
            print(f"🔍 DEBUG: Tìm thấy {len(gyms)} gym trong bán kính {max_distance}km")
            for i, gym in enumerate(gyms):
                print(f"  {i+1}. {gym['gymName']} - {gym.get('distance_km', 'N/A')}km")
            
            prompt_response = create_simple_response(gyms, user_input, is_nearby=True)

            current_conversation.append({
                "role": "assistant",
                "content": sanitize_text_for_json(prompt_response),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "gyms": gyms, 
                "promptResponse": sanitize_text_for_json(prompt_response),
                "conversation_history": current_conversation
            }
        
        # PRIORITY 3: Truy vấn cơ sở dữ liệu thông thường (gym search)
        is_db_query, sql_query = classify_query_with_context(user_input, conversation_context)
        print(f"🔍 QUERY_CLASSIFICATION: is_db_query={is_db_query}, user_input='{user_input}'")
        
        if is_db_query:
            results = query_database(sql_query)
            if isinstance(results, str) or not results:
                response_text = "Không tìm thấy gym nào phù hợp với tiêu chí của bạn. Hãy thử tìm kiếm khác!"
                current_conversation.append({
                    "role": "assistant",
                    "content": sanitize_text_for_json(response_text),
                    "timestamp": datetime.now().isoformat()
                })
                return {
                    "promptResponse": sanitize_text_for_json(response_text),
                    "conversation_history": current_conversation
                }

            gyms = [safe_get_row_data(row) for row in results]
            print(f"🎯 SEARCH_RESULT: Tìm thấy {len(gyms)} gym từ database")
            
            prompt_response = create_simple_response(gyms, user_input)

            current_conversation.append({
                "role": "assistant",
                "content": sanitize_text_for_json(prompt_response),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "gyms": gyms, 
                "promptResponse": sanitize_text_for_json(prompt_response),
                "conversation_history": current_conversation
            }

        # PRIORITY 4: Hội thoại tự do với Gemini
        enhanced_context = f"""
        Bạn là FitBridge AI - trợ lý tìm kiếm phòng gym và huấn luyện viên cá nhân thân thiện và chuyên nghiệp tại Việt Nam.
        
        Khả năng:
        - Đưa ra gợi ý phòng gym, huấn luyện viên cá nhân (PT) và thông tin chi tiết
        - Tư vấn thể dục và lịch tập luyện dựa trên mục tiêu
        - Chia sẻ kiến thức về sức khỏe và thể hình
        - Nhớ ngữ cảnh hội thoại để tư vấn nhất quán
        - Chỉ trả lời các câu hỏi về gym, PT, thể dục, sức khỏe
        
        Ví dụ: Nếu người dùng hỏi về 1 chủ đề bất kỳ không liên quan đến gym, PT, thể dục, sức khỏe, 
        bạn hãy trả lời rằng: "Xin lỗi, tôi chỉ có thể hỗ trợ các câu hỏi liên quan đến gym, huấn luyện viên cá nhân, thể dục. Những lĩnh vực khác không nằm trong chuyên môn của tôi."
        
        Phong cách: Thân thiện, chuyên nghiệp, hiểu biết. Không sử dụng emoji.
        Luôn kết thúc bằng câu hỏi hoặc gợi ý hành động.
        
        Lịch sử hội thoại:
        {conversation_context}
        """
        
        prompt = f"{enhanced_context}\n\nCâu hỏi của người dùng: {user_input}"
        response = model.generate_content(prompt)
        
        current_conversation.append({
            "role": "assistant", 
            "content": sanitize_text_for_json(response.text),
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "promptResponse": sanitize_text_for_json(response.text),
            "conversation_history": current_conversation
        }

    except Exception as e:
        print(f"Lỗi trong get_response_with_history: {str(e)}")
        error_response = "Xin lỗi, đã xảy ra lỗi hệ thống. Vui lòng thử lại!"

        if 'current_conversation' in locals():
            current_conversation.append({
                "role": "assistant", 
                "content": sanitize_text_for_json(error_response),
                "timestamp": datetime.now().isoformat()
            })
            return {
                "promptResponse": sanitize_text_for_json(error_response),
                "conversation_history": current_conversation
            }
        
        return {"promptResponse": sanitize_text_for_json(error_response)}