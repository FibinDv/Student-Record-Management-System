"""Student data model."""


class Student:
    """Represents an individual student record."""

    def __init__(self, student_id, name, email, course, semester, cgpa):
        self.student_id = str(student_id).strip()
        self.name = str(name).strip()
        self.email = str(email).strip()
        self.course = str(course).strip()
        self.semester = int(semester)
        self.cgpa = float(cgpa)

    @classmethod
    def from_row(cls, row):
        """Create a Student instance from a database row tuple."""
        return cls(
            student_id=row[0],
            name=row[1],
            email=row[2],
            course=row[3],
            semester=row[4],
            cgpa=row[5],
        )

    def to_tuple(self):
        """Convert student attributes to a tuple for SQL queries."""
        return (
            self.student_id,
            self.name,
            self.email,
            self.course,
            self.semester,
            self.cgpa,
        )

    def __str__(self):
        return f"Student(ID={self.student_id}, Name={self.name}, Course={self.course}, CGPA={self.cgpa})"
