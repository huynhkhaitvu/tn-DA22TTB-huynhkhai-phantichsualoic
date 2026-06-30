"""
Module phân tích mã C - Biên dịch, chạy và so sánh output
"""
import subprocess
import os
import tempfile
import sys


class CodeAnalyzer:
    """Phân tích và thực thi mã C"""

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.gcc_command = 'gcc'  # Sẽ được tìm kiếm từ PATH

    def _check_gcc(self):
        """Kiểm tra GCC có sẵn không"""
        try:
            subprocess.run([self.gcc_command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def compile(self, code):
        """
        Biên dịch mã C
        Return: {'success': bool, 'error': str, 'executable': str}
        """
        if not self._check_gcc():
            return {
                'success': False,
                'error': 'GCC not found. Please install MinGW-w64'
            }

        try:
            # Tạo file .c tạm thời
            c_file = os.path.join(self.temp_dir, 'temp_program.c')
            exe_file = os.path.join(self.temp_dir, 'temp_program.exe')

            with open(c_file, 'w', encoding='utf-8') as f:
                f.write(code)

            # Biên dịch
            result = subprocess.run(
                [self.gcc_command, c_file, '-o', exe_file],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout
                }

            return {
                'success': True,
                'executable': exe_file,
                'message': 'Compilation successful'
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Compilation timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run(self, code, input_data=''):
        """
        Chạy mã C với input
        Return: {'success': bool, 'output': str, 'error': str}
        """
        compile_result = self.compile(code)
        
        if not compile_result['success']:
            return {
                'success': False,
                'error': compile_result.get('error', 'Compilation failed'),
                'compile_output': compile_result.get('output', '')
            }

        try:
            exe_file = compile_result['executable']
            result = subprocess.run(
                [exe_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8'
            )

            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Program timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def evaluate_testcases(self, code, testcases=None):
        """Biên dịch và chạy chương trình trên từng testcase, trả về số testcase đạt."""
        compile_result = self.compile(code)
        if not compile_result['success']:
            return {
                'success': False,
                'passed_count': 0,
                'total_count': len(testcases or []),
                'test_results': [],
                'error': compile_result.get('error', 'Compilation failed'),
                'compile_output': compile_result.get('output', '')
            }

        executable = compile_result['executable']
        test_results = []
        passed_count = 0
        for i, testcase in enumerate(testcases or []):
            test_input = testcase.get('input', '')
            expected_output = testcase.get('expected_output', '')
            try:
                result = subprocess.run(
                    [executable],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding='utf-8'
                )
                actual_output = result.stdout.strip()
                expected = expected_output.strip()
                passed = result.returncode == 0 and actual_output == expected
                if passed:
                    passed_count += 1
                test_results.append({
                    'testcase': i + 1,
                    'passed': passed,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': result.stdout
                })
            except subprocess.TimeoutExpired:
                test_results.append({
                    'testcase': i + 1,
                    'passed': False,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': 'Program timeout'
                })

        return {
            'success': True,
            'passed_count': passed_count,
            'total_count': len(testcases or []),
            'test_results': test_results
        }

    def analyze(self, code, testcases=None):
        """
        Phân tích toàn diện mã C
        Return: Analysis result object
        """
        result = {
            'has_errors': False,
            'compile_status': None,
            'test_results': [],
            'errors': [],
            'warnings': []
        }

        # Kiểm tra GCC
        if not self._check_gcc():
            result['has_errors'] = True
            result['errors'].append('GCC not installed')
            return result

        # Biên dịch
        compile_result = self.compile(code)
        result['compile_status'] = compile_result

        if not compile_result['success']:
            result['has_errors'] = True
            result['errors'].append(compile_result.get('error', 'Unknown error'))
            return result

        # Chạy testcases
        if testcases:
            for i, testcase in enumerate(testcases):
                test_input = testcase.get('input', '')
                expected_output = testcase.get('expected_output', '')

                run_result = self.run(code, test_input)

                test_result = {
                    'testcase': i + 1,
                    'passed': False,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': run_result.get('output', '')
                }

                if run_result['success']:
                    # So sánh output
                    actual = run_result['output'].strip()
                    expected = expected_output.strip()
                    test_result['passed'] = actual == expected
                    
                    if not test_result['passed']:
                        result['has_errors'] = True

                result['test_results'].append(test_result)

        return result
