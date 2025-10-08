# app/services/pt_recommendation_service.py - PT recommendation and response formatting

from datetime import datetime
from app.utils.format_utils import format_distance_friendly
from app.models.trainer_models import safe_get_trainer_data


def create_trainer_response(trainers, user_input, is_nearby=False):
    """Tạo phản hồi cho kết quả tìm kiếm Personal Trainer"""
    if not trainers:
        return "Không tìm thấy huấn luyện viên nào phù hợp với yêu cầu của bạn. Hãy thử mở rộng tiêu chí tìm kiếm!"

    if len(trainers) == 1:
        trainer = trainers[0]
        response = f"**{trainer['fullName']}**"

        if trainer.get('gymName'):
            response += f"\nPhòng gym: **{trainer['gymName']}**"

        if trainer.get('distance_km'):
            response += f" - {format_distance_friendly(trainer['distance_km'])}"

        if trainer.get('gymAddress'):
            response += f"\nĐịa chỉ gym: {trainer['gymAddress']}"

        if trainer.get('experience'):
            response += f"\nKinh nghiệm: {trainer['experience']} năm"

        if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
            goals = ', '.join(trainer['goalTrainings'])
            response += f"\nChuyên môn: {goals}"

        if trainer.get('certificates') and len(trainer['certificates']) > 0:
            response += f"\nChứng chỉ: {len(trainer['certificates'])} chứng chỉ"

        return response

    elif len(trainers) <= 5:
        response = f"**Tìm thấy {len(trainers)} huấn luyện viên phù hợp:**\n\n"

        for i, trainer in enumerate(trainers, 1):
            name = trainer['fullName']
            gym_info = f" - {trainer['gymName']}" if trainer.get('gymName') else ""

            distance_info = ""
            if trainer.get('distance_km'):
                distance_info = f" ({format_distance_friendly(trainer['distance_km'])})"

            experience_info = ""
            if trainer.get('experience'):
                experience_info = f" - {trainer['experience']} năm kinh nghiệm"

            goals_info = ""
            if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
                goals_info = f"\n  Chuyên môn: {', '.join(trainer['goalTrainings'][:3])}"

            response += f"{i}. **{name}**{gym_info}{distance_info}{experience_info}{goals_info}\n\n"

        return response

    else:
        # Group trainers by gym
        trainers_by_gym = {}
        for trainer in trainers:
            gym_name = trainer.get('gymName', 'Gym không xác định')
            if gym_name not in trainers_by_gym:
                trainers_by_gym[gym_name] = {
                    'trainers': [],
                    'distance_km': trainer.get('distance_km'),
                    'gymAddress': trainer.get('gymAddress'),
                    'gymHotResearch': trainer.get('gymHotResearch', False)
                }
            trainers_by_gym[gym_name]['trainers'].append(trainer)

        # Sort gyms by distance and hot status
        sorted_gyms = sorted(
            trainers_by_gym.items(),
            key=lambda x: (
                x[1]['distance_km'] if x[1]['distance_km'] is not None else float('inf'),
                not x[1]['gymHotResearch']
            )
        )

        response = f"**Tìm thấy {len(trainers)} huấn luyện viên tại {len(trainers_by_gym)} phòng gym:**\n\n"

        for gym_name, gym_data in sorted_gyms[:10]:  # Hiển thị tối đa 10 gym
            gym_trainers = gym_data['trainers']
            distance_info = ""
            if gym_data['distance_km']:
                distance_info = f" - {format_distance_friendly(gym_data['distance_km'])}"

            hot_badge = " 🔥" if gym_data['gymHotResearch'] else ""

            response += f"**{gym_name}**{distance_info}{hot_badge}\n"

            # if gym_data['gymAddress']:
            #     response += f"Địa chỉ: {gym_data['gymAddress']}\n"

            response += f"Có {len(gym_trainers)} huấn luyện viên:\n"

            for i, trainer in enumerate(gym_trainers[:3], 1):  # Hiển thị tối đa 3 PT/gym
                exp_info = f" ({trainer['experience']} năm)" if trainer.get('experience') else ""
                response += f"  {i}. {trainer['fullName']}{exp_info}\n"

            if len(gym_trainers) > 3:
                response += f"  ... và {len(gym_trainers) - 3} huấn luyện viên khác\n"

            # response += "\n"

        if len(sorted_gyms) > 10:
            response += f"\n_Còn {len(sorted_gyms) - 10} phòng gym khác với huấn luyện viên..._"

        return response


def format_trainer_detailed_info(trainer):
    """Format chi tiết thông tin một PT"""
    response = f"**Thông tin huấn luyện viên: {trainer['fullName']}**\n\n"

    # Basic info
    if trainer.get('email'):
        response += f"📧 Email: {trainer['email']}\n"
    if trainer.get('phoneNumber'):
        response += f"📱 Điện thoại: {trainer['phoneNumber']}\n"

    # Gym info
    if trainer.get('gymName'):
        response += f"\n🏢 Phòng gym: **{trainer['gymName']}**\n"
        if trainer.get('gymAddress'):
            response += f"📍 Địa chỉ: {trainer['gymAddress']}\n"
        if trainer.get('distance_km'):
            response += f"📏 Khoảng cách: {format_distance_friendly(trainer['distance_km'])}\n"

    # Professional info
    if trainer.get('experience'):
        response += f"\n💼 Kinh nghiệm: {trainer['experience']} năm\n"

    if trainer.get('certificates') and len(trainer['certificates']) > 0:
        response += f"🏆 Chứng chỉ: {len(trainer['certificates'])} chứng chỉ chuyên môn\n"

    if trainer.get('goalTrainings') and len(trainer['goalTrainings']) > 0:
        goals = ', '.join(trainer['goalTrainings'])
        response += f"🎯 Chuyên môn: {goals}\n"

    # Physical stats
    physical_info = []
    if trainer.get('height'):
        physical_info.append(f"Chiều cao: {trainer['height']}cm")
    if trainer.get('weight'):
        physical_info.append(f"Cân nặng: {trainer['weight']}kg")

    if physical_info:
        response += f"\n📊 Thể trạng: {', '.join(physical_info)}\n"

    return response

