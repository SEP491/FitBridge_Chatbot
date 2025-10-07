# app/services/search_service.py - Search logic and query building functions

import math
import re
from app.utils.text_utils import normalize_vietnamese_text, extract_search_keywords
from app.database.connection import query_database

def build_nearby_gym_query(longitude, latitude, max_distance_km= 10):
    """Xây dựng truy vấn SQL để tìm gym gần sử dụng công thức Haversine"""
    # Tối ưu hóa với bounding box để giảm tải tính toán
    lat_range = max_distance_km / 111.0  # 1 độ vĩ độ ≈ 111km
    lng_range = max_distance_km / (111.0 * abs(math.cos(math.radians(latitude))))
    
    return f"""
    WITH BoundedGyms AS (
        SELECT 
            u."Id" as id, 
            u."GymName" as gymname, 
            u."FullName" as fullname,
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
            u."TaxCode" as taxcode,
            CAST(u."Longitude" AS DOUBLE PRECISION) AS longitude,
            CAST(u."Latitude" AS DOUBLE PRECISION) AS latitude,
            u."hotResearch" as hotresearch, 
            u."AccountStatus" as accountstatus,
            u."Email" as email, 
            u."PhoneNumber" as phonenumber,
            u."GymDescription" as gymdescription, 
            u."AvatarUrl" as avatarurl,
            u."GymImages" as gymimages, 
            u."CreatedAt" as createdat,
            u."UpdatedAt" as updatedat, 
            u."Dob" as dob
        FROM "AspNetUsers" u
        LEFT JOIN "Addresses" a ON u."Id" = a."CustomerId" AND a."IsEnabled" = true
        WHERE u."AccountStatus" = 'Active'
        AND u."GymName" IS NOT NULL 
        AND u."GymName" != ''
        AND u."Latitude" IS NOT NULL 
        AND u."Longitude" IS NOT NULL
        AND CAST(u."Latitude" AS DOUBLE PRECISION) BETWEEN {latitude - lat_range} AND {latitude + lat_range}
        AND CAST(u."Longitude" AS DOUBLE PRECISION) BETWEEN {longitude - lng_range} AND {longitude + lng_range}
    ),
    DistanceCalculated AS (
        SELECT *,
            6371.0 * 2 * ASIN(
                SQRT(
                    POWER(SIN(RADIANS({latitude} - latitude) / 2), 2) +
                    COS(RADIANS({latitude})) * COS(RADIANS(latitude)) *
                    POWER(SIN(RADIANS({longitude} - longitude) / 2), 2)
                )
            ) AS distance_km
        FROM BoundedGyms
    )
    SELECT * 
    FROM DistanceCalculated
    WHERE distance_km <= {max_distance_km}
    ORDER BY distance_km ASC, hotresearch DESC, gymname ASC;
    """

def get_nearby_distance_preference(user_input):
    """Phân tích đầu vào của người dùng để xác định bán kính tìm kiếm phù hợp"""
    user_input_lower = user_input.lower()
    
    # 1. Tìm số km cụ thể trong câu (ưu tiên cao nhất)
    import re
    km_match = re.search(r'(\d+)\s*km', user_input_lower)
    if km_match:
        distance = int(km_match.group(1))
        # Giới hạn khoảng cách hợp lý (1-50km)
        return max(1, min(distance, 50))
    
    # 2. Phân tích theo cấp độ khoảng cách với từ khóa thông minh
    distance_patterns = {
        # Rất gần - 2km
        2: [
            r'(rất gần|very close|walking distance|đi bộ|đi bộ được)',
            r'(ngay gần|sát bên|cực gần|siêu gần)',
            r'(trong phạm vi \d{1,3}\s*m|dưới 1km|under 1km)'
        ],
        
        # Gần - 5km  
        5: [
            r'(gần|nearby|close|lân cận|kề bên)',
            r'(quanh đây|xung quanh|around here)',
            r'(không xa|not far|gần nhà|near home)'
        ],
        
        # Trung bình - 10km
        10: [
            r'(khu vực|trong khu|in the area|local)',
            r'(xa một chút|bit farther|hơi xa)',
            r'(trong thành phố|in the city|cùng thành phố)'
        ],
        
        # Xa - 15km
        15: [
            r'(xa hơn|farther|more distant)',
            r'(trong tỉnh|in province|cùng tỉnh)',
            r'(mở rộng|expand|extend)'
        ],
        
        # Rất xa - 25km
        25: [
            r'(rất xa|very far|distant)',
            r'(khắp nơi|everywhere|anywhere)',
            r'(toàn bộ|all|entire|whole)'
        ],
        
        # Không giới hạn - 50km
        50: [
            r'(tất cả|all gyms|mọi|every|bất kỳ đâu)',
            r'(không giới hạn|unlimited|no limit)',
            r'(toàn quốc|nationwide|whole country)'
        ]
    }
    
    # 3. Duyệt qua các pattern theo thứ tự ưu tiên
    for distance, patterns in distance_patterns.items():
        for pattern in patterns:
            if re.search(pattern, user_input_lower):
                return distance
    
    # 4. Phân tích thông minh dựa trên ngữ cảnh
    
    # Nếu có từ khóa về phương tiện di chuyển
    transport_keywords = {
        r'(xe đạp|bicycle|bike)': 8,
        r'(xe máy|motorbike|scooter)': 15, 
        r'(ô tô|car|drive|driving)': 20,
        r'(xe bus|bus|public transport)': 12
    }
    
    for pattern, distance in transport_keywords.items():
        if re.search(pattern, user_input_lower):
            return distance
    
    # Nếu có từ khóa về thời gian
    time_keywords = {
        r'(5 phút|5min|năm phút)': 3,
        r'(10 phút|10min|mười phút)': 5,
        r'(15 phút|15min|mười lăm phút)': 8,
        r'(20 phút|20min|hai mươi phút)': 12,
        r'(30 phút|30min|nửa giờ|half hour)': 18
    }
    
    for pattern, distance in time_keywords.items():
        if re.search(pattern, user_input_lower):
            return distance
    
    # 5. Phân tích theo địa danh cụ thể
    location_keywords = {
        r'(quận \d+|district \d+)': 8,        # Trong quận
        r'(thành phố|city|tp\.)': 15,         # Trong thành phố  
        r'(tỉnh|province|tỉnh thành)': 25,    # Trong tỉnh
        r'(huyện|county|suburban)': 20        # Ngoại thành
    }
    
    for pattern, distance in location_keywords.items():
        if re.search(pattern, user_input_lower):
            return distance
    
    # 6. Mặc định thông minh dựa trên độ dài câu
    if len(user_input_lower.split()) <= 3:
        return 8   # Câu ngắn -> tìm gần
    elif len(user_input_lower.split()) <= 6:
        return 10  # Câu trung bình -> tìm vừa
    else:
        return 12  # Câu dài -> có thể muốn tìm rộng hơn

def intelligent_gym_search(user_input):
    """Tìm kiếm gym thông minh với khả năng phân tích ngữ nghĩa nâng cao"""
    try:
        # Kiểm tra đầu vào
        if not user_input or not isinstance(user_input, str):
            return None
        
        user_input_lower = user_input.lower()
        
        # 1. Danh sách từ khóa chỉ rõ KHÔNG cần tìm kiếm gym (mở rộng)
        non_gym_indicators = [
            # Chào hỏi và lịch sự
            'xin chào', 'hello', 'hi', 'chào bạn', 'hey there',
            'cảm ơn', 'thank you', 'thanks', 'cám ơn', 'tks',
            'tạm biệt', 'bye', 'goodbye', 'see you',
            
            # Câu hỏi cá nhân  
            'tên tôi', 'my name', 'lặp lại tên', 'nhắc lại tên',
            'tôi là ai', 'who am i', 'remember me',
            
            # Tư vấn sức khỏe không cần gym cụ thể
            'làm sao để', 'how to', 'cách để', 'how can i',
            'ăn gì để', 'what to eat', 'what should i eat',
            'bài tập nào', 'what exercise', 'which workout',
            'tăng cân', 'giảm cân', 'lose weight', 'gain weight',
            'thời tiết', 'weather', 'nhiệt độ', 'temperature',
            
            # Phản hồi chung
            'ok', 'được rồi', 'tốt', 'good', 'fine', 'great',
            'đồng ý', 'agree', 'yes', 'no problem'
        ]
        
        # Nếu có từ khóa không liên quan gym, return None ngay
        if any(indicator in user_input_lower for indicator in non_gym_indicators):
            return None
        
        # 2. Phân tích ý định tìm kiếm gym (cải thiện)
        gym_search_patterns = [
            # Tìm kiếm trực tiếp
            r'(tìm|find|search|looking for)\s*(gym|phòng gym|fitness|thể dục)',
            r'(gym|phòng gym|fitness)\s*(nào|what|which|where)',
            r'(có|is there|are there)\s*(gym|phòng gym|fitness)',
            
            # Tìm kiếm theo địa điểm
            r'(gym|phòng gym|fitness)\s*(ở|at|in|near|gần)\s*(\w+)',
            r'(quận|district|huyện|thành phố|city)\s*\d*.*?(gym|phòng gym|fitness)',
            
            # Tìm kiếm theo đặc điểm
            r'(gym|phòng gym|fitness)\s*(hot|nổi tiếng|phổ biến|tốt|best)',
            r'(hot|nổi tiếng|phổ biến|tốt|best)\s*(gym|phòng gym|fitness)',
            
            # Tìm kiếm mở
            r'(danh sách|list)\s*(gym|phòng gym|fitness)',
            r'(tất cả|all)\s*(gym|phòng gym|fitness)',
            r'(những|the)\s*(gym|phòng gym|fitness)\s*(nào|what)'
        ]
        
        # Kiểm tra xem có khớp với pattern tìm kiếm gym không
        has_gym_search_intent = any(re.search(pattern, user_input_lower) for pattern in gym_search_patterns)
        
        # Nếu không có ý định tìm kiếm gym rõ ràng, return None
        if not has_gym_search_intent:
            return None
        
        # 3. Trích xuất thông tin tìm kiếm thông minh
        search_info = {
            'keywords': [],
            'location': None,
            'hot_search': False,
            'search_type': 'general'
        }
        
        # Trích xuất từ khóa quan trọng (bỏ stop words)
        stop_words = {
            'tìm', 'find', 'search', 'có', 'không', 'nào', 'đâu', 'where', 
            'what', 'gì', 'là', 'ở', 'tại', 'trong', 'của', 'một', 'vài', 
            'những', 'các', 'the', 'a', 'an', 'and', 'or', 'for', 'gym', 
            'phòng', 'fitness', 'center', 'club', 'quận', 'district', 'quan',
            'tim', 'phong'  # Thêm các từ đã được normalize
        }
        
        words = re.findall(r'\b\w+\b', normalize_vietnamese_text(user_input))
        keywords = [word for word in words if word not in stop_words and len(word) >= 2]
        search_info['keywords'] = keywords[:5]  # Lấy tối đa 5 từ khóa quan trọng nhất
        
        # Phát hiện tìm kiếm hot/phổ biến
        hot_patterns = [
            r'(hot|nổi tiếng|phổ biến|được yêu thích|tốt nhất|best|top)',
            r'(recommend|gợi ý|đề xuất|suggest)'
        ]
        search_info['hot_search'] = any(re.search(pattern, user_input_lower) for pattern in hot_patterns)
        
        # Phát hiện địa điểm cụ thể
        location_patterns = [
            r'(quận|district)\s*([\w\s]+?)(?:\s|$|,|\.)',  # Match multi-word district names
            r'(huyện|county)\s*([\w\s]+?)(?:\s|$|,|\.)',
            r'(thành phố|city|tp\.?)\s*([\w\s]+?)(?:\s|$|,|\.)',
            r'(ở|tại|in|at)\s*([\w\s]+?)(?:\s|$|,|\.)'
        ]
        
        district_number = None
        district_name = None
        specific_location = None

        for pattern in location_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                if 'quận' in pattern or 'district' in pattern:
                    location_part = match.group(2).strip()

                    # Xử lý quận có số (Quận 1, Quận 3, Quận 7, etc.)
                    number_match = re.search(r'^(\d+)$', location_part)
                    if number_match:
                        district_number = number_match.group(1)
                        specific_location = f"quận {district_number}"
                    else:
                        # Xử lý quận có tên (Quận Hải Châu, Quận Đống Đa, etc.)
                        # Loại bỏ các từ không cần thiết ở cuối
                        cleaned_name = re.sub(r'\s*(gym|phòng|fitness|tìm|find).*$', '', location_part, flags=re.IGNORECASE).strip()
                        if cleaned_name:
                            district_name = cleaned_name
                            specific_location = f"quận {district_name}"

                    search_info['location'] = specific_location
                    search_info['search_type'] = 'district_specific'
                    break
                else:
                    search_info['location'] = match.group(0)
                    break

        # 4. Xây dựng truy vấn SQL thông minh cho AspNetUsers table
        base_conditions = ['"AccountStatus" = \'Active\'', '"GymName" IS NOT NULL', '"GymName" != \'\'']

        # Ưu tiên gym hot nếu có yêu cầu
        if search_info['hot_search']:
            base_conditions.append('"hotResearch" = true')
            search_info['search_type'] = 'hot'
        
        # Xây dựng điều kiện tìm kiếm từ keywords - chỉ khi không phải district_specific
        search_conditions = []
        valid_keywords = []
        
        # Nếu không phải tìm kiếm theo quận cụ thể, mới áp dụng keyword filtering
        if search_info['search_type'] != 'district_specific':
            for keyword in search_info['keywords']:
                if keyword and len(keyword) >= 2:
                    # Escape single quotes để tránh SQL injection
                    safe_keyword = keyword.replace("'", "''")
                    valid_keywords.append(safe_keyword)
                    search_conditions.extend([
                        f'"GymName" ILIKE \'%{safe_keyword}%\'',
                        f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%{safe_keyword}%\'',
                        f'"FullName" ILIKE \'%{safe_keyword}%\''
                    ])

        # Thêm điều kiện địa điểm nếu có - Cải thiện logic filtering
        district_conditions = []
        if search_info['location']:
            safe_location = search_info['location'].replace("'", "''")

            # Nếu tìm kiếm theo quận cụ thể, sử dụng logic filtering chính xác
            if search_info['search_type'] == 'district_specific':
                if district_number:
                    # Xử lý quận có số (Quận 1, Quận 3, Quận 7, etc.)
                    district_conditions = [
                        f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%quận {district_number}%\'',
                        f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%district {district_number}%\'',
                        f'a."District" ILIKE \'%quận {district_number}%\'',
                        f'a."District" ILIKE \'%district {district_number}%\''
                    ]
                elif district_name:
                    # Xử lý quận có tên (Quận Hải Châu, Quận Đống Đa, etc.)
                    safe_district_name = district_name.replace("'", "''")
                    district_conditions = [
                        f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%quận {safe_district_name}%\'',
                        f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%district {safe_district_name}%\'',
                        f'a."District" ILIKE \'%quận {safe_district_name}%\'',
                        f'a."District" ILIKE \'%{safe_district_name}%\'',
                        f'a."District" = \'Quận {safe_district_name}\''
                    ]

                # Thêm điều kiện quận như một điều kiện bắt buộc (AND), không phải tùy chọn (OR)
                base_conditions.append(f"({' OR '.join(district_conditions)})")
            else:
                # Tìm kiếm địa điểm chung khác
                search_conditions.extend([
                    f'COALESCE(CONCAT_WS(\', \', NULLIF(a."HouseNumber", \'\'), NULLIF(a."Street", \'\'), NULLIF(a."Ward", \'\'), NULLIF(a."District", \'\'), NULLIF(a."City", \'\')), \'Địa chỉ chưa cập nhật\') ILIKE \'%{safe_location}%\'',
                    f'"GymName" ILIKE \'%{safe_location}%\''
                ])

        # Xây dựng mệnh đề WHERE
        where_clause = " AND ".join(base_conditions)
        
        if search_conditions:
            keyword_clause = " OR ".join(search_conditions)
            where_clause += f" AND ({keyword_clause})"
        elif not search_info['hot_search'] and search_info['search_type'] != 'district_specific':
            # Nếu không có từ khóa và không phải tìm kiếm hot và không phải tìm kiếm theo quận cụ thể, return None
            return None
        
        # 5. Tạo SQL query với scoring thông minh
        if valid_keywords or search_info['search_type'] == 'district_specific':
            primary_keyword = valid_keywords[0] if valid_keywords else 'gym'
            sql_query = f"""
            SELECT 
                u."Id" as id, u."GymName" as gymname, u."FullName" as fullname,
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
                u."TaxCode" as taxcode,
                u."Longitude" as longitude, u."Latitude" as latitude,
                u."hotResearch" as hotresearch, u."AccountStatus" as accountstatus,
                u."Email" as email, u."PhoneNumber" as phonenumber,
                u."GymDescription" as gymdescription, u."AvatarUrl" as avatarurl,
                u."GymImages" as gymimages, u."CreatedAt" as createdat,
                u."UpdatedAt" as updatedat, u."Dob" as dob,
                CASE WHEN u."hotResearch" = true THEN 20 ELSE 0 END as hot_score,
                CASE 
                    WHEN u."GymName" ILIKE '%{primary_keyword}%' THEN 30
                    WHEN COALESCE(
                        CONCAT_WS(', ', 
                            NULLIF(a."HouseNumber", ''), 
                            NULLIF(a."Street", ''), 
                            NULLIF(a."Ward", ''), 
                            NULLIF(a."District", ''), 
                            NULLIF(a."City", '')
                        ), 
                        'Địa chỉ chưa cập nhật'
                    ) ILIKE '%{primary_keyword}%' THEN 25
                    WHEN u."FullName" ILIKE '%{primary_keyword}%' THEN 15
                    ELSE 5
                END as relevance_score,
                CASE 
                    WHEN u."CreatedAt" >= (CURRENT_DATE - INTERVAL '1 year') THEN 5 
                    ELSE 0 
                END as recency_score
            FROM "AspNetUsers" u
            LEFT JOIN "Addresses" a ON u."Id" = a."CustomerId" AND a."IsEnabled" = true
            WHERE {where_clause}
            ORDER BY hot_score DESC, relevance_score DESC, recency_score DESC, gymname ASC
            """
        else:
            # Query cho tìm kiếm general hoặc hot gym
            sql_query = f"""
            SELECT 
                u."Id" as id, u."GymName" as gymname, u."FullName" as fullname,
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
                u."TaxCode" as taxcode,
                u."Longitude" as longitude, u."Latitude" as latitude,
                u."hotResearch" as hotresearch, u."AccountStatus" as accountstatus,
                u."Email" as email, u."PhoneNumber" as phonenumber,
                u."GymDescription" as gymdescription, u."AvatarUrl" as avatarurl,
                u."GymImages" as gymimages, u."CreatedAt" as createdat,
                u."UpdatedAt" as updatedat, u."Dob" as dob,
                CASE WHEN u."hotResearch" = true THEN 20 ELSE 0 END as hot_score,
                10 as relevance_score,
                CASE 
                    WHEN u."CreatedAt" >= (CURRENT_DATE - INTERVAL '1 year') THEN 5 
                    ELSE 0 
                END as recency_score
            FROM "AspNetUsers" u
            LEFT JOIN "Addresses" a ON u."Id" = a."CustomerId" AND a."IsEnabled" = true
            WHERE {where_clause}
            ORDER BY hot_score DESC, relevance_score DESC, recency_score DESC, gymname ASC
            """
        
        print(f"🤖 INTELLIGENT SEARCH: Input='{user_input}' | Type={search_info['search_type']} | Keywords={search_info['keywords'][:3]}")
        return sql_query
        
    except Exception as e:
        print(f"Lỗi trong intelligent_gym_search: {str(e)}")
        return None

def detect_search_intent(user_input):
    """Phát hiện ý định tìm kiếm từ đầu vào của người dùng"""
    user_lower = user_input.lower()
    
    intent_patterns = {
        'location_search': [r'(gần|near|nearby|xung quanh|lân cận|quanh đây)', r'(district \d+|quận \d+|huyện)'],
        'name_search': [r'(tìm .+ gym|gym .+|.+ fitness|.+ center)'],
        'popular_search': [r'(hot|nổi tiếng|phổ biến|được yêu thích|tốt nhất|best|top)', r'(gym hot|phòng gym hot|fitness hot)'],
        'new_search': [r'(mới|new|vừa mở|recently|gần đây)'],
        'old_search': [r'(cũ|old|lâu năm|uy tín|established)'],
        'price_search': [r'(rẻ|cheap|affordable|giá tốt|budget)'],
        'equipment_search': [r'(thiết bị|equipment|máy tập|facilities)']
    }
    
    detected_intents = []
    for intent, patterns in intent_patterns.items():
        for pattern in patterns:
            if re.search(pattern, user_lower):
                detected_intents.append(intent)
                break
    
    return detected_intents

def classify_query(user_input):
    """Phân loại truy vấn và tạo SQL nếu cần - Được cải thiện"""
    try:
        # 1. Ưu tiên sử dụng intelligent search trước
        intelligent_query = intelligent_gym_search(user_input)
        if intelligent_query:
            print(f"✅ INTELLIGENT_SEARCH: Query generated successfully")
            return True, intelligent_query
        
        # 2. Nếu intelligent search không tạo được query, có nghĩa là:
        # - Câu hỏi không liên quan đến tìm kiếm gym
        # - Hoặc là câu hỏi chào hỏi, tư vấn chung
        
        user_input_lower = user_input.lower()
        
        # 3. Kiểm tra một số trường hợp đặc biệt cuối cùng
        special_gym_cases = [
            'danh sách gym', 'list gym', 'all gym', 'tất cả gym',
            'gym có những gì', 'gym nào', 'which gym'
        ]
        
        if any(case in user_input_lower for case in special_gym_cases):
            # Trường hợp muốn xem tất cả gym
            return True, """
            SELECT 
                u."Id" as id, u."GymName" as gymname, u."FullName" as fullname,
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
                u."TaxCode" as taxcode,
                u."Longitude" as longitude, u."Latitude" as latitude,
                u."hotResearch" as hotresearch, u."AccountStatus" as accountstatus,
                u."Email" as email, u."PhoneNumber" as phonenumber,
                u."GymDescription" as gymdescription, u."AvatarUrl" as avatarurl,
                u."GymImages" as gymimages, u."CreatedAt" as createdat,
                u."UpdatedAt" as updatedat, u."Dob" as dob,
                CASE WHEN u."hotResearch" = true THEN 20 ELSE 0 END as hot_score,
                10 as relevance_score
            FROM "AspNetUsers" u
            LEFT JOIN "Addresses" a ON u."Id" = a."CustomerId" AND a."IsEnabled" = true
            WHERE u."AccountStatus" = 'Active'
            AND u."GymName" IS NOT NULL 
            AND u."GymName" != ''
            ORDER BY hot_score DESC, gymname ASC
            """
        
        # 4. Nếu không khớp với trường hợp nào -> không cần truy vấn database
        print(f"❌ NO_DB_QUERY: '{user_input}' không cần truy vấn database")
        return False, None
        
    except Exception as e:
        print(f"Lỗi trong classify_query: {str(e)}")
        return False, None

def classify_query_with_context(user_input, conversation_context):
    """Phân loại truy vấn với ngữ cảnh hội thoại"""
    user_input_lower = user_input.lower()
    
    # Danh sách từ khóa chỉ các câu hỏi KHÔNG cần truy vấn database
    non_gym_keywords = [
        # Câu hỏi cá nhân
        'tên tôi', 'tên của tôi', 'lặp lại tên', 'nhắc lại tên', 
        'my name', 'what is my name', 'repeat my name',
        'tôi tên', 'tôi là ai', 'who am i',
        
        # Chào hỏi và lịch sự
        'xin chào', 'hello', 'hi', 'chào bạn', 'hey',
        'cảm ơn', 'thank you', 'thanks', 'cám ơn',
        'tạm biệt', 'bye', 'goodbye', 'chào tạm biệt',
        
        # Tư vấn sức khỏe chung (không cần tìm gym cụ thể)
        'làm sao để', 'cách để', 'how to',
        'ăn gì để', 'what to eat',
        'bài tập nào', 'exercise for',
        'tăng cân', 'giảm cân', 'lose weight', 'gain weight',
        
        # Phản hồi chung
        'ok', 'được rồi', 'tốt', 'good', 'fine', 'đồng ý'
    ]
    
    # Kiểm tra nếu input chứa từ khóa không cần truy vấn DB
    if any(keyword in user_input_lower for keyword in non_gym_keywords):
        return False, None
    
    # Danh sách từ khóa chỉ rõ cần tìm kiếm gym
    gym_search_keywords = [
        'gym', 'fitness', 'thể dục', 'thể hình', 'tập luyện',
        'phòng gym', 'trung tâm', 'center', 'club',
        'tìm', 'search', 'ở đâu', 'where', 'địa chỉ', 'address',
        'gần', 'near', 'nearby', 'quanh', 'xung quanh',
        'quận', 'district', 'thành phố', 'city'
    ]
    
    # Chỉ tiếp tục nếu có từ khóa liên quan đến tìm kiếm gym
    has_gym_intent = any(keyword in user_input_lower for keyword in gym_search_keywords)
    if not has_gym_intent:
        return False, None
    
    detected_intents = detect_search_intent(user_input)
    context_keywords = extract_search_keywords(conversation_context) if conversation_context else []
    
    # Xử lý truy vấn nhận biết ngữ cảnh
    if conversation_context:
        gym_names_in_context = re.findall(r'(\w+\s*(?:gym|fitness|center))', conversation_context.lower())
        
        if gym_names_in_context and any(word in user_input.lower() for word in ['khác', 'other', 'nào khác', 'còn']):
            excluded_gyms = ' AND '.join([f"GymName NOT LIKE '%{name.split()[0]}%'" for name in gym_names_in_context])
            base_query = intelligent_gym_search(user_input)
            if base_query and excluded_gyms:
                enhanced_query = base_query.replace('WHERE Active = 1', f'WHERE Active = 1 AND {excluded_gyms}')
                return True, enhanced_query
    
    # Sử dụng phân loại thông thường
    return classify_query(user_input)