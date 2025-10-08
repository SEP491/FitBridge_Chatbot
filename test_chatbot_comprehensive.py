#!/usr/bin/env python3
"""
Comprehensive Test Cases for FitBridge Chatbot
Tests tất cả chức năng: PT Search, Gym Search, General Chat
"""

import asyncio
import json
from datetime import datetime
from app.models.chat_models import ChatRequest
from app.services.response_service import get_response_with_history

# Test coordinates (Đà Nẵng và TP.HCM)
DANANG_COORDS = {"latitude": 16.0544, "longitude": 108.2022}
HCMC_COORDS = {"latitude": 10.8231, "longitude": 106.6297}

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_test(test_num, description):
    """Print test case header"""
    print(f"{Colors.OKCYAN}{Colors.BOLD}Test {test_num}: {description}{Colors.ENDC}")

def print_result(has_data, data_type, count=0):
    """Print test result"""
    if has_data:
        print(f"{Colors.OKGREEN}✅ PASS - Tìm thấy {count} {data_type}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}❌ FAIL - Không tìm thấy {data_type}{Colors.ENDC}")

def print_response(response):
    """Print formatted response"""
    print(f"{Colors.WARNING}Response:{Colors.ENDC}")
    print(f"{response[:300]}..." if len(response) > 300 else response)

def run_test(test_num, description, prompt, coords=None, conversation_history=None):
    """Run a single test case"""
    print_test(test_num, description)
    print(f"  Prompt: '{prompt}'")
    if coords:
        print(f"  Coords: Lat {coords['latitude']}, Lng {coords['longitude']}")

    try:
        result = get_response_with_history(
            user_input=prompt,
            conversation_history=conversation_history or [],
            longitude=coords.get('longitude') if coords else None,
            latitude=coords.get('latitude') if coords else None
        )

        prompt_response = result.get('promptResponse', '')
        trainers = result.get('trainers', [])
        gyms = result.get('gyms', [])

        if trainers:
            print_result(True, "PT", len(trainers))
            print(f"  Sample PTs:")
            for i, pt in enumerate(trainers[:3], 1):
                gym_name = pt.get('gymName', 'N/A')
                distance = f" ({pt.get('distance_km')}km)" if pt.get('distance_km') else ""
                exp = f" - {pt.get('experience')} năm" if pt.get('experience') else ""
                print(f"    {i}. {pt['fullName']} @ {gym_name}{distance}{exp}")

        elif gyms:
            print_result(True, "Gym", len(gyms))
            print(f"  Sample Gyms:")
            for i, gym in enumerate(gyms[:3], 1):
                distance = f" ({gym.get('distance_km')}km)" if gym.get('distance_km') else ""
                hot = " 🔥" if gym.get('hotResearch') else ""
                print(f"    {i}. {gym['gymName']}{distance}{hot}")

        else:
            print_result(False, "data")

        print_response(prompt_response)
        print()

        return result

    except Exception as e:
        print(f"{Colors.FAIL}❌ ERROR: {str(e)}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
        return None

def test_pt_search():
    """Test cases cho tìm kiếm Personal Trainer"""
    print_section("🏋️ PERSONAL TRAINER SEARCH TESTS")

    # Test 1: Tìm PT theo giới tính
    run_test(1, "Tìm PT nữ", "Tìm PT nữ")

    # Test 2: Tìm PT theo goal
    run_test(2, "Tìm PT chuyên giảm cân", "Tìm PT chuyên giảm cân")

    # Test 3: Tìm PT theo giới tính + goal
    run_test(3, "Tìm PT nữ chuyên tăng cơ", "Tìm PT nữ chuyên tăng cơ cho tôi")

    # Test 4: Tìm PT theo nhiều goals
    run_test(4, "Tìm PT chuyên thể hình và sức mạnh", "Tìm huấn luyện viên chuyên thể hình và sức mạnh")

    # Test 5: Tìm PT nam chuyên giảm cân
    run_test(5, "Tìm PT nam chuyên giảm cân", "Tìm PT nam chuyên giảm cân")

    # Test 6: Tìm PT gần vị trí (Đà Nẵng)
    run_test(6, "Tìm PT gần tôi (Đà Nẵng)", "Tìm PT gần tôi", DANANG_COORDS)

    # Test 7: Tìm PT gần vị trí (TP.HCM)
    run_test(7, "Tìm PT gần tôi (TP.HCM)", "Tìm PT gần đây", HCMC_COORDS)

    # Test 8: Tìm PT gần + filter goal
    run_test(8, "Tìm PT gần chuyên giảm cân", "Tìm PT gần tôi chuyên giảm cân", DANANG_COORDS)

    # Test 9: Tìm PT với khoảng cách cụ thể
    run_test(9, "Tìm PT trong vòng 5km", "Tìm PT trong vòng 5km chuyên yoga", DANANG_COORDS)

    # Test 10: Tìm PT chuyên sức bền
    run_test(10, "Tìm PT chuyên cardio", "Tìm trainer chuyên cardio và sức bền")

    # Test 11: Tìm PT chuyên phục hồi
    run_test(11, "Tìm PT phục hồi chức năng", "Tìm PT giúp phục hồi chấn thương")

    # Test 12: Tìm PT với ngữ cảnh tập luyện
    run_test(12, "Tìm PT dạy tập riêng", "Tìm PT dạy tập riêng cho người mới bắt đầu")

def test_gym_search():
    """Test cases cho tìm kiếm Gym"""
    print_section("🏢 GYM SEARCH TESTS")

    # Test 13: Tìm gym gần vị trí
    run_test(13, "Tìm gym gần tôi", "Tìm gym gần tôi", DANANG_COORDS)

    # Test 14: Tìm gym hot
    run_test(14, "Tìm gym phổ biến", "Tìm gym hot và phổ biến")

    # Test 15: Tìm gym theo tên
    run_test(15, "Tìm gym theo tên", "Tìm gym California Fitness")

    # Test 16: Tìm gym trong khu vực
    run_test(16, "Tìm gym quận 1", "Tìm gym ở quận 1")

    # Test 17: Tìm gym với khoảng cách
    run_test(17, "Tìm gym trong 10km", "Tìm gym trong vòng 10km", HCMC_COORDS)

    # Test 18: Tìm gym gần nhất
    run_test(18, "Gym nào gần nhất", "Gym nào gần nhất với tôi", DANANG_COORDS)

    # Test 19: Tìm tất cả gym
    run_test(19, "Danh sách gym", "Cho tôi danh sách các gym")

    # Test 20: Tìm gym trong thành phố
    run_test(20, "Gym ở Đà Nẵng", "Tìm gym ở Đà Nẵng")

    # Test 21: Tìm gym hot gần vị trí
    run_test(21, "Gym hot gần tôi", "Tìm gym hot gần tôi", HCMC_COORDS)

    # Test 22: Tìm gym rất gần (bán kính nhỏ)
    run_test(22, "Gym rất gần", "Gym nào rất gần tôi", DANANG_COORDS)

def test_general_chat():
    """Test cases cho hội thoại chung"""
    print_section("💬 GENERAL CHAT TESTS")

    # Test 23: Chào hỏi
    run_test(23, "Chào hỏi", "Xin chào")

    # Test 24: Hỏi về tập luyện
    run_test(24, "Tư vấn tập luyện", "Tôi nên tập gì để giảm cân?")

    # Test 25: Hỏi về dinh dưỡng
    run_test(25, "Tư vấn dinh dưỡng", "Ăn gì để tăng cơ hiệu quả?")

    # Test 26: Hỏi về lịch tập
    run_test(26, "Lịch tập", "Tôi nên tập bao nhiêu ngày một tuần?")

    # Test 27: Cảm ơn
    run_test(27, "Cảm ơn", "Cảm ơn bạn nhiều")

    # Test 28: Câu hỏi ngoài phạm vi
    run_test(28, "Out of scope", "Thời tiết hôm nay thế nào?")

    # Test 29: Hỏi về bài tập cụ thể
    run_test(29, "Bài tập cụ thể", "Squat có tốt không?")

    # Test 30: Hỏi về mục tiêu tập luyện
    run_test(30, "Mục tiêu tập luyện", "Làm sao để có body 6 múi?")

def test_conversational_flow():
    """Test cases cho luồng hội thoại"""
    print_section("🔄 CONVERSATIONAL FLOW TESTS")

    # Test 31: Hội thoại nhiều lượt - tìm gym rồi hỏi thêm
    conv_history = []

    print_test(31, "Luồng hội thoại: Tìm gym -> Hỏi về PT")
    result1 = run_test("31a", "Bước 1: Tìm gym", "Tìm gym gần tôi", DANANG_COORDS, conv_history)

    if result1:
        conv_history = result1.get('conversation_history', [])
        run_test("31b", "Bước 2: Hỏi về PT", "Gym đó có PT nào tốt không?", None, conv_history)

    # Test 32: Hội thoại nhiều lượt - tìm PT rồi hỏi thêm
    conv_history2 = []

    print_test(32, "Luồng hội thoại: Tìm PT -> Hỏi chi tiết")
    result2 = run_test("32a", "Bước 1: Tìm PT", "Tìm PT nữ chuyên giảm cân", None, conv_history2)

    if result2:
        conv_history2 = result2.get('conversation_history', [])
        run_test("32b", "Bước 2: Hỏi kinh nghiệm", "PT nào có kinh nghiệm nhất?", None, conv_history2)

    # Test 33: Conversation context memory
    conv_history3 = []

    print_test(33, "Test memory: Nhớ ngữ cảnh")
    result3 = run_test("33a", "Bước 1: Nói tên", "Tên tôi là John", None, conv_history3)

    if result3:
        conv_history3 = result3.get('conversation_history', [])
        run_test("33b", "Bước 2: Hỏi tên", "Tên tôi là gì?", None, conv_history3)

def test_edge_cases():
    """Test cases cho các trường hợp đặc biệt"""
    print_section("⚠️ EDGE CASES & ERROR HANDLING")

    # Test 34: Query rất ngắn
    run_test(34, "Query ngắn", "PT")

    # Test 35: Query rất dài
    run_test(35, "Query dài",
             "Tôi muốn tìm một personal trainer nữ có kinh nghiệm chuyên về giảm cân và thể hình "
             "gần vị trí của tôi trong vòng 5km và có thể dạy tập vào buổi tối")

    # Test 36: Query với typo
    run_test(36, "Query với lỗi chính tả", "Tim pt nu chuyen giam can")

    # Test 37: Mixed language (Tiếng Việt + English)
    run_test(37, "Mixed language", "Find PT female chuyên lose weight")

    # Test 38: Emoji trong query
    run_test(38, "Query với emoji", "Tìm PT 💪 chuyên gym 🏋️")

    # Test 39: Tọa độ không hợp lệ
    run_test(39, "Tọa độ lỗi", "Tìm gym gần tôi", {"latitude": 0, "longitude": 0})

    # Test 40: Query trống
    run_test(40, "Empty query", "")

    # Test 41: Special characters
    run_test(41, "Special chars", "Tìm PT @#$% gym?!?!")

    # Test 42: Numbers in query
    run_test(42, "Với số", "Tìm PT có 5 năm kinh nghiệm")

def test_location_based():
    """Test cases cho tìm kiếm theo vị trí"""
    print_section("📍 LOCATION-BASED TESTS")

    # Test 43: Khoảng cách rất gần (2km)
    run_test(43, "Rất gần (2km)", "Gym rất gần tôi", DANANG_COORDS)

    # Test 44: Khoảng cách trung bình (10km)
    run_test(44, "Trung bình (10km)", "Gym trong khu vực", DANANG_COORDS)

    # Test 45: Khoảng cách xa (25km)
    run_test(45, "Xa (25km)", "Gym xa hơn một chút", HCMC_COORDS)

    # Test 46: Không giới hạn khoảng cách
    run_test(46, "Không giới hạn", "Tất cả gym", DANANG_COORDS)

    # Test 47: Tìm theo phương tiện (xe đạp)
    run_test(47, "Đi xe đạp", "Gym tôi có thể đi xe đạp đến", DANANG_COORDS)

    # Test 48: Tìm theo thời gian (10 phút)
    run_test(48, "Trong 10 phút", "Gym tôi đến trong 10 phút", HCMC_COORDS)

def test_combined_filters():
    """Test cases kết hợp nhiều filter"""
    print_section("🔍 COMBINED FILTERS TESTS")

    # Test 49: Gender + Goal + Location
    run_test(49, "Nữ + Giảm cân + Gần",
             "Tìm PT nữ chuyên giảm cân gần tôi", DANANG_COORDS)

    # Test 50: Gender + Multiple Goals
    run_test(50, "Nam + Nhiều goals",
             "Tìm PT nam chuyên thể hình và tăng cơ")

    # Test 51: Hot Gym + Location
    run_test(51, "Hot gym + Gần",
             "Tìm gym hot gần tôi", HCMC_COORDS)

    # Test 52: Experience + Goal
    run_test(52, "Kinh nghiệm + Goal",
             "Tìm PT có kinh nghiệm chuyên sức mạnh")

def generate_test_report(results):
    """Generate summary report"""
    print_section("📊 TEST SUMMARY REPORT")

    total = len(results)
    passed = sum(1 for r in results if r and (r.get('trainers') or r.get('gyms') or r.get('promptResponse')))
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"{Colors.OKGREEN}Passed: {passed}{Colors.ENDC}")
    print(f"{Colors.FAIL}Failed: {failed}{Colors.ENDC}")
    print(f"Success Rate: {(passed/total*100):.1f}%")

    print(f"\n{Colors.BOLD}Test Coverage:{Colors.ENDC}")
    print(f"  ✓ PT Search: Gender, Goals, Location, Experience")
    print(f"  ✓ Gym Search: Location, Hot/Popular, Name, District")
    print(f"  ✓ General Chat: Greetings, Advice, Out-of-scope")
    print(f"  ✓ Conversational Flow: Multi-turn, Context memory")
    print(f"  ✓ Edge Cases: Empty, Long, Typos, Special chars")
    print(f"  ✓ Location-based: Various distances, Transport modes")
    print(f"  ✓ Combined Filters: Multiple criteria")

def main():
    """Run all test suites"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                  FITBRIDGE CHATBOT - COMPREHENSIVE TEST SUITE                ║")
    print("║                              By FitBridge Team                                ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")

    print(f"{Colors.WARNING}Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")

    results = []

    try:
        # Run all test suites
        test_pt_search()
        test_gym_search()
        test_general_chat()
        test_conversational_flow()
        test_edge_cases()
        test_location_based()
        test_combined_filters()

        # Generate report
        # Note: For actual tracking, you'd need to modify run_test to return success/failure

        print_section("✅ TEST EXECUTION COMPLETED")
        print(f"{Colors.OKGREEN}All test suites executed successfully!{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Note: Review output above for individual test results{Colors.ENDC}")

    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Test suite failed with error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

    print(f"\n{Colors.OKCYAN}Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")

if __name__ == "__main__":
    main()

