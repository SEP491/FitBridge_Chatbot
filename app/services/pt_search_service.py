# app/services/pt_search_service.py - Personal Trainer search logic and query building

import math
import re
from app.utils.text_utils import normalize_vietnamese_text
from app.database.connection import query_database


def build_nearby_trainer_query(longitude, latitude, max_distance_km=10):
    """
    Xây dựng truy vấn SQL để tìm Personal Trainer gần người dùng
    Ưu tiên trainer từ các gym gần nhất
    """
    lat_range = max_distance_km / 111.0
    lng_range = max_distance_km / (111.0 * abs(math.cos(math.radians(latitude))))

    return f"""
    WITH NearbyGyms AS (
        -- Tìm các gym gần người dùng
        SELECT 
            gym."Id" as gym_id,
            gym."GymName" as gymname,
            COALESCE(
                CONCAT_WS(', ', 
                    NULLIF(a."HouseNumber", ''), 
                    NULLIF(a."Street", ''), 
                    NULLIF(a."Ward", ''), 
                    NULLIF(a."District", ''), 
                    NULLIF(a."City", '')
                ), 
                'Địa chỉ chưa cập nhật'
            ) as gymaddress,
            CAST(gym."Longitude" AS DOUBLE PRECISION) AS gym_longitude,
            CAST(gym."Latitude" AS DOUBLE PRECISION) AS gym_latitude,
            gym."hotResearch" as gym_hotresearch,
            6371.0 * 2 * ASIN(
                SQRT(
                    POWER(SIN(RADIANS({latitude} - CAST(gym."Latitude" AS DOUBLE PRECISION)) / 2), 2) +
                    COS(RADIANS({latitude})) * COS(RADIANS(CAST(gym."Latitude" AS DOUBLE PRECISION))) *
                    POWER(SIN(RADIANS({longitude} - CAST(gym."Longitude" AS DOUBLE PRECISION)) / 2), 2)
                )
            ) AS distance_km
        FROM "AspNetUsers" gym
        LEFT JOIN "Addresses" a ON gym."Id" = a."CustomerId" AND a."IsEnabled" = true
        WHERE gym."AccountStatus" = 'Active'
            AND gym."GymName" IS NOT NULL 
            AND gym."GymName" != ''
            AND gym."Latitude" IS NOT NULL 
            AND gym."Longitude" IS NOT NULL
            AND CAST(gym."Latitude" AS DOUBLE PRECISION) BETWEEN {latitude - lat_range} AND {latitude + lat_range}
            AND CAST(gym."Longitude" AS DOUBLE PRECISION) BETWEEN {longitude - lng_range} AND {longitude + lng_range}
    ),
    RankedGyms AS (
        SELECT *
        FROM NearbyGyms
        WHERE distance_km <= {max_distance_km}
    ),
    TrainersWithGoals AS (
        -- Lấy tất cả PT và thông tin mục tiêu tập luyện
        SELECT 
            pt."Id" as id,
            pt."FullName" as fullname,
            pt."Email" as email,
            pt."PhoneNumber" as phonenumber,
            pt."IsMale" as ismale,
            pt."Dob" as dob,
            pt."AvatarUrl" as avatarurl,
            pt."AccountStatus" as accountstatus,
            pt."CreatedAt" as createdat,
            pt."UpdatedAt" as updatedat,
            pt."GymOwnerId" as gym_id,
            ud."Experience" as experience,
            ud."Certificates" as certificates,
            ud."Height" as height,
            ud."Weight" as weight,
            ud."Biceps" as biceps,
            ud."Chest" as chest,
            ud."Waist" as waist,
            ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings
        FROM "AspNetUsers" pt
        LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
        LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
        LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
        WHERE pt."AccountStatus" = 'Active'
            AND pt."GymOwnerId" IS NOT NULL
        GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                 ud."Weight", ud."Biceps", ud."Chest", ud."Waist"
    )
    -- Kết hợp PT với gym gần nhất
    SELECT 
        t.*,
        g.gym_id,
        g.gymname,
        g.gymaddress,
        g.gym_latitude,
        g.gym_longitude,
        g.gym_hotresearch,
        g.distance_km
    FROM TrainersWithGoals t
    INNER JOIN RankedGyms g ON t.gym_id = g.gym_id
    ORDER BY 
        g.distance_km ASC,
        g.gym_hotresearch DESC,
        t.experience DESC NULLS LAST,
        t.fullname ASC
    """


def build_trainer_search_query(user_input, longitude=None, latitude=None):
    """
    Xây dựng truy vấn tìm kiếm PT thông minh dựa trên input của người dùng
    """
    try:
        user_input_lower = user_input.lower()

        # Phân tích từ khóa tìm kiếm
        search_keywords = []
        goal_keywords = []

        # Mapping mục tiêu tập luyện phổ biến
        goal_mapping = {
            'Giảm cân': ['giảm cân', 'lose weight', 'weight loss', 'fat loss', 'giam can'],
            'Tăng cơ': ['tăng cơ', 'build muscle', 'muscle gain', 'bulk', 'tang co'],
            'Thể hình': ['thể hình', 'bodybuilding', 'physique', 'the hinh'],
            'Sức mạnh': ['sức mạnh', 'strength', 'power', 'suc manh'],
            'Sức bền': ['sức bền', 'endurance', 'stamina', 'cardio', 'suc ben'],
            'Linh hoạt': ['linh hoạt', 'flexibility', 'yoga', 'stretching', 'linh hoat'],
            'Phục hồi chức năng': ['phục hồi', 'rehabilitation', 'recovery', 'injury', 'phuc hoi'],
            'Thể lực tổng hợp': ['thể lực', 'fitness', 'general fitness', 'the luc'],
        }

        # Tìm mục tiêu trong input
        for goal, keywords in goal_mapping.items():
            if any(kw in user_input_lower for kw in keywords):
                goal_keywords.append(goal)

        # Trích xuất các từ khóa quan trọng (bỏ các từ liên quan đến goal, gender và common words)
        stop_words = {
            # Common words
            'tìm', 'find', 'search', 'tim', 'cho', 'giúp', 'giup', 'help', 'me',
            'tôi', 'toi', 'mình', 'minh', 'của', 'cua', 'my', 'i', 'we', 'us',
            'muốn', 'muon', 'cần', 'can', 'need', 'want', 'hãy', 'hay', 'please',
            'với', 'voi', 'và', 'va', 'or', 'and', 'with',

            # PT related
            'pt', 'huấn luyện viên', 'huan luyen vien', 'trainer', 'hlv',
            'personal', 'coach', 'giáo viên', 'giao vien', 'thể dục', 'the duc',

            # Goal related
            'chuyên', 'chuyen', 'giảm', 'giam', 'cân', 'can', 'tăng', 'tang',
            'cơ', 'co', 'thể', 'the', 'hình', 'hinh', 'sức', 'suc', 'mạnh',
            'manh', 'bền', 'ben',

            # Gender related
            'nữ', 'nu', 'nam', 'male', 'female', 'girl', 'boy', 'woman', 'man',
            'đàn ông', 'dan ong', 'đàn bà', 'dan ba', 'phụ nữ', 'phu nu'
        }
        words = re.findall(r'\b\w+\b', normalize_vietnamese_text(user_input))
        search_keywords = [w for w in words if w not in stop_words and len(w) >= 2][:3]

        # Xây dựng base conditions cho PT
        pt_base_conditions = [
            'pt."AccountStatus" = \'Active\'',
            'pt."GymOwnerId" IS NOT NULL'
        ]

        # Nếu có tọa độ và yêu cầu tìm gần
        if longitude and latitude and any(kw in user_input_lower for kw in
            ['gần', 'near', 'nearby', 'xung quanh', 'lân cận']):
            max_distance = get_trainer_distance_preference(user_input)
            return build_nearby_trainer_query(longitude, latitude, max_distance)

        # Thêm filter theo goal trainings (JOIN trực tiếp với GoalTrainings)
        goal_join_conditions = []
        if goal_keywords:
            goal_list = "', '".join([g.replace("'", "''") for g in goal_keywords])
            goal_join_conditions.append(f"gt.\"Name\" IN ('{goal_list}')")

        # Xây dựng search conditions cho tên PT
        name_conditions = []

        # Kiểm tra gender - Ưu tiên cao hơn, check trước khi xử lý keywords
        if 'nữ' in user_input_lower or 'female' in user_input_lower or 'nu' in normalize_vietnamese_text(user_input):
            pt_base_conditions.append('pt."IsMale" = false')
        elif 'nam' in user_input_lower or 'male' in user_input_lower:
            pt_base_conditions.append('pt."IsMale" = true')

        # Search by name keywords (chỉ khi có keywords hợp lệ)
        if search_keywords:
            for keyword in search_keywords:
                if keyword and len(keyword) >= 3:  # Tăng minimum length lên 3 để tránh noise
                    safe_kw = keyword.replace("'", "''")
                    name_conditions.append(f'pt."FullName" ILIKE \'%{safe_kw}%\'')

        # Build WHERE clause - QUAN TRỌNG: Chỉ thêm name_conditions nếu có
        where_parts = []
        where_parts.append(f"({' AND '.join(pt_base_conditions)})")

        if goal_join_conditions:
            where_parts.append(f"({' AND '.join(goal_join_conditions)})")

        # CHỈ thêm name_conditions nếu THỰC SỰ có keywords hợp lệ
        # KHÔNG thêm vào where_clause nếu rỗng
        if name_conditions:
            where_parts.append(f"({' OR '.join(name_conditions)})")

        where_clause = " AND ".join(where_parts)

        # Build final query với cấu trúc mới
        query = f"""
        WITH FilteredPTs AS (
            SELECT DISTINCT
                pt."Id" as pt_id
            FROM "AspNetUsers" pt
            LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
            LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
            WHERE {where_clause}
        ),
        TrainersWithGoals AS (
            SELECT 
                pt."Id" as id,
                pt."FullName" as fullname,
                pt."Email" as email,
                pt."PhoneNumber" as phonenumber,
                pt."IsMale" as ismale,
                pt."Dob" as dob,
                pt."AvatarUrl" as avatarurl,
                pt."AccountStatus" as accountstatus,
                pt."CreatedAt" as createdat,
                pt."UpdatedAt" as updatedat,
                pt."GymOwnerId" as gym_id,
                ud."Experience" as experience,
                ud."Certificates" as certificates,
                ud."Height" as height,
                ud."Weight" as weight,
                ud."Biceps" as biceps,
                ud."Chest" as chest,
                ud."Waist" as waist,
                ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings
            FROM "AspNetUsers" pt
            INNER JOIN FilteredPTs fp ON pt."Id" = fp.pt_id
            LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
            LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
            LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
            GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                     ud."Weight", ud."Biceps", ud."Chest", ud."Waist"
        )
        SELECT 
            t.*,
            gym."Id" as gym_id,
            gym."GymName" as gymname,
            COALESCE(
                CONCAT_WS(', ', 
                    NULLIF(a."HouseNumber", ''), 
                    NULLIF(a."Street", ''), 
                    NULLIF(a."Ward", ''), 
                    NULLIF(a."District", ''), 
                    NULLIF(a."City", '')
                ), 
                'Địa chỉ chưa cập nhật'
            ) as gymaddress,
            CAST(gym."Latitude" AS DOUBLE PRECISION) as gym_latitude,
            CAST(gym."Longitude" AS DOUBLE PRECISION) as gym_longitude,
            gym."hotResearch" as gym_hotresearch
        FROM TrainersWithGoals t
        INNER JOIN "AspNetUsers" gym ON t.gym_id = gym."Id"
        LEFT JOIN "Addresses" a ON gym."Id" = a."CustomerId" AND a."IsEnabled" = true
        WHERE gym."AccountStatus" = 'Active'
        ORDER BY 
            gym."hotResearch" DESC,
            t.experience DESC NULLS LAST,
            t.fullname ASC
        """

        return query

    except Exception as e:
        print(f"Lỗi trong build_trainer_search_query: {str(e)}")
        return None


def get_trainer_distance_preference(user_input):
    """Phân tích khoảng cách tìm kiếm PT tương tự như gym"""
    user_input_lower = user_input.lower()

    # Tìm số km cụ thể
    km_match = re.search(r'(\d+)\s*km', user_input_lower)
    if km_match:
        distance = int(km_match.group(1))
        return max(1, min(distance, 50))

    # Pattern matching
    distance_patterns = {
        2: [r'(rất gần|very close|đi bộ)'],
        5: [r'(gần|nearby|close)'],
        10: [r'(khu vực|trong khu|area)'],
        15: [r'(xa hơn|farther)'],
        25: [r'(rất xa|very far)'],
        50: [r'(tất cả|all|bất kỳ)']
    }

    for distance, patterns in distance_patterns.items():
        for pattern in patterns:
            if re.search(pattern, user_input_lower):
                return distance

    return 10  # Default


def detect_trainer_search_intent(user_input):
    """Phát hiện ý định tìm kiếm Personal Trainer"""
    user_lower = user_input.lower()

    # Từ khóa chỉ rõ tìm PT
    pt_keywords = [
        r'\bpt\b', r'huấn luyện viên', r'personal trainer', r'trainer',
        r'hlv', r'coach', r'giáo viên thể dục',
        r'tìm pt', r'find trainer', r'tìm trainer'
    ]

    # Kiểm tra có từ khóa PT không
    has_pt_keyword = any(re.search(pattern, user_lower) for pattern in pt_keywords)

    # Ngữ cảnh về tập luyện cá nhân
    training_context = [
        r'tập riêng', r'tập cá nhân', r'personal training',
        r'hướng dẫn tập', r'chỉ tập', r'dạy tập',
        r'tư vấn tập', r'lên lịch tập'
    ]

    has_training_context = any(re.search(pattern, user_lower) for pattern in training_context)

    # Mục tiêu cụ thể
    has_specific_goal = any(goal in user_lower for goal in [
        'giảm cân', 'tăng cơ', 'thể hình', 'sức mạnh', 'sức bền',
        'lose weight', 'build muscle', 'bodybuilding', 'strength'
    ])

    return has_pt_keyword or (has_training_context and has_specific_goal)


def classify_trainer_query(user_input, longitude=None, latitude=None):
    """
    Phân loại truy vấn tìm kiếm PT và tạo SQL
    Returns: (is_trainer_query, sql_query)
    """
    try:
        if not detect_trainer_search_intent(user_input):
            return False, None

        sql_query = build_trainer_search_query(user_input, longitude, latitude)

        if sql_query:
            print(f"✅ TRAINER_SEARCH: Query generated for '{user_input}'")
            return True, sql_query

        return False, None

    except Exception as e:
        print(f"Lỗi trong classify_trainer_query: {str(e)}")
        return False, None
