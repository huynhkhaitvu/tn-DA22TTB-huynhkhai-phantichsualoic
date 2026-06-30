"""
Ứng dụng Flask chính cho hệ thống phân tích và sửa lỗi mã C.
Hỗ trợ 3 vai trò: admin, giaovien, hoc_sinh.
"""
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from datetime import timedelta
import os
from dotenv import load_dotenv
from config import get_config
from analyzer import CodeAnalyzer
from ai_handler import AIHandler
from utils import validate_c_syntax, detect_common_errors
from utils import sanitize_ai_response
import json

load_dotenv()

app = Flask(__name__)
config = get_config()
app.config.from_object(config)
app.permanent_session_lifetime = timedelta(hours=24)

CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"], "allow_headers": ["Content-Type"]}}, supports_credentials=True)

analyzer = CodeAnalyzer()
ai_handler = AIHandler(
    api_key=app.config.get('GEMINI_API_KEY', ''),
    openrouter_key=app.config.get('OPENROUTER_API_KEY', ''),
    groq_key=app.config.get('GROQ_API_KEY', '')
)

from db_manager import DatabaseManager

db = DatabaseManager()

app.analyzer = analyzer
app.ai_handler = ai_handler
app.db = db


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Server is running'})


@app.route('/api/compile', methods=['POST'])
def compile_code():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        if not code:
            return jsonify({'error': 'Code is required'}), 400

        result = analyzer.compile(code)
        testcases = data.get('testcases', [])
        problem_id = data.get('problem_id')
        if problem_id and not testcases:
            problem = db.get_problem_by_id(problem_id)
            if problem:
                testcases = db.list_testcases(problem_id)
                testcases = [{"input": tc.get('input_data', ''), "expected_output": tc.get('expected_output', ''), "name": tc.get('ten_testcase', '')} for tc in testcases]

        if result.get('success') and testcases:
            evaluation = analyzer.evaluate_testcases(code, testcases)
            result['passed_count'] = evaluation.get('passed_count', 0)
            result['total_count'] = evaluation.get('total_count', len(testcases))
            result['test_results'] = evaluation.get('test_results', [])

        user_id = session.get('user_id')
        if user_id:
            try:
                db.save_submission(
                    user_id,
                    problem_id,
                    code,
                    compile_status=result,
                    test_results=result.get('test_results', []),
                    run_output=result.get('output', '')
                )
            except Exception:
                pass

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        input_data = data.get('input', '')
        if not code:
            return jsonify({'error': 'Code is required'}), 400

        result = analyzer.run(code, input_data)
        user_id = session.get('user_id')
        if user_id:
            try:
                db.save_submission(
                    user_id,
                    data.get('problem_id'),
                    code,
                    compile_status=result,
                    test_results=[],
                    run_output=result.get('output', '')
                )
            except Exception:
                pass

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        if not code:
            return jsonify({'error': 'Code is required'}), 400

        problem_id = data.get('problem_id')
        testcases = data.get('testcases', [])
        if problem_id and not testcases:
            problem = db.get_problem_by_id(problem_id)
            if problem:
                testcases = db.list_testcases(problem_id)
                testcases = [{"input": tc.get('input_data', ''), "expected_output": tc.get('expected_output', ''), "name": tc.get('ten_testcase', '')} for tc in testcases]

        analysis_result = analyzer.analyze(code, testcases)
        static_errors = detect_common_errors(code)
        if static_errors:
            analysis_result.setdefault('errors', [])
            analysis_result['errors'].extend(static_errors)
            analysis_result['has_errors'] = True

        test_results_for_classification = analysis_result.get('test_results', []) or []
        submission_id = None
        user_id = session.get('user_id')
        if user_id:
            try:
                submission_id = db.save_submission(
                    user_id,
                    problem_id,
                    code,
                    compile_status=analysis_result.get('compile_status'),
                    test_results=analysis_result.get('test_results', []),
                    run_output=analysis_result.get('run_output', '')
                )
            except Exception:
                pass

        should_save_ai_analysis = analysis_result.get('has_errors') or any(not tr.get('passed', False) for tr in test_results_for_classification)
        if should_save_ai_analysis:
            try:
                classification = ai_handler.classify_bug_type(code, data.get('requirements', ''), test_results_for_classification)
            except Exception:
                classification = {'bug_type_id': 'CF001', 'bug_type_name': 'Unknown', 'confidence': 0}

            error_message = ''
            if analysis_result.get('compile_status') and not analysis_result['compile_status'].get('success'):
                error_message = analysis_result['compile_status'].get('error', '')
            else:
                failed_tests = [tr for tr in test_results_for_classification if not tr.get('passed', False)]
                if failed_tests:
                    error_message = '\n'.join([f"Test {t.get('testcase')}: expected='{t.get('expected')}' actual='{t.get('actual')}'" for t in failed_tests])

            provider = data.get('ai_provider', 'gemini')
            if not (app.config.get('GEMINI_API_KEY') or app.config.get('OPENROUTER_API_KEY') or app.config.get('GROQ_API_KEY')):
                detailed = 'AI analysis unavailable: no API key configured'
            else:
                try:
                    detailed = ai_handler.get_detailed_suggestions(code, error_message, '', provider=provider)
                except Exception:
                    detailed = 'AI analysis unavailable'
            if not isinstance(detailed, str) or not detailed.strip():
                detailed = 'AI analysis unavailable'

            analysis_result['classification'] = classification
            analysis_result['ai_analysis'] = detailed

        if submission_id and (analysis_result.get('classification') or analysis_result.get('ai_analysis')):
            try:
                classification = analysis_result.get('classification') or {'bug_type_id': 'CF001', 'bug_type_name': 'Unknown', 'confidence': 0}
                detailed = analysis_result.get('ai_analysis') or 'AI analysis unavailable'
                prompt_text = data.get('requirements', '') or ''
                db.save_ai_analysis(submission_id, classification, detailed if isinstance(detailed, str) else json.dumps(detailed), prompt_text)
            except Exception:
                pass

        if problem_id:
            problem = db.get_problem_by_id(problem_id)
            analysis_result['problem'] = problem

        return jsonify(analysis_result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/suggestions', methods=['POST'])
def get_suggestions():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        error_message = data.get('error_message', '')
        output = data.get('output', '')
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        provider = data.get('ai_provider', 'gemini')
        suggestions = ai_handler.get_detailed_suggestions(code, error_message, output, provider=provider)
        return jsonify({'suggestions': suggestions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/check-syntax', methods=['POST'])
def check_syntax():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        issues = validate_c_syntax(code)
        return jsonify({'valid': len(issues) == 0, 'issues': issues})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect-errors', methods=['POST'])
def detect_errors():
    try:
        data = request.get_json(silent=True) or {}
        code = data.get('code')
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        errors = detect_common_errors(code)
        return jsonify({'has_errors': len(errors) > 0, 'errors': errors})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/problems', methods=['GET'])
def list_problems():
    problems = db.list_problems()
    enriched_problems = []
    for problem in problems:
        testcases = db.list_testcases(problem['id'])
        enriched_problems.append({
            **problem,
            'testcases': [{
                'id': tc.get('id'),
                'name': tc.get('ten_testcase'),
                'input': tc.get('input_data'),
                'expected_output': tc.get('expected_output')
            } for tc in testcases]
        })
    return jsonify({'problems': enriched_problems})


@app.route('/api/problems/<int:problem_id>', methods=['GET'])
def get_problem(problem_id):
    problem = db.get_problem_by_id(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404
    testcases = db.list_testcases(problem_id)
    problem['testcases'] = testcases
    return jsonify({'problem': problem})


@app.route('/api/problems', methods=['POST'])
def create_problem():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401
    if user.get('vai_tro') not in {'admin', 'giaovien'}:
        return jsonify({'success': False, 'error': 'Chỉ giáo viên/admin mới được tạo đề bài'}), 403

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    requirements = (data.get('requirements') or '').strip()
    if not title or not requirements:
        return jsonify({'success': False, 'error': 'Thiếu tiêu đề hoặc yêu cầu'}), 400

    standard_code = data.get('standard_code', data.get('starter_code', ''))
    result = db.create_problem(
        title=title,
        description=description,
        requirements=requirements,
        created_by=user['id'],
        difficulty=data.get('difficulty', 'medium'),
        standard_code=standard_code
    )
    return jsonify(result)


@app.route('/api/problems/<int:problem_id>', methods=['DELETE'])
def delete_problem(problem_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    problem = db.get_problem_by_id(problem_id)
    if not problem:
        return jsonify({'success': False, 'error': 'Không tìm thấy đề bài'}), 404

    if user.get('vai_tro') == 'admin':
        result = db.delete_problem(problem_id)
        return jsonify(result)

    if user.get('vai_tro') == 'giaovien' and problem.get('created_by') == user['id']:
        result = db.delete_problem(problem_id)
        return jsonify(result)

    return jsonify({'success': False, 'error': 'Bạn chỉ được xóa đề bài do chính mình tạo'}), 403


@app.route('/api/problems/<int:problem_id>/testcases', methods=['POST'])
def add_testcase(problem_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    problem = db.get_problem_by_id(problem_id)
    if not problem:
        return jsonify({'success': False, 'error': 'Không tìm thấy đề bài'}), 404

    if user.get('vai_tro') == 'admin':
        pass
    elif user.get('vai_tro') == 'giaovien' and problem.get('created_by') == user['id']:
        pass
    else:
        return jsonify({'success': False, 'error': 'Bạn chỉ được thêm testcase cho đề bài do chính mình tạo'}), 403

    data = request.get_json(silent=True) or {}
    input_data = (data.get('input_data') or '').strip()
    expected_output = (data.get('expected_output') or '').strip()
    if not input_data or not expected_output:
        return jsonify({'success': False, 'error': 'Thiếu input hoặc expected output'}), 400

    testcase_id = db.add_testcase(problem_id, input_data, expected_output, name=data.get('name', ''))
    return jsonify({'success': True, 'testcase_id': testcase_id})


@app.route('/api/problems/<int:problem_id>/testcases', methods=['GET'])
def list_problem_testcases(problem_id):
    return jsonify({'testcases': db.list_testcases(problem_id)})


@app.route('/api/testcases/<int:testcase_id>', methods=['DELETE'])
def delete_testcase(testcase_id):
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    testcase = db.get_testcase_by_id(testcase_id)
    if not testcase:
        return jsonify({'success': False, 'error': 'Không tìm thấy testcase'}), 404

    problem = db.get_problem_by_id(testcase.get('de_bai_id'))
    if not problem:
        return jsonify({'success': False, 'error': 'Không tìm thấy đề bài'}), 404

    if user.get('vai_tro') == 'admin':
        result = db.delete_testcase(testcase_id)
        return jsonify(result)

    if user.get('vai_tro') == 'giaovien' and problem.get('created_by') == user['id']:
        result = db.delete_testcase(testcase_id)
        return jsonify(result)

    return jsonify({'success': False, 'error': 'Bạn chỉ được xóa testcase của đề bài do chính mình tạo'}), 403


@app.route('/api/admin/users', methods=['GET'])
def admin_list_users():
    user = get_current_user()
    if not user or user.get('vai_tro') not in {'admin', 'giaovien'}:
        return jsonify({'success': False, 'error': 'Chỉ admin hoặc giáo viên mới được xem người dùng'}), 403
    return jsonify({'users': db.list_users()})


@app.route('/api/admin/users/<int:user_id>/role', methods=['POST'])
def admin_update_role(user_id):
    user = get_current_user()
    if not user or user.get('vai_tro') != 'admin':
        return jsonify({'success': False, 'error': 'Chỉ admin mới được cập nhật vai trò'}), 403
    data = request.get_json(silent=True) or {}
    return jsonify(db.update_user_role(user_id, data.get('role', 'hoc_sinh')))


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def admin_delete_user(user_id):
    user = get_current_user()
    if not user or user.get('vai_tro') != 'admin':
        return jsonify({'success': False, 'error': 'Chỉ admin mới được xóa người dùng'}), 403
    return jsonify(db.delete_user(user_id))


@app.route('/api/submissions/me', methods=['GET'])
def list_my_submissions():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Vui lòng đăng nhập'}), 401

    submissions = db.get_submissions_by_user(user['id'])
    enriched = []
    for submission in submissions:
        problem = None
        problem_id = submission.get('de_bai_id')
        if problem_id:
            problem = db.get_problem_by_id(problem_id)
        test_results = json.loads(submission['test_results']) if submission.get('test_results') else []
        passed_count = sum(1 for tr in test_results if tr.get('passed')) if test_results else 0
        total_count = len(test_results)
        enriched.append({
            'id': submission.get('id'),
            'created_at': submission.get('created_at'),
            'problem_id': problem_id,
            'problem_title': problem.get('tieu_de') if problem else None,
            'code': submission.get('ma_nguon') or '',
            'compile_status': json.loads(submission['compile_status']) if submission.get('compile_status') else None,
            'test_results': test_results,
            'passed_count': passed_count,
            'total_count': total_count,
            'run_output': submission.get('run_output') or ''
        })

    return jsonify({'success': True, 'submissions': enriched})


@app.route('/api/admin/users/<int:user_id>/submissions', methods=['GET'])
def admin_list_user_submissions(user_id):
    user = get_current_user()
    if not user or user.get('vai_tro') not in {'admin', 'giaovien'}:
        return jsonify({'success': False, 'error': 'Chỉ admin hoặc giáo viên mới được xem bài làm học sinh'}), 403

    target_user = db.get_user_by_id(user_id)
    if not target_user:
        return jsonify({'success': False, 'error': 'Không tìm thấy người dùng'}), 404
    if target_user.get('vai_tro') != 'hoc_sinh' and user.get('vai_tro') != 'admin':
        return jsonify({'success': False, 'error': 'Giáo viên chỉ có thể xem bài làm của học sinh'}), 403

    submissions = db.get_submissions_by_user(user_id)
    enriched = []
    for submission in submissions:
        problem = None
        problem_id = submission.get('de_bai_id')
        if problem_id:
            problem = db.get_problem_by_id(problem_id)
        test_results = json.loads(submission['test_results']) if submission.get('test_results') else []
        passed_count = sum(1 for tr in test_results if tr.get('passed')) if test_results else 0
        total_count = len(test_results)
        enriched.append({
            'id': submission.get('id'),
            'created_at': submission.get('created_at'),
            'problem_id': problem_id,
            'problem_title': problem.get('tieu_de') if problem else None,
            'problem_description': problem.get('mo_ta') if problem else None,
            'problem_requirements': problem.get('yeu_cau') if problem else None,
            'code': submission.get('ma_nguon') or '',
            'compile_status': json.loads(submission['compile_status']) if submission.get('compile_status') else None,
            'test_results': test_results,
            'passed_count': passed_count,
            'total_count': total_count,
            'run_output': submission.get('run_output') or ''
        })

    return jsonify({'success': True, 'submissions': enriched})


@app.route('/api/admin/users/<int:user_id>/teacher-info', methods=['GET'])
def admin_list_teacher_info(user_id):
    user = get_current_user()
    if not user or user.get('vai_tro') != 'admin':
        return jsonify({'success': False, 'error': 'Chỉ admin mới được xem thông tin giáo viên'}), 403

    problems = db.list_problems_by_creator(user_id)
    enriched_problems = []
    for problem in problems:
        testcases = db.list_testcases(problem['id'])
        enriched_problems.append({
            'id': problem['id'],
            'title': problem.get('tieu_de'),
            'description': problem.get('mo_ta'),
            'requirements': problem.get('yeu_cau'),
            'difficulty': problem.get('do_kho'),
            'testcases': [{
                'id': tc.get('id'),
                'name': tc.get('ten_testcase'),
                'input': tc.get('input_data'),
                'expected_output': tc.get('expected_output')
            } for tc in testcases]
        })

    return jsonify({'success': True, 'problems': enriched_problems})


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = (data.get('password') or '').strip()
    password_confirm = (data.get('password_confirm') or '').strip()
    full_name = (data.get('full_name') or '').strip()
    role = (data.get('role') or 'hoc_sinh').strip().lower()
    if role not in {'hoc_sinh', 'giaovien'}:
        role = 'hoc_sinh'

    if not username or not email or not password:
        return jsonify({'success': False, 'error': 'Vui lòng nhập đầy đủ thông tin'}), 400
    if len(username) < 3:
        return jsonify({'success': False, 'error': 'Tên đăng nhập phải từ 3 ký tự trở lên'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Mật khẩu phải từ 6 ký tự trở lên'}), 400
    if password != password_confirm:
        return jsonify({'success': False, 'error': 'Mật khẩu không khớp'}), 400
    if '@' not in email or '.' not in email:
        return jsonify({'success': False, 'error': 'Email không hợp lệ'}), 400

    result = db.register_user(username, email, password, full_name=full_name, role=role)
    return jsonify(result), 201 if result.get('success') else 400


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    if not username or not password:
        return jsonify({'success': False, 'error': 'Vui lòng nhập username và password'}), 400

    result = db.verify_password(username, password)
    if result['success']:
        session.permanent = True
        session['user_id'] = result['user_id']
        session['username'] = result['username']
        session['role'] = result.get('role', 'hoc_sinh')
        return jsonify({'success': True, 'username': result['username'], 'user_id': result['user_id'], 'role': result.get('role', 'hoc_sinh')})
    return jsonify(result), 401


@app.route('/api/auth/google-login', methods=['POST'])
def google_login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    full_name = data.get('full_name', '')
    if not email:
        return jsonify({'success': False, 'error': 'Email không hợp lệ'}), 400

    result = db.get_or_create_google_user(email, full_name)
    if result['success']:
        session.permanent = True
        session['user_id'] = result['user_id']
        session['username'] = result['username']
        session['role'] = result.get('role', 'hoc_sinh')
        return jsonify({'success': True, 'username': result['username'], 'user_id': result['user_id'], 'role': result.get('role', 'hoc_sinh'), 'is_new': result.get('is_new', False)})
    return jsonify(result), 400


@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'Chưa đăng nhập'}), 401
    return jsonify({'success': True, 'user': user})


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    user = get_current_user()
    if user:
        return jsonify({'authenticated': True, 'user_id': user['id'], 'username': user.get('ten_dang_nhap') or user.get('username'), 'role': user.get('vai_tro') or user.get('role')})
    return jsonify({'authenticated': False})


def get_frontend_dir():
    base_dir = os.path.dirname(__file__)
    candidates = [
        os.path.abspath(os.path.join(base_dir, '..', 'frontend')),
        os.path.abspath(os.path.join(base_dir, 'frontend')),
    ]
    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return os.path.abspath(os.path.join(base_dir, 'frontend'))


@app.route('/')
def serve_root():
    return send_from_directory(get_frontend_dir(), 'index.html')


@app.route('/auth')
@app.route('/login')
@app.route('/register')
def serve_auth_page():
    return send_from_directory(get_frontend_dir(), 'auth.html')


@app.route('/<path:path>')
def serve_frontend(path):
    if path.startswith('api/'):
        return jsonify({'error': 'Not Found'}), 404
    return send_from_directory(get_frontend_dir(), path)


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    user = db.get_user_by_id(user_id)
    if user:
        session['role'] = user.get('vai_tro') or user.get('role') or session.get('role', 'hoc_sinh')
    return user


if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    if app.config.get('DEBUG', True):
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['SESSION_COOKIE_SECURE'] = False
    else:
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['SESSION_COOKIE_SECURE'] = True
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
