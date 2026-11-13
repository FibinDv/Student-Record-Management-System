"""Database operations for Student Record Management System using SQLite."""

import sqlite3
from models import Student


class DuplicateStudentError(Exception):
    """Raised when trying to add a student ID that already exists."""
    pass


class DatabaseManager:
    """Handles all database operations for student records."""

    def __init__(self, db_path="students.db"):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        """Create and return a database connection."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Create the students table if it does not exist, and migrate older columns if needed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    course TEXT NOT NULL,
                    semester INTEGER NOT NULL,
                    cgpa REAL NOT NULL
                )
                """
            )
            # Automatic column migration if existing DB used 'gpa'
            cursor.execute("PRAGMA table_info(students)")
            existing_columns = [col[1] for col in cursor.fetchall()]
            if "gpa" in existing_columns and "cgpa" not in existing_columns:
                cursor.execute("ALTER TABLE students RENAME COLUMN gpa TO cgpa")
            conn.commit()

    def add_student(self, student):
        """Add a new student record to the database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    """
                    INSERT INTO students (student_id, name, email, course, semester, cgpa)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    student.to_tuple(),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise DuplicateStudentError(
                    f"A student with ID '{student.student_id}' already exists."
                )

    def get_student_by_id(self, student_id):
        """Fetch a single student by their ID. Returns Student or None."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT student_id, name, email, course, semester, cgpa
                FROM students
                WHERE student_id = ?
                """,
                (str(student_id).strip(),),
            )
            row = cursor.fetchone()
            if row:
                return Student.from_row(row)
            return None

    def get_all_students(self):
        """Fetch all student records sorted by student ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT student_id, name, email, course, semester, cgpa
                FROM students
                ORDER BY student_id ASC
                """
            )
            rows = cursor.fetchall()
            return [Student.from_row(row) for row in rows]

    def search_students(self, keyword):
        """Search students by matching ID, Name, or Course."""
        pattern = f"%{str(keyword).strip()}%"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT student_id, name, email, course, semester, cgpa
                FROM students
                WHERE student_id LIKE ? OR name LIKE ? OR course LIKE ?
                ORDER BY student_id ASC
                """,
                (pattern, pattern, pattern),
            )
            rows = cursor.fetchall()
            return [Student.from_row(row) for row in rows]

    def update_student(self, student):
        """Update an existing student's details. Returns True if updated, False otherwise."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE students
                SET name = ?, email = ?, course = ?, semester = ?, cgpa = ?
                WHERE student_id = ?
                """,
                (
                    student.name,
                    student.email,
                    student.course,
                    student.semester,
                    student.cgpa,
                    student.student_id,
                ),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_student(self, student_id):
        """Delete a student record by ID. Returns True if deleted, False otherwise."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM students
                WHERE student_id = ?
                """,
                (str(student_id).strip(),),
            )
            conn.commit()
            return cursor.rowcount > 0
