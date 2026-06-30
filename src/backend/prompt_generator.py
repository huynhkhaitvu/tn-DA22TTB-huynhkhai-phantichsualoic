"""
Smart Prompt Generator
Tạo prompt thông minh dựa trên bug taxonomy
"""
from bug_taxonomy import BUG_TAXONOMY, get_hints_for_bug


class PromptGenerator:
    """Tạo prompt chi tiết cho AI"""
    
    def __init__(self):
        self.template_base = """Bạn là một giáo viên lập trình C giỏi. 
Nhiệm vụ của bạn: Giúp học sinh sửa lỗi logic trong code, NHƯNG KHÔNG cung cấp code hoàn chỉnh.
Thay vào đó, hãy gợi ý từng bước để học sinh tự phát hiện và sửa.

QUAN TRỌNG: 
- ĐẠO phân tích từng bước
- Đặt câu hỏi hướng dẫn
- Không cung cấp code đã fix
- Giúp học sinh tự suy luận"""

    def generate_analysis_prompt(self, code, bug_type, bug_taxonomy_id, 
                                 requirements, test_cases):
        """Tạo prompt để phân tích lỗi"""
        
        bug_info = self._get_bug_info(bug_taxonomy_id)
        
        prompt = f"""{self.template_base}

## MIỀN KIẾN THỨC: Cấu Trúc Rẽ Nhánh (If/Else/Switch)

## LOẠI LỖI NGHI NGỜ: {bug_info['name']}
Mô tả: {bug_info['description']}

## MÃ C CẦN PHÂN TÍCH:
```c
{code}
```

## YÊU CẦU ĐỀ BÀI:
{requirements}

## CÁC TEST CASE:
"""
        for i, tc in enumerate(test_cases, 1):
            prompt += f"\nTest {i}:\n"
            prompt += f"  Input: {tc.get('input', 'N/A')}\n"
            prompt += f"  Expected Output: {tc.get('expected_output', 'N/A')}\n"
        
        prompt += f"""

## HƯỚNG DẪN PHÂN TÍCH:
1. Xác định các nhánh điều kiện trong code
2. Kiểm tra logic của từng điều kiện
3. So sánh output thực tế với expected output
4. Xác định điều kiện nào sai và tại sao

## CÂU HỎI HƯỚNG DẪN (Trả lời từng câu):
1. Code có bao nhiêu nhánh if/else?
2. Điều kiện trong mỗi if là gì? Nó đúng với requirements không?
3. Với test case nào, output sai? Tại sao?
4. Điều kiện nào cần được sửa? Như thế nào?

## FORMAT TRẢ LỜI:
```json
{{
  "branches_count": <số nhánh>,
  "analysis": [
    {{
      "branch": <tên nhánh>,
      "condition": "<điều kiện>",
      "assessment": "<đúng hay sai? tại sao?>",
      "related_tests": [<test indices sai>]
    }}
  ],
  "root_cause": "<nguyên nhân gốc của lỗi>",
  "guided_questions": [
    "<câu hỏi 1 để hướng dẫn>",
    "<câu hỏi 2>",
    "<câu hỏi 3>"
  ],
  "hints": [
    {{
      "level": 1,
      "hint": "<gợi ý vague>"
    }},
    {{
      "level": 2,
      "hint": "<gợi ý cụ thể hơn>"
    }},
    {{
      "level": 3,
      "hint": "<gợi ý chi tiết nhất, gần với fix>"
    }}
  ]
}}
```

Trả lời bằng tiếng Việt, JSON format chính xác."""

        return prompt

    def generate_hint_prompt(self, code, bug_type, bug_taxonomy_id, 
                             current_hint_level, test_case, error_info):
        """Tạo prompt để tạo gợi ý từng bước"""
        
        bug_info = self._get_bug_info(bug_taxonomy_id)
        level_names = {1: "Rất vague", 2: "Trung bình", 3: "Rất cụ thể"}
        
        prompt = f"""{self.template_base}

## MÃ HIỆN TẠI:
```c
{code}
```

## LOẠI LỖI: {bug_info['name']}

## TEST CASE LỖI:
Input: {test_case.get('input', 'N/A')}
Expected: {test_case.get('expected_output', 'N/A')}
Actual: {error_info.get('actual_output', 'N/A')}

## YÊU CẦU:
Tạo gợi ý ở level {current_hint_level} ({level_names.get(current_hint_level, '?')})

## HƯỚNG DẪN TẠO GỢI ý:

**Level 1 (Vague):** Chỉ hỏi câu hỏi, không cho lời giải
Ví dụ: "Kiểm tra điều kiện này, nó match với requirement không?"

**Level 2 (Medium):** Hỏi + Gợi ý hướng
Ví dụ: "Điều kiện x < 5 có đúng không? Kiểm tra kỹ toán tử so sánh"

**Level 3 (Specific):** Chi tiết nhất, gần code pattern
Ví dụ: "Trong if này, điều kiện nên là x <= 5 chứ không phải x < 5. 
         Lý do: requirement yêu cầu bao gồm trường hợp x = 5"

## TRẢ LỜI:
```json
{{
  "hint_level": {current_hint_level},
  "hint_text": "<gợi ý theo level>",
  "follow_up_question": "<câu hỏi tiếp theo để học sinh suy luận>",
  "code_area": "<vùng code nào cần chú ý? line numbers>"
}}
```
"""
        return prompt

    def generate_step_by_step_prompt(self, code, requirements, test_cases, 
                                     attempt_history):
        """Tạo prompt để tạo hướng dẫn step-by-step"""
        
        prompt = f"""{self.template_base}

## MÃ HIỆN TẠI:
```c
{code}
```

## YÊU CẦU:
{requirements}

## TEST CASES:
"""
        for i, tc in enumerate(test_cases, 1):
            prompt += f"\nTest {i}: Input='{tc['input']}' → Expected='{tc['expected_output']}'"
        
        if attempt_history:
            prompt += f"""

## LỊCH SỬ ATTEMPT:
- Số lần đã sửa: {len(attempt_history)}
- Hints đã xem: {', '.join([h['hint_id'] for h in attempt_history if h['action'] == 'view_hint'])}
"""
        
        prompt += """

## NHIỆM VỤ:
Tạo hướng dẫn step-by-step để sửa code, mỗi step là:
1. Nhận diện vấn đề cụ thể
2. Đặt câu hỏi để học sinh tự suy luận
3. Gợi ý hướng sửa (không fix trực tiếp)

## TRẢ LỜI:
```json
{
  "current_issues": [
    {
      "issue": "<vấn đề cụ thể>",
      "affected_tests": [<test indices>],
      "severity": "high|medium|low"
    }
  ],
  "next_step": {
    "step_number": <số thứ tự>,
    "focus_area": "<vùng code cần chú ý>",
    "question": "<câu hỏi để hướng dẫn>",
    "hint": "<gợi ý cụ thể>"
  }
}
```
"""
        return prompt

    def generate_classification_prompt(self, code, requirements, test_results):
        """
        Tạo prompt để AI tự động phân loại loại lỗi
        Return: Prompt để phân loại lỗi thành CF001-CF006
        """
        
        # Tạo danh sách bug types với mô tả
        bug_types_str = """
Các loại lỗi logic trong cấu trúc rẽ nhánh (if/else/switch):
- CF001: Conditional Logic - Điều kiện sai (>, <, >=, <=, ==, !=, &&, ||)
- CF002: Branch Missing - Thiếu nhánh xử lý (if/else không đầy đủ)
- CF003: Nested Condition - Lỗi điều kiện lồng nhau
- CF004: Operator Precedence - Thứ tự ưu tiên toán tử sai
- CF005: Switch Case - Lỗi Switch/Case (quên break, case không match)
- CF006: Boundary Condition - Lỗi ranh giới (off-by-one, boundary test fail)
"""
        
        prompt = f"""{self.template_base}

## NHIỆM VỤ: Phân loại loại lỗi logic

## MÃ C:
```c
{code}
```

## YÊU CẦU:
{requirements}

## KẾT QUẢ KIỂM THỬ:
"""
        
        for i, result in enumerate(test_results, 1):
            status = "✓ PASS" if result.get('passed') else "✗ FAIL"
            prompt += f"\nTest {i}: {status}\n"
            if not result.get('passed'):
                prompt += f"  Input: {result.get('input', 'N/A')}\n"
                prompt += f"  Expected: {result.get('expected', 'N/A')}\n"
                prompt += f"  Actual: {result.get('actual', 'N/A')}\n"
        
        prompt += f"""

{bug_types_str}

## HƯỚNG DẪN PHÂN LOẠI:
1. Phân tích các nhánh if/else/switch trong code
2. So sánh với requirements để xác định vấn đề
3. Xem xét các failed test cases
4. Xác định loại lỗi chính (CF001-CF006)

## FORMAT TRẢ LỜI:
```json
{{
  "bug_type_id": "CF###",
  "bug_type_name": "<tên loại lỗi>",
  "bug_type_description": "<mô tả chi tiết lỗi>",
  "evidence": [
    "<bằng chứng 1 từ code>",
    "<bằng chứng 2 từ test results>"
  ],
  "root_cause": "<nguyên nhân gốc>",
  "affected_lines": [<số dòng code có vấn đề>],
  "affected_tests": [<indices test cases fail>],
  "confidence": <0.0-1.0>
}}
```

Trả lời bằng tiếng Việt, JSON format chính xác."""
        
        return prompt

    def _get_bug_info(self, bug_taxonomy_id):
        """Lấy thông tin bug từ taxonomy"""
        for category, info in BUG_TAXONOMY.items():
            if info["id"] == bug_taxonomy_id:
                return info
        return {"name": "Unknown", "description": "Unknown bug", "id": bug_taxonomy_id}


# Test
if __name__ == "__main__":
    generator = PromptGenerator()
    
    code = """int main() {
    int x = 5;
    if (x < 5) {
        printf("Less");
    } else {
        printf("Not less");
    }
    return 0;
}"""
    
    prompt = generator.generate_analysis_prompt(
        code, 
        "boundary_error",
        "CF006",
        "In ra 'Less' nếu x < 5, ngược lại ra 'Not less'",
        [
            {"input": "4", "expected_output": "Less"},
            {"input": "5", "expected_output": "Not less"},
            {"input": "6", "expected_output": "Not less"}
        ]
    )
    
    print("Generated Prompt:")
    print("=" * 80)
    print(prompt)
