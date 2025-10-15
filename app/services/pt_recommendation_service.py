# app/services/pt_recommendation_service.py - PT recommendation and response formatting

from app.utils.format_utils import format_distance_friendly


def create_trainer_response(trainers, user_input, is_nearby=False):
    """Tạo phản hồi cho kết quả tìm kiếm Personal Trainer (tối đa 10 PT, mixed gym và freelance)"""
    if not trainers:
        return "Không tìm thấy huấn luyện viên nào phù hợp với yêu cầu của bạn. Hãy thử mở rộng tiêu chí tìm kiếm!"

    # Đếm số lượng PT theo loại
    gym_count = sum(1 for t in trainers if t.get('ptType') == 'gym')
    freelance_count = sum(1 for t in trainers if t.get('ptType') == 'freelance')

    if len(trainers) == 1:
        trainer = trainers[0]
        response = f"**{trainer['fullName']}**"

        # Hiển thị loại PT
        if trainer.get('ptType') == 'freelance':
            response += " 💼 (Huấn luyện viên tự do)"

        if trainer.get('gymName') and trainer.get('ptType') == 'gym':
            response += f"\nPhòng gym: **{trainer['gymName']}**"

        if trainer.get('distance_km'):
            response += f" - {format_distance_friendly(trainer['distance_km'])}"

        if trainer.get('gymAddress') and trainer.get('ptType') == 'gym':
            response += f"\nĐịa chỉ gym: {trainer['gymAddress']}"
        elif trainer.get('ptType') == 'freelance':
            response += f"\n📍 Địa điểm: {trainer.get('gymAddress', 'Linh hoạt theo yêu cầu')}"

        if trainer.get('experience'):
            response += f"\nKinh nghiệm: {trainer['experience']} năm"

        if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
            goals = ', '.join(trainer['goalTrainings'])
            response += f"\nChuyên môn: {goals}"

        if trainer.get('certificates') and len(trainer['certificates']) > 0:
            response += f"\nChứng chỉ: {len(trainer['certificates'])} chứng chỉ"

        if trainer.get('bio'):
            response += f"\nGiới thiệu: {trainer['bio']}"

        return response

    else:
        # Hiển thị tất cả PT (đã mixed sẵn từ query, tối đa 10)
        response = f"**Tìm thấy {len(trainers)} huấn luyện viên**"

        if gym_count > 0 and freelance_count > 0:
            response += f" *({gym_count} PT gym, {freelance_count} PT tự do)*"

        response += ":\n\n"

        for i, trainer in enumerate(trainers, 1):
            name = trainer['fullName']

            # Badge và thông tin gym/freelance
            if trainer.get('ptType') == 'freelance':
                type_badge = " - PT tự do"
                location_info = ""
                if trainer.get('distance_km'):
                    location_info = f"Cách bạn {format_distance_friendly(trainer['distance_km'])}"
            else:
                type_badge = ""
                gym_name = trainer.get('gymName', '')
                location_info = f"\nLàm việc tại {gym_name}\n" if gym_name else ""
                if trainer.get('distance_km'):
                    location_info += f"Cách bạn {format_distance_friendly(trainer['distance_km'])}"

            experience_info = ""
            if trainer.get('experience'):
                experience_info = f"\nCó {trainer['experience']} năm kinh nghiệm"

            response += f"{i}. **{name}**{type_badge}{location_info}{experience_info}\n"

            # Chuyên môn (nếu có)
            if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
                goals = ', '.join(trainer['goalTrainings'][:3])
                response += f"Chuyên môn: {goals}\n"

            response += "\n"

        return response.rstrip()


def format_trainer_detailed_info(trainer):
    """Format chi tiết thông tin một PT"""
    response = f"**Thông tin huấn luyện viên: {trainer['fullName']}**\n\n"

    # PT Type badge
    if trainer.get('ptType') == 'freelance':
        response += "**Huấn luyện viên tự do**\n\n"

    # Basic info
    if trainer.get('email'):
        response += f"📧 Email: {trainer['email']}\n"
    if trainer.get('phoneNumber'):
        response += f"📱 Điện thoại: {trainer['phoneNumber']}\n"

    # Gym info for gym PTs
    if trainer.get('ptType') == 'gym' and trainer.get('gymName'):
        response += f"\n🏢 Phòng gym: **{trainer['gymName']}**\n"
        if trainer.get('gymAddress'):
            response += f"📍 Địa chỉ: {trainer['gymAddress']}\n"
        if trainer.get('distance_km'):
            response += f"📏 Khoảng cách: {format_distance_friendly(trainer['distance_km'])}\n"
    elif trainer.get('ptType') == 'freelance':
        response += f"\n📍 Địa điểm tập: Linh hoạt theo yêu cầu\n"
        if trainer.get('distance_km'):
            response += f"📏 Khoảng cách: {format_distance_friendly(trainer['distance_km'])}\n"

    # Professional info
    if trainer.get('experience'):
        response += f"\nKinh nghiệm: {trainer['experience']} năm\n"

    if trainer.get('certificates') and len(trainer['certificates']) > 0:
        response += f"🏆 Chứng chỉ: {len(trainer['certificates'])} chứng chỉ chuyên môn\n"

    if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
        goals = ', '.join(trainer['goalTrainings'])
        response += f"🎯 Chuyên môn: {goals}\n"

    if trainer.get('bio'):
        response += f"\n📝 Giới thiệu: {trainer['bio']}\n"

    # Physical stats
    physical_info = []
    if trainer.get('height'):
        physical_info.append(f"Chiều cao: {trainer['height']}cm")
    if trainer.get('weight'):
        physical_info.append(f"Cân nặng: {trainer['weight']}kg")

    if physical_info:
        response += f"\n📊 Thể trạng: {', '.join(physical_info)}\n"

    return response
