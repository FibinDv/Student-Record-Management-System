"""Student Record Management System - CLI Interface.

Run this script to interact with the student records database.
"""

import sys
from database import DatabaseManager, DuplicateStudentError
from models import Student


def print_header(title):
    """Print a styled section header."""
    print("\n" + "=" * 50)
    print(f"  {title}")
    print("=" * 50)


def prompt_non_empty(prompt_text, default=None):
    """Prompt the user for a non-empty string."""
    while True:
        if default is not None:
            user_input = input(f"{prompt_text} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt_text}: ").strip()

        if user_input:
            return user_input
        print("  [!] This field cannot be empty. Please try again.")


def prompt_int(prompt_text, min_val=1, max_val=20, default=None):
    """Prompt the user for a valid integer within a range."""
    while True:
        if default is not None:
            user_input = input(f"{prompt_text} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt_text}: ").strip()

        try:
            val = int(user_input)
            if min_val is not None and val < min_val:
                print(f"  [!] Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [!] Value cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("  [!] Please enter a valid whole number.")


def prompt_float(prompt_text, min_val=0.0, max_val=4.0, default=None):
    """Prompt the user for a valid decimal number within a range."""
    while True:
        if default is not None:
            user_input = input(f"{prompt_text} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt_text}: ").strip()

        try:
            val = float(user_input)
            if min_val is not None and val < min_val:
                print(f"  [!] Value must be at least {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [!] Value cannot exceed {max_val}.")
                continue
            return val
        except ValueError:
            print("  [!] Please enter a valid number (e.g., 3.75).")


def display_students_table(students):
    """Display student records in a neatly aligned table."""
    if not students:
        print("\n  No student records found.")
        return

    # Table formatting
    col_id = max(max(len(s.student_id) for s in students), 10)
    col_name = max(max(len(s.name) for s in students), 16)
    col_email = max(max(len(s.email) for s in students), 22)
    col_course = max(max(len(s.course) for s in students), 16)
    col_sem = 8
    col_gpa = 6

    separator = (
        f"+-{'-' * col_id}-+-{'-' * col_name}-+-{'-' * col_email}-+-"
        f"{'-' * col_course}-+-{'-' * col_sem}-+-{'-' * col_gpa}-+"
    )

    print("\n" + separator)
    print(
        f"| {'ID'.ljust(col_id)} | {'Name'.ljust(col_name)} | "
        f"{'Email'.ljust(col_email)} | {'Course'.ljust(col_course)} | "
        f"{'Semester'.center(col_sem)} | {'GPA'.center(col_gpa)} |"
    )
    print(separator)

    for s in students:
        print(
            f"| {s.student_id.ljust(col_id)} | {s.name.ljust(col_name)} | "
            f"{s.email.ljust(col_email)} | {s.course.ljust(col_course)} | "
            f"{str(s.semester).center(col_sem)} | {f'{s.gpa:.2f}'.center(col_gpa)} |"
        )
    print(separator)
    print(f"Total Records: {len(students)}\n")


def add_student_view(db):
    """Handle adding a new student."""
    print_header("Add New Student")

    student_id = prompt_non_empty("Enter Student ID (e.g. S101)")

    # Pre-check if ID already exists
    if db.get_student_by_id(student_id):
        print(f"\n  [!] Error: Student ID '{student_id}' already exists!")
        return

    name = prompt_non_empty("Enter Full Name")
    email = prompt_non_empty("Enter Email Address")
    course = prompt_non_empty("Enter Course / Major")
    semester = prompt_int("Enter Current Semester (1-12)", min_val=1, max_val=12)
    gpa = prompt_float("Enter GPA (0.00 to 4.00)", min_val=0.0, max_val=4.0)

    new_student = Student(
        student_id=student_id,
        name=name,
        email=email,
        course=course,
        semester=semester,
        gpa=gpa,
    )

    try:
        db.add_student(new_student)
        print(f"\n  [✓] Success: Student '{name}' (ID: {student_id}) has been added.")
    except DuplicateStudentError as err:
        print(f"\n  [!] Error: {err}")


def view_all_students_view(db):
    """Handle displaying all student records."""
    print_header("All Student Records")
    students = db.get_all_students()
    display_students_table(students)


def search_student_view(db):
    """Handle searching students by keyword."""
    print_header("Search Student Records")
    keyword = prompt_non_empty("Enter search keyword (ID, Name, or Course)")
    results = db.search_students(keyword)
    print(f"\nSearch results for '{keyword}':")
    display_students_table(results)


def update_student_view(db):
    """Handle updating an existing student."""
    print_header("Update Student Record")
    student_id = prompt_non_empty("Enter Student ID to update")

    student = db.get_student_by_id(student_id)
    if not student:
        print(f"\n  [!] No student found with ID '{student_id}'.")
        return

    print(f"\nEditing Student: {student.name} ({student.student_id})")
    print("Press [Enter] to keep current value, or type a new value:")

    name = prompt_non_empty("Full Name", default=student.name)
    email = prompt_non_empty("Email", default=student.email)
    course = prompt_non_empty("Course", default=student.course)
    semester = prompt_int("Semester", min_val=1, max_val=12, default=student.semester)
    gpa = prompt_float("GPA", min_val=0.0, max_val=4.0, default=student.gpa)

    updated_student = Student(
        student_id=student.student_id,
        name=name,
        email=email,
        course=course,
        semester=semester,
        gpa=gpa,
    )

    if db.update_student(updated_student):
        print(f"\n  [✓] Success: Record for Student ID '{student_id}' has been updated.")
    else:
        print(f"\n  [!] Failed to update student record.")


def delete_student_view(db):
    """Handle deleting a student record."""
    print_header("Delete Student Record")
    student_id = prompt_non_empty("Enter Student ID to delete")

    student = db.get_student_by_id(student_id)
    if not student:
        print(f"\n  [!] No student found with ID '{student_id}'.")
        return

    print(f"\nFound Record: {student.name} | Course: {student.course} | GPA: {student.gpa:.2f}")
    confirm = input("Are you sure you want to delete this record? (y/N): ").strip().lower()

    if confirm == "y" or confirm == "yes":
        if db.delete_student(student_id):
            print(f"\n  [✓] Student '{student.name}' (ID: {student_id}) has been deleted.")
        else:
            print("\n  [!] Failed to delete record.")
    else:
        print("\n  [-] Deletion cancelled.")


def main():
    """Main application loop."""
    db = DatabaseManager(db_path="students.db")

    while True:
        print_header("Student Record Management System")
        print("  1. Add New Student")
        print("  2. View All Students")
        print("  3. Search Student Records")
        print("  4. Update Student Details")
        print("  5. Delete Student Record")
        print("  6. Exit")
        print("-" * 50)

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            add_student_view(db)
        elif choice == "2":
            view_all_students_view(db)
        elif choice == "3":
            search_student_view(db)
        elif choice == "4":
            update_student_view(db)
        elif choice == "5":
            delete_student_view(db)
        elif choice == "6":
            print("\nExiting Student Record Management System. Goodbye!\n")
            sys.exit(0)
        else:
            print("\n  [!] Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()

