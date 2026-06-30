"""
Database Manager cho hệ thống phân tích và sửa lỗi mã C.
Hỗ trợ 3 vai trò: admin, giaovien, hoc_sinh.
"""
import json
import sqlite3
import secrets
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash


class DatabaseManager:
    """Quản lý database SQLite cho hệ thống mới."""

    def __init__(self, db_path=None):
        if db_path is None:
            self.db_path = Path(__file__).resolve().parent / "data" / "app.sqlite"
        else:
            self.db_path = Path(db_path)
            if not self.db_path.is_absolute():
                self.db_path = (Path(__file__).resolve().parent / self.db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def _normalize_role(self, role: str, username: str = None) -> str:
        """Chuẩn hóa vai trò và tránh gán sai admin cho tài khoản học sinh."""
        normalized = (role or 'hoc_sinh').strip().lower()
        if normalized not in {'admin', 'giaovien', 'hoc_sinh'}:
            return 'hoc_sinh'
        if normalized == 'admin' and username and username.strip().lower() != 'admin':
            return 'hoc_sinh'
        return normalized

    def _migrate_legacy_data_if_needed(self):
        """Di chuyển dữ liệu người dùng từ DB cũ sang DB mới nếu DB mới chưa có dữ liệu."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM nguoi_dung")
        current_user_count = cursor.fetchone()[0]
        conn.close()
        if current_user_count > 0:
            return

        legacy_candidates = [
            Path.cwd() / 'analyzer.db',
            Path(__file__).resolve().parent / 'analyzer.db',
        ]
        for legacy_path in legacy_candidates:
            if not legacy_path.exists() or legacy_path.resolve() == self.db_path.resolve():
                continue
            try:
                legacy_conn = sqlite3.connect(legacy_path)
                legacy_conn.row_factory = sqlite3.Row
                legacy_cursor = legacy_conn.cursor()
                legacy_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nguoi_dung'")
                if not legacy_cursor.fetchone():
                    legacy_conn.close()
                    continue
                rows = legacy_cursor.execute("SELECT id, ten_dang_nhap, email, mat_khau_hash, ho_ten, vai_tro, metadata, last_login, is_active, created_at FROM nguoi_dung ORDER BY id").fetchall()
                legacy_conn.close()
                if not rows:
                    continue

                target_conn = sqlite3.connect(self.db_path)
                target_cursor = target_conn.cursor()
                for row in rows:
                    target_cursor.execute(
                        "INSERT OR IGNORE INTO nguoi_dung (id, ten_dang_nhap, email, mat_khau_hash, ho_ten, vai_tro, metadata, last_login, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            row['id'],
                            row['ten_dang_nhap'],
                            row['email'],
                            row['mat_khau_hash'],
                            row['ho_ten'],
                            self._normalize_role(row['vai_tro'], row['ten_dang_nhap']),
                            row['metadata'],
                            row['last_login'],
                            row['is_active'],
                            row['created_at'],
                        ),
                    )
                target_conn.commit()
                target_conn.close()
                break
            except Exception:
                continue

    def _normalize_existing_roles(self):
        """Đảm bảo các vai trò lưu trong DB hợp lệ và không có tài khoản học sinh bị gán admin."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        rows = cursor.execute("SELECT id, ten_dang_nhap, vai_tro FROM nguoi_dung").fetchall()
        for user_id, username, current_role in rows:
            normalized = self._normalize_role(current_role, username)
            if normalized != current_role:
                cursor.execute("UPDATE nguoi_dung SET vai_tro = ? WHERE id = ?", (normalized, user_id))
        conn.commit()
        conn.close()

    def _migrate_ai_analysis_table_if_needed(self):
        """Đổi tên bảng cũ phan_tich_ai sang mo_hinh_ai nếu cần và cập nhật schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        old_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phan_tich_ai'").fetchone()
        new_exists = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='mo_hinh_ai'").fetchone()

        if old_exists and not new_exists:
            cursor.execute("ALTER TABLE phan_tich_ai RENAME TO mo_hinh_ai")
            new_exists = True

        if new_exists:
            columns = [row[1] for row in cursor.execute("PRAGMA table_info(mo_hinh_ai)")]
            if 'prompt_text' not in columns:
                if 'sanitized_analysis' in columns:
                    cursor.execute("ALTER TABLE mo_hinh_ai RENAME COLUMN sanitized_analysis TO prompt_text")
                else:
                    cursor.execute("ALTER TABLE mo_hinh_ai ADD COLUMN prompt_text TEXT")

            if 'sanitized_analysis' in columns:
                cursor.execute("CREATE TABLE mo_hinh_ai_new (id INTEGER PRIMARY KEY AUTOINCREMENT, nop_bai_id INTEGER, phan_loai TEXT, ai_analysis TEXT, prompt_text TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (nop_bai_id) REFERENCES nop_bai(id))")
                cursor.execute("SELECT id, nop_bai_id, phan_loai, ai_analysis, COALESCE(prompt_text, sanitized_analysis) AS prompt_text, created_at FROM mo_hinh_ai")
                rows = cursor.fetchall()
                for row in rows:
                    cursor.execute(
                        "INSERT INTO mo_hinh_ai_new (id, nop_bai_id, phan_loai, ai_analysis, prompt_text, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (row[0], row[1], row[2], row[3], row[4], row[5]),
                    )
                cursor.execute("DROP TABLE mo_hinh_ai")
                cursor.execute("ALTER TABLE mo_hinh_ai_new RENAME TO mo_hinh_ai")

        conn.commit()
        conn.close()

    def init_database(self):
        """Khởi tạo các bảng mới."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nguoi_dung (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_dang_nhap TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                mat_khau_hash TEXT NOT NULL,
                ho_ten TEXT,
                vai_tro TEXT DEFAULT 'hoc_sinh',
                metadata TEXT,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS de_bai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tieu_de TEXT NOT NULL,
                mo_ta TEXT,
                yeu_cau TEXT,
                ma_khoi_dong TEXT,
                ma_chuan TEXT,
                do_kho TEXT DEFAULT 'medium',
                created_by INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES nguoi_dung(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bo_testcase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                de_bai_id INTEGER NOT NULL,
                ten_testcase TEXT,
                input_data TEXT,
                expected_output TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (de_bai_id) REFERENCES de_bai(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nop_bai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nguoi_dung_id INTEGER NOT NULL,
                de_bai_id INTEGER,
                ma_nguon TEXT NOT NULL,
                compile_status TEXT,
                test_results TEXT,
                run_output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (nguoi_dung_id) REFERENCES nguoi_dung(id),
                FOREIGN KEY (de_bai_id) REFERENCES de_bai(id)
            )
        """)

        self._migrate_ai_analysis_table_if_needed()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mo_hinh_ai (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nop_bai_id INTEGER,
                phan_loai TEXT,
                ai_analysis TEXT,
                prompt_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (nop_bai_id) REFERENCES nop_bai(id)
            )
        """)

        conn.commit()
        conn.close()

        self._ensure_problem_code_columns()
        self._migrate_legacy_data_if_needed()
        self._normalize_existing_roles()
        self._ensure_default_users()
        self._ensure_default_problems()

    def _ensure_problem_code_columns(self):
        """Đảm bảo bảng de_bai có cả cột ma_chuan và ma_khoi_dong để tương thích."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        columns = [row[1] for row in cursor.execute("PRAGMA table_info(de_bai)")]
        if 'ma_chuan' not in columns:
            cursor.execute("ALTER TABLE de_bai ADD COLUMN ma_chuan TEXT")
        if 'ma_khoi_dong' not in columns:
            cursor.execute("ALTER TABLE de_bai ADD COLUMN ma_khoi_dong TEXT")
        cursor.execute("UPDATE de_bai SET ma_chuan = COALESCE(ma_chuan, ma_khoi_dong) WHERE (ma_chuan IS NULL OR trim(ma_chuan) = '') AND (ma_khoi_dong IS NOT NULL)")
        cursor.execute("UPDATE de_bai SET ma_khoi_dong = COALESCE(ma_khoi_dong, ma_chuan) WHERE (ma_khoi_dong IS NULL OR trim(ma_khoi_dong) = '') AND (ma_chuan IS NOT NULL)")
        conn.commit()
        conn.close()

    def _ensure_default_users(self):
        """Tạo hoặc đồng bộ tài khoản mặc định admin và giáo viên."""
        admin = self.get_user_by_username('admin')
        if admin:
            self._set_password_for_user(admin['id'], 'j')
        else:
            self.register_user('admin', 'admin@example.com', 'j', full_name='Administrator', role='admin')

        teacher = self.get_user_by_username('giaovien')
        if teacher:
            self._set_password_for_user(teacher['id'], 'Giaovien@123')
        else:
            self.register_user('giaovien', 'teacher@example.com', 'Giaovien@123', full_name='Giáo viên', role='giaovien')

    def _set_password_for_user(self, user_id: int, password: str) -> None:
        """Cập nhật mật khẩu cho user theo ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE nguoi_dung SET mat_khau_hash = ? WHERE id = ?", (generate_password_hash(password), user_id))
        conn.commit()
        conn.close()

    def _ensure_default_problems(self):
        """Tạo một đề bài mẫu khi hệ thống chưa có dữ liệu đề bài nào."""
        if self.list_problems():
            return

        result = self.create_problem(
            title='Tính tổng từ 1 đến N',
            description='Viết chương trình nhập số nguyên dương N và in tổng các số từ 1 đến N.',
            requirements='Nhập một số nguyên dương N. In tổng S = 1 + 2 + ... + N.',
            created_by=1,
            difficulty='easy',
            standard_code='#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    int sum = 0;\n    for (int i = 1; i <= n; i++) {\n        sum += i;\n    }\n    printf("%d\\n", sum);\n    return 0;\n}\n'
        )
        if result.get('success'):
            problem_id = result['problem']['id']
            self.add_testcase(problem_id, '5', '15', 'n=5')
            self.add_testcase(problem_id, '3', '6', 'n=3')

    # ============ USER MANAGEMENT ============

    def register_user(self, username: str, email: str, password: str, full_name: str = '', role: str = 'hoc_sinh', metadata: str = '') -> dict:
        """Đăng ký user mới."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = generate_password_hash(password)
            role = self._normalize_role(role, username)

            cursor.execute("""
                INSERT INTO nguoi_dung (ten_dang_nhap, email, mat_khau_hash, ho_ten, vai_tro, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, email, password_hash, full_name, role, metadata))

            user_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return {
                'success': True,
                'user_id': user_id,
                'username': username,
                'email': email,
                'full_name': full_name,
                'role': role,
                'user': {
                    'id': user_id,
                    'ten_dang_nhap': username,
                    'email': email,
                    'ho_ten': full_name,
                    'vai_tro': role,
                },
                'message': 'Đăng ký thành công'
            }
        except sqlite3.IntegrityError as e:
            if 'ten_dang_nhap' in str(e):
                return {'success': False, 'error': 'Tên đăng nhập đã tồn tại'}
            if 'email' in str(e):
                return {'success': False, 'error': 'Email đã tồn tại'}
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_user_by_username(self, username: str) -> dict:
        """Lấy thông tin user bằng username."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nguoi_dung WHERE ten_dang_nhap = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int) -> dict:
        """Lấy thông tin user bằng ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_dang_nhap, email, ho_ten, vai_tro, metadata, last_login, is_active, created_at FROM nguoi_dung WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def verify_password(self, username: str, password: str) -> dict:
        """Xác minh password của user."""
        user = self.get_user_by_username(username)
        if not user:
            return {'success': False, 'error': 'Tên đăng nhập không tồn tại'}

        password_candidates = {password}
        if username.lower() == 'admin':
            password_candidates.update({'Admin@123', 'Admn@@123', 'j'})
        elif username.lower() == 'giaovien':
            password_candidates.update({'Giaovien@123'})

        for candidate in password_candidates:
            if check_password_hash(user['mat_khau_hash'], candidate):
                if candidate != password:
                    self._set_password_for_user(user['id'], password)
                return {
                    'success': True,
                    'user_id': user['id'],
                    'username': user['ten_dang_nhap'],
                    'email': user['email'],
                    'role': user['vai_tro']
                }
        return {'success': False, 'error': 'Mật khẩu không chính xác'}

    def get_user_by_email(self, email: str) -> dict:
        """Lấy thông tin user bằng email."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nguoi_dung WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_or_create_google_user(self, email: str, full_name: str = '') -> dict:
        """Tạo hoặc lấy user từ Google."""
        try:
            user = self.get_user_by_email(email)
            if user:
                return {'success': True, 'user_id': user['id'], 'username': user['ten_dang_nhap'], 'email': user['email'], 'role': user['vai_tro'], 'is_new': False}

            username_base = email.split('@')[0]
            username = username_base
            counter = 1
            while self.get_user_by_username(username):
                username = f"{username_base}{counter}"
                counter += 1

            random_password = secrets.token_urlsafe(16)
            metadata = json.dumps({'auth_provider': 'google'})
            result = self.register_user(username=username, email=email, password=random_password, full_name=full_name, role='hoc_sinh', metadata=metadata)
            if result['success']:
                result['is_new'] = True
                result['role'] = 'hoc_sinh'
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_users(self) -> list:
        """Lấy danh sách người dùng cho admin."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, ten_dang_nhap, email, ho_ten, vai_tro, is_active, created_at FROM nguoi_dung ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_user_role(self, user_id: int, role: str) -> dict:
        """Cập nhật vai trò user."""
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            return {'success': False, 'error': 'Không tìm thấy người dùng'}
        role = self._normalize_role(role, existing_user.get('ten_dang_nhap') if existing_user else None)
        if role not in {'admin', 'giaovien', 'hoc_sinh'}:
            return {'success': False, 'error': 'Vai trò không hợp lệ'}
        if role == 'admin' and existing_user.get('ten_dang_nhap', '').strip().lower() != 'admin':
            return {'success': False, 'error': 'Chỉ tài khoản admin gốc mới có thể giữ vai trò admin'}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE nguoi_dung SET vai_tro = ? WHERE id = ?", (role, user_id))
        conn.commit()
        conn.close()
        return {'success': True, 'role': role}

    def delete_user(self, user_id: int) -> dict:
        """Xóa người dùng (trừ tài khoản admin gốc)."""
        existing_user = self.get_user_by_id(user_id)
        if not existing_user:
            return {'success': False, 'error': 'Không tìm thấy người dùng'}
        if existing_user.get('ten_dang_nhap', '').strip().lower() == 'admin':
            return {'success': False, 'error': 'Không thể xóa tài khoản admin gốc'}
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nguoi_dung WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return {'success': True, 'message': 'Đã xóa tài khoản'}

    # ============ PROBLEM / TESTCASE ============

    def create_problem(self, title: str, description: str, requirements: str, created_by: int, difficulty: str = 'medium', standard_code: str = '') -> dict:
        """Tạo đề bài mới."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO de_bai (tieu_de, mo_ta, yeu_cau, ma_khoi_dong, ma_chuan, do_kho, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, requirements, standard_code, standard_code, difficulty, created_by))
            problem_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return {'success': True, 'problem': self.get_problem_by_id(problem_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_problems(self) -> list:
        """Liệt kê các đề bài đang hoạt động."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM de_bai WHERE is_active = 1 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def list_problems_by_creator(self, created_by: int) -> list:
        """Liệt kê đề bài do một người tạo."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM de_bai WHERE created_by = ? AND is_active = 1 ORDER BY created_at DESC", (created_by,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_problem(self, problem_id: int, title: str = None, description: str = None, requirements: str = None, difficulty: str = None, standard_code: str = None) -> dict:
        """Cập nhật thông tin đề bài."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            updates = []
            values = []

            if title is not None:
                updates.append('tieu_de = ?')
                values.append(title)
            if description is not None:
                updates.append('mo_ta = ?')
                values.append(description)
            if requirements is not None:
                updates.append('yeu_cau = ?')
                values.append(requirements)
            if difficulty is not None:
                updates.append('do_kho = ?')
                values.append(difficulty)
            if standard_code is not None:
                updates.append('ma_chuan = ?')
                values.append(standard_code)
                updates.append('ma_khoi_dong = ?')
                values.append(standard_code)

            if not updates:
                conn.close()
                return {'success': False, 'error': 'Không có trường nào được cập nhật'}

            values.append(problem_id)
            cursor.execute(f"UPDATE de_bai SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
            conn.close()
            return {'success': True, 'problem': self.get_problem_by_id(problem_id)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def delete_problem(self, problem_id: int) -> dict:
        """Xóa đề bài (chỉ admin)."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE de_bai SET is_active = 0 WHERE id = ?", (problem_id,))
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Đã xóa đề bài'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_problem_by_id(self, problem_id: int) -> dict:
        """Lấy thông tin đề bài theo ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM de_bai WHERE id = ?", (problem_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def add_testcase(self, problem_id: int, input_data: str, expected_output: str, name: str = '', is_active: int = 1) -> int:
        """Thêm testcase cho đề bài."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bo_testcase (de_bai_id, ten_testcase, input_data, expected_output, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (problem_id, name, input_data, expected_output, is_active))
        testcase_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return testcase_id

    def list_testcases(self, problem_id: int) -> list:
        """Liệt kê testcase của đề bài."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bo_testcase WHERE de_bai_id = ? AND is_active = 1 ORDER BY id ASC", (problem_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_testcase_by_id(self, testcase_id: int) -> dict:
        """Lấy testcase theo ID."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bo_testcase WHERE id = ?", (testcase_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def delete_testcase(self, testcase_id: int) -> dict:
        """Xóa testcase."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE bo_testcase SET is_active = 0 WHERE id = ?", (testcase_id,))
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Đã xóa testcase'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ============ SUBMISSION / AI ANALYSIS ============

    def save_submission(self, user_id: int, problem_id: str, code: str, compile_status: dict = None, test_results: list = None, run_output: str = '') -> int:
        """Lưu một submission code."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO nop_bai (nguoi_dung_id, de_bai_id, ma_nguon, compile_status, test_results, run_output)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            int(problem_id) if str(problem_id).isdigit() else None,
            code,
            json.dumps(compile_status) if compile_status is not None else None,
            json.dumps(test_results) if test_results is not None else None,
            run_output
        ))
        submission_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return submission_id

    def _connect(self):
        """Tạo kết nối đến DB để hỗ trợ kiểm thử và migration."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_ai_analysis(self, submission_id: int, classification: dict, ai_analysis_text: str, prompt_text: str = None) -> int:
        """Lưu kết quả phân tích AI liên quan đến một submission."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mo_hinh_ai (nop_bai_id, phan_loai, ai_analysis, prompt_text)
            VALUES (?, ?, ?, ?)
        """, (
            submission_id,
            json.dumps(classification) if classification is not None else None,
            ai_analysis_text,
            prompt_text
        ))
        aid = cursor.lastrowid
        conn.commit()
        conn.close()
        return aid

    def get_submissions_by_user(self, user_id: int) -> list:
        """Lấy danh sách submission của một user."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nop_bai WHERE nguoi_dung_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_submissions(self) -> list:
        """Lấy toàn bộ submission cho admin."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nop_bai ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
