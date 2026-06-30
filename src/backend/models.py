"""
Database Models for Tracking Attempts
"""
Database Models for the current system
"""

# SQLite Schema for the current system
DATABASE_SCHEMA = """
# SQLite Schema for the current system
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT,
    metadata TEXT,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    metadata TEXT,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1,
CREATE TABLE IF NOT EXISTS code_submissions (
);

    problem_id TEXT,
    code TEXT NOT NULL,
    compile_status TEXT,
    test_results TEXT,
    run_output TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    test_results TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
CREATE TABLE IF NOT EXISTS ai_analysis (
);
    submission_id INTEGER,
    classification TEXT,
    ai_analysis TEXT,
    sanitized_analysis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES code_submissions(id)
        self.current_hint_index = 0
        self.tests_passed = 0
        self.tests_total = 0
        self.is_solved = False
        self.steps = []
        self.start_time = datetime.now()
        self.last_modified = datetime.now()
        self.completed_time = None
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'problem_id': self.problem_id,
            'original_code': self.original_code,

    code TEXT NOT NULL,
