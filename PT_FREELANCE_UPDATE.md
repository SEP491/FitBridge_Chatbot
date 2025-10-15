# PT Freelance Integration Update

## Overview
Updated the FitBridge Chatbot to query and return both gym-affiliated PTs and freelance PTs in search results.

## Changes Made

### 1. **pt_search_service.py** - Query Logic Updated
- **Modified `build_nearby_trainer_query()`**: Now includes both gym and freelance PTs
  - Added `pt_latitude` and `pt_longitude` fields for freelance PTs
  - Created separate CTEs for `GymPTs` and `FreelancePTs`
  - Freelance PTs calculate distance from their own location (not gym location)
  - Added `pt_type` field ('gym' or 'freelance') to distinguish PT types
  - Results are combined using UNION ALL

- **Modified `build_trainer_search_query()`**: General PT search now includes freelance
  - Changed base condition from requiring `GymOwnerId IS NOT NULL` to:
    ```sql
    (pt."GymOwnerId" IS NOT NULL OR EXISTS (
        SELECT 1 FROM "PTFreelancePackages" pfp 
        WHERE pfp."PtId" = pt."Id" AND pfp."IsEnabled" = true
    ))
    ```
  - Added `is_freelance` flag using COUNT of PTFreelancePackages
  - Separate CTEs for gym and freelance PTs with appropriate fields
  - Freelance PTs show as "Huấn luyện viên tự do" with "Tập tại địa điểm linh hoạt"

### 2. **trainer_models.py** - Data Model Updated
- **Added new fields to `safe_get_trainer_data()`**:
  - `ptType`: 'gym' or 'freelance' 
  - `isFreelance`: Boolean flag
  - `bio`: Personal bio/description field
- **Updated default values** in error handling to include new fields

### 3. **pt_recommendation_service.py** - Response Formatting Updated
- **Enhanced `create_trainer_response()`**:
  - **Single trainer**: Shows 💼 badge for freelance PTs
  - **Few trainers (2-5)**: Each freelance PT gets 💼 badge and "Huấn luyện viên tự do" label
  - **Many trainers**: 
    - Separates into two sections: "🏢 Huấn luyện viên tại phòng gym" and "💼 Huấn luyện viên tự do"
    - Shows count breakdown (e.g., "15 huấn luyện viên (10 PT gym, 5 PT tự do)")
    - Gym PTs grouped by gym (max 8 gyms, 3 PTs per gym)
    - Freelance PTs listed separately (max 5 shown)

- **Enhanced `format_trainer_detailed_info()`**:
  - Shows "💼 Huấn luyện viên tự do" badge for freelance PTs
  - Different location display: "Địa điểm tập: Linh hoạt theo yêu cầu"
  - Includes bio field if available

## How It Works

### Database Detection
The system identifies freelance PTs by checking if they have entries in the `PTFreelancePackages` table:
- **Gym PT**: Has `GymOwnerId` NOT NULL
- **Freelance PT**: Has at least one active package in `PTFreelancePackages`
- **Both**: A PT can theoretically be both (works at gym AND offers freelance services)

### Distance Calculation
- **Gym PTs**: Distance calculated from gym's location (Latitude/Longitude in gym's AspNetUsers record)
- **Freelance PTs**: Distance calculated from PT's personal location (their own Latitude/Longitude)

### Search Priority
When searching for PTs, the system:
1. Prioritizes gym PTs first (pt_type DESC)
2. Then orders by distance (closest first)
3. Then by hot research status
4. Then by experience level
5. Finally by name alphabetically

## Example Queries

### Query 1: "Tìm PT gần tôi"
Returns both gym and freelance PTs within 10km, sorted by type then distance.

### Query 2: "PT giảm cân"
Returns all PTs (gym + freelance) specializing in weight loss.

### Query 3: "Tìm PT nữ có kinh nghiệm từ 3 năm"
Returns female PTs from both gym and freelance with 3+ years experience.

## Response Format Examples

### Few Results (2-5 PTs):
```
**Tìm thấy 3 huấn luyện viên phù hợp:**

1. **Nguyễn Văn A** - FitZone Gym (2.5km) - 5 năm kinh nghiệm
  Chuyên môn: Giảm cân, Tăng cơ

2. **Trần Thị B** 💼 - Huấn luyện viên tự do (3.2km) - 3 năm kinh nghiệm
  Chuyên môn: Yoga, Linh hoạt

3. **Lê Văn C** - PowerGym (4.1km) - 7 năm kinh nghiệm
  Chuyên môn: Thể hình, Sức mạnh
```

### Many Results (6+ PTs):
```
**Tìm thấy 15 huấn luyện viên (10 PT gym, 5 PT tự do):**

**🏢 Huấn luyện viên tại phòng gym:**

**FitZone Gym** - 2.5km 🔥
Có 4 huấn luyện viên:
  1. Nguyễn Văn A (5 năm)
  2. Phạm Thị D (4 năm)
  3. Hoàng Văn E (3 năm)
  ... và 1 huấn luyện viên khác

**PowerGym** - 4.1km
Có 6 huấn luyện viên:
  1. Lê Văn C (7 năm)
  2. Đặng Thị F (6 năm)
  3. Vũ Văn G (4 năm)
  ... và 3 huấn luyện viên khác

**💼 Huấn luyện viên tự do:**

1. **Trần Thị B** - 3.2km (3 năm)
  Chuyên môn: Yoga, Linh hoạt
2. **Mai Văn H** - 5.5km (8 năm)
  Chuyên môn: Giảm cân, Cardio
...
```

## Testing Recommendations

1. Test with PT that has only gym affiliation
2. Test with PT that has only freelance packages
3. Test with PT that has both
4. Test distance calculations for freelance PTs
5. Test filtering (gender, experience, goals) works for both types
6. Test nearby search includes both types correctly

## Notes

- Freelance PTs without location data (NULL latitude/longitude) will still appear in non-location searches
- The system maintains backward compatibility - existing gym PT searches work exactly as before
- New fields are optional - if a PT doesn't have bio or freelance packages, they're handled gracefully

