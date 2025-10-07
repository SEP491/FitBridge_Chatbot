# app/utils/format_utils.py - Formatting and display utilities

def format_distance_friendly(distance_km):
    """Định dạng khoảng cách theo cách thân thiện với người dùng"""
    if distance_km < 0.5:
        return f"{int(distance_km * 1000)}m"
    elif distance_km < 1:
        return f"{distance_km:.1f}km (đi bộ được)" 
    elif distance_km < 3:
        return f"{distance_km:.1f}km (gần)"
    elif distance_km < 5:
        return f"{distance_km:.1f}km (xe đạp/xe máy)"
    elif distance_km < 10:
        return f"{distance_km:.1f}km (ô tô/xe máy)"
    else:
        return f"{distance_km:.1f}km (xa)"