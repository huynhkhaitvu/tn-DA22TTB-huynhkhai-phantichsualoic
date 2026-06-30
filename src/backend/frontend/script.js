// API Configuration: use relative path so requests are same-origin
const API_BASE_URL = '/api';
let currentProblem = null;
let currentTestcases = [];
let currentUser = null;
let availableProblems = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    checkUserAuthAndRedirect();
    initializeEventListeners();
    renderTestCases();
    checkBackendConnection();
    checkUserAuth();
    loadProblems();
    loadStudentSubmissionHistory();
    setupLogout();
});

// Check backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend connected');
        }
    } catch (error) {
        console.warn('⚠️ Backend not available yet. Start backend with: python app.py');
    }
}

// Event Listeners
function initializeEventListeners() {
    const compileBtn = document.getElementById('compileBtn');
    if (compileBtn) compileBtn.addEventListener('click', handleCompile);

    const runBtn = document.getElementById('runBtn');
    if (runBtn) runBtn.addEventListener('click', handleRun);

    const helpBtn = document.getElementById('helpBtn');
    if (helpBtn) helpBtn.addEventListener('click', handleHelp);

    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) clearBtn.addEventListener('click', handleClear);

    const requirementsAnalyzeBtn = document.getElementById('requirementsAnalyzeBtn');
    if (requirementsAnalyzeBtn) {
        requirementsAnalyzeBtn.addEventListener('click', handleRequirementsAnalyze);
    }

    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) clearBtn.addEventListener('click', handleClear);

    const addTestCaseBtn = document.getElementById('addTestCaseBtn');
    if (addTestCaseBtn) addTestCaseBtn.addEventListener('click', handleAddTestCase);

    const problemSelect = document.getElementById('problemSelect');
    if (problemSelect) {
        problemSelect.addEventListener('change', (event) => loadProblemDetails(event.target.value));
    }

    const createProblemBtn = document.getElementById('createProblemBtn');
    if (createProblemBtn) createProblemBtn.addEventListener('click', handleCreateProblem);

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

    const addTestcaseBtn = document.getElementById('addTestcaseBtn');
    if (addTestcaseBtn) addTestcaseBtn.addEventListener('click', handleAddTestcase);

    const deleteProblemBtn = document.getElementById('deleteProblemBtn');
    if (deleteProblemBtn) deleteProblemBtn.addEventListener('click', handleDeleteProblem);

    const submitTestcaseBtn = document.getElementById('submitTestcaseBtn');
    if (submitTestcaseBtn) submitTestcaseBtn.addEventListener('click', handleAddTestcase);

    const openBtn = document.getElementById('openFileBtn');
    const fileInput = document.getElementById('fileInput');
    if (openBtn && fileInput) {
        openBtn.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
    }

    document.querySelectorAll('.management-menu .menu-item, .management-menu .menu-submenu a').forEach((item) => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelectorAll('.management-menu .menu-item, .management-menu .menu-submenu a').forEach((link) => {
                link.classList.remove('active');
            });
            item.classList.add('active');

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

// Handle file selection: read first file and put into editor
function handleFileSelect(event) {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    const file = files[0];
    const maxSize = 1024 * 1024; // 1MB limit
    const fileNameDisplay = document.getElementById('fileNameDisplay');

    if (file.size > maxSize) {
        showError('File quá lớn (tối đa 1MB)');
        event.target.value = '';
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        document.getElementById('codeEditor').value = text;
        if (fileNameDisplay) fileNameDisplay.textContent = file.name;
        showSuccess('Đã tải file vào trình soạn thảo');
    };
    reader.onerror = function() {
        showError('Không thể đọc file');
    };
    reader.readAsText(file);
}

// Get code
function getCode() {
    return document.getElementById('codeEditor').value;
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

function resetProblemForm() {
    currentProblem = null;
    currentTestcases = [];
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
    const container = document.getElementById('testCasesContainer');
    if (container) {
        container.innerHTML = '<div class="empty">Chưa có testcase nào.</div>';
    }
}

function openRequirementsModal() {
    const modalElement = document.getElementById('requirementsModal');
    if (!modalElement) {
        showError('Không tìm thấy hộp nhập đề bài');
        return;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.show();
    setTimeout(() => {
        const input = document.getElementById('requirementsInput');
        if (input) input.focus();
    }, 150);
}

async function handleRequirementsAnalyze() {
    const requirements = document.getElementById('requirementsInput')?.value.trim() || '';
    if (!requirements) {
        showError('Vui lòng nhập đề bài trước khi phân tích');
        return;
    }

    const modalElement = document.getElementById('requirementsModal');
    if (modalElement) {
        const modal = bootstrap.Modal.getInstance(modalElement);
        if (modal) modal.hide();
    }

    await handleAnalyze(requirements);
}

async function loadProblems() {
    try {
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
            return;
        }
        availableProblems.forEach(problem => {
            const option = document.createElement('option');
            option.value = problem.id;
            option.textContent = problem.tieu_de;
            select.appendChild(option);
        });
        const initialId = availableProblems[0].id;
        select.value = initialId;
        renderTeacherProblemList(availableProblems, initialId);
        await loadProblemDetails(initialId);
    } catch (error) {
        console.error('Load problems error:', error);
    }
}

async function loadProblemDetails(problemId) {
    try {
        const response = await fetch(`${API_BASE_URL}/problems/${problemId}`);
        const data = await response.json();
        currentProblem = data.problem;
        renderTeacherProblemList(availableProblems, problemId);
        const problemTestcases = Array.isArray(data.problem?.testcases) ? data.problem.testcases : [];
        const listProblem = availableProblems.find(item => String(item.id) === String(problemId));
        const fallbackTestcases = Array.isArray(listProblem?.testcases) ? listProblem.testcases : [];
        currentTestcases = (problemTestcases.length ? problemTestcases : fallbackTestcases).map(tc => ({
            id: tc.id,
            input: tc.input_data || tc.input || '',
            expected_output: tc.expected_output || tc.expectedOutput || ''
        }));
        const details = document.getElementById('problemDetails');
        if (!details) return;
        if (!currentProblem) {
            details.innerHTML = '<div class="empty">Vui lòng chọn một đề bài để xem chi tiết.</div>';
            return;
        }
        const difficultyMap = { easy: 'Dễ', medium: 'Trung bình', hard: 'Khó' };
        const difficultyLabel = difficultyMap[currentProblem?.do_kho] || 'Trung bình';
        const testcaseCount = currentTestcases.length;
        details.innerHTML = `
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
                    <div class="fw-semibold">${escapeHtml(currentProblem?.tieu_de || '')}</div>
                </div>
            </div>
            <div class="problem-meta-box">
                <span class="problem-meta-label">Mô tả</span>
                <p>${escapeHtml(currentProblem?.mo_ta || 'Chưa có mô tả cho đề bài này.')}</p>
            </div>
            <div class="problem-meta-box">
                <span class="problem-meta-label">Yêu cầu</span>
                <p>${escapeHtml(currentProblem?.yeu_cau || 'Chưa có yêu cầu chi tiết.')}</p>
            </div>
        `;

        const titleInput = document.getElementById('problemTitle');
        const descriptionInput = document.getElementById('problemDescription');
        const requirementsInput = document.getElementById('problemRequirements');
        const standardCodeInput = document.getElementById('problemStandardCode');
        const difficultySelect = document.getElementById('problemDifficulty');
        if (titleInput) titleInput.value = currentProblem?.tieu_de || '';
        if (descriptionInput) descriptionInput.value = currentProblem?.mo_ta || '';
        if (requirementsInput) requirementsInput.value = currentProblem?.yeu_cau || '';
        if (standardCodeInput) standardCodeInput.value = currentProblem?.ma_chuan || '';
        if (difficultySelect) difficultySelect.value = currentProblem?.do_kho || 'medium';

        const container = document.getElementById('testCasesContainer');
        if (container) {
            if (!currentTestcases.length) {
                container.innerHTML = '<div class="empty">Chưa có testcase nào.</div>';
            } else {
                container.innerHTML = currentTestcases.map((tc, index) => `
                    <div class="testcase-card">
                        <div class="d-flex justify-content-between align-items-start">
                            <strong>Testcase ${index + 1}</strong>
                            <button class="btn btn-outline-danger btn-sm" type="button" onclick="deleteTestcase(${tc.id})">Xóa</button>
                        </div>
                        <p><strong>Input:</strong><br>${escapeHtml(tc.input || '')}</p>
                        <p><strong>Expected:</strong><br>${escapeHtml(tc.expected_output || '')}</p>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Load problem details error:', error);
    }
}

// Get test cases
function getTestCases() {
    const testCases = [];
    const testElements = document.querySelectorAll('.test-case');
    testElements.forEach(el => {
        const input = el.querySelector('.test-input').value;
        const output = el.querySelector('.test-output').value;
        if (input || output) {
            testCases.push({
                input: input,
                expected_output: output
            });
        }
    });
    return testCases;
}

// Handle Compile
async function handleCompile() {
    const code = getCode();
    if (!code.trim()) {
        showError('Vui lòng nhập mã C');
        return;
    }

    showLoading('compileSpinner');
    try {
        const testcases = currentTestcases.length ? currentTestcases : getTestCases();
        const response = await fetch(`${API_BASE_URL}/compile`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, problem_id: currentProblem?.id || null, testcases })
        });

        const data = await response.json();
        hideLoading('compileSpinner');

        if (data.success) {
            showSuccess('✓ Biên dịch thành công');
            showCompileResult(data);
        } else {
            showError(data.error || 'Biên dịch thất bại');
            showCompileResult(data);
        }
        await loadStudentSubmissionHistory();
    } catch (error) {
        hideLoading('compileSpinner');
        showError('Lỗi kết nối: ' + error.message);
    }
}

function showCompileResult(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;

    let html = '';
    const testcaseSummary = data.total_count ? `<div class="mb-2"><strong>📊 Testcase:</strong> ${data.passed_count ?? 0}/${data.total_count}</div>` : '';
    const detailRows = (data.test_results || []).map((item, index) => {
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
    if (data.success) {
        html = `
            <div class="alert alert-success alert-custom">✓ Biên dịch thành công</div>
            ${data.message ? `<div class="mb-2"><strong>Thông báo:</strong> ${escapeHtml(data.message)}</div>` : ''}
            ${testcaseSummary}
            ${detailRows ? `<div class="mt-3">${detailRows}</div>` : ''}
            ${data.executable ? `<div><strong>Executable:</strong> ${escapeHtml(data.executable)}</div>` : ''}
            ${data.output ? `<pre class="mt-3 p-3 bg-dark text-light rounded">${escapeHtml(data.output)}</pre>` : ''}
        `;
    } else {
        html = `
            <div class="alert alert-danger alert-custom">✗ Biên dịch thất bại</div>
            ${data.error ? `<pre class="mt-3 p-3 bg-dark text-light rounded">${escapeHtml(data.error)}</pre>` : ''}
            ${data.output ? `<pre class="mt-3 p-3 bg-dark text-light rounded">${escapeHtml(data.output)}</pre>` : ''}
        `;
    }

    resultsContainer.innerHTML = html;
}

async function handleRun() {
    const code = getCode();
    if (!code.trim()) {
        showError('Vui lòng nhập mã C');
        return;
    }

    const testCases = getTestCases();
    const inputData = testCases.length > 0 ? (testCases[0].input || '') : '';

    showLoading('runSpinner');
    try {
        const response = await fetch(`${API_BASE_URL}/run`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, input: inputData })
        });

        const data = await response.json();
        hideLoading('runSpinner');

        showRunResult(data);
        if (data.success) {
            showSuccess('✓ Chạy chương trình thành công');
        } else {
            showError(data.error || 'Chạy chương trình thất bại');
        }
        await loadStudentSubmissionHistory();
    } catch (error) {
        hideLoading('runSpinner');
        showError('Lỗi kết nối: ' + error.message);
    }
}

function showRunResult(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;

    let html = '';
    if (data.success) {
        html = `
            <div class="alert alert-success alert-custom">✓ Chạy chương trình thành công</div>
            ${data.output ? `<div class="mb-2"><strong>Output:</strong></div><pre class="mt-2 p-3 bg-dark text-light rounded">${escapeHtml(data.output)}</pre>` : '<div class="text-muted">Chương trình không in ra gì.</div>'}
            ${data.error ? `<div class="mt-3"><strong>Stderr:</strong><pre class="mt-2 p-3 bg-dark text-light rounded">${escapeHtml(data.error)}</pre></div>` : ''}
        `;
    } else {
        html = `
            <div class="alert alert-danger alert-custom">✗ Chạy chương trình thất bại</div>
            ${data.error ? `<div class="mb-2"><strong>Lỗi:</strong></div><pre class="mt-2 p-3 bg-dark text-light rounded">${escapeHtml(data.error)}</pre>` : ''}
            ${data.compile_output ? `<div class="mt-3"><strong>Compile output:</strong><pre class="mt-2 p-3 bg-dark text-light rounded">${escapeHtml(data.compile_output)}</pre></div>` : ''}
        `;
    }

    resultsContainer.innerHTML = html;
}

function escapeHtml(text) {
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
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

async function handleHelp() {
    const code = getCode();
    if (!code.trim()) {
        showError('Vui lòng nhập mã C trước khi nhận gợi ý.');
        return;
    }

    const resultsContainer = document.getElementById('resultsContainer');
    const latestText = resultsContainer?.textContent || '';
    const passedAll = /\b(\d+)\/(\d+)\b/.exec(latestText);
    if (passedAll && Number(passedAll[1]) > 0 && Number(passedAll[1]) === Number(passedAll[2])) {
        resultsContainer.innerHTML = '<div class="suggestion-box mt-3"><h6>✅ Kết quả</h6><div class="suggestion-text">Mã của bạn đã đúng. Không cần gợi ý thêm vì đã vượt qua tất cả testcase.</div></div>';
        return;
    }

    try {
        const aiProviderEl = document.getElementById('aiProviderSelect');
        const aiProvider = aiProviderEl ? aiProviderEl.value : 'gemini';
        const response = await fetch(`${API_BASE_URL}/suggestions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code,
                error_message: latestText,
                output: '',
                ai_provider: aiProvider
            })
        });

        const data = await response.json();
        const message = data.suggestions || data.error || 'Không có gợi ý từ AI.';
        document.getElementById('resultsContainer').innerHTML = `<div class="suggestion-box mt-3"><h6>💡 Gợi ý từ AI:</h6><div class="suggestion-text" style="white-space: pre-wrap; word-wrap: break-word;">${escapeHtml(message)}</div></div>`;
    } catch (error) {
        showError('Lỗi kết nối: ' + error.message);
    }
}

// Handle Analyze
async function handleAnalyze(requirements = '') {
    const code = getCode();
    const testcases = getTestCases();

    if (!code.trim()) {
        showError('Vui lòng nhập mã C');
        return;
    }

    showLoading('analyzeSpinner');
    try {
        const aiProviderEl = document.getElementById('aiProviderSelect');
        const aiProvider = aiProviderEl ? aiProviderEl.value : 'gemini';

        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code, testcases, requirements, ai_provider: aiProvider })
        });

        const data = await response.json();
        hideLoading('analyzeSpinner');

        let resultHTML = '';

        // Compile status
        if (data.compile_status) {
            if (data.compile_status.success) {
                resultHTML += '<div class="alert alert-success alert-custom">✓ Biên dịch thành công</div>';
            } else {
                resultHTML += '<div class="alert alert-error alert-custom">';
                resultHTML += '<strong>Lỗi biên dịch:</strong>';
                resultHTML += `<div class="error-details">${escapeHtml(data.compile_status.error)}</div>`;
                resultHTML += '</div>';
            }
        }

        // Test results - HIDDEN (only for backend processing)
        // if (data.test_results && data.test_results.length > 0) {
        //     resultHTML += '<h6 class="mt-3">Test Results:</h6>';
        //     data.test_results.forEach((test, idx) => {
        //         const status = test.passed ? '✓ PASS' : '✗ FAIL';
        //         const statusClass = test.passed ? 'passed' : 'failed';
        //         resultHTML += `<div class="test-case-result ${statusClass}">`;
        //         resultHTML += `<strong>Test ${idx + 1}: ${status}</strong><br>`;
        //         resultHTML += `Input: ${escapeHtml(test.input)}<br>`;
        //         resultHTML += `Expected: ${escapeHtml(test.expected)}<br>`;
        //         resultHTML += `Actual: ${escapeHtml(test.actual)}`;
        //         resultHTML += '</div>';
        //     });
        // }

        // AI Suggestions
        // AI Suggestions / Classification
            if (data.classification) {
                const cls = data.classification;
                // Show localized Vietnamese name if provided by backend
                const name = cls.bug_type_name || cls.bug_type_id || 'Unknown';
                resultHTML += '<div class="suggestion-box mt-3">';
                resultHTML += '<h6>🔎 Phân loại lỗi (AI):</h6>';
                resultHTML += `<div class="suggestion-text"><strong>${escapeHtml(name)}</strong></div>`;
                resultHTML += '</div>';
            }

        if (data.ai_analysis) {
            resultHTML += '<div class="suggestion-box mt-3">';
            resultHTML += '<h6>💡 Phân tích & Gợi ý sửa (AI):</h6>';
            // Format with line breaks and preserve whitespace for better readability
            const formattedAnalysis = escapeHtml(data.ai_analysis)
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');
            resultHTML += `<div class="suggestion-text" style="white-space: pre-wrap; word-wrap: break-word;"><p>${formattedAnalysis}</p></div>`;
            resultHTML += '</div>';
        } else if (data.ai_suggestions) {
            resultHTML += '<div class="suggestion-box mt-3">';
            resultHTML += '<h6>💡 Gợi ý từ AI:</h6>';
            const formattedSuggestions = escapeHtml(data.ai_suggestions)
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');
            resultHTML += `<div class="suggestion-text" style="white-space: pre-wrap; word-wrap: break-word;"><p>${formattedSuggestions}</p></div>`;
            resultHTML += '</div>';
        }

        if (!resultHTML.trim()) {
            resultHTML = '<p class="text-muted">Không có kết quả</p>';
        }

        document.getElementById('resultsContainer').innerHTML = resultHTML;

    } catch (error) {
        hideLoading('analyzeSpinner');
        showError('Lỗi kết nối: ' + error.message);
    }
}

async function deleteTestcase(testcaseId) {
    if (!testcaseId || !confirm('Bạn có chắc chắn muốn xóa testcase này?')) return;
    try {
        const result = await requestJson(`/testcases/${testcaseId}`, null, 'DELETE');
        showSuccess(result.success ? 'Đã xóa testcase.' : (result.error || 'Không thể xóa testcase'));
        if (result.success && currentProblem?.id) {
            await loadProblemDetails(currentProblem.id);
        }
    } catch (error) {
        showError('Lỗi khi xóa testcase: ' + error.message);
    }
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
        showError('Vui lòng nhập tiêu đề và yêu cầu đề bài.');
        return;
    }

    try {
        const result = await requestJson('/problems', { title, description, requirements, standard_code: standardCode, difficulty }, 'POST');
        if (result.success) {
            showSuccess('✅ Tạo đề tài thành công.');
            if (titleInput) titleInput.value = '';
            if (descriptionInput) descriptionInput.value = '';
            if (requirementsInput) requirementsInput.value = '';
            if (standardCodeInput) standardCodeInput.value = '';
            if (difficultyInput) difficultyInput.value = 'medium';
            await loadProblems();
        } else {
            showError(result.error || 'Không thể tạo đề tài.');
        }
    } catch (error) {
        showError('Lỗi khi tạo đề tài: ' + error.message);
    }
}

// Handle Add Test Case
async function handleDeleteProblem() {
    if (!currentProblem?.id) {
        showError('Vui lòng chọn đề bài trước.');
        return;
    }
    if (!confirm(`Xóa đề bài "${currentProblem.tieu_de}"?`)) return;
    try {
        const result = await requestJson(`/problems/${currentProblem.id}`, null, 'DELETE');
        if (result.success) {
            showSuccess('Đã xóa đề bài.');
            await loadProblems();
        } else {
            showError(result.error || 'Không thể xóa đề bài.');
        }
    } catch (error) {
        showError('Lỗi khi xóa đề bài: ' + error.message);
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
        showError('Vui lòng chọn đề bài trước.');
        return;
    }

    const name = nameInput?.value.trim() || '';
    const inputData = inputInput?.value.trim() || '';
    const expectedOutput = outputInput?.value.trim() || '';

    if (!inputData || !expectedOutput) {
        showError('Vui lòng nhập input và expected output.');
        return;
    }

    try {
        const result = await requestJson(`/problems/${currentProblem.id}/testcases`, {
            name,
            input_data: inputData,
            expected_output: expectedOutput
        }, 'POST');

        if (result.success) {
            showSuccess('Đã thêm testcase mới.');
            if (nameInput) nameInput.value = '';
            if (inputInput) inputInput.value = '';
            if (outputInput) outputInput.value = '';
            if (form) form.style.display = 'none';
            if (addButton) addButton.textContent = '+ Thêm Test Case';
            await loadProblemDetails(currentProblem.id);
        } else {
            showError(result.error || 'Không thể thêm testcase.');
        }
    } catch (error) {
        showError('Lỗi khi thêm testcase: ' + error.message);
    }
}

// Handle Clear
function handleClear() {
    if (confirm('Bạn có chắc chắn muốn xóa mã?')) {
        const codeEditor = document.getElementById('codeEditor');
        const resultsContainer = document.getElementById('resultsContainer');
        if (codeEditor) codeEditor.value = '';
        if (resultsContainer) resultsContainer.innerHTML = '<p class="text-muted">Kết quả sẽ hiển thị tại đây...</p>';
    }
}

// Render test cases
function renderTestCases() {
    // Mặc định có 1 test case trống
    handleAddTestCase();
}

// Show/Hide Loading
function showLoading(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('d-none');
}

function hideLoading(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('d-none');
}

// Show Messages
function showSuccess(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    const html = `<div class="alert alert-success alert-custom">${message}</div>`;
    resultsContainer.innerHTML = html + resultsContainer.innerHTML;
}

function showError(message) {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) return;
    const html = `<div class="alert alert-error alert-custom"><strong>Lỗi:</strong> ${escapeHtml(message)}</div>`;
    resultsContainer.innerHTML = html + resultsContainer.innerHTML;
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

    const role = String(currentUser?.role || '').toLowerCase();
    if (!currentUser || role !== 'giaovien') {
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
    try {
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
    } catch (error) {
        console.error('Load admin users error:', error);
    }
}

async function updateUserRole(userId) {
    const select = document.getElementById(`role-${userId}`);
    if (!select) return;
    const result = await requestJson(`/admin/users/${userId}/role`, { role: select.value }, 'POST');
    showSuccess(result.success ? 'Đã cập nhật vai trò.' : (result.error || 'Không thể cập nhật'));
    if (result.success) {
        await loadAdminUsers();
    }
}

async function deleteUser(userId) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) return;
    const result = await requestJson(`/admin/users/${userId}`, null, 'DELETE');
    showSuccess(result.success ? 'Đã xóa tài khoản.' : (result.error || 'Không thể xóa tài khoản'));
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

function roleLabel(role) {
    return {'admin': 'Admin', 'giaovien': 'Giáo viên', 'hoc_sinh': 'Học sinh'}[role] || 'Học sinh';
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Check User Authentication
// Check authentication and redirect if not logged in
async function checkUserAuthAndRedirect() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (!data.authenticated) {
            // Not logged in, redirect to login page
            window.location.href = 'auth.html';
        }
    } catch (error) {
        console.error('Auth check error:', error);
        // On error, redirect to login to be safe
        window.location.href = 'auth.html';
    }
}

async function checkUserAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/check`, {
            credentials: 'include'
        });
        const data = await response.json();
        const loginLink = document.getElementById('loginLink');
        const userDisplay = document.getElementById('userDisplay');
        const username = document.getElementById('username');
        const logoutBtn = document.getElementById('logoutBtn');
        const roleDisplay = document.getElementById('roleDisplay');
        const teacherPanel = document.getElementById('teacherPanel');
        const adminPanel = document.getElementById('adminPanel');
        const heroCard = document.getElementById('heroCard');
        const studentProblemSection = document.getElementById('studentProblemSection');
        const inputSection = document.getElementById('studentInputSection');
        const testcaseSection = document.getElementById('studentTestcaseSection');
        const workspaceSection = document.getElementById('workspaceSection');
        const role = String(data.role || '').toLowerCase();
        const isTeacherOrAdmin = ['admin', 'giaovien'].includes(role);
        const isStudent = role === 'hoc_sinh';
        const deleteProblemBtn = document.getElementById('deleteProblemBtn');

        if (data.authenticated) {
            currentUser = data;
            if (loginLink) loginLink.style.display = 'none';
            if (userDisplay) userDisplay.style.display = 'inline';
            if (username) username.textContent = data.username;
            if (roleDisplay) roleDisplay.textContent = roleLabel(data.role || 'hoc_sinh');
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            if (teacherPanel) teacherPanel.style.display = isTeacherOrAdmin ? 'block' : 'none';
            if (adminPanel) adminPanel.style.display = role === 'admin' ? 'block' : 'none';
            if (heroCard) heroCard.style.display = isStudent ? 'block' : 'none';
            if (studentProblemSection) studentProblemSection.style.display = isStudent ? 'block' : 'none';
            if (deleteProblemBtn) deleteProblemBtn.style.display = role === 'admin' ? 'block' : 'none';
            if (inputSection) inputSection.style.display = isTeacherOrAdmin ? 'block' : 'none';
            if (testcaseSection) testcaseSection.style.display = isTeacherOrAdmin ? 'block' : 'none';
            if (workspaceSection) workspaceSection.style.display = isTeacherOrAdmin ? 'none' : 'block';
            if (role === 'giaovien') {
                await loadTeacherStudents();
            }
        } else {
            if (loginLink) loginLink.style.display = 'inline-block';
            if (userDisplay) userDisplay.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking auth:', error);
    }
}

// Setup Logout
function setupLogout() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function() {
            try {
                const response = await fetch(`${API_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    credentials: 'include'
                });
                const data = await response.json();
                
                if (data.success) {
                    // Redirect to login page
                    window.location.href = 'auth.html';
                }
            } catch (error) {
                console.error('Logout error:', error);
            }
        });
    }
}
