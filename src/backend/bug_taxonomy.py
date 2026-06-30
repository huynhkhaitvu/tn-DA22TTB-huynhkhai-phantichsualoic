"""
Bug Taxonomy for Control Flow Structures
Danh mục các loại lỗi trong cấu trúc rẽ nhánh
"""

BUG_TAXONOMY = {
    "CONDITIONAL_LOGIC": {
        "id": "CF001",
        "name": "Lỗi Logic Điều Kiện",
        "description": "Điều kiện sai hoặc logic boolean lỗi",
        "examples": [
            "if (x < 5) vs if (x <= 5)",
            "if (a && b) vs if (a || b)",
            "Missing condition check",
            "Reversed logic (> vs <)"
        ],
        "hints": [
            "Kiểm tra toán tử so sánh: <, >, <=, >=, ==, !=",
            "Kiểm tra toán tử logic: &&, ||, !",
            "Vẽ sơ đồ: khi nào điều kiện TRUE, khi nào FALSE",
            "So sánh với testcase: input nào đúng, input nào sai?"
        ]
    },
    
    "BRANCH_MISSING": {
        "id": "CF002",
        "name": "Thiếu Nhánh Xử Lý",
        "description": "Không xử lý tất cả các case có thể",
        "examples": [
            "if (age >= 18) printf(\"Adult\"); // thiếu else",
            "if (x > 0) ... else if (x < 0) ... // thiếu x == 0",
            "switch không có default case"
        ],
        "hints": [
            "Liệt kê tất cả trường hợp có thể xảy ra",
            "Mỗi input có nên xử lý trong 1 branch không?",
            "Có thiếu case nào không?",
            "Thêm else hoặc else if để xử lý các trường hợp còn lại"
        ]
    },
    
    "NESTED_CONDITION": {
        "id": "CF003",
        "name": "Lỗi Điều Kiện Lồng Nhau",
        "description": "Logic sai trong if/else lồng nhau",
        "examples": [
            "if (a) { if (b) ... else ... } // else thuộc if nào?",
            "Thứ tự kiểm tra điều kiện sai",
            "Quên ngoặc trong lồng nhau"
        ],
        "hints": [
            "Vẽ sơ đồ cây quyết định (decision tree)",
            "Đánh số từng level của lồng nhau",
            "Xác định else thuộc if nào",
            "Thêm ngoặc {} rõ ràng để tránh nhầm lẫn"
        ]
    },
    
    "OPERATOR_PRECEDENCE": {
        "id": "CF004",
        "name": "Lỗi Thứ Tự Toán Tử",
        "description": "Thứ tự ưu tiên toán tử sai",
        "examples": [
            "if (a > 5 && b < 10) vs nếu quên &&",
            "if (x == 1 && y == 2 || z == 3) // ưu tiên sai",
            "(a || b && c) vs (a || (b && c))"
        ],
        "hints": [
            "Nhớ: && có ưu tiên cao hơn ||",
            "Dùng dấu ngoặc () để rõ ràng",
            "Test từng điều kiện riêng lẻ",
            "Kết hợp từng phần, từ bên trong ra bên ngoài"
        ]
    },
    
    "SWITCH_CASE": {
        "id": "CF005",
        "name": "Lỗi Switch/Case",
        "description": "Switch/case logic sai hoặc thiếu break",
        "examples": [
            "Quên break → fall-through",
            "case value không khớp với input",
            "Thiếu default case"
        ],
        "hints": [
            "Kiểm tra từng case: điều kiện match không?",
            "Thêm break; ở cuối mỗi case",
            "Thêm default: để xử lý case không expected",
            "Test fall-through có cố ý không?"
        ]
    },
    
    "BOUNDARY_CONDITION": {
        "id": "CF006",
        "name": "Lỗi Điều Kiện Ranh Giới",
        "description": "Sai lầm với điều kiện biên (boundary)",
        "examples": [
            "if (age >= 18) vs if (age > 18)",
            "if (i < n) vs if (i <= n)",
            "Off-by-one error"
        ],
        "hints": [
            "Test edge cases: 0, 1, -1, n-1, n, n+1",
            "Dùng <= hoặc >= khi cần bao gồm giá trị biên",
            "Dùng < hoặc > khi chỉ cần giá trị bên trong",
            "Vẽ trục số để hình dung ranh giới"
        ]
    },
    
    "TYPE_COMPARISON": {
        "id": "CF007",
        "name": "Lỗi So Sánh Kiểu Dữ Liệu",
        "description": "So sánh sai kiểu dữ liệu",
        "examples": [
            "char c = '5'; if (c == 5) // so sánh char vs int",
            "Float precision: if (f == 0.1) // nên dùng epsilon",
            "String compare: if (str == \"hello\") // nên dùng strcmp"
        ],
        "hints": [
            "Kiểm tra kiểu của biến được so sánh",
            "Char '5' ≠ int 5",
            "Float so sánh cần epsilon (tolerance)",
            "String cần strcmp(), không phải =="
        ]
    }
}

def get_bug_info(bug_id):
    """Lấy thông tin chi tiết về 1 loại bug"""
    for category, info in BUG_TAXONOMY.items():
        if info["id"] == bug_id:
            return info
    return None

def get_all_bugs():
    """Lấy danh sách tất cả bugs"""
    return [(k, v) for k, v in BUG_TAXONOMY.items()]

def get_hints_for_bug(bug_id):
    """Lấy gợi ý cho loại bug cụ thể"""
    bug = get_bug_info(bug_id)
    return bug["hints"] if bug else []
