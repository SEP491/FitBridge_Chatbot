# app/models/trainer_models.py - Trainer-related data processing functions

def safe_get_trainer_data(row):
    """Trích xuất dữ liệu Personal Trainer từ hàng cơ sở dữ liệu một cách an toàn"""
    try:
        def get_attr(attr_name, default=None):
            try:
                value = row.get(attr_name, default) if row else default
                return value
            except (AttributeError, KeyError):
                return default

        def get_bool_attr(attr_name, default=False):
            try:
                value = row.get(attr_name, default) if row else default
                if value is None:
                    return default
                if isinstance(value, int):
                    return bool(value)
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes', 'on')
                return bool(value)
            except (AttributeError, KeyError):
                return default

        def format_date(date_field):
            if date_field:
                try:
                    return date_field.isoformat() if hasattr(date_field, 'isoformat') else str(date_field)
                except:
                    return None
            return None

        trainer_data = {
            "id": str(get_attr('id', '')),
            "fullName": get_attr('fullname', ''),
            "email": get_attr('email', ''),
            "phoneNumber": get_attr('phonenumber', ''),
            "isMale": get_bool_attr('ismale', True),
            "dob": format_date(get_attr('dob')),
            "avatarUrl": get_attr('avatarurl', ''),
            "bio": get_attr('bio', ''),
            "accountStatus": get_attr('accountstatus', 'Active'),
            "createdAt": format_date(get_attr('createdat')),
            "updatedAt": format_date(get_attr('updatedat')),

            # User Details
            "experience": get_attr('experience'),
            "certificates": get_attr('certificates', []),
            "height": get_attr('height'),
            "weight": get_attr('weight'),
            "biceps": get_attr('biceps'),
            "chest": get_attr('chest'),
            "waist": get_attr('waist'),

            # Goal Trainings
            "goalTrainings": get_attr('goal_trainings', []),

            # PT Type (gym or freelance)
            "ptType": get_attr('pt_type', 'gym'),
            "isFreelance": get_bool_attr('is_freelance', False),

            # Gym Information
            "gymId": str(get_attr('gym_id', '')) if get_attr('gym_id') else None,
            "gymName": get_attr('gymname', ''),
            "gymAddress": get_attr('gymaddress', ''),
            "gymLatitude": get_attr('gym_latitude'),
            "gymLongitude": get_attr('gym_longitude'),
            "gymHotResearch": get_bool_attr('gym_hotresearch', False),
        }

        # Handle distance for nearby queries
        distance = get_attr('distance_km')
        if distance is not None:
            try:
                trainer_data["distance_km"] = round(float(distance), 2)
            except:
                trainer_data["distance_km"] = 0

        return trainer_data

    except Exception as e:
        print(f"Lỗi trong safe_get_trainer_data: {str(e)}")
        return {
            "id": "",
            "fullName": "Huấn luyện viên không xác định",
            "email": "",
            "phoneNumber": "",
            "isMale": True,
            "dob": None,
            "avatarUrl": "",
            "bio": "",
            "accountStatus": "Active",
            "createdAt": None,
            "updatedAt": None,
            "experience": None,
            "certificates": [],
            "height": None,
            "weight": None,
            "biceps": None,
            "chest": None,
            "waist": None,
            "goalTrainings": [],
            "ptType": "gym",
            "isFreelance": False,
            "gymId": None,
            "gymName": "",
            "gymAddress": "",
            "gymLatitude": None,
            "gymLongitude": None,
            "gymHotResearch": False,
            "distance_km": None
        }
