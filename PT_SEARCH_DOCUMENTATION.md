# 🏋️ Personal Trainer Search Feature - Documentation

## Tổng quan

Tính năng mới này cho phép chatbot tìm kiếm và gợi ý Personal Trainer (PT) phù hợp với nhu cầu người dùng, với **ưu tiên hiển thị trainer từ các gym gần vị trí người dùng**.

## Kiến trúc hệ thống

### Files mới được tạo:

1. **`app/models/trainer_models.py`**
   - Xử lý và format dữ liệu Personal Trainer từ database
   - Function chính: `safe_get_trainer_data(row)`

2. **`app/services/pt_search_service.py`**
   - Logic tìm kiếm PT thông minh
   - Phát hiện ý định tìm kiếm PT
   - Xây dựng SQL query tối ưu
   - Functions chính:
     - `detect_trainer_search_intent()`: Phát hiện ý định tìm PT
     - `build_trainer_search_query()`: Xây dựng query tìm kiếm
     - `build_nearby_trainer_query()`: Tìm PT gần người dùng
     - `classify_trainer_query()`: Phân loại và tạo SQL

3. **`app/services/pt_recommendation_service.py`**
   - Format phản hồi về PT cho người dùng
   - Nhóm PT theo gym
   - Hiển thị thông tin chi tiết
   - Functions chính:
     - `create_trainer_response()`: Tạo phản hồi tìm kiếm PT
     - `format_trainer_detailed_info()`: Format chi tiết 1 PT

4. **`test_pt_search.py`**
   - Script test chức năng tìm kiếm PT

### Files được cập nhật:

1. **`app/services/response_service.py`**
   - Tích hợp logic tìm kiếm PT vào main chatbot flow
   - Ưu tiên xử lý: PT Search → Gym Search → General Chat

## Cách hoạt động

### 1. Phát hiện ý định tìm kiếm PT

Hệ thống nhận diện các từ khóa:
- **PT keywords**: "pt", "huấn luyện viên", "personal trainer", "trainer", "hlv", "coach"
- **Training context**: "tập riêng", "tập cá nhân", "hướng dẫn tập", "tư vấn tập"
- **Specific goals**: "giảm cân", "tăng cơ", "thể hình", "sức mạnh", "sức bền"

### 2. Tìm kiếm theo vị trí

Khi có tọa độ người dùng (latitude, longitude):
- Tìm các **gym gần người dùng** trước (dùng Haversine formula)
- Lấy **tất cả PT thuộc các gym đó**
- Sắp xếp theo:
  1. Khoảng cách gym gần nhất
  2. Gym hot research
  3. Kinh nghiệm PT (giảm dần)
  4. Tên PT (A-Z)

### 3. Tìm kiếm theo mục tiêu

Hệ thống map các mục tiêu phổ biến:
- Giảm cân → "lose weight", "weight loss"
- Tăng cơ → "build muscle", "muscle gain"
- Thể hình → "bodybuilding", "physique"
- Sức mạnh → "strength", "power"
- Sức bền → "endurance", "cardio"
- Linh hoạt → "flexibility", "yoga"

### 4. Dữ liệu được trả về

Response bao gồm:
```json
{
  "trainers": [
    {
      "id": "uuid",
      "fullName": "Tên PT",
      "email": "email@example.com",
      "phoneNumber": "0123456789",
      "experience": 5,
      "certificates": ["cert1.jpg", "cert2.jpg"],
      "goalTrainings": ["Giảm cân", "Tăng cơ"],
      "gymId": "gym-uuid",
      "gymName": "Tên Gym",
      "gymAddress": "Địa chỉ gym",
      "distance_km": 2.5,
      "gymHotResearch": true
    }
  ],
  "promptResponse": "Formatted response text",
  "conversation_history": [...]
}
```

## Ví dụ sử dụng

### API Request:

```json
POST /chat
{
  "prompt": "Tìm PT gần tôi chuyên giảm cân",
  "latitude": 16.0544,
  "longitude": 108.2022,
  "conversation_history": []
}
```

### Các query mẫu:

1. **Tìm PT gần vị trí**:
   - "Tìm PT gần tôi"
   - "Có huấn luyện viên nào gần đây không?"
   - "Tìm trainer trong vòng 5km"

2. **Tìm PT theo mục tiêu**:
   - "Tìm PT chuyên giảm cân"
   - "Huấn luyện viên tăng cơ ở đâu?"
   - "Tìm coach thể hình"

3. **Tìm PT kết hợp**:
   - "Tìm PT gần tôi chuyên tăng cơ"
   - "PT nào gần đây giúp giảm cân?"
   - "Trainer sức mạnh trong vòng 10km"

### Response mẫu:

**Ít PT (1-5):**
```
**Tìm thấy 3 huấn luyện viên phù hợp:**

1. **Nguyễn Văn A** - FitLife Gym (2.3km) - 5 năm kinh nghiệm
   Chuyên môn: Giảm cân, Tăng cơ, Sức mạnh

2. **Trần Thị B** - PowerHouse Gym (3.1km) - 7 năm kinh nghiệm
   Chuyên môn: Thể hình, Sức mạnh

3. **Lê Văn C** - Active Fitness (4.5km) - 3 năm kinh nghiệm
   Chuyên môn: Giảm cân, Sức bền
```

**Nhiều PT (nhóm theo gym):**
```
**Tìm thấy 15 huấn luyện viên tại 5 phòng gym:**

**FitLife Gym** - 2.3km 🔥
Địa chỉ: 123 Lê Duẩn, Hải Châu, Đà Nẵng
Có 4 huấn luyện viên:
  1. Nguyễn Văn A (5 năm)
  2. Phạm Văn D (3 năm)
  3. Hoàng Thị E (6 năm)
  ... và 1 huấn luyện viên khác

**PowerHouse Gym** - 3.1km
Địa chỉ: 456 Nguyễn Văn Linh, Thanh Khê, Đà Nẵng
Có 3 huấn luyện viên:
  1. Trần Thị B (7 năm)
  2. Võ Văn F (4 năm)
  3. Đặng Thị G (2 năm)
```

## Testing

Chạy test script:
```bash
python test_pt_search.py
```

Test cases bao gồm:
1. ✅ Phát hiện ý định tìm kiếm PT
2. ✅ Xây dựng query tìm kiếm
3. ✅ Tìm PT gần người dùng
4. ✅ Format phản hồi
5. ✅ Tìm theo chuyên môn

## Database Schema

### Tables được sử dụng:

1. **AspNetUsers** (PT và Gym)
   - GymOwnerId: Link PT với Gym
   - Longitude, Latitude: Tọa độ gym

2. **UserDetails**
   - Experience: Kinh nghiệm PT (năm)
   - Certificates: Chứng chỉ
   - Physical stats: Height, Weight, etc.

3. **PTGoalTrainings** (Many-to-Many)
   - ApplicationUsersId → PT
   - GoalTrainingsId → Goal

4. **GoalTrainings**
   - Name: Tên mục tiêu tập luyện

5. **Addresses**
   - Địa chỉ chi tiết của gym

## Tối ưu hóa

### Performance:
- ✅ Sử dụng CTE (Common Table Expressions) để optimize query
- ✅ Bounding box trước khi tính Haversine (giảm tải tính toán)
- ✅ Index trên GymOwnerId, Latitude, Longitude
- ✅ ARRAY_AGG để gộp goal trainings (1 query thay vì N+1)

### UX:
- ✅ Nhóm PT theo gym để dễ nhìn
- ✅ Hiển thị khoảng cách gym
- ✅ Badge 🔥 cho gym hot
- ✅ Sắp xếp thông minh (gần → xa, hot → thường, exp cao → thấp)

## Mở rộng trong tương lai

1. **Filter nâng cao**:
   - Giá PT package
   - Availability (lịch trống)
   - Rating từ customers

2. **Recommendation AI**:
   - ML model để match PT với customer dựa trên:
     - Mục tiêu
     - Physical stats
     - Preference history

3. **Booking integration**:
   - Direct booking từ chat
   - Check PT schedule
   - Price comparison

## Lưu ý quan trọng

⚠️ **Yêu cầu dữ liệu**:
- PT phải có `GymOwnerId` (thuộc gym nào)
- Gym phải có coordinates (Latitude, Longitude)
- PT nên có `UserDetails` record
- PT nên link với `GoalTrainings`

⚠️ **Data quality**:
- AccountStatus = 'Active' (cả PT và Gym)
- IsEnabled = true (cho các bảng liên quan)
- GymName không null/empty

## Support

Nếu gặp vấn đề:
1. Check logs cho error messages
2. Verify database connections
3. Ensure test data exists
4. Run test script để debug

---
**Version**: 1.0.0
**Last Updated**: January 2025
**Author**: FitBridge Development Team

