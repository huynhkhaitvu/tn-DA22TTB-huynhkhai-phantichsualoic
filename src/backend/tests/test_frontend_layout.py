from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_problem_management_fields_are_outside_create_panel():
    for relative_path in ['frontend/index.html', 'backend/frontend/index.html']:
        content = (REPO_ROOT / relative_path).read_text(encoding='utf-8')
        problem_title_index = content.index('id="problemTitle"')
        management_content_index = content.index('id="teacherManagementContent"')
        create_button_index = content.index('id="createProblemBtn"')

        assert problem_title_index < management_content_index, f'{relative_path} should place problem fields outside the create panel'
        assert create_button_index > management_content_index, f'{relative_path} should keep the create action inside the create panel'


def test_problem_menu_no_longer_shows_parent_label_and_list_view_hides_create_button():
    for relative_path in ['frontend/index.html', 'backend/frontend/index.html']:
        content = (REPO_ROOT / relative_path).read_text(encoding='utf-8')
        assert 'Quản lý đề bài' not in content.split('<aside class="management-menu">', 1)[1].split('</aside>', 1)[0], (
            f'{relative_path} should not render the parent menu label inside the management sidebar'
        )

    for script_path in ['frontend/script.js', 'backend/frontend/script.js']:
        script = (REPO_ROOT / script_path).read_text(encoding='utf-8')
        assert "if (createButton) createButton.style.display = 'none';" in script, (
            f'{script_path} should hide the create button in the list view'
        )


def test_delete_problem_and_testcase_controls_exist():
    for relative_path in ['frontend/index.html', 'backend/frontend/index.html']:
        content = (REPO_ROOT / relative_path).read_text(encoding='utf-8')
        assert 'id="deleteProblemBtn"' in content, f'{relative_path} should render the delete-problem button in the list view'

    for script_path in ['frontend/script.js', 'backend/frontend/script.js']:
        script = (REPO_ROOT / script_path).read_text(encoding='utf-8')
        assert 'async function deleteTestcase' in script, f'{script_path} should define a delete-testcase handler'

    app_text = (REPO_ROOT / 'backend/app.py').read_text(encoding='utf-8')
    assert 'def delete_testcase' in app_text, 'backend/app.py should expose a delete-testcase endpoint'


def test_create_menu_keeps_problem_form_visible():
    for script_path in ['frontend/script.js', 'backend/frontend/script.js']:
        script = (REPO_ROOT / script_path).read_text(encoding='utf-8')
        assert "if (problemInfoBlock) problemInfoBlock.style.display = 'block';" in script, (
            f'{script_path} should keep the problem form visible while creating a new problem'
        )


def test_student_clear_button_is_bound_to_handler():
    for script_path in ['frontend/script.js', 'backend/frontend/script.js']:
        script = (REPO_ROOT / script_path).read_text(encoding='utf-8')
        assert "const clearBtn = document.getElementById('clearBtn');" in script, (
            f'{script_path} should look up the student clear button'
        )
        assert "if (clearBtn) clearBtn.addEventListener('click', handleClear);" in script, (
            f'{script_path} should bind the student clear button to handleClear'
        )
        assert "function handleClear()" in script, (
            f'{script_path} should define the clear handler'
        )
