"""
Module xử lý AI - Tích hợp Gemini và OpenRouter
"""
import requests
import json
from typing import List, Dict
from utils import sanitize_ai_response
try:
    from groq import Groq
except Exception:
    Groq = None
try:
    from openai import OpenAI as OpenAIClient
except Exception:
    OpenAIClient = None


class AIHandler:
    """Xử lý yêu cầu với Gemini AI (OpenRouter support removed)"""

    def __init__(self, api_key: str, openrouter_key: str = '', groq_key: str = ''):
        # Gemini config
        self.api_key = api_key
        self.base_url = 'https://generativelanguage.googleapis.com/v1beta/models'
        self.model = 'gemini-flash-latest'
        # OpenRouter config
        self.openrouter_key = openrouter_key
        # OpenRouter endpoint and default free model (per OpenRouter examples)
        self.openrouter_url = 'https://openrouter.ai/api/v1/chat/completions'
        self.openrouter_model = 'openrouter/free'
        # Groq config
        self.groq_key = groq_key
        # Use Groq's OpenAI-compatible Responses endpoint
        self.groq_url = 'https://api.groq.com/openai/v1/responses'
        # Default to OpenAI-compatible Groq model commonly used
        self.groq_model = 'openai/gpt-oss-20b'

    def get_suggestions(self, code: str, analysis_result: Dict, provider: str = 'gemini') -> str:
        """Lấy gợi ý từ AI dựa trên kết quả phân tích"""
        
        errors = analysis_result.get('errors', [])
        test_results = analysis_result.get('test_results', [])

        # Tạo prompt
        prompt = self._build_prompt(code, errors, test_results)

        # For OpenRouter and Groq, prepend explicit formatting instructions
        format_instructions = (
            "Vui lòng trả lời bằng tiếng Việt. Trả lời theo cấu trúc rõ ràng:\n"
            "1) Xác định lỗi chính;\n2) Giải thích tại sao sai;\n3) Gợi ý cách sửa cụ thể (từng bước).\n"
            "Sử dụng tiêu đề và xuống dòng để dễ đọc."
        )

        if provider in ('openrouter', 'groq'):
            prompt = format_instructions + "\n\n" + prompt

        if provider == 'gemini':
            return self._call_gemini(prompt, strip_code=True)
        elif provider == 'openrouter':
            return self._call_openrouter(prompt, strip_code=True)
        elif provider == 'groq':
            return self._call_groq(prompt, strip_code=True)
        else:
            return 'AI provider not supported'

    def get_detailed_suggestions(self, code: str, error_message: str, 
                                output: str, provider: str = 'gemini') -> str:
        """Lấy gợi ý chi tiết từ AI"""
        
        prompt = f"""Tôi có đoạn mã C có lỗi logic. Vui lòng phân tích và gợi ý cách sửa:

**Mã C:**
```c
{code}
```

**Lỗi/Output:**
{error_message or output}

**Yêu cầu:**
1. Xác định lỗi logic
2. Giải thích tại sao nó sai
3. Gợi ý cách sửa cụ thể (viết rõ từng bước)

Vui lòng trả lời bằng tiếng Việt, xuống dòng để dễ đọc."""

        if provider == 'gemini':
            return self._call_gemini(prompt, strip_code=True)
        elif provider == 'openrouter':
            # Prepend formatting instructions so OpenRouter matches Gemini style
            format_instructions = (
                "Vui lòng trả lời bằng tiếng Việt. Trả lời theo cấu trúc rõ ràng:\n"
                "1) Xác định lỗi chính;\n2) Giải thích tại sao sai;\n3) Gợi ý cách sửa cụ thể (từng bước).\n"
                "Sử dụng tiêu đề và xuống dòng để dễ đọc."
            )
            return self._call_openrouter(format_instructions + "\n\n" + prompt, strip_code=True)
        elif provider == 'groq':
            # Prepend formatting instructions for Groq as well
            format_instructions = (
                "Vui lòng trả lời bằng tiếng Việt. Trả lời theo cấu trúc rõ ràng:\n"
                "1) Xác định lỗi chính;\n2) Giải thích tại sao sai;\n3) Gợi ý cách sửa cụ thể (từng bước).\n"
                "Sử dụng tiêu đề và xuống dòng để dễ đọc."
            )
            return self._call_groq(format_instructions + "\n\n" + prompt, strip_code=True)
        else:
            return 'AI provider not supported'

    def _build_prompt(self, code: str, errors: List[str], 
                     test_results: List[Dict]) -> str:
        """Xây dựng prompt cho Gemini"""
        
        prompt = f"""Phân tích lỗi logic trong đoạn mã C sau và gợi ý sửa:

**Mã C:**
```c
{code}
```

"""
        
        if errors:
            prompt += f"**Lỗi biên dịch:**\n"
            for error in errors:
                prompt += f"- {error}\n"
            prompt += "\n"

        if test_results:
            prompt += "**Input & Kết quả kiểm thử:**\n"
            for result in test_results:
                status = "✓ Đúng" if result['passed'] else "✗ Sai"
                prompt += f"\n**Test Case:**\n"
                prompt += f"- Input: `{result['input']}`\n"
                prompt += f"- Expected Output: `{result['expected']}`\n"
                prompt += f"- Actual Output: `{result['actual']}`\n"
                prompt += f"- Status: {status}\n"

        prompt += """\n**Yêu cầu:**
1. Xác định lỗi chính
2. Giải thích kỹ tại sao sai
3. Gợi ý sửa cụ thể (viết rõ từng bước)

Trả lời bằng tiếng Việt. **Hãy xuống dòng và định dạng rõ ràng để dễ đọc.**"""

        return prompt

    def classify_bug_type(self, code: str, requirements: str, test_results: list, provider: str = 'gemini') -> dict:
        """
        Tự động phân loại loại lỗi logic
        Return: {
            'bug_type_id': 'CF001',
            'bug_type_name': '...',
            'evidence': [...],
            'root_cause': '...',
            'confidence': 0.85
        }
        """
        from prompt_generator import PromptGenerator
        
        prompt_gen = PromptGenerator()
        prompt = prompt_gen.generate_classification_prompt(code, requirements, test_results)
        
        # Classification expects structured JSON; do not strip code/blocks here
        if provider == 'gemini':
            response_text = self._call_gemini(prompt, strip_code=False)
        elif provider == 'openrouter':
            response_text = self._call_openrouter(prompt, strip_code=False)
        elif provider == 'groq':
            response_text = self._call_groq(prompt, strip_code=False)
        else:
            response_text = 'AI provider not supported'
        
        try:
            # Parse JSON from response
            import json
            # Tìm JSON trong response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                # Fallback: Mặc định CF001
                return {
                    'bug_type_id': 'CF001',
                    'bug_type_name': 'Conditional Logic',
                    'bug_type_description': 'Điều kiện logic sai - lỗi mặc định',
                    'evidence': ['Không thể phân loại'],
                    'root_cause': 'Không xác định',
                    'confidence': 0.5
                }
        except Exception as e:
            # Fallback nếu parse JSON lỗi
            return {
                'bug_type_id': 'CF001',
                'bug_type_name': 'Conditional Logic',
                'bug_type_description': f'Conditional Logic (fallback: {str(e)})',
                'evidence': ['Lỗi parse response'],
                'root_cause': 'Không xác định',
                'confidence': 0.3
            }

    def _call_gemini(self, prompt: str, strip_code: bool = True) -> str:
        """Gọi Gemini API"""
        
        if not self.api_key:
            return "API key not configured"

        try:
            url = f"{self.base_url}/{self.model}:generateContent"
            
            headers = {
                'Content-Type': 'application/json',
                'X-goog-api-key': self.api_key
            }
            
            payload = {
                'contents': [{
                    'parts': [{
                        'text': prompt
                    }]
                }],
                'generationConfig': {
                    'temperature': 0.7,
                    'topP': 0.95,
                    'topK': 40,
                    'maxOutputTokens': 2048,
                }
            }

            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if parts and 'text' in parts[0]:
                        text = parts[0]['text']
                        if strip_code:
                            try:
                                text = sanitize_ai_response(text)
                            except Exception:
                                pass
                        return text

            return "Không thể nhận được gợi ý từ AI"

        except requests.exceptions.Timeout:
            return "AI request timeout"
        except requests.exceptions.RequestException as e:
            return f"AI API error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _call_openrouter(self, prompt: str, strip_code: bool = True) -> str:
        """Gọi OpenRouter Chat Completions API"""

        if not self.openrouter_key:
            return "OpenRouter API key not configured"

        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.openrouter_key}'
            }

            payload = {
                'model': self.openrouter_model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.7,
                'max_tokens': 1024
            }

            response = requests.post(self.openrouter_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # Try to extract text in OpenAI-like response
            if isinstance(result, dict):
                choices = result.get('choices') or []
                if choices and isinstance(choices[0], dict):
                    # Chat completion style
                    msg = choices[0].get('message') or choices[0].get('delta') or {}
                    if isinstance(msg, dict):
                        text = msg.get('content') or msg.get('content', '')
                        if not text:
                            # fallback to 'text' or nested structure
                            text = choices[0].get('text', '')
                    else:
                        text = choices[0].get('text', '')

                    if text:
                        if strip_code:
                            try:
                                text = sanitize_ai_response(text)
                            except Exception:
                                pass
                        return text

            # Fallback
            return "Không thể nhận được gợi ý từ AI"

        except requests.exceptions.Timeout:
            return "AI request timeout"
        except requests.exceptions.RequestException as e:
            return f"AI API error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _call_groq(self, prompt: str, strip_code: bool = True) -> str:
        """Gọi Groq Chat Completions API (basic implementation)"""

        if not self.groq_key:
            return "Groq API key not configured"

        try:
            # Prefer OpenAI-compatible client if available (as per Groq example)
            if OpenAIClient is not None:
                try:
                    client = OpenAIClient(api_key=self.groq_key, base_url="https://api.groq.com/openai/v1")
                    resp = client.responses.create(
                        model=self.groq_model,
                        input=prompt,
                        max_output_tokens=1024,
                        temperature=0.7
                    )

                    # Try to extract output_text (common in client responses)
                    text = getattr(resp, 'output_text', None)
                    if not text:
                        out = getattr(resp, 'output', None) or []
                        parts = []
                        for item in out:
                            if isinstance(item, str):
                                parts.append(item)
                            elif isinstance(item, dict):
                                if 'content' in item and isinstance(item['content'], str):
                                    parts.append(item['content'])
                                elif 'content' in item and isinstance(item['content'], list):
                                    for c in item['content']:
                                        if isinstance(c, str):
                                            parts.append(c)
                                        elif isinstance(c, dict) and c.get('text'):
                                            parts.append(c.get('text'))
                            elif hasattr(item, 'text'):
                                parts.append(getattr(item, 'text', ''))
                        text = '\n'.join([p for p in parts if p]).strip()

                    if text:
                        if strip_code:
                            try:
                                text = sanitize_ai_response(text)
                            except Exception:
                                pass
                        return text
                except Exception:
                    # fall through to HTTP fallback
                    pass
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.groq_key}'
            }

            # Use Responses API shape (OpenAI-compatible)
            payload = {
                'model': self.groq_model,
                'input': prompt,
                'max_output_tokens': 1024,
                'temperature': 0.7
            }

            response = requests.post(self.groq_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()

            # Groq/OpenAI-like Responses may provide 'output_text' or 'output'
            text = ''
            if isinstance(result, dict):
                if 'output_text' in result and result['output_text']:
                    text = result['output_text']
                elif 'output' in result and isinstance(result['output'], list):
                    parts = []
                    for item in result['output']:
                        if isinstance(item, str):
                            parts.append(item)
                        elif isinstance(item, dict):
                            # try common shapes
                            if 'content' in item and isinstance(item['content'], str):
                                parts.append(item['content'])
                            elif 'content' in item and isinstance(item['content'], list):
                                for c in item['content']:
                                    if isinstance(c, str):
                                        parts.append(c)
                                    elif isinstance(c, dict) and c.get('text'):
                                        parts.append(c.get('text'))
                            elif item.get('text'):
                                parts.append(item.get('text'))
                    text = '\n'.join(parts).strip()

            if text:
                if strip_code:
                    try:
                        text = sanitize_ai_response(text)
                    except Exception:
                        pass
                return text

            return "Không thể nhận được gợi ý từ AI"

        except requests.exceptions.Timeout:
            return "AI request timeout"
        except requests.exceptions.RequestException as e:
            return f"AI API error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"

    def _call_groq_streaming(self, prompt: str, model: str = 'openai/gpt-oss-20b', max_tokens: int = 1024) -> str:
        """Use the official Groq SDK to stream completions when available."""

        if not self.groq_key:
            return "Groq API error: missing GROQ_API_KEY"

        if Groq is None:
            return "Groq SDK not installed"

        try:
            client = Groq(api_key=self.groq_key)
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_completion_tokens=max_tokens,
                top_p=1,
                reasoning_effort="medium",
                stream=True,
                stop=None,
            )

            text = ""
            for chunk in completion:
                try:
                    # prefer delta.content, fallback to delta.text or choices[0].text
                    delta = ""
                    if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                        choice = chunk.choices[0]
                        if isinstance(choice, dict):
                            delta = (choice.get('delta') or {}).get('content') or (choice.get('delta') or {}).get('text') or choice.get('text', '')
                        else:
                            delta = getattr(choice, 'delta', {}).get('content', '') or getattr(choice, 'delta', {}).get('text', '') or getattr(choice, 'text', '') or ''
                    else:
                        # fallback generic
                        delta = getattr(chunk, 'text', '') or ''
                except Exception:
                    delta = ''
                text += delta or ''

            return sanitize_ai_response(text)

        except Exception as e:
            return f"AI API error: {e}"
