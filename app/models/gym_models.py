# app/models/gym_models.py - Gym-related data processing functions

def safe_get_row_data(row):
    """Trích xuất dữ liệu từ hàng cơ sở dữ liệu một cách an toàn"""
    try:

        def get_attr(attr_name, default=None):
            try:
                # Use dictionary access for psycopg dict_row
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
        
        gym_data = {
            "id": str(get_attr('id', '')),
            "gymName": get_attr('gymname', ''),
            "fullName": get_attr('fullname', ''),
            "address": get_attr('gymaddress', ''),
            "taxCode": get_attr('taxcode', ''),
            "longitude": get_attr('longitude'),
            "latitude": get_attr('latitude'),
            "hotResearch": get_bool_attr('hotresearch', False),
            "accountStatus": get_attr('accountstatus', 'Active'),
            "email": get_attr('email', ''),
            "phoneNumber": get_attr('phonenumber', ''),
            "gymDescription": get_attr('gymdescription', ''),
            "avatarUrl": get_attr('avatarurl', ''),
            "gymImages": get_attr('gymimages', []),
            "createdAt": format_date(get_attr('createdat')),
            "updatedAt": format_date(get_attr('updatedat')),
            "dob": format_date(get_attr('dob'))
        }
        
        # Handle distance for nearby queries
        distance = get_attr('distance_km')
        if distance is not None:
            try:
                gym_data["distance_km"] = round(float(distance), 2)
            except:
                gym_data["distance_km"] = 0
        
        return gym_data
        
    except Exception as e:
        print(f"Lỗi trong safe_get_row_data: {str(e)}")
        return {
            "id": "",
            "gymName": "Phòng gym không xác định",
            "fullName": "",
            "address": "",
            "taxCode": "",
            "longitude": None,
            "latitude": None,
            "hotResearch": False,
            "accountStatus": "Active",
            "email": "",
            "phoneNumber": "",
            "gymDescription": "",
            "avatarUrl": "",
            "gymImages": [],
            "createdAt": None,
            "updatedAt": None,
            "dob": None
        }