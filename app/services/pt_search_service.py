# app/services/pt_search_service.py - Personal Trainer search logic and query building

import math
import re
from app.utils.text_utils import normalize_vietnamese_text
from app.database.connection import query_database


def build_nearby_trainer_query(longitude, latitude, max_distance_km=10, user_input=""):
    """
    Xây dựng truy vấn SQL để tìm Personal Trainer gần người dùng
    Bao gồm cả PT gym và PT freelance, mixed và giới hạn 10 kết quả
    """
    lat_range = max_distance_km / 111.0
    lng_range = max_distance_km / (111.0 * abs(math.cos(math.radians(latitude))))

    # Extract experience requirement nếu có
    exp_operator, exp_years = extract_experience_requirement(user_input)
    experience_filter = ""
    if exp_operator and exp_years:
        experience_filter = f"\n        HAVING ud.\"Experience\" {exp_operator} {exp_years}"
        print(f"🎯 EXPERIENCE_FILTER (nearby): Lọc PT có kinh nghiệm {exp_operator} {exp_years} năm")

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
        -- Lấy tất cả PT (gym và freelance) và thông tin mục tiêu tập luyện
        SELECT 
            pt."Id" as id,
            pt."FullName" as fullname,
            pt."Email" as email,
            pt."PhoneNumber" as phonenumber,
            pt."IsMale" as ismale,
            pt."Dob" as dob,
            pt."AvatarUrl" as avatarurl,
            pt."Bio" as bio,
            pt."AccountStatus" as accountstatus,
            pt."CreatedAt" as createdat,
            pt."UpdatedAt" as updatedat,
            pt."GymOwnerId" as pt_gym_id,
            pt."Latitude" as pt_latitude,
            pt."Longitude" as pt_longitude,
            ud."Experience" as experience,
            ud."Certificates" as certificates,
            ud."Height" as height,
            ud."Weight" as weight,
            ud."Biceps" as biceps,
            ud."Chest" as chest,
            ud."Waist" as waist,
            ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings,
            -- Kiểm tra xem có package freelance không
            CASE 
                WHEN COUNT(DISTINCT pfp."Id") > 0 THEN true 
                ELSE false 
            END as is_freelance
        FROM "AspNetUsers" pt
        LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
        LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
        LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
        LEFT JOIN "PTFreelancePackages" pfp ON pt."Id" = pfp."PtId" AND pfp."IsEnabled" = true
        WHERE pt."AccountStatus" = 'Active'
            AND (pt."GymOwnerId" IS NOT NULL OR EXISTS (
                SELECT 1 FROM "PTFreelancePackages" pfp2 
                WHERE pfp2."PtId" = pt."Id" AND pfp2."IsEnabled" = true
            ))
        GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                 ud."Weight", ud."Biceps", ud."Chest", ud."Waist"{experience_filter}
    ),
    -- PT Gym với khoảng cách từ gym
    GymPTs AS (
        SELECT 
            t.id,
            t.fullname,
            t.email,
            t.phonenumber,
            t.ismale,
            t.dob,
            t.avatarurl,
            t.bio,
            t.accountstatus,
            t.createdat,
            t.updatedat,
            t.pt_gym_id,
            t.experience,
            t.certificates,
            t.height,
            t.weight,
            t.biceps,
            t.chest,
            t.waist,
            t.goal_trainings,
            t.is_freelance,
            g.gym_id,
            g.gymname,
            g.gymaddress,
            g.gym_latitude,
            g.gym_longitude,
            g.gym_hotresearch,
            g.distance_km,
            'gym' as pt_type,
            ROW_NUMBER() OVER (ORDER BY g.distance_km ASC, g.gym_hotresearch DESC, t.experience DESC NULLS LAST) as rn
        FROM TrainersWithGoals t
        INNER JOIN RankedGyms g ON t.pt_gym_id = g.gym_id
    ),
    -- PT Freelance với khoảng cách từ vị trí cá nhân
    FreelancePTs AS (
        SELECT 
            t.id,
            t.fullname,
            t.email,
            t.phonenumber,
            t.ismale,
            t.dob,
            t.avatarurl,
            t.bio,
            t.accountstatus,
            t.createdat,
            t.updatedat,
            t.pt_gym_id,
            t.experience,
            t.certificates,
            t.height,
            t.weight,
            t.biceps,
            t.chest,
            t.waist,
            t.goal_trainings,
            t.is_freelance,
            NULL::UUID as gym_id,
            'Huấn luyện viên tự do' as gymname,
            'Tập tại địa điểm linh hoạt' as gymaddress,
            CAST(t.pt_latitude AS DOUBLE PRECISION) as gym_latitude,
            CAST(t.pt_longitude AS DOUBLE PRECISION) as gym_longitude,
            false as gym_hotresearch,
            CASE 
                WHEN t.pt_latitude IS NOT NULL AND t.pt_longitude IS NOT NULL THEN
                    6371.0 * 2 * ASIN(
                        SQRT(
                            POWER(SIN(RADIANS({latitude} - CAST(t.pt_latitude AS DOUBLE PRECISION)) / 2), 2) +
                            COS(RADIANS({latitude})) * COS(RADIANS(CAST(t.pt_latitude AS DOUBLE PRECISION))) *
                            POWER(SIN(RADIANS({longitude} - CAST(t.pt_longitude AS DOUBLE PRECISION)) / 2), 2)
                        )
                    )
                ELSE NULL
            END as distance_km,
            'freelance' as pt_type,
            ROW_NUMBER() OVER (ORDER BY 
                CASE 
                    WHEN t.pt_latitude IS NOT NULL AND t.pt_longitude IS NOT NULL THEN
                        6371.0 * 2 * ASIN(
                            SQRT(
                                POWER(SIN(RADIANS({latitude} - CAST(t.pt_latitude AS DOUBLE PRECISION)) / 2), 2) +
                                COS(RADIANS({latitude})) * COS(RADIANS(CAST(t.pt_latitude AS DOUBLE PRECISION))) *
                                POWER(SIN(RADIANS({longitude} - CAST(t.pt_longitude AS DOUBLE PRECISION)) / 2), 2)
                            )
                        )
                    ELSE 999999
                END ASC,
                t.experience DESC NULLS LAST
            ) as rn
        FROM TrainersWithGoals t
        WHERE t.is_freelance = true
            AND t.pt_gym_id IS NULL
            AND (
                t.pt_latitude IS NULL OR t.pt_longitude IS NULL OR
                (CAST(t.pt_latitude AS DOUBLE PRECISION) BETWEEN {latitude - lat_range} AND {latitude + lat_range}
                AND CAST(t.pt_longitude AS DOUBLE PRECISION) BETWEEN {longitude - lng_range} AND {longitude + lng_range})
            )
    ),
    -- Mixed kết quả: xen kẽ gym và freelance
    MixedResults AS (
        SELECT * FROM GymPTs WHERE rn <= 10
        UNION ALL
        SELECT * FROM FreelancePTs WHERE rn <= 10
    )
    -- Lấy 10 PT, ưu tiên xen kẽ giữa gym và freelance
    SELECT 
        id, fullname, email, phonenumber, ismale, dob, avatarurl, bio,
        accountstatus, createdat, updatedat, pt_gym_id as gym_id, experience, certificates,
        height, weight, biceps, chest, waist, goal_trainings, is_freelance,
        gymname, gymaddress, gym_latitude, gym_longitude, gym_hotresearch,
        distance_km, pt_type
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (
                PARTITION BY (rn % 2)
                ORDER BY 
                    CASE WHEN pt_type = 'gym' THEN 0 ELSE 1 END,
                    distance_km ASC NULLS LAST,
                    experience DESC NULLS LAST
            ) as mixed_rn
        FROM MixedResults
        WHERE distance_km IS NULL OR distance_km <= {max_distance_km}
    ) mixed
    WHERE mixed_rn <= 5
    ORDER BY 
        (mixed_rn - 1) * 2 + CASE WHEN pt_type = 'gym' THEN 0 ELSE 1 END,
        distance_km ASC NULLS LAST
    LIMIT 10
    """


def extract_experience_requirement(user_input):
    """
    Trích xuất yêu cầu về kinh nghiệm từ input của người dùng
    Returns: tuple (operator, years) hoặc (None, None) nếu không có
    Operator: '>=', '>', '=', '<', '<='
    """
    user_input_lower = user_input.lower()

    # Pattern 1: "ít nhất X năm" hoặc "tối thiểu X năm"
    patterns_gte = [
        r'ít nhất\s+(\d+)\s*năm',
        r'tối thiểu\s+(\d+)\s*năm',
        r'từ\s+(\d+)\s*năm',
        r'trên\s+(\d+)\s*năm',
        r'at least\s+(\d+)\s*year',
        r'minimum\s+(\d+)\s*year',
    ]

    for pattern in patterns_gte:
        match = re.search(pattern, user_input_lower)
        if match:
            years = int(match.group(1))
            return ('>=', years)

    # Pattern 2: "nhiều hơn X năm" hoặc "hơn X năm"
    patterns_gt = [
        r'nhiều hơn\s+(\d+)\s*năm',
        r'hơn\s+(\d+)\s*năm',
        r'more than\s+(\d+)\s*year',
        r'over\s+(\d+)\s*year',
    ]

    for pattern in patterns_gt:
        match = re.search(pattern, user_input_lower)
        if match:
            years = int(match.group(1))
            return ('>', years)

    # Pattern 3: "dưới X năm" hoặc "ít hơn X năm"
    patterns_lt = [
        r'dưới\s+(\d+)\s*năm',
        r'ít hơn\s+(\d+)\s*năm',
        r'under\s+(\d+)\s*year',
        r'less than\s+(\d+)\s*year',
    ]

    for pattern in patterns_lt:
        match = re.search(pattern, user_input_lower)
        if match:
            years = int(match.group(1))
            return ('<', years)

    # Pattern 4: "có X năm kinh nghiệm" (exact match)
    patterns_eq = [
        r'có\s+(\d+)\s*năm\s+kinh nghiệm',
        r'(\d+)\s*năm\s+kinh nghiệm',
        r'kinh nghiệm\s+(\d+)\s*năm',
        r'(\d+)\s*year[s]?\s+experience',
        r'experience[d]?\s+(\d+)\s*year',
    ]

    for pattern in patterns_eq:
        match = re.search(pattern, user_input_lower)
        if match:
            years = int(match.group(1))
            return ('=', years)  # Interpret "có X năm" as "ít nhất X năm"

    return (None, None)


def build_trainer_search_query(user_input, longitude=None, latitude=None):
    """
    Xây dựng truy vấn tìm kiếm PT thông minh dựa trên input của người dùng
    Bao gồm cả PT gym và PT freelance
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

        # Extract experience requirement
        exp_operator, exp_years = extract_experience_requirement(user_input)

        # Kiểm tra yêu cầu chỉ PT freelance hoặc chỉ PT gym
        only_freelance = any(kw in user_input_lower for kw in ['tự do', 'freelance', 'tu do', 'không gym', 'khong gym'])
        only_gym = any(kw in user_input_lower for kw in ['tại gym', 'tai gym', 'phòng gym', 'phong gym', 'gym pt'])

        print(f"🔍 PT_TYPE_FILTER: only_freelance={only_freelance}, only_gym={only_gym}")

        # Xây dựng base conditions cho PT
        pt_base_conditions = [
            'pt."AccountStatus" = \'Active\'',
            # Bỏ điều kiện GymOwnerId để bao gồm cả freelance
            '(pt."GymOwnerId" IS NOT NULL OR EXISTS (SELECT 1 FROM "PTFreelancePackages" pfp WHERE pfp."PtId" = pt."Id" AND pfp."IsEnabled" = true))'
        ]

        # Nếu có tọa độ và yêu cầu tìm gần
        if longitude and latitude and any(kw in user_input_lower for kw in
            ['gần', 'near', 'nearby', 'xung quanh', 'lân cận']):
            max_distance = get_trainer_distance_preference(user_input)
            return build_nearby_trainer_query(longitude, latitude, max_distance, user_input)

        # Thêm filter theo goal trainings (JOIN trực tiếp với GoalTrainings)
        goal_join_conditions = []
        if goal_keywords:
            goal_list = "', '".join([g.replace("'", "''") for g in goal_keywords])
            goal_join_conditions.append(f"gt.\"Name\" IN ('{goal_list}')")

        # Kiểm tra gender - Ưu tiên cao hơn, check trước khi xử lý keywords
        if 'nữ' in user_input_lower or 'female' in user_input_lower or 'nu' in normalize_vietnamese_text(user_input):
            pt_base_conditions.append('pt."IsMale" = false')
        elif 'nam' in user_input_lower or 'male' in user_input_lower:
            pt_base_conditions.append('pt."IsMale" = true')

        # Build WHERE clause
        where_parts = []
        where_parts.append(f"({' AND '.join(pt_base_conditions)})")

        if goal_join_conditions:
            where_parts.append(f"({' AND '.join(goal_join_conditions)})")

        where_clause = " AND ".join(where_parts)

        # Build experience filter cho TrainersWithGoals CTE
        experience_filter = ""
        if exp_operator and exp_years:
            experience_filter = f"\n            HAVING ud.\"Experience\" {exp_operator} {exp_years}"
            print(f"🎯 EXPERIENCE_FILTER: Lọc PT có kinh nghiệm {exp_operator} {exp_years} năm")

        # Xây dựng query khác nhau tùy theo loại PT được yêu cầu
        if only_freelance:
            # Chỉ trả về PT freelance
            print("💼 Chỉ tìm PT FREELANCE")
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
                    pt."Bio" as bio,
                    pt."AccountStatus" as accountstatus,
                    pt."CreatedAt" as createdat,
                    pt."UpdatedAt" as updatedat,
                    pt."GymOwnerId" as pt_gym_id,
                    ud."Experience" as experience,
                    ud."Certificates" as certificates,
                    ud."Height" as height,
                    ud."Weight" as weight,
                    ud."Biceps" as biceps,
                    ud."Chest" as chest,
                    ud."Waist" as waist,
                    ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings,
                    CASE 
                        WHEN COUNT(DISTINCT pfp."Id") > 0 THEN true 
                        ELSE false 
                    END as is_freelance
                FROM "AspNetUsers" pt
                INNER JOIN FilteredPTs fp ON pt."Id" = fp.pt_id
                LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
                LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
                LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
                LEFT JOIN "PTFreelancePackages" pfp ON pt."Id" = pfp."PtId" AND pfp."IsEnabled" = true
                GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                         ud."Weight", ud."Biceps", ud."Chest", ud."Waist"{experience_filter}
            )
            SELECT 
                t.id,
                t.fullname,
                t.email,
                t.phonenumber,
                t.ismale,
                t.dob,
                t.avatarurl,
                t.bio,
                t.accountstatus,
                t.createdat,
                t.updatedat,
                t.pt_gym_id as gym_id,
                t.experience,
                t.certificates,
                t.height,
                t.weight,
                t.biceps,
                t.chest,
                t.waist,
                t.goal_trainings,
                t.is_freelance,
                NULL::UUID as gym_id_unused,
                'Huấn luyện viên tự do' as gymname,
                'Tập tại địa điểm linh hoạt' as gymaddress,
                NULL::DOUBLE PRECISION as gym_latitude,
                NULL::DOUBLE PRECISION as gym_longitude,
                false as gym_hotresearch,
                'freelance' as pt_type
            FROM TrainersWithGoals t
            WHERE t.is_freelance = true AND t.pt_gym_id IS NULL
            ORDER BY t.experience DESC NULLS LAST, t.fullname ASC
            LIMIT 10
            """
        elif only_gym:
            # Chỉ trả về PT gym
            print("🏢 Chỉ tìm PT GYM")
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
                    pt."Bio" as bio,
                    pt."AccountStatus" as accountstatus,
                    pt."CreatedAt" as createdat,
                    pt."UpdatedAt" as updatedat,
                    pt."GymOwnerId" as pt_gym_id,
                    ud."Experience" as experience,
                    ud."Certificates" as certificates,
                    ud."Height" as height,
                    ud."Weight" as weight,
                    ud."Biceps" as biceps,
                    ud."Chest" as chest,
                    ud."Waist" as waist,
                    ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings,
                    CASE 
                        WHEN COUNT(DISTINCT pfp."Id") > 0 THEN true 
                        ELSE false 
                    END as is_freelance
                FROM "AspNetUsers" pt
                INNER JOIN FilteredPTs fp ON pt."Id" = fp.pt_id
                LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
                LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
                LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
                LEFT JOIN "PTFreelancePackages" pfp ON pt."Id" = pfp."PtId" AND pfp."IsEnabled" = true
                GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                         ud."Weight", ud."Biceps", ud."Chest", ud."Waist"{experience_filter}
            )
            SELECT 
                t.id,
                t.fullname,
                t.email,
                t.phonenumber,
                t.ismale,
                t.dob,
                t.avatarurl,
                t.bio,
                t.accountstatus,
                t.createdat,
                t.updatedat,
                t.pt_gym_id as gym_id,
                t.experience,
                t.certificates,
                t.height,
                t.weight,
                t.biceps,
                t.chest,
                t.waist,
                t.goal_trainings,
                t.is_freelance,
                gym."Id" as gym_id_unused,
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
                gym."hotResearch" as gym_hotresearch,
                'gym' as pt_type
            FROM TrainersWithGoals t
            INNER JOIN "AspNetUsers" gym ON t.pt_gym_id = gym."Id"
            LEFT JOIN "Addresses" a ON gym."Id" = a."CustomerId" AND a."IsEnabled" = true
            WHERE gym."AccountStatus" = 'Active' AND t.pt_gym_id IS NOT NULL
            ORDER BY gym."hotResearch" DESC, t.experience DESC NULLS LAST, t.fullname ASC
            LIMIT 10
            """
        else:
            # Mixed cả gym và freelance (default behavior)
            print("🔀 Tìm cả PT GYM và FREELANCE (mixed)")
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
                    pt."Bio" as bio,
                    pt."AccountStatus" as accountstatus,
                    pt."CreatedAt" as createdat,
                    pt."UpdatedAt" as updatedat,
                    pt."GymOwnerId" as pt_gym_id,
                    ud."Experience" as experience,
                    ud."Certificates" as certificates,
                    ud."Height" as height,
                    ud."Weight" as weight,
                    ud."Biceps" as biceps,
                    ud."Chest" as chest,
                    ud."Waist" as waist,
                    ARRAY_AGG(DISTINCT gt."Name") FILTER (WHERE gt."Name" IS NOT NULL) as goal_trainings,
                    -- Kiểm tra xem có package freelance không
                    CASE 
                        WHEN COUNT(DISTINCT pfp."Id") > 0 THEN true 
                        ELSE false 
                    END as is_freelance
                FROM "AspNetUsers" pt
                INNER JOIN FilteredPTs fp ON pt."Id" = fp.pt_id
                LEFT JOIN "UserDetails" ud ON pt."Id" = ud."Id"
                LEFT JOIN "PTGoalTrainings" pgt ON pt."Id" = pgt."ApplicationUsersId"
                LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
                LEFT JOIN "PTFreelancePackages" pfp ON pt."Id" = pfp."PtId" AND pfp."IsEnabled" = true
                GROUP BY pt."Id", ud."Experience", ud."Certificates", ud."Height", 
                         ud."Weight", ud."Biceps", ud."Chest", ud."Waist"{experience_filter}
            ),
            -- PT Gym
            GymPTs AS (
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
                    gym."hotResearch" as gym_hotresearch,
                    'gym' as pt_type,
                    ROW_NUMBER() OVER (ORDER BY gym."hotResearch" DESC, t.experience DESC NULLS LAST, t.fullname ASC) as rn
                FROM TrainersWithGoals t
                INNER JOIN "AspNetUsers" gym ON t.pt_gym_id = gym."Id"
                LEFT JOIN "Addresses" a ON gym."Id" = a."CustomerId" AND a."IsEnabled" = true
                WHERE gym."AccountStatus" = 'Active'
            ),
            -- PT Freelance
            FreelancePTs AS (
                SELECT 
                    t.*,
                    NULL::UUID as gym_id,
                    'Huấn luyện viên tự do' as gymname,
                    'Tập tại địa điểm linh hoạt' as gymaddress,
                    NULL::DOUBLE PRECISION as gym_latitude,
                    NULL::DOUBLE PRECISION as gym_longitude,
                    false as gym_hotresearch,
                    'freelance' as pt_type,
                    ROW_NUMBER() OVER (ORDER BY t.experience DESC NULLS LAST, t.fullname ASC) as rn
                FROM TrainersWithGoals t
                WHERE t.is_freelance = true AND t.pt_gym_id IS NULL
            ),
            -- Mixed kết quả: xen kẽ gym và freelance
            MixedResults AS (
                SELECT * FROM GymPTs WHERE rn <= 10
                UNION ALL
                SELECT * FROM FreelancePTs WHERE rn <= 10
            )
            -- Lấy 10 PT, xen kẽ giữa gym và freelance
            SELECT 
                id, fullname, email, phonenumber, ismale, dob, avatarurl, bio,
                accountstatus, createdat, updatedat, pt_gym_id as gym_id, experience, certificates,
                height, weight, biceps, chest, waist, goal_trainings, is_freelance,
                gymname, gymaddress, gym_latitude, gym_longitude, gym_hotresearch,
                pt_type
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (
                        PARTITION BY (rn % 2)
                        ORDER BY 
                            CASE WHEN pt_type = 'gym' THEN 0 ELSE 1 END,
                            gym_hotresearch DESC,
                            experience DESC NULLS LAST
                    ) as mixed_rn
                FROM MixedResults
            ) mixed
            WHERE mixed_rn <= 5
            ORDER BY 
                (mixed_rn - 1) * 2 + CASE WHEN pt_type = 'gym' THEN 0 ELSE 1 END,
                gym_hotresearch DESC,
                experience DESC NULLS LAST
            LIMIT 10
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
