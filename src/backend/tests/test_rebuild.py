import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import app as app_module
from db_manager import DatabaseManager
from analyzer import CodeAnalyzer


def test_database_supports_roles_problems_and_testcases(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / 'rebuild_test.db'))

    admin = db.get_user_by_username('admin')
    assert admin is not None
    assert admin['vai_tro'] == 'admin'

    student_result = db.register_user('student01', 'student01@example.com', 'password123', role='hoc_sinh')
    assert student_result['success'] is True

    problem_result = db.create_problem(
        title='Tổng hai số',
        description='Viết chương trình tính tổng hai số',
        requirements='Nhập hai số nguyên và in tổng',
        created_by=admin['id'],
    )
    assert problem_result['success'] is True

    testcase_id = db.add_testcase(
        problem_id=problem_result['problem']['id'],
        input_data='3 5',
        expected_output='8',
        name='Case 1',
    )
    assert testcase_id is not None

    problems = db.list_problems()
    assert len(problems) >= 1

    stored_testcases = db.list_testcases(problem_result['problem']['id'])
    assert len(stored_testcases) == 1


def test_update_problem_updates_fields(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / 'rebuild_test.db'))

    admin = db.get_user_by_username('admin')
    problem_result = db.create_problem(
        title='Tổng hai số',
        description='Viết chương trình tính tổng hai số',
        requirements='Nhập hai số nguyên và in tổng',
        created_by=admin['id'],
    )

    update_result = db.update_problem(
        problem_id=problem_result['problem']['id'],
        title='Tổng ba số',
        description='Viết chương trình tính tổng ba số',
        requirements='Nhập ba số nguyên và in tổng',
        difficulty='hard',
        standard_code='#include <stdio.h>\nint main(){return 0;}'
    )

    assert update_result['success'] is True
    updated_problem = db.get_problem_by_id(problem_result['problem']['id'])
    assert updated_problem['tieu_de'] == 'Tổng ba số'
    assert updated_problem['mo_ta'] == 'Viết chương trình tính tổng ba số'
    assert updated_problem['yeu_cau'] == 'Nhập ba số nguyên và in tổng'
    assert updated_problem['do_kho'] == 'hard'
    assert updated_problem['ma_chuan'] == '#include <stdio.h>\nint main(){return 0;}'


def test_list_problems_by_creator_returns_associated_testcases(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / 'teacher_detail_test.db'))

    teacher = db.register_user('teacher01', 'teacher01@example.com', 'password123', role='giaovien')
    assert teacher['success'] is True

    problem_result = db.create_problem(
        title='Đếm chữ số',
        description='Viết chương trình đếm số chữ số',
        requirements='Nhập một số nguyên dương và in số lượng chữ số',
        created_by=teacher['user']['id'],
    )
    assert problem_result['success'] is True

    testcase_id = db.add_testcase(
        problem_id=problem_result['problem']['id'],
        input_data='123',
        expected_output='3',
        name='Case 1',
    )
    assert testcase_id is not None

    problems = db.list_problems_by_creator(teacher['user']['id'])
    assert len(problems) == 1
    assert problems[0]['id'] == problem_result['problem']['id']
    assert len(db.list_testcases(problem_result['problem']['id'])) == 1


def test_compile_reports_passed_testcase_count():
    analyzer = CodeAnalyzer()
    code = '''#include <stdio.h>\nint main(){int a,b; scanf("%d %d", &a, &b); printf("%d\\n", a+b); return 0;}'''
    testcases = [{"input": "3 5", "expected_output": "8"}]

    result = analyzer.evaluate_testcases(code, testcases)

    assert result['success'] is True
    assert result['passed_count'] == 1
    assert result['total_count'] == 1


def test_list_problems_endpoint_includes_testcases_for_each_problem(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / 'list_problems_test.db'))
    app_module.db = db

    admin = db.get_user_by_username('admin')
    problem_result = db.create_problem(
        title='Tìm max',
        description='Viết chương trình tìm số lớn nhất',
        requirements='Nhập 3 số nguyên và in giá trị lớn nhất',
        created_by=admin['id'],
    )
    assert problem_result['success'] is True

    db.add_testcase(problem_result['problem']['id'], '1 2 3', '3', 'Case 1')
    db.add_testcase(problem_result['problem']['id'], '4 5 6', '6', 'Case 2')

    with app_module.app.test_client() as client:
        response = client.get('/api/problems')

    assert response.status_code == 200
    problems = response.get_json()['problems']
    assert len(problems) >= 1
    problem = next(item for item in problems if item['id'] == problem_result['problem']['id'])
    assert isinstance(problem.get('testcases'), list)
    assert len(problem['testcases']) == 2


def test_ai_analysis_saves_prompt_text_and_not_sanitized_column(tmp_path):
    db = DatabaseManager(db_path=str(tmp_path / 'ai_analysis_test.db'))
    admin = db.get_user_by_username('admin')
    problem_result = db.create_problem(
        title='Đếm số chẵn',
        description='Viết chương trình đếm số chẵn',
        requirements='Nhập một dãy số và đếm số chẵn',
        created_by=admin['id'],
    )
    submission_id = db.save_submission(admin['id'], problem_result['problem']['id'], '#include <stdio.h>\nint main(){return 0;}')
    analysis_id = db.save_ai_analysis(submission_id, {'bug_type_id': 'CF001'}, 'analysis text', 'prompt text')

    assert analysis_id is not None

    conn = db._connect()
    try:
        row = conn.execute('SELECT prompt_text, ai_analysis FROM mo_hinh_ai WHERE id = ?', (analysis_id,)).fetchone()
        assert row[0] == 'prompt text'
        assert row[1] == 'analysis text'
        cols = [c[1] for c in conn.execute('PRAGMA table_info(mo_hinh_ai)')]
        assert 'prompt_text' in cols
        assert 'sanitized_analysis' not in cols
    finally:
        conn.close()
