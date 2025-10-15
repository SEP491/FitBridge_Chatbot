-- Script to add 5 freelance PTs for testing
-- Run this script in your PostgreSQL database

-- Note: You'll need to replace the password hashes with actual hashed passwords
-- This script uses sample UUIDs - adjust as needed

-- PT 1: Trần Minh Tuấn - Male, Weight Loss & Cardio specialist
INSERT INTO "AspNetUsers" (
    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "AvatarUrl"
) VALUES (
    gen_random_uuid(),
    'Trần Minh Tuấn',
    'tuantm.pt@gmail.com',
    '0901234567',
    'AQAAAAEAACcQAAAAEDummy', -- Replace with actual hashed password
    true,
    '1990-05-15',
    'Active',
    NOW(),
    NOW(),
    'tuantm.pt@gmail.com',
    'TUANTM.PT@GMAIL.COM',
    'TUANTM.PT@GMAIL.COM',
    true,
    true,
    false,
    false,
    0,
    10.7769, -- Latitude (Ho Chi Minh City area)
    106.7009, -- Longitude
    'Chuyên gia giảm cân với 8 năm kinh nghiệm. Đã giúp hơn 200 học viên đạt mục tiêu sức khỏe.',
    'https://example.com/avatar1.jpg'
);

-- Get the last inserted PT ID for PT 1
WITH last_pt AS (
    SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'tuantm.pt@gmail.com'
)
-- Add UserDetails for PT 1
INSERT INTO "UserDetails" (
    "Id", "Experience", "Certificates", "Height", "Weight", "Biceps", "Chest", "Waist",
    "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    "Id",
    8, -- 8 years experience
    ARRAY['CPT - Certified Personal Trainer', 'Weight Loss Specialist', 'Nutrition Coach'],
    175.0,
    78.0,
    38.0,
    105.0,
    82.0,
    true,
    NOW(),
    NOW()
FROM last_pt;

-- Add Goal Trainings for PT 1
WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'tuantm.pt@gmail.com'),
goals AS (SELECT "Id" FROM "GoalTrainings" WHERE "Name" IN ('Giảm cân', 'Sức bền') AND "IsEnabled" = true)
INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
SELECT lp."Id", g."Id" FROM last_pt lp CROSS JOIN goals g;

-- Add Freelance Package for PT 1
WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'tuantm.pt@gmail.com')
INSERT INTO "PTFreelancePackages" (
    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", "SessionDurationInMinutes",
    "Description", "ImageUrl", "PtId", "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    gen_random_uuid(),
    'Gói giảm cân cơ bản',
    2500000,
    30,
    12,
    60,
    'Gói tập 12 buổi trong 1 tháng, tập trung vào giảm mỡ và tăng sức bền',
    'https://example.com/package1.jpg',
    "Id",
    true,
    NOW(),
    NOW()
FROM last_pt;

-- PT 2: Nguyễn Thị Hương - Female, Yoga & Flexibility specialist
INSERT INTO "AspNetUsers" (
    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "AvatarUrl"
) VALUES (
    gen_random_uuid(),
    'Nguyễn Thị Hương',
    'huongnt.yoga@gmail.com',
    '0912345678',
    'AQAAAAEAACcQAAAAEDummy',
    false,
    '1992-08-20',
    'Active',
    NOW(),
    NOW(),
    'huongnt.yoga@gmail.com',
    'HUONGNT.YOGA@GMAIL.COM',
    'HUONGNT.YOGA@GMAIL.COM',
    true,
    true,
    false,
    false,
    0,
    10.7629,
    106.6820,
    'Giảng viên Yoga chuyên nghiệp với chứng chỉ quốc tế. Chuyên về Hatha Yoga và Vinyasa Flow.',
    'https://example.com/avatar2.jpg'
);

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huongnt.yoga@gmail.com')
INSERT INTO "UserDetails" (
    "Id", "Experience", "Certificates", "Height", "Weight", "Chest", "Waist",
    "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    "Id",
    5,
    ARRAY['RYT-200 Yoga Alliance', 'Prenatal Yoga Specialist', 'Meditation Instructor'],
    165.0,
    52.0,
    85.0,
    62.0,
    true,
    NOW(),
    NOW()
FROM last_pt;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huongnt.yoga@gmail.com'),
goals AS (SELECT "Id" FROM "GoalTrainings" WHERE "Name" IN ('Linh hoạt', 'Sức bền') AND "IsEnabled" = true)
INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
SELECT lp."Id", g."Id" FROM last_pt lp CROSS JOIN goals g;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huongnt.yoga@gmail.com')
INSERT INTO "PTFreelancePackages" (
    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", "SessionDurationInMinutes",
    "Description", "ImageUrl", "PtId", "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    gen_random_uuid(),
    'Gói Yoga cơ bản',
    1800000,
    30,
    10,
    75,
    'Gói 10 buổi Yoga cho người mới bắt đầu, tập trung vào tư thế cơ bản và hơi thở',
    'https://example.com/package2.jpg',
    "Id",
    true,
    NOW(),
    NOW()
FROM last_pt;

-- PT 3: Lê Quang Huy - Male, Bodybuilding & Strength specialist
INSERT INTO "AspNetUsers" (
    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "AvatarUrl"
) VALUES (
    gen_random_uuid(),
    'Lê Quang Huy',
    'huylq.bodybuilding@gmail.com',
    '0923456789',
    'AQAAAAEAACcQAAAAEDummy',
    true,
    '1988-03-10',
    'Active',
    NOW(),
    NOW(),
    'huylq.bodybuilding@gmail.com',
    'HUYLQ.BODYBUILDING@GMAIL.COM',
    'HUYLQ.BODYBUILDING@GMAIL.COM',
    true,
    true,
    false,
    false,
    0,
    10.8020,
    106.7150,
    'Vận động viên thể hình chuyên nghiệp. Top 3 Men Physique 2023. Chuyên hướng dẫn tăng cơ và điêu khắc cơ thể.',
    'https://example.com/avatar3.jpg'
);

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huylq.bodybuilding@gmail.com')
INSERT INTO "UserDetails" (
    "Id", "Experience", "Certificates", "Height", "Weight", "Biceps", "Chest", "Waist", "Shoulder",
    "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    "Id",
    10,
    ARRAY['ISSA Bodybuilding Specialist', 'Sports Nutrition Certification', 'Strength & Conditioning Coach'],
    180.0,
    92.0,
    42.0,
    115.0,
    78.0,
    125.0,
    true,
    NOW(),
    NOW()
FROM last_pt;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huylq.bodybuilding@gmail.com'),
goals AS (SELECT "Id" FROM "GoalTrainings" WHERE "Name" IN ('Thể hình', 'Tăng cơ', 'Sức mạnh') AND "IsEnabled" = true)
INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
SELECT lp."Id", g."Id" FROM last_pt lp CROSS JOIN goals g;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'huylq.bodybuilding@gmail.com')
INSERT INTO "PTFreelancePackages" (
    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", "SessionDurationInMinutes",
    "Description", "ImageUrl", "PtId", "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    gen_random_uuid(),
    'Gói tăng cơ chuyên sâu',
    3500000,
    60,
    20,
    90,
    'Gói 20 buổi tập trong 2 tháng, chương trình tăng cơ bài bản kèm hướng dẫn dinh dưỡng',
    'https://example.com/package3.jpg',
    "Id",
    true,
    NOW(),
    NOW()
FROM last_pt;

-- PT 4: Phạm Thị Mai - Female, General Fitness & Rehabilitation
INSERT INTO "AspNetUsers" (
    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "AvatarUrl"
) VALUES (
    gen_random_uuid(),
    'Phạm Thị Mai',
    'maipt.fitness@gmail.com',
    '0934567890',
    'AQAAAAEAACcQAAAAEDummy',
    false,
    '1995-11-25',
    'Active',
    NOW(),
    NOW(),
    'maipt.fitness@gmail.com',
    'MAIPT.FITNESS@GMAIL.COM',
    'MAIPT.FITNESS@GMAIL.COM',
    true,
    true,
    false,
    false,
    0,
    10.7900,
    106.6650,
    'PT chuyên phục hồi chức năng sau chấn thương. Làm việc với nhiều vận động viên và người cao tuổi.',
    'https://example.com/avatar4.jpg'
);

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'maipt.fitness@gmail.com')
INSERT INTO "UserDetails" (
    "Id", "Experience", "Certificates", "Height", "Weight", "Chest", "Waist",
    "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    "Id",
    6,
    ARRAY['Physical Therapy Assistant', 'Corrective Exercise Specialist', 'Senior Fitness Specialist'],
    168.0,
    58.0,
    88.0,
    68.0,
    true,
    NOW(),
    NOW()
FROM last_pt;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'maipt.fitness@gmail.com'),
goals AS (SELECT "Id" FROM "GoalTrainings" WHERE "Name" IN ('Phục hồi chức năng', 'Thể lực tổng hợp') AND "IsEnabled" = true)
INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
SELECT lp."Id", g."Id" FROM last_pt lp CROSS JOIN goals g;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'maipt.fitness@gmail.com')
INSERT INTO "PTFreelancePackages" (
    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", "SessionDurationInMinutes",
    "Description", "ImageUrl", "PtId", "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    gen_random_uuid(),
    'Gói phục hồi chức năng',
    2200000,
    45,
    15,
    60,
    'Chương trình phục hồi sau chấn thương hoặc phẫu thuật, bài tập điều chỉnh tư thế',
    'https://example.com/package4.jpg',
    "Id",
    true,
    NOW(),
    NOW()
FROM last_pt;

-- PT 5: Võ Đức Thắng - Male, Functional Training & CrossFit
INSERT INTO "AspNetUsers" (
    "Id", "FullName", "Email", "PhoneNumber", "Password", "IsMale", "Dob",
    "AccountStatus", "CreatedAt", "UpdatedAt", "UserName", "NormalizedUserName",
    "NormalizedEmail", "EmailConfirmed", "PhoneNumberConfirmed", "TwoFactorEnabled",
    "LockoutEnabled", "AccessFailedCount", "Latitude", "Longitude", "Bio", "AvatarUrl"
) VALUES (
    gen_random_uuid(),
    'Võ Đức Thắng',
    'thangvd.crossfit@gmail.com',
    '0945678901',
    'AQAAAAEAACcQAAAAEDummy',
    true,
    '1991-07-08',
    'Active',
    NOW(),
    NOW(),
    'thangvd.crossfit@gmail.com',
    'THANGVD.CROSSFIT@GMAIL.COM',
    'THANGVD.CROSSFIT@GMAIL.COM',
    true,
    true,
    false,
    false,
    0,
    10.7500,
    106.6900,
    'CrossFit Level 2 Trainer. Chuyên functional training và HIIT. Giúp bạn đạt thể lực đỉnh cao.',
    'https://example.com/avatar5.jpg'
);

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'thangvd.crossfit@gmail.com')
INSERT INTO "UserDetails" (
    "Id", "Experience", "Certificates", "Height", "Weight", "Biceps", "Chest", "Waist", "Shoulder",
    "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    "Id",
    7,
    ARRAY['CrossFit Level 2', 'Olympic Weightlifting Coach', 'Functional Movement Screen'],
    178.0,
    85.0,
    40.0,
    108.0,
    80.0,
    120.0,
    true,
    NOW(),
    NOW()
FROM last_pt;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'thangvd.crossfit@gmail.com'),
goals AS (SELECT "Id" FROM "GoalTrainings" WHERE "Name" IN ('Sức mạnh', 'Sức bền', 'Thể lực tổng hợp') AND "IsEnabled" = true)
INSERT INTO "PTGoalTrainings" ("ApplicationUsersId", "GoalTrainingsId")
SELECT lp."Id", g."Id" FROM last_pt lp CROSS JOIN goals g;

WITH last_pt AS (SELECT "Id" FROM "AspNetUsers" WHERE "Email" = 'thangvd.crossfit@gmail.com')
INSERT INTO "PTFreelancePackages" (
    "Id", "Name", "Price", "DurationInDays", "NumOfSessions", "SessionDurationInMinutes",
    "Description", "ImageUrl", "PtId", "IsEnabled", "CreatedAt", "UpdatedAt"
)
SELECT
    gen_random_uuid(),
    'Gói CrossFit Intensive',
    3000000,
    30,
    16,
    75,
    'Gói 16 buổi CrossFit trong 1 tháng, bao gồm Olympic lifting và conditioning',
    'https://example.com/package5.jpg',
    "Id",
    true,
    NOW(),
    NOW()
FROM last_pt;

-- Verify the insertions
SELECT
    u."FullName",
    u."Email",
    u."PhoneNumber",
    u."IsMale",
    ud."Experience",
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
GROUP BY u."FullName", u."Email", u."PhoneNumber", u."IsMale", ud."Experience", ud."Certificates"
ORDER BY u."FullName";

