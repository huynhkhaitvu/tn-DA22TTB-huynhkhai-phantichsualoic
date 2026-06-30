"""
Utility functions
"""
import re
import os


def extract_includes(code):
    """Trích xuất các thư viện include từ code"""
    pattern = r'#include\s+[<"]([^>"]+)[>"]'
    return re.findall(pattern, code)


def extract_functions(code):
    """Trích xuất tên các hàm từ code"""
    pattern = r'\b\w+\s+(\w+)\s*\('
    return re.findall(pattern, code)


def detect_common_errors(code):
    """Phát hiện các lỗi logic phổ biến"""
    errors = []
    
    # Kiểm tra vòng lặp
    if 'for' in code:
        # Kiểm tra i < n (có thể nên là <=)
        # Hỗ trợ cả 'for (int i = 1; i < n; ...)' và 'for(i = 1; i < n; ... )'
        if re.search(r'for\s*\(\s*(?:int\s+)?\w+\s*=\s*\d+\s*;\s*\w+\s*<\s*\w+', code):
            errors.append("Vòng lặp dùng '<' - có thể nên dùng '<=' tùy theo logic")
    
    # Kiểm tra khởi tạo biến max/min
    if 'max' in code.lower() or 'min' in code.lower():
        if 'max = 0' in code or 'min = 0' in code:
            errors.append("Khởi tạo max/min bằng 0 - có thể sai nếu có số âm")
    
    # Kiểm tra chia cho 0
    if '/ 0' in code or '/ zero' in code.lower():
        errors.append("Chia cho 0 - sẽ gây lỗi runtime")
    
    # Kiểm tra quên dấu chấm phẩy
    if 'printf' in code and not code.count(';') >= code.count('printf'):
        errors.append("Có thể thiếu dấu chấm phẩy ở cuối dòng")
    
    return errors


def format_code(code):
    """Format code với indentation"""
    lines = code.split('\n')
    formatted = []
    indent_level = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Giảm indent trước '}'
        if stripped.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        # Add formatted line
        if stripped:
            formatted.append('    ' * indent_level + stripped)
        else:
            formatted.append('')
        
        # Tăng indent sau '{'
        if stripped.endswith('{'):
            indent_level += 1
    
    return '\n'.join(formatted)


def validate_c_syntax(code):
    """Kiểm tra cú pháp C cơ bản"""
    issues = []
    
    # Kiểm tra main function
    if 'int main' not in code and 'void main' not in code:
        issues.append("Thiếu main() function")
    
    # Kiểm tra include stdio.h
    if 'printf' in code and '#include <stdio.h>' not in code:
        issues.append("Dùng printf nhưng thiếu #include <stdio.h>")
    
    # Kiểm tra brace balance
    if code.count('{') != code.count('}'):
        issues.append(f"Mismatch braces: {{ {code.count('{')} vs }} {code.count('}')}")
    
    # Kiểm tra return statement
    if 'int main' in code and 'return' not in code:
        issues.append("main() không có return statement")
    
    return issues


def get_file_size(path):
    """Lấy kích thước file"""
    try:
        return os.path.getsize(path)
    except:
        return 0


def safe_truncate(text, max_length=1000):
    """Cắt text an toàn"""
    if len(text) > max_length:
        return text[:max_length] + f"\n... [Truncated, {len(text)-max_length} chars more]"
    return text


def sanitize_ai_response(text: str) -> str:
    """
    Loại bỏ các khối code từ phản hồi AI để chỉ giữ phần gợi ý, tránh hiển thị code đã sửa.
    Xử lý:
    - Bỏ các fenced code blocks ```...```
    - Bỏ các thẻ <pre>...</pre> hoặc <code>...</code>
    - Loại bỏ các dòng nhìn giống code (chứa ';' hoặc '{' or '}' hoặc bắt đầu bằng '#include' hoặc 'int ' hoặc 'return ' hoặc chứa 'printf(')
    - Trả về chuỗi đã được rút gọn và trim
    """
    import re

    if not text:
        return text

    # Remove fenced code blocks ```...```
    text = re.sub(r'```[\s\S]*?```', '', text)

    # Remove HTML pre/code blocks
    text = re.sub(r'<pre[\s\S]*?>[\s\S]*?<\/pre>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<code[\s\S]*?>[\s\S]*?<\/code>', '', text, flags=re.IGNORECASE)

    # Remove paragraphs headed by 'Kết quả cuối cùng' (and variants) including following lines until blank line
    text = re.sub(r'\*{0,2}\s*Kết quả cuối cùng[^\n]*\*{0,2}[:\-–—]?[^\n]*\n(?:.*?\n){0,20}?\s*\n', '', text, flags=re.IGNORECASE)
    # Remove single-line occurrences that state final result lines beginning with 'Kết quả cuối cùng' without blank line after
    text = re.sub(r'\*{0,2}\s*Kết quả cuối cùng[^\n]*\*{0,2}[:\-–—]?.*\n', '', text, flags=re.IGNORECASE)
    # Remove English drafting remnants like 'If you want...' or 'Thus answer' expressed in English as short heuristic
    text = re.sub(r"^.*\b(If you|Thus answer|Let's produce|We should|Also mention|Let's answer)\b.*$\n", '', text, flags=re.IGNORECASE|re.M)

    # Remove lines that look like code
    lines = text.splitlines()
    filtered = []
    for ln in lines:
        s = ln.strip()
        # Remove specific headings the frontend shouldn't show
        if s.startswith('Mã C') or 'Mã C sau' in s or 'Kết quả sau' in s:
            continue
        # Remove variants like 'Mã đã sửa hoàn chỉnh' (may include markdown asterisks)
        if 'Mã đã sửa' in s or 'Mã đã sửa hoàn chỉnh' in s or s.replace('*', '').strip().startswith('Mã đã sửa'):
            continue
        # Remove summary/result lines that start with 'Sau khi sửa' or similar
        if s.startswith('Sau khi sửa') or 'Sau khi sửa' in s:
            continue
        if not s:
            filtered.append(ln)
            continue
        # heuristics to detect code-like lines
        if ('#include' in s) or s.startswith('int ') or s.startswith('void ') or s.startswith('return ') or s.startswith('for(') or s.startswith('for ') or s.startswith('while(') or s.startswith('while ') or 'printf(' in s:
            continue
        if ';' in s or '{' in s or '}' in s:
            # skip likely code line
            continue
        # Remove numbered headings like '4.' or '1.' which may be AI drafting artifacts
        if re.match(r'^\d+\.', s):
            continue
        # Remove simple HTML/markup tags or AI internal markers like <think>...</think>
        if re.search(r'<\/?\w+', s):
            continue
        # Remove lines that are mainly English (heuristic): many ASCII letters and English stopwords
        ascii_letters = len(re.findall(r'[A-Za-z]', s))
        non_ascii_letters = len(re.findall(r'[^\x00-\x7F]', s))
        words = s.split()
        if words:
            ascii_word_frac = sum(1 for w in words if re.match(r"^[A-Za-z'\-]+$", w)) / len(words)
        else:
            ascii_word_frac = 0
        common_english = 0
        eng_keywords = {'if', 'the', 'then', 'also', 'should', 'option', 'final', 'result', 'please', 'we', "let's", 'answer', 'note'}
        for w in words:
            if w.lower().strip("*()[]:,.") in eng_keywords:
                common_english += 1

        # Remove if line is mostly ASCII words AND contains at least one English keyword
        if (ascii_letters > non_ascii_letters * 2 or ascii_word_frac > 0.6) and common_english > 0:
            continue
        # Remove lines that explicitly recommend changing loop condition to i <= 5 or i < 6,
        # but preserve table rows (which start with '|') so table content isn't lost.
        if re.search(r'\b(i\s*(?:<=|<)\s*5|i\s*<\s*6|i\s*<=\s*5)\b', s, flags=re.IGNORECASE) and not s.startswith('|'):
            continue
        # Remove lines that start with 'Như vậy,' or similar conclusion phrasing, but preserve table rows
        if re.match(r'^\s*Như vậy', s, flags=re.IGNORECASE) and not s.startswith('|'):
            continue
        filtered.append(ln)

    result = '\n'.join(filtered).strip()

    # If result becomes empty, keep a short message instead
    if not result:
        return '[Gợi ý đã được rút gọn — code đã bị loại bỏ để chỉ hiển thị hướng dẫn.]'

    return result
