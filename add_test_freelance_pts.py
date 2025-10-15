#!/usr/bin/env python3
"""
Script to add 5 freelance PTs to the database for testing
Run this script: python add_test_freelance_pts.py
"""

import sys
import uuid
from datetime import datetime
from app.database.connection import get_database_connection

def add_freelance_pts():
    """Add 5 freelance PTs to the database"""
    conn, cursor = get_database_connection()

    if conn is None or cursor is None:
        print("❌ Không thể kết nối database")
        return False

    # Test data for 5 freelance PTs
    freelance_pts = [
        {
            'full_name': 'Trần Minh Tuấn',
            'email': 'tuantm.pt@gmail.com',
            'phone': '0901234567',
            'is_male': True,
            'dob': '1990-05-15',
            'lat': 10.7769,
            'lng': 106.7009,
            'bio': 'Chuyên gia giảm cân với 8 năm kinh nghiệm. Đã giúp hơn 200 học viên đạt mục tiêu sức khỏe.',
            'experience': 8,
            'certificates': ['CPT - Certified Personal Trainer', 'Weight Loss Specialist', 'Nutrition Coach'],
            'height': 175.0,
            'weight': 78.0,
            'biceps': 38.0,
            'chest': 105.0,
            'waist': 82.0,
            'goals': ['Giảm cân', 'Sức bền'],
            'package_name': 'Gói giảm cân cơ bản',
            'package_price': 2500000,
            'package_duration': 30,
            'package_sessions': 12,
            'package_session_duration': 60,
            'package_desc': 'Gói tập 12 buổi trong 1 tháng, tập trung vào giảm mỡ và tăng sức bền'
        },
        {
            'full_name': 'Nguyễn Thị Hương',
            'email': 'huongnt.yoga@gmail.com',
            'phone': '0912345678',
            'is_male': False,
            'dob': '1992-08-20',
            'lat': 10.7629,
            'lng': 106.6820,
            'bio': 'Giảng viên Yoga chuyên nghiệp với chứng chỉ quốc tế. Chuyên về Hatha Yoga và Vinyasa Flow.',
            'experience': 5,
            'certificates': ['RYT-200 Yoga Alliance', 'Prenatal Yoga Specialist', 'Meditation Instructor'],
            'height': 165.0,
            'weight': 52.0,
            'chest': 85.0,
            'waist': 62.0,
            'goals': ['Linh hoạt', 'Sức bền'],
            'package_name': 'Gói Yoga cơ bản',
            'package_price': 1800000,
            'package_duration': 30,
            'package_sessions': 10,
            'package_session_duration': 75,
            'package_desc': 'Gói 10 buổi Yoga cho người mới bắt đầu, tập trung vào tư thế cơ bản và hơi thở'
        },
        {
            'full_name': 'Lê Quang Huy',
            'email': 'huylq.bodybuilding@gmail.com',
            'phone': '0923456789',
            'is_male': True,
            'dob': '1988-03-10',
            'lat': 10.8020,
            'lng': 106.7150,
            'bio': 'Vận động viên thể hình chuyên nghiệp. Top 3 Men Physique 2023. Chuyên hướng dẫn tăng cơ và điêu khắc cơ thể.',
            'experience': 10,
            'certificates': ['ISSA Bodybuilding Specialist', 'Sports Nutrition Certification', 'Strength & Conditioning Coach'],
            'height': 180.0,
            'weight': 92.0,
            'biceps': 42.0,
            'chest': 115.0,
            'waist': 78.0,
            'shoulder': 125.0,
            'goals': ['Thể hình', 'Tăng cơ', 'Sức mạnh'],
            'package_name': 'Gói tăng cơ chuyên sâu',
            'package_price': 3500000,
            'package_duration': 60,
            'package_sessions': 20,
            'package_session_duration': 90,
            'package_desc': 'Gói 20 buổi tập trong 2 tháng, chương trình tăng cơ bài bản kèm hướng dẫn dinh dưỡng'
        },
        {
            'full_name': 'Phạm Thị Mai',
            'email': 'maipt.fitness@gmail.com',
            'phone': '0934567890',
            'is_male': False,
            'dob': '1995-11-25',
            'lat': 10.7900,
            'lng': 106.6650,
            'bio': 'PT chuyên phục hồi chức năng sau chấn thương. Làm việc với nhiều vận động viên và người cao tuổi.',
            'experience': 6,
            'certificates': ['Physical Therapy Assistant', 'Corrective Exercise Specialist', 'Senior Fitness Specialist'],
            'height': 168.0,
            'weight': 58.0,
            'chest': 88.0,
            'waist': 68.0,
            'goals': ['Phục hồi chức năng', 'Thể lực tổng hợp'],
            'package_name': 'Gói phục hồi chức năng',
            'package_price': 2200000,
            'package_duration': 45,
            'package_sessions': 15,
            'package_session_duration': 60,
            'package_desc': 'Chương trình phục hồi sau chấn thương hoặc phẫu thuật, bài tập điều chỉnh tư thế'
        },
        {
            'full_name': 'Võ Đức Thắng',
            'email': 'thangvd.crossfit@gmail.com',
            'phone': '0945678901',
            'is_male': True,
            'dob': '1991-07-08',
            'lat': 10.7500,
            'lng': 106.6900,
            'bio': 'CrossFit Level 2 Trainer. Chuyên functional training và HIIT. Giúp bạn đạt thể lực đỉnh cao.',
            'experience': 7,
            'certificates': ['CrossFit Level 2', 'Olympic Weightlifting Coach', 'Functional Movement Screen'],
            'height': 178.0,
            'weight': 85.0,
            'biceps': 40.0,
            'chest': 108.0,
            'waist': 80.0,
            'shoulder': 120.0,
            'goals': ['Sức mạnh', 'Sức bền', 'Thể lực tổng hợp'],
            'package_name': 'Gói CrossFit Intensive',
            'package_price': 3000000,
            'package_duration': 30,
            'package_sessions': 16,
            'package_session_duration': 75,
            'package_desc': 'Gói 16 buổi CrossFit trong 1 tháng, bao gồm Olympic lifting và conditioning'
        }
    ]

    try:
        added_count = 0

        for pt_data in freelance_pts:
            print(f"\n{'='*60}")
            print(f"Đang thêm PT: {pt_data['full_name']}")

            # Check if PT already exists
            cursor.execute(f"""
                SELECT "Id" FROM "AspNetUsers" WHERE "Email" = '{pt_data['email']}'
            """)
            existing = cursor.fetchone()

            if existing:
                print(f"⚠️  PT {pt_data['full_name']} đã tồn tại (Email: {pt_data['email']})")
                continue

            pt_id = str(uuid.uuid4())

            # 1. Insert into AspNetUsers (with GymImages as empty array)
            cursor.execute(f"""
                INSERT INTO "AspNetUsers" (
                    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
                    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
                    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
                    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "GymImages"
                ) VALUES (
                    '{pt_id}',
                    '{pt_data['full_name']}',
                    '{pt_data['email']}',
                    '{pt_data['phone']}',
                    'AQAAAAEAACcQAAAAETestPassword123!',
                    {pt_data['is_male']},
                    '{pt_data['dob']}',
                    'Active',
                    NOW(),
                    NOW(),
                    '{pt_data['email']}',
                    '{pt_data['email'].upper()}',
                    '{pt_data['email'].upper()}',
                    true,
                    true,
                    false,
                    false,
                    0,
                    {pt_data['lat']},
                    {pt_data['lng']},
                    '{pt_data['bio']}',
                    ARRAY[]::TEXT[]
                )
            """)
            print(f"✅ Đã thêm vào AspNetUsers")

            # 2. Insert into UserDetails
            certificates_str = '{' + ','.join([f'"{c}"' for c in pt_data['certificates']]) + '}'

            user_details_fields = [
                f'"Id" = \'{pt_id}\'',
                f'"Experience" = {pt_data['experience']}',
                f'"Certificates" = \'{certificates_str}\'',
                f'"Height" = {pt_data['height']}',
                f'"Weight" = {pt_data['weight']}',
                f'"IsEnabled" = true',
                f'"CreatedAt" = NOW()',
                f'"UpdatedAt" = NOW()'
            ]

            if 'biceps' in pt_data:
                user_details_fields.append(f'"Biceps" = {pt_data["biceps"]}')
            if 'chest' in pt_data:
                user_details_fields.append(f'"Chest" = {pt_data["chest"]}')
            if 'waist' in pt_data:
                user_details_fields.append(f'"Waist" = {pt_data["waist"]}')
            if 'shoulder' in pt_data:
                user_details_fields.append(f'"Shoulder" = {pt_data["shoulder"]}')

            cursor.execute(f"""
                INSERT INTO "UserDetails" ({', '.join([f.split(' = ')[0] for f in user_details_fields])})
                VALUES ({', '.join([f.split(' = ')[1] for f in user_details_fields])})
            """)
            print(f"✅ Đã thêm vào UserDetails")

            # 3. Insert into PTGoalTrainings
            for goal_name in pt_data['goals']:
                cursor.execute(f"""
                    INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
                    SELECT '{pt_id}', "Id" FROM "GoalTrainings" 
                    WHERE "Name" = '{goal_name}' AND "IsEnabled" = true
                """)
            print(f"✅ Đã thêm {len(pt_data['goals'])} mục tiêu tập luyện")

            # 4. Insert into PTFreelancePackages
            package_id = str(uuid.uuid4())
            cursor.execute(f"""
                INSERT INTO "PTFreelancePackages" (
                    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", 
                    "SessionDurationInMinutes", "Description", "PtId", 
                    "IsEnabled", "CreatedAt", "UpdatedAt"
                ) VALUES (
                    '{package_id}',
                    '{pt_data['package_name']}',
                    {pt_data['package_price']},
                    {pt_data['package_duration']},
                    {pt_data['package_sessions']},
                    {pt_data['package_session_duration']},
                    '{pt_data['package_desc']}',
                    '{pt_id}',
                    true,
                    NOW(),
                    NOW()
                )
            """)
            print(f"✅ Đã thêm gói freelance: {pt_data['package_name']}")

            conn.commit()
            added_count += 1
            print(f"🎉 Hoàn thành thêm PT: {pt_data['full_name']}")

        print(f"\n{'='*60}")
        print(f"✨ TỔNG KẾT: Đã thêm thành công {added_count}/5 PT freelance")
        print(f"{'='*60}")

        # Verify
        print("\n📊 KIỂM TRA DỮ LIỆU:")
        cursor.execute("""
            SELECT 
                u."FullName" as fullname,
                u."Email" as email,
                u."IsMale" as ismale,
                ud."Experience" as experience,
                ARRAY_LENGTH(ud."Certificates", 1) as num_certificates,
                COUNT(DISTINCT pfp."Id") as num_packages,
                STRING_AGG(DISTINCT gt."Name", ', ') as specializations
            FROM "AspNetUsers" u
            LEFT JOIN "UserDetails" ud ON u."Id" = ud."Id"
            LEFT JOIN "PTFreelancePackages" pfp ON u."Id" = pfp."PtId" AND pfp."IsEnabled" = true
            LEFT JOIN "PTGoalTrainings" pgt ON u."Id" = pgt."ApplicationUsersId"
            LEFT JOIN "GoalTrainings" gt ON pgt."GoalTrainingsId" = gt."Id" AND gt."IsEnabled" = true
            WHERE u."Email" IN (
                'tuantm.pt@gmail.com',
                'huongnt.yoga@gmail.com',
                'huylq.bodybuilding@gmail.com',
                'maipt.fitness@gmail.com',
                'thangvd.crossfit@gmail.com'
            )
            GROUP BY u."FullName", u."Email", u."IsMale", ud."Experience", ud."Certificates"
            ORDER BY u."FullName"
        """)

        results = cursor.fetchall()
        if results:
            print(f"\n{'Tên':<25} {'Email':<30} {'Giới':<6} {'KN':<4} {'CC':<4} {'Gói':<4} {'Chuyên môn'}")
            print("-" * 130)
            for row in results:
                gender = "Nam" if row['ismale'] else "Nữ"
                specializations = row['specializations'] if row['specializations'] else 'N/A'
                print(f"{row['fullname']:<25} {row['email']:<30} {gender:<6} {row['experience']:<4} {row['num_certificates']:<4} {row['num_packages']:<4} {specializations}")
        else:
            print("⚠️  Không tìm thấy dữ liệu (nhưng đã insert thành công)")

        return True

    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False

if __name__ == "__main__":
    print("🚀 BẮT ĐẦU THÊM 5 PT FREELANCE VÀO DATABASE")
    print("=" * 60)

    success = add_freelance_pts()

    if success:
        print("\n✅ HOÀN THÀNH!")
        print("\n💡 BẠN CÓ THỂ TEST VỚI CÁC QUERY SAU:")
        print("   - Tìm PT gần tôi")
        print("   - Tìm PT giảm cân")
        print("   - Tìm PT nữ")
        print("   - Tìm PT yoga")
        print("   - Tìm PT thể hình có kinh nghiệm từ 8 năm")
        sys.exit(0)
    else:
        print("\n❌ CÓ LỖI XẢY RA!")
        sys.exit(1)
