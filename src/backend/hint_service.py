"""
Hint Service
Quản lý việc tạo và cung cấp hints
"""
from prompt_generator import PromptGenerator
from ai_handler import AIHandler
import json


class HintService:
    """Cung cấp hints từ AI"""
    
    def __init__(self, ai_handler: AIHandler):
        self.ai_handler = ai_handler
        self.prompt_gen = PromptGenerator()
        self.hint_cache = {}
    
    def analyze_and_create_hints(self, code, bug_type, bug_taxonomy_id, 
                                 requirements, test_cases):
        """
        Phân tích code và tạo hints
        Return: {
            'branches': [...],
            'root_cause': '...',
            'guided_questions': [...],
            'hints': [
                {'level': 1, 'hint': '...'},
                {'level': 2, 'hint': '...'},
                {'level': 3, 'hint': '...'}
            ]
        }
        """
        
        # Generate prompt
        prompt = self.prompt_gen.generate_analysis_prompt(
            code, bug_type, bug_taxonomy_id, requirements, test_cases
        )
        
        # Call AI với prompt cụ thể (yêu cầu JSON) -> không strip code/blocks
        response = self.ai_handler._call_gemini(prompt, strip_code=False)
        
        # Parse response
        try:
            # Tìm JSON trong response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)
        except:
            # Fallback: tạo generic hints
            result = self._create_generic_hints(code, bug_type, bug_taxonomy_id)
        
        return result
    
    def get_next_hint(self, code, bug_type, bug_taxonomy_id, 
                      current_hint_level, test_case, error_info):
        """
        Lấy hint tiếp theo (level by level)
        
        Args:
            current_hint_level: 1, 2, hoặc 3
            
        Return: {
            'hint_level': 2,
            'hint_text': '...',
            'follow_up_question': '...',
            'code_area': 'line 5-7'
        }
        """
        
        # Generate prompt
        prompt = self.prompt_gen.generate_hint_prompt(
            code, bug_type, bug_taxonomy_id, 
            current_hint_level, test_case, error_info
        )
        
        # Call AI
        response = self.ai_handler.get_detailed_suggestions(code, "", "")
        
        # Parse
        try:
            result = json.loads(response)
        except:
            result = self._create_generic_hint(current_hint_level, bug_type)
        
        return result
    
    def get_step_by_step_guidance(self, code, requirements, test_cases, 
                                  attempt_history):
        """
        Tạo hướng dẫn step-by-step
        
        Return: {
            'current_issues': [{...}],
            'next_step': {
                'step_number': 1,
                'focus_area': '...',
                'question': '...',
                'hint': '...'
            }
        }
        """
        
        prompt = self.prompt_gen.generate_step_by_step_prompt(
            code, requirements, test_cases, attempt_history
        )
        
        response = self.ai_handler.get_detailed_suggestions(code, "", "")
        
        try:
            result = json.loads(response)
        except:
            result = self._create_generic_step_guidance()
        
        return result
    
    def _create_generic_hints(self, code, bug_type, bug_taxonomy_id):
        """Tạo generic hints nếu AI không response"""
        return {
            'branches_count': code.count('if'),
            'analysis': [
                {
                    'branch': 'Main condition',
                    'condition': 'Phân tích điều kiện if',
                    'assessment': 'Kiểm tra xem điều kiện có đúng logic không?',
                    'related_tests': []
                }
            ],
            'root_cause': 'Lỗi logic trong điều kiện',
            'guided_questions': [
                'Điều kiện này đúng với requirement không?',
                'Kiểm tra toán tử so sánh: <, >, <=, >=, ==, !=',
                'Test với edge case: giá trị biên'
            ],
            'hints': [
                {
                    'level': 1,
                    'hint': 'Hãy kiểm tra lại điều kiện trong if/else'
                },
                {
                    'level': 2,
                    'hint': 'So sánh output thực tế với expected output. Cái nào sai?'
                },
                {
                    'level': 3,
                    'hint': 'Điều kiện nên sử dụng toán tử nào? <, >, <=, >=, ==?'
                }
            ]
        }
    
    def _create_generic_hint(self, level, bug_type):
        """Tạo generic hint cho 1 level"""
        hints = {
            1: {
                'hint_level': 1,
                'hint_text': 'Xem lại vùng code có if/else',
                'follow_up_question': 'Điều kiện này check cái gì?',
                'code_area': 'Toàn bộ function'
            },
            2: {
                'hint_level': 2,
                'hint_text': 'So sánh output với testcase. Cái nào sai?',
                'follow_up_question': 'Tại sao output sai? Điều kiện có match input không?',
                'code_area': 'Vùng if/else'
            },
            3: {
                'hint_level': 3,
                'hint_text': 'Kiểm tra toán tử: < vs <=, == vs !=',
                'follow_up_question': 'Toán tử nào là đúng?',
                'code_area': 'Dòng điều kiện'
            }
        }
        return hints.get(level, hints[1])
    
    def _create_generic_step_guidance(self):
        """Tạo generic step guidance"""
        return {
            'current_issues': [
                {
                    'issue': 'Điều kiện logic sai',
                    'affected_tests': [],
                    'severity': 'high'
                }
            ],
            'next_step': {
                'step_number': 1,
                'focus_area': 'Kiểm tra điều kiện trong if',
                'question': 'Điều kiện này có match requirement không?',
                'hint': 'Vẽ sơ đồ: input nào → expected output nào'
            }
        }
