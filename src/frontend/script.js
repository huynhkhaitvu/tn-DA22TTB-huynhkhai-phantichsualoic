const API_BASE_URL = '/api';
let currentProblem = null;
let currentUser = null;
let availableProblems = [];

window.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkAuthAndLoad();
});

function initializeEventListeners() {
    const compileBtn = document.getElementById('compileBtn');
    if (compileBtn) compileBtn.addEventListener('click', handleCompile);

    const runBtn = document.getElementById('runBtn');
    if (runBtn) runBtn.addEventListener('click', handleRun);

    const openFileBtn = document.getElementById('openFileBtn');
    const fileInput = document.getElementById('fileInput');
    if (openFileBtn && fileInput) {
        openFileBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
    }

    const problemSelect = document.getElementById('problemSelect');
    if (problemSelect) {
        problemSelect.addEventListener('change', (e) => loadProblemDetails(e.target.value));
    }

    const createProblemBtn = document.getElementById('createProblemBtn');
    if (createProblemBtn) {
        createProblemBtn.addEventListener('click', handleCreateProblem);
    }

    const openTeacherFormBtn = document.getElementById('openTeacherFormBtn');
    const teacherManagementContent = document.getElementById('teacherManagementContent');
    if (openTeacherFormBtn && teacherManagementContent) {
        openTeacherFormBtn.addEventListener('click', () => {
            const shouldShow = teacherManagementContent.style.display === 'none' || teacherManagementContent.style.display === '';
            teacherManagementContent.style.display = shouldShow ? 'block' : 'none';
            if (shouldShow) {
                resetProblemForm();
            }
        });
    }

    const deleteProblemBtn = document.getElementById('deleteProblemBtn');
    if (deleteProblemBtn) {
        deleteProblemBtn.addEventListener('click', handleDeleteProblem);
    }

    const addTestcaseBtn = document.getElementById('addTestcaseBtn');
    if (addTestcaseBtn) {
        addTestcaseBtn.addEventListener('click', handleAddTestcase);
    }

    const submitTestcaseBtn = document.getElementById('submitTestcaseBtn');
    if (submitTestcaseBtn) {
        submitTestcaseBtn.addEventListener('click', handleAddTestcase);
    }

    const helpBtn = document.getElementById('helpBtn');
    if (helpBtn) {
        helpBtn.addEventListener('click', handleHelp);
    }

    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) clearBtn.addEventListener('click', handleClear);

    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    document.querySelectorAll('.management-menu .menu-item, .management-menu .menu-submenu a').forEach((item) => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelectorAll('.management-menu .menu-item, .management-menu .menu-submenu a').forEach((link) => {
                link.classList.remove('active');
            });
            item.classList.add('active');

            const content = document.querySelector('.management-content');
            if (!content) return;
            const problemSelectBlock = document.getElementById('problemSelect')?.closest('.mb-3');
            const problemInfoBlock = document.querySelector('.management-content > .border.rounded');
            const testcaseBlock = document.querySelector('.management-content > .mt-3');
            const createBlock = document.getElementById('teacherManagementContent');
            const createButton = document.getElementById('openTeacherFormBtn');
            const problemListSection = document.getElementById('teacherProblemListSection');

            const text = item.textContent.trim();
            if (text.includes('Danh sách đề')) {
                if (problemSelectBlock) problemSelectBlock.style.display = 'block';
                if (problemInfoBlock) problemInfoBlock.style.display = 'block';
                if (testcaseBlock) testcaseBlock.style.display = 'block';
                if (createBlock) createBlock.style.display = 'none';
                if (createButton) createButton.style.display = 'none';
                if (problemListSection) problemListSection.style.display = 'block';
            } else if (text.includes('Tạo đề')) {
                if (problemSelectBlock) problemSelectBlock.style.display = 'none';
                if (problemInfoBlock) problemInfoBlock.style.display = 'block';
                if (testcaseBlock) testcaseBlock.style.display = 'none';
                if (createBlock) createBlock.style.display = 'block';
                if (createButton) createButton.style.display = 'none';
                if (problemListSection) problemListSection.style.display = 'none';
                resetProblemForm();
            } else {
                if (problemSelectBlock) problemSelectBlock.style.display = 'block';
                if (problemInfoBlock) problemInfoBlock.style.display = 'block';
                if (testcaseBlock) testcaseBlock.style.display = 'block';
                if (createBlock) createBlock.style.display = 'none';
                if (createButton) createButton.style.display = 'none';
                if (problemListSection) problemListSection.style.display = 'block';
            }
        });
    });
}

async function checkAuthAndLoad() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, { credentials: 'include' });
        const data = await response.json();
        if (!data.authenticated) {
            window.location.href = 'auth.html';
            return;
        }
        currentUser = data;
        const userDisplay = document.getElementById('userDisplay');
        const usernameDisplay = document.getElementById('usernameDisplay');
        const roleDisplay = document.getElementById('roleDisplay');
        const loginLink = document.getElementById('loginLink');
        const logoutBtn = document.getElementById('logoutBtn');
        const teacherPanel = document.getElementById('teacherPanel');
        const adminPanel = document.getElementById('adminPanel');
        const heroCard = document.getElementById('heroCard');
        const studentProblemSection = document.getElementById('studentProblemSection');
        const testcaseSection = document.getElementById('studentTestcaseSection');
        const workspaceActions = document.getElementById('workspaceActions');
        const openFileBtn = document.getElementById('openFileBtn');
        const fileNameDisplay = document.getElementById('fileNameDisplay');
        const workspaceSection = document.getElementById('workspaceSection');
        const codeEditor = document.getElementById('codeEditor');
        const workspaceTitle = document.getElementById('workspaceTitle');
        const addTestcaseBtn = document.getElementById('addTestcaseBtn');
        const deleteProblemBtn = document.getElementById('deleteProblemBtn');
        const role = String(data.role || '').toLowerCase();
        const isTeacherOrAdmin = ['admin', 'giaovien'].includes(role);
        const isStudent = role === 'hoc_sinh';
        if (userDisplay) userDisplay.style.display = 'inline-block';
        if (usernameDisplay) usernameDisplay.textContent = data.username || 'user';
        if (roleDisplay) roleDisplay.textContent = roleLabel(data.role || 'hoc_sinh');
        if (loginLink) loginLink.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'inline-block';
        if (teacherPanel) teacherPanel.style.display = isTeacherOrAdmin ? 'block' : 'none';
        if (adminPanel) adminPanel.style.display = role === 'admin' ? 'block' : 'none';
        if (heroCard) heroCard.style.display = isStudent ? 'block' : 'none';
        if (studentProblemSection) studentProblemSection.style.display = isStudent ? 'block' : 'none';
        if (testcaseSection) testcaseSection.style.display = isTeacherOrAdmin ? 'block' : 'none';
        if (workspaceActions) workspaceActions.style.display = isTeacherOrAdmin ? 'none' : 'flex';
        if (openFileBtn) openFileBtn.style.display = isTeacherOrAdmin ? 'none' : 'inline-block';
        if (fileNameDisplay) fileNameDisplay.style.display = isTeacherOrAdmin ? 'none' : 'inline';
        const compileBtn = document.getElementById('compileBtn');
        const runBtn = document.getElementById('runBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const clearBtn = document.getElementById('clearBtn');
        if (compileBtn) compileBtn.style.display = isTeacherOrAdmin ? 'none' : 'inline-block';
        if (runBtn) runBtn.style.display = isTeacherOrAdmin ? 'none' : 'inline-block';
        if (analyzeBtn) analyzeBtn.style.display = isTeacherOrAdmin ? 'none' : 'inline-block';
        if (clearBtn) clearBtn.style.display = isTeacherOrAdmin ? 'none' : 'inline-block';
        if (codeEditor) {
            codeEditor.readOnly = isTeacherOrAdmin;
            codeEditor.style.backgroundColor = isTeacherOrAdmin ? '#f8f9fa' : '#fff';
        }
        if (workspaceTitle) workspaceTitle.textContent = isTeacherOrAdmin ? '✅ Code chuẩn' : '📝 Mã C';
        if (workspaceSection) workspaceSection.style.display = isTeacherOrAdmin ? 'none' : 'block';
        if (addTestcaseBtn) addTestcaseBtn.style.display = isTeacherOrAdmin ? 'inline-block' : 'none';
        if (deleteProblemBtn) deleteProblemBtn.style.display = role === 'admin' ? 'block' : 'none';
        if (isStudent && testcaseSection) {
            testcaseSection.style.display = 'none';
        }
        await loadProblems();
        await loadStudentSubmissionHistory();
        if (role === 'admin') {
            await loadAdminUsers();
        }
        if (role === 'giaovien') {
            await loadTeacherStudents();
        }
    } catch (error) {
        showResult('Không thể xác thực người dùng: ' + error.message, 'error');
    }
}

async function loadProblems() {
    const response = await fetch(`${API_BASE_URL}/problems`);
    const data = await response.json();
    const select = document.getElementById('problemSelect');
    const problemDetails = document.getElementById('problemDetails');
    const teacherProblemList = document.getElementById('teacherProblemList');
    if (!select) return;
    select.innerHTML = '';
    availableProblems = data.problems || [];
    if (!availableProblems.length) {
        select.innerHTML = '<option value="">Chưa có đề bài</option>';
        if (problemDetails) {
            problemDetails.innerHTML = '<div class="empty">Chưa có đề bài nào trong hệ thống. Giáo viên hoặc admin có thể tạo mới.</div>';
        }
        if (teacherProblemList) {
            teacherProblemList.innerHTML = '<div class="empty">Chưa có đề bài nào.</div>';
        }
        showResult('Chưa có đề bài trong hệ thống. Giáo viên/admin có thể tạo mới.', 'info');
        return;
    }
    availableProblems.forEach(problem => {
        const option = document.createElement('option');
        option.value = problem.id;
        option.textContent = problem.tieu_de;
        select.appendChild(option);
    });
    const selectedId = select.value || availableProblems[0].id;
    select.value = selectedId;
    renderTeacherProblemList(availableProblems, selectedId);
    await loadProblemDetails(selectedId);
}

function renderTeacherProblemList(problems, selectedId = null) {
    const container = document.getElementById('teacherProblemList');
    if (!container) return;
    if (!problems || !problems.length) {
        container.innerHTML = '<div class="empty">Chưa có đề bài nào.</div>';
        return;
    }
    const difficultyMap = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };
    container.innerHTML = problems.map((problem) => {
        const isActive = String(problem.id) === String(selectedId);
        const difficultyLabel = difficultyMap[problem.do_kho] || 'Trung bình';
        const testcaseCount = Array.isArray(problem.testcases) ? problem.testcases.length : 0;
        return `
            <div class="problem-list-item ${isActive ? 'active' : ''}" onclick="loadProblemDetails(${problem.id})">
                <div class="problem-list-title">${escapeHtml(problem.tieu_de || 'Đề chưa có tên')}</div>
                <div class="problem-list-meta">Độ khó: ${escapeHtml(difficultyLabel)} • Testcase: ${testcaseCount}</div>
            </div>
        `;
    }).join('');
}

async function loadProblemDetails(problemId) {
    const response = await fetch(`${API_BASE_URL}/problems/${problemId}`);
    const data = await response.json();
    currentProblem = data.problem;
    renderTeacherProblemList(availableProblems, problemId);
    const problemDetails = document.getElementById('problemDetails');
    if (!problemDetails) return;
    if (!currentProblem) {
        problemDetails.innerHTML = '<div class="empty">Vui lòng chọn một đề bài để xem chi tiết.</div>';
        return;
    }
    const difficultyMap = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };
    const difficultyLabel = difficultyMap[currentProblem.do_kho] || 'Trung bình';
    const testcaseCount = currentProblem.testcases ? currentProblem.testcases.length : 0;
    problemDetails.innerHTML = `
        <div class="problem-meta-grid">
            <div class="problem-meta-box">
                <span class="problem-meta-label">Độ khó</span>
                <div><span class="problem-pill">${escapeHtml(difficultyLabel)}</span></div>
            </div>
            <div class="problem-meta-box">
                <span class="problem-meta-label">Testcase</span>
                <div class="fw-semibold">${testcaseCount} mẫu</div>
            </div>
            <div class="problem-meta-box">
                <span class="problem-meta-label">Tiêu đề</span>
                <div class="fw-semibold">${escapeHtml(currentProblem.tieu_de || '')}</div>
            </div>
        </div>
        <div class="problem-meta-box">
            <span class="problem-meta-label">Mô tả</span>
            <p>${escapeHtml(currentProblem.mo_ta || 'Chưa có mô tả cho đề bài này.')}</p>
        </div>
        <div class="problem-meta-box">
            <span class="problem-meta-label">Yêu cầu</span>
            <p>${escapeHtml(currentProblem.yeu_cau || 'Chưa có yêu cầu chi tiết.')}</p>
        </div>
    `;

    const titleInput = document.getElementById('problemTitle');
    const descriptionInput = document.getElementById('problemDescription');
    const requirementsInput = document.getElementById('problemRequirements');
    const standardCodeInput = document.getElementById('problemStandardCode');
    const difficultySelect = document.getElementById('problemDifficulty');
    if (titleInput) titleInput.value = currentProblem.tieu_de || '';
    if (descriptionInput) descriptionInput.value = currentProblem.mo_ta || '';
    if (requirementsInput) requirementsInput.value = currentProblem.yeu_cau || '';
    if (standardCodeInput) standardCodeInput.value = currentProblem.ma_chuan || '';
    if (difficultySelect) difficultySelect.value = currentProblem.do_kho || 'medium';

    renderTestcases(currentProblem.testcases || []);
    const editor = document.getElementById('codeEditor');
    if (editor) {
        const isTeacherOrAdmin = ['admin', 'giaovien'].includes(currentUser?.role);
        if (isTeacherOrAdmin) {
            editor.value = currentProblem.ma_chuan || currentProblem.ma_khoi_dong || '';
        } else if (!editor.value.trim()) {
            editor.value = '';
        }
    }
}

function resetProblemForm() {
    currentProblem = null;
    const titleInput = document.getElementById('problemTitle');
    const descriptionInput = document.getElementById('problemDescription');
    const requirementsInput = document.getElementById('problemRequirements');
    const standardCodeInput = document.getElementById('problemStandardCode');
    const difficultySelect = document.getElementById('problemDifficulty');
    const problemSelect = document.getElementById('problemSelect');
    if (titleInput) titleInput.value = '';
    if (descriptionInput) descriptionInput.value = '';
    if (requirementsInput) requirementsInput.value = '';
    if (standardCodeInput) standardCodeInput.value = '';
    if (difficultySelect) difficultySelect.value = 'medium';
    if (problemSelect) problemSelect.value = '';
    renderTestcases([]);
}

async function loadStudentSubmissionHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/submissions/me`, { credentials: 'include' });
        const data = await response.json();
        const list = document.getElementById('studentHistoryList');
        const count = document.getElementById('studentHistoryCount');
        if (!list) return;
        if (!data.success || !data.submissions || !data.submissions.length) {
            list.innerHTML = '<div class="empty">Bạn chưa có lần làm bài nào.</div>';
            if (count) count.textContent = '0';
            return;
        }
        if (count) count.textContent = String(data.submissions.length);
        list.innerHTML = data.submissions.slice(0, 6).map((item) => {
            const createdAt = item.created_at ? new Date(item.created_at).toLocaleString('vi-VN') : 'Không rõ thời gian';
            const problemTitle = item.problem_title || 'Đề chưa xác định';
            const passedCount = Number(item.passed_count ?? (Array.isArray(item.test_results) ? item.test_results.filter((t) => t.passed).length : 0));
            const totalCount = Number(item.total_count ?? (Array.isArray(item.test_results) ? item.test_results.length : 0));
            const statusText = item.compile_status && item.compile_status.success === false ? 'Lỗi' : (totalCount ? `Đã vượt ${passedCount}/${totalCount} testcase` : 'Đã chạy');
            return `
                <div class="student-history-item">
                    <div class="history-title">${escapeHtml(problemTitle)}</div>
                    <div class="history-meta">${escapeHtml(statusText)} • ${escapeHtml(createdAt)}</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Load submission history error:', error);
    }
}

function renderTestcases(testcases) {
    const container = document.getElementById('testCasesContainer');
    if (!container) return;
    if (!testcases.length) {
        container.innerHTML = '<div class="empty">Chưa có testcase nào.</div>';
        return;
    }
    container.innerHTML = testcases.map((tc, index) => `
        <div class="testcase-card">
            <div class="d-flex justify-content-between align-items-start">
                <strong>Testcase ${index + 1}: ${escapeHtml(tc.ten_testcase || '')}</strong>
                <button class="btn btn-outline-danger btn-sm" type="button" onclick="deleteTestcase(${tc.id})">Xóa</button>
            </div>
            <p><strong>Input:</strong><br>${escapeHtml(tc.input_data || '')}</p>
            <p><strong>Expected:</strong><br>${escapeHtml(tc.expected_output || '')}</p>
        </div>
    `).join('');
}

function getCode() {
    const editor = document.getElementById('codeEditor');
    return editor ? editor.value : '';
}

function getActiveTestcases() {
    if (currentProblem && currentProblem.testcases) {
        return currentProblem.testcases.map(tc => ({
            input: tc.input_data || '',
            expected_output: tc.expected_output || ''
        }));
    }
    return [];
}

async function handleCompile() {
    const code = getCode();
    if (!code.trim()) {
        showResult('Vui lòng nhập mã C trước khi biên dịch.', 'error');
        return;
    }
    const payload = {
        code,
        problem_id: currentProblem ? currentProblem.id : null,
        testcases: getActiveTestcases()
    };
    const result = await requestJson('/compile', payload);
    showResult(formatCompileResult(result), 'result');
    await loadStudentSubmissionHistory();
}

async function handleRun() {
    const code = getCode();
    if (!code.trim()) {
        showResult('Vui lòng nhập mã C trước khi chạy.', 'error');
        return;
    }
    const payload = {
        code,
        problem_id: currentProblem ? currentProblem.id : null,
        testcases: getActiveTestcases()
    };
    const result = await requestJson('/compile', payload);
    showResult(formatRunResult(result), 'result');
    await loadStudentSubmissionHistory();
}

async function handleHelp() {
    const code = getCode();
    if (!code.trim()) {
        showResult('Vui lòng nhập mã C trước khi nhận gợi ý.', 'error');
        return;
    }

    const resultsContainer = document.getElementById('resultsContainer');
    const latestText = resultsContainer?.textContent || '';
    const passedAll = /\b(\d+)\/(\d+)\b/.exec(latestText);
    if (passedAll && Number(passedAll[1]) > 0 && Number(passedAll[1]) === Number(passedAll[2])) {
        showResult('<strong>✅ Mã của bạn đã đúng.</strong><br>Không cần gợi ý thêm vì đã vượt qua tất cả testcase.', 'success');
        return;
    }

    const payload = {
        code,
        error_message: latestText,
        output: '',
        ai_provider: document.getElementById('aiProviderSelect')?.value || 'gemini'
    };
    const result = await requestJson('/suggestions', payload);
    showResult(`<strong>💡 Gợi ý từ AI:</strong><br>${escapeHtml(result.suggestions || 'Không có gợi ý.')}`, 'result');
}

async function handleCreateProblem() {
    const titleInput = document.getElementById('problemTitle');
    const descriptionInput = document.getElementById('problemDescription');
    const requirementsInput = document.getElementById('problemRequirements');
    const standardCodeInput = document.getElementById('problemStandardCode');
    const difficultyInput = document.getElementById('problemDifficulty');

    const title = titleInput?.value.trim() || '';
    const description = descriptionInput?.value.trim() || '';
    const requirements = requirementsInput?.value.trim() || '';
    const standardCode = standardCodeInput?.value || '';
    const difficulty = difficultyInput?.value || 'medium';

    if (!title || !requirements) {
        showResult('Vui lòng nhập tiêu đề và yêu cầu đề bài.', 'error');
        return;
    }

    const result = await requestJson('/problems', { title, description, requirements, standard_code: standardCode, difficulty }, 'POST');
    if (result.success) {
        showResult('✅ Tạo đề tài thành công.', 'success');
        if (titleInput) titleInput.value = '';
        if (descriptionInput) descriptionInput.value = '';
        if (requirementsInput) requirementsInput.value = '';
        if (standardCodeInput) standardCodeInput.value = '';
        if (difficultyInput) difficultyInput.value = 'medium';
        await loadProblems();
    } else {
        showResult(result.error || 'Không thể tạo đề tài.', 'error');
    }
}

async function handleDeleteProblem() {
    if (!currentProblem?.id) {
        showResult('Vui lòng chọn đề bài trước.', 'error');
        return;
    }
    if (!confirm(`Xóa đề bài "${currentProblem.tieu_de}"?`)) {
        return;
    }
    const result = await requestJson(`/problems/${currentProblem.id}`, null, 'DELETE');
    if (result.success) {
        showResult('Đã xóa đề bài.', 'success');
        await loadProblems();
    } else {
        showResult(result.error || 'Không thể xóa đề bài.', 'error');
    }
}

async function deleteTestcase(testcaseId) {
    if (!testcaseId || !confirm('Bạn có chắc chắn muốn xóa testcase này?')) return;
    const result = await requestJson(`/testcases/${testcaseId}`, null, 'DELETE');
    showResult(result.success ? 'Đã xóa testcase.' : (result.error || 'Không thể xóa testcase'), result.success ? 'success' : 'error');
    if (result.success && currentProblem?.id) {
        await loadProblemDetails(currentProblem.id);
    }
}

async function handleAddTestcase() {
    const form = document.getElementById('testcaseFormContainer');
    const addButton = document.getElementById('addTestcaseBtn');
    const nameInput = document.getElementById('testcaseName');
    const inputInput = document.getElementById('testcaseInput');
    const outputInput = document.getElementById('testcaseOutput');

    if (form && form.style.display === 'none') {
        form.style.display = 'block';
        if (addButton) addButton.textContent = '➕ Thêm testcase';
        if (nameInput) nameInput.focus();
        return;
    }

    if (!currentProblem?.id) {
        showResult('Vui lòng chọn đề bài trước.', 'error');
        return;
    }

    const name = nameInput?.value.trim() || '';
    const inputData = inputInput?.value.trim() || '';
    const expectedOutput = outputInput?.value.trim() || '';

    if (!inputData || !expectedOutput) {
        showResult('Vui lòng nhập input và expected output.', 'error');
        return;
    }

    const result = await requestJson(`/problems/${currentProblem.id}/testcases`, { name, input_data: inputData, expected_output: expectedOutput }, 'POST');
    if (result.success) {
        showResult('Đã thêm testcase mới.', 'success');
        if (nameInput) nameInput.value = '';
        if (inputInput) inputInput.value = '';
        if (outputInput) outputInput.value = '';
        if (form) form.style.display = 'none';
        if (addButton) addButton.textContent = '+ Thêm Test Case';
        await loadProblemDetails(currentProblem.id);
    } else {
        showResult(result.error || 'Không thể thêm testcase.', 'error');
    }
}

function buildRoleSection(users, role, title, subtitle, icon) {
    const filteredUsers = users.filter(user => (user.vai_tro || 'hoc_sinh').toLowerCase() === role);
    return `
        <div class="management-section">
            <div class="management-section-header">
                <div>
                    <h5>${icon} ${title}</h5>
                    <div class="management-section-subtitle">${subtitle}</div>
                </div>
                <span class="management-badge">${filteredUsers.length}</span>
            </div>
            ${filteredUsers.length ? filteredUsers.map(user => `
                <div class="management-row">
                    <div class="management-user">
                        <strong>${escapeHtml(user.ten_dang_nhap || user.username || 'user')}</strong>
                        <div class="management-meta">${escapeHtml(user.email || '—')}</div>
                    </div>
                    <div class="management-controls">
                        <span class="role-pill role-${(user.vai_tro || 'hoc_sinh').toLowerCase()}">${roleLabel(user.vai_tro || 'hoc_sinh')}</span>
                        <select class="form-control form-control-sm" id="role-${user.id}">
                            <option value="hoc_sinh" ${user.vai_tro === 'hoc_sinh' ? 'selected' : ''}>Học sinh</option>
                            <option value="giaovien" ${user.vai_tro === 'giaovien' ? 'selected' : ''}>Giáo viên</option>
                        </select>
                        <button class="btn btn-small" onclick="updateUserRole(${user.id})">Cập nhật</button>
                        <button class="btn btn-small btn-danger" onclick="deleteUser(${user.id})">Xóa</button>
                        <button class="btn btn-small btn-outline-info" onclick="viewStudentDetail(${user.id})">Xem chi tiết</button>
                    </div>
                </div>
            `).join('') : `<div class="empty">${title} chưa có dữ liệu.</div>`}
        </div>
    `;
}

async function loadTeacherStudents() {
    const section = document.getElementById('teacherStudentManagementSection');
    const list = document.getElementById('teacherStudentList');
    const detailPanel = document.getElementById('teacherStudentDetailPanel');
    if (!section || !list) return;

    if (!currentUser || String(currentUser.role || '').toLowerCase() !== 'giaovien') {
        section.style.display = 'none';
        if (detailPanel) detailPanel.innerHTML = '';
        return;
    }

    section.style.display = 'block';
    list.innerHTML = '<div class="empty">Đang tải danh sách học sinh...</div>';

    try {
        const result = await requestJson('/admin/users');
        const students = Array.isArray(result.users)
            ? result.users.filter(user => String(user.vai_tro || 'hoc_sinh').toLowerCase() === 'hoc_sinh')
            : [];

        if (!students.length) {
            list.innerHTML = '<div class="empty">Chưa có học sinh nào.</div>';
            return;
        }

        list.innerHTML = students.map(student => `
            <div class="management-row">
                <div class="management-user">
                    <strong>${escapeHtml(student.ten_dang_nhap || student.username || 'user')}</strong>
                    <div class="management-meta">${escapeHtml(student.email || '—')}</div>
                </div>
                <div class="management-controls">
                    <span class="role-pill role-hoc_sinh">Học sinh</span>
                    <button class="btn btn-small btn-outline-info" onclick="viewTeacherStudentDetail(${student.id})">Xem chi tiết</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        list.innerHTML = '<div class="empty">Không thể tải danh sách học sinh.</div>';
        console.error('Load teacher students error:', error);
    }
}

async function viewTeacherStudentDetail(userId) {
    const panel = document.getElementById('teacherStudentDetailPanel');
    if (!panel) return;
    panel.innerHTML = '<div class="empty">Đang tải thông tin học sinh...</div>';

    try {
        const [usersResult, submissionsResult] = await Promise.all([
            requestJson('/admin/users'),
            requestJson(`/admin/users/${userId}/submissions`)
        ]);
        const user = (usersResult.users || []).find(item => String(item.id) === String(userId));
        if (!user) {
            panel.innerHTML = '<div class="empty">Không tìm thấy học sinh.</div>';
            return;
        }

        const submissions = submissionsResult.success ? (submissionsResult.submissions || []) : [];
        panel.innerHTML = `
            <div class="management-section">
                <div class="management-section-header">
                    <div>
                        <h5>👤 Chi tiết học sinh</h5>
                        <div class="management-section-subtitle">Thông tin tài khoản và lịch sử làm bài</div>
                    </div>
                </div>
                <div class="management-row" style="display:block;">
                    <div class="management-user">
                        <strong>${escapeHtml(user.ten_dang_nhap || user.username || 'user')}</strong>
                        <div class="management-meta"><strong>Email:</strong> ${escapeHtml(user.email || '—')}</div>
                        <div class="management-meta"><strong>Vai trò:</strong> ${escapeHtml(roleLabel(user.vai_tro || 'hoc_sinh'))}</div>
                        <div class="management-meta"><strong>Trạng thái:</strong> ${user.is_active === 0 ? 'Bị khóa' : 'Hoạt động'}</div>
                    </div>
                </div>
                <div class="management-section-header" style="margin-top:12px;">
                    <div>
                        <h5>🧾 Lịch sử làm bài</h5>
                        <div class="management-section-subtitle">Danh sách bài làm của học sinh</div>
                    </div>
                </div>
                ${submissions.length ? submissions.map(sub => `
                    <div class="management-row" style="display:block;">
                        <div class="management-user">
                            <strong>${escapeHtml(sub.problem_title || `Bài làm #${sub.id}`)}</strong>
                            <div class="management-meta">${escapeHtml(sub.created_at || '')}</div>
                            <div class="management-meta"><strong>Đề bài:</strong> ${escapeHtml(sub.problem_title || 'Không xác định')}</div>
                            <div class="management-meta"><strong>Trạng thái:</strong> ${escapeHtml(getSubmissionSummary(sub))}</div>
                        </div>
                        <div class="management-controls" style="justify-content:flex-start; margin-top:8px;">
                            <div style="width:100%;">
                                <div class="management-meta"><strong>Code đã nộp:</strong></div>
                                <pre style="white-space:pre-wrap; word-break:break-word; background:#f8f9fa; padding:10px; border-radius:6px; margin-top:6px;">${escapeHtml(sub.code || '')}</pre>
                                ${sub.compile_status ? `<div class="management-meta"><strong>Kết quả biên dịch:</strong> ${sub.compile_status.success ? 'Thành công' : 'Thất bại'}</div>` : ''}
                                ${Array.isArray(sub.test_results) && sub.test_results.length ? `<div class="management-meta"><strong>Chi tiết testcase:</strong></div>${sub.test_results.map((test, index) => `<div class="management-meta" style="margin-top:6px;"><strong>${index + 1}. ${test.passed ? '✅' : '❌'} ${escapeHtml(test.name || `Testcase ${index + 1}`)}:</strong><br>Input: ${escapeHtml(test.input || '')}<br>Expected: ${escapeHtml(test.expected_output || '')}<br>Actual: ${escapeHtml(test.actual_output || '')}</div>`).join('')}` : ''}
                                ${sub.run_output ? `<div class="management-meta"><strong>Output:</strong> ${escapeHtml(sub.run_output)}</div>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('') : '<div class="empty">Học sinh này chưa có bài làm nào.</div>'}
            </div>
        `;
    } catch (error) {
        panel.innerHTML = '<div class="empty">Không thể tải thông tin học sinh.</div>';
        console.error('View teacher student detail error:', error);
    }
}

async function viewTeacherStudentSubmissions(userId) {
    const panel = document.getElementById('teacherStudentSubmissions');
    if (!panel) return;
    panel.innerHTML = '<div class="empty">Đang tải bài làm...</div>';
    const result = await requestJson(`/admin/users/${userId}/submissions`);
    if (!result.success || !result.submissions || !result.submissions.length) {
        panel.innerHTML = '<div class="empty">Học sinh này chưa có bài làm nào.</div>';
        return;
    }
    panel.innerHTML = `
        <div class="management-section">
            <div class="management-section-header">
                <div>
                    <h5>🧾 Lịch sử bài làm học sinh</h5>
                    <div class="management-section-subtitle">Code đã dán và đề bài liên quan</div>
                </div>
            </div>
            ${result.submissions.map(sub => `
                <div class="management-row" style="display:block;">
                    <div class="management-user">
                        <strong>Bài làm #${sub.id}</strong>
                        <div class="management-meta">${escapeHtml(sub.created_at || '')}</div>
                        <div class="management-meta"><strong>Đề bài:</strong> ${escapeHtml(sub.problem_title || 'Không xác định')}</div>
                        <div class="management-meta"><strong>Trạng thái:</strong> ${escapeHtml(getSubmissionSummary(sub))}</div>
                        <div class="management-meta"><strong>Mô tả:</strong> ${escapeHtml(sub.problem_description || '')}</div>
                    </div>
                    <div class="management-controls" style="justify-content:flex-start; margin-top:8px;">
                        <div style="width:100%;">
                            <div class="management-meta"><strong>Code đã dán:</strong></div>
                            <pre style="white-space:pre-wrap; word-break:break-word; background:#f8f9fa; padding:10px; border-radius:6px; margin-top:6px;">${escapeHtml(sub.code || '')}</pre>
                            <div class="management-meta"><strong>Yêu cầu đề bài:</strong> ${escapeHtml(sub.problem_requirements || '')}</div>
                            ${sub.compile_status ? `<div class="management-meta"><strong>Biên dịch:</strong> ${sub.compile_status.success ? 'Thành công' : 'Thất bại'}</div>` : ''}
                            ${Array.isArray(sub.test_results) && sub.test_results.length ? `<div class="management-meta"><strong>Chi tiết testcase:</strong></div>${sub.test_results.map((test, index) => `<div class="management-meta" style="margin-top:6px;"><strong>${index + 1}. ${test.passed ? '✅' : '❌'} ${escapeHtml(test.name || `Testcase ${index + 1}`)}:</strong><br>Input: ${escapeHtml(test.input || '')}<br>Expected: ${escapeHtml(test.expected_output || '')}<br>Actual: ${escapeHtml(test.actual_output || '')}</div>`).join('')}` : ''}
                            ${sub.run_output ? `<div class="management-meta"><strong>Output:</strong> ${escapeHtml(sub.run_output)}</div>` : ''}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function loadAdminUsers() {
    const result = await requestJson('/admin/users');
    const container = document.getElementById('userManagementList');
    if (!container) return;
    if (!result.users || !result.users.length) {
        container.innerHTML = '<div class="empty">Không có người dùng.</div>';
        return;
    }
    const users = result.users;
    container.innerHTML = `
        <div class="management-section">
            <div class="management-section-header">
                <div>
                    <h5>🛡️ Quản trị hệ thống</h5>
                    <div class="management-section-subtitle">Quản lý vai trò người dùng trong hệ thống</div>
                </div>
            </div>
        </div>
        <div class="management-note">Chỉ admin có thể chuyển vai trò giữa giáo viên và học sinh.</div>
        ${buildRoleSection(users, 'giaovien', 'Quản lý giáo viên', 'Danh sách giáo viên trong hệ thống', '')}
        <div id="teacherDetailPanel" class="mt-3"></div>
        ${buildRoleSection(users, 'hoc_sinh', 'Danh sách học sinh', 'Danh sách học sinh trong hệ thống', '')}
        <div id="studentDetailPanel" class="mt-3"></div>
    `;
}

async function updateUserRole(userId) {
    const select = document.getElementById(`role-${userId}`);
    if (!select) return;
    const result = await requestJson(`/admin/users/${userId}/role`, { role: select.value }, 'POST');
    showResult(result.success ? 'Đã cập nhật vai trò.' : (result.error || 'Không thể cập nhật'), result.success ? 'success' : 'error');
    if (result.success) {
        await loadAdminUsers();
    }
}

async function deleteUser(userId) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) return;
    const result = await requestJson(`/admin/users/${userId}`, null, 'DELETE');
    showResult(result.success ? 'Đã xóa tài khoản.' : (result.error || 'Không thể xóa tài khoản'), result.success ? 'success' : 'error');
    if (result.success) {
        await loadAdminUsers();
    }
}

async function viewStudentDetail(userId, panelId = null) {
    const [usersResult, submissionsResult, teacherInfoResult] = await Promise.all([
        requestJson('/admin/users'),
        requestJson(`/admin/users/${userId}/submissions`),
        requestJson(`/admin/users/${userId}/teacher-info`)
    ]);
    const user = (usersResult.users || []).find(item => String(item.id) === String(userId));
    if (!user) {
        const fallbackPanel = document.getElementById(panelId || 'studentDetailPanel');
        if (fallbackPanel) fallbackPanel.innerHTML = '<div class="empty">Không tìm thấy người dùng.</div>';
        return;
    }
    const role = (user.vai_tro || 'hoc_sinh').toLowerCase();
    const panel = document.getElementById(panelId || (role === 'giaovien' ? 'teacherDetailPanel' : 'studentDetailPanel'));
    if (!panel) return;
    const isTeacher = role === 'giaovien';
    const roleLabelText = isTeacher ? 'giáo viên' : role === 'hoc_sinh' ? 'học sinh' : 'người dùng';
    const infoTitle = isTeacher ? 'Chi tiết giáo viên' : 'Chi tiết học sinh';
    const infoSubtitle = isTeacher ? 'Thông tin tài khoản và các đề bài do giáo viên này tạo' : 'Thông tin tài khoản và lịch sử làm bài';
    const submissions = submissionsResult.success ? (submissionsResult.submissions || []) : [];
    const teacherProblems = isTeacher && teacherInfoResult.success ? (teacherInfoResult.problems || []) : [];
    panel.innerHTML = `
        <div class="management-section">
            <div class="management-section-header">
                <div>
                    <h5>${infoTitle}</h5>
                    <div class="management-section-subtitle">${infoSubtitle}</div>
                </div>
            </div>
            <div class="management-row" style="display:block;">
                <div class="management-user">
                    <strong>${escapeHtml(user.ten_dang_nhap || user.username || 'user')}</strong>
                    <div class="management-meta"><strong>Email:</strong> ${escapeHtml(user.email || '—')}</div>
                    <div class="management-meta"><strong>Vai trò:</strong> ${escapeHtml(roleLabel(user.vai_tro || 'hoc_sinh'))}</div>
                    <div class="management-meta"><strong>Trạng thái:</strong> ${user.is_active === 0 ? 'Bị khóa' : 'Hoạt động'}</div>
                    ${isTeacher ? '<div class="management-meta"><strong>Loại tài khoản:</strong> Giáo viên có thể quản lý bài tập và học sinh</div>' : ''}
                </div>
            </div>
            ${isTeacher ? `
                <div class="management-section-header" style="margin-top:12px;">
                    <div>
                        <h5>Đề bài đã tạo</h5>
                        <div class="management-section-subtitle">Danh sách đề bài và testcase do giáo viên này tạo</div>
                    </div>
                </div>
                ${teacherProblems.length ? teacherProblems.map(problem => `
                    <div class="management-row" style="display:block;">
                        <div class="management-user">
                            <strong>${escapeHtml(problem.title || 'Đề bài không tên')}</strong>
                            <div class="management-meta"><strong>Độ khó:</strong> ${escapeHtml(problem.difficulty || 'medium')}</div>
                            <div class="management-meta"><strong>Mô tả:</strong> ${escapeHtml(problem.description || '—')}</div>
                            <div class="management-meta"><strong>Yêu cầu:</strong> ${escapeHtml(problem.requirements || '—')}</div>
                        </div>
                        <div class="management-controls" style="justify-content:flex-start; margin-top:8px;">
                            <div style="width:100%;">
                                <div class="management-meta"><strong>Testcase:</strong></div>
                                ${problem.testcases && problem.testcases.length ? problem.testcases.map(tc => `
                                    <div class="management-meta" style="margin-top:6px;">
                                        <strong>${escapeHtml(tc.name || `Testcase ${tc.id}`)}:</strong><br>
                                        Input: ${escapeHtml(tc.input || '')}<br>
                                        Expected output: ${escapeHtml(tc.expected_output || '')}
                                    </div>
                                `).join('') : '<div class="management-meta">Chưa có testcase nào.</div>'}
                            </div>
                        </div>
                    </div>
                `).join('') : '<div class="empty">Giáo viên này chưa tạo đề bài nào.</div>'}
            ` : ''}
            <div class="management-section-header" style="margin-top:12px;">
                <div>
                    <h5>${isTeacher ? '' : 'Lịch sử làm bài'}</h5>
                    <div class="management-section-subtitle">${isTeacher ? '' : 'Tên đề bài và code đã nộp của học sinh'}</div>
                </div>
            </div>
            ${isTeacher ? '' : submissions.length ? submissions.map(sub => `
                <div class="management-row" style="display:block;">
                    <div class="management-user">
                        <strong>${escapeHtml(sub.problem_title || `Bài làm #${sub.id}`)}</strong>
                        <div class="management-meta">${escapeHtml(sub.created_at || '')}</div>
                        <div class="management-meta"><strong>Đề bài:</strong> ${escapeHtml(sub.problem_title || 'Không xác định')}</div>
                        <div class="management-meta"><strong>Trạng thái:</strong> ${escapeHtml(getSubmissionSummary(sub))}</div>
                    </div>
                    <div class="management-controls" style="justify-content:flex-start; margin-top:8px;">
                        <div style="width:100%;">
                            <div class="management-meta"><strong>Code đã nộp:</strong></div>
                            <pre style="white-space:pre-wrap; word-break:break-word; background:#f8f9fa; padding:10px; border-radius:6px; margin-top:6px;">${escapeHtml(sub.code || '')}</pre>
                            ${sub.compile_status ? `<div class="management-meta"><strong>Kết quả biên dịch:</strong> ${sub.compile_status.success ? 'Thành công' : 'Thất bại'}</div>` : ''}
                            ${Array.isArray(sub.test_results) && sub.test_results.length ? `<div class="management-meta"><strong>Chi tiết testcase:</strong></div>${sub.test_results.map((test, index) => `<div class="management-meta" style="margin-top:6px;"><strong>${index + 1}. ${test.passed ? '✅' : '❌'} ${escapeHtml(test.name || `Testcase ${index + 1}`)}:</strong><br>Input: ${escapeHtml(test.input || '')}<br>Expected: ${escapeHtml(test.expected_output || '')}<br>Actual: ${escapeHtml(test.actual_output || '')}</div>`).join('')}` : ''}
                            ${sub.run_output ? `<div class="management-meta"><strong>Output:</strong> ${escapeHtml(sub.run_output)}</div>` : ''}
                        </div>
                    </div>
                </div>
            `).join('') : '<div class="empty">Học sinh này chưa có bài làm nào.</div>'}
        </div>
    `;
}

async function requestJson(path, body = null, method = null) {
    const requestMethod = method || (body ? 'POST' : 'GET');
    const options = { method: requestMethod, headers: { 'Content-Type': 'application/json' }, credentials: 'include' };
    if (body && requestMethod !== 'GET') {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    return response.json();
}

function formatCompileResult(result) {
    if (result.success) {
        return `<strong>✅ Biên dịch thành công</strong>`;
    }
    return `<strong>❌ Biên dịch thất bại</strong>${result.error ? `<br>${escapeHtml(result.error)}` : ''}`;
}

function formatRunResult(result) {
    const testcaseSummary = result.total_count ? `<div><strong>📊 Tiến độ testcase:</strong> ${result.passed_count ?? 0}/${result.total_count}</div>` : '';
    const detailRows = (result.test_results || []).map((item, index) => {
        const statusLabel = item.passed ? '✅ Đúng' : '❌ Sai';
        const expected = item.expected_output ?? '';
        const actual = item.actual_output ?? '';
        const detailParts = [];
        if (expected) detailParts.push(`<div><strong>Expected:</strong> ${escapeHtml(expected)}</div>`);
        if (actual) detailParts.push(`<div><strong>Actual:</strong> ${escapeHtml(actual)}</div>`);
        return `
            <div class="mt-2 border rounded p-2">
                <div><strong>Test ${index + 1}:</strong> ${statusLabel}</div>
                ${detailParts.join('')}
            </div>
        `;
    }).join('');
    if (result.success) {
        return `<strong>▶ Chạy testcase hoàn tất</strong><br>${testcaseSummary}${detailRows}`;
    }
    return `<strong>❌ Chạy testcase thất bại</strong><br>${escapeHtml(result.error || '')}`;
}

function formatAnalyzeResult(result) {
    const parts = [];
    if (result.classification) {
        parts.push(`<strong>🔎 Phân loại lỗi:</strong> ${escapeHtml(result.classification.bug_type_name || result.classification.bug_type_id || 'Unknown')}`);
    }
    if (result.ai_analysis) {
        parts.push(`<strong>💡 Gợi ý sửa:</strong><br>${escapeHtml(result.ai_analysis)}`);
    }
    if (result.errors && result.errors.length) {
        parts.push(`<strong>⚠️ Lỗi phát hiện:</strong><br>${result.errors.map(err => `• ${escapeHtml(err)}`).join('<br>')}`);
    }
    return parts.join('<br><br>') || 'Không có kết quả phân tích.';
}

function handleClear() {
    const codeEditor = document.getElementById('codeEditor');
    const resultsContainer = document.getElementById('resultsContainer');
    if (codeEditor) {
        codeEditor.value = '';
    }
    if (resultsContainer) {
        resultsContainer.innerHTML = '<div class="empty">Kết quả biên dịch, chạy testcase và gợi ý từ AI sẽ hiển thị tại đây.</div>';
    }
}

function showResult(message, type = 'result') {
    const container = document.getElementById('resultsContainer');
    if (!container) return;
    const classes = { error: 'error', success: 'success', info: 'info', result: '' };
    container.className = `card-body results ${classes[type]}`.trim();
    container.innerHTML = message;
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function getSubmissionSummary(sub) {
    const passedCount = Number(sub?.passed_count ?? (Array.isArray(sub?.test_results) ? sub.test_results.filter((t) => t && t.passed).length : 0));
    const totalCount = Number(sub?.total_count ?? (Array.isArray(sub?.test_results) ? sub.test_results.length : 0));
    if (sub?.compile_status && sub.compile_status.success === false) {
        return 'Lỗi biên dịch';
    }
    if (totalCount) {
        return `Đã vượt ${passedCount}/${totalCount} testcase`;
    }
    return 'Đã chạy';
}

function roleLabel(role) {
    return {'admin': 'Admin', 'giaovien': 'Giáo viên', 'hoc_sinh': 'Học sinh'}[role] || 'Học sinh';
}

async function logout() {
    await fetch(`${API_BASE_URL}/auth/logout`, { method: 'POST', credentials: 'include' });
    window.location.href = 'auth.html';
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
        const editor = document.getElementById('codeEditor');
        if (editor) editor.value = e.target.result;
    };
    reader.readAsText(file);
}
