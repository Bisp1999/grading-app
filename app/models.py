from . import db
from flask_login import UserMixin
from datetime import datetime

class Teacher(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    preferred_language = db.Column(db.String(5), default='en', nullable=False)
    schools = db.relationship('School', backref='teacher', lazy=True)

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    classrooms = db.relationship('Classroom', backref='school', lazy=True, cascade="all, delete-orphan")

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), nullable=False)
    students = db.relationship('Student', backref='classroom', lazy=True, cascade="all, delete-orphan")

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)

class SetupWizardData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    teacher_type = db.Column(db.String(20), nullable=False)  # 'homeroom' or 'specialist'
    school_name = db.Column(db.String(100), nullable=False)
    num_semesters = db.Column(db.Integer, nullable=False)
    competencies = db.Column(db.Text, nullable=True)  # JSON string of competencies list
    subjects = db.Column(db.Text, nullable=True)  # JSON string of subjects list (homeroom)
    grades = db.Column(db.Text, nullable=True)  # JSON string of grades list (specialist)
    weights = db.Column(db.Text, nullable=True)  # JSON string of competency weights
    classrooms = db.Column(db.Text, nullable=True)  # JSON string of classroom data (specialist)
    grade_name = db.Column(db.String(100), nullable=True)  # Grade/class name for homeroom
    subject_name = db.Column(db.String(100), nullable=True)  # Subject name for specialist
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    teacher = db.relationship('Teacher', backref='setup_wizard_data', lazy=True)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    semester = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.String(50))  # For specialist teachers
    class_name = db.Column(db.String(100))  # For specialist teachers
    subject = db.Column(db.String(100))  # For homeroom teachers
    competency = db.Column(db.String(200), nullable=False)
    test_name = db.Column(db.String(200), nullable=False)
    max_points = db.Column(db.Integer, nullable=False)
    test_date = db.Column(db.Date, nullable=False)
    test_weight = db.Column(db.Float, nullable=False)  # Percentage weight
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to grades
    grades = db.relationship('Grade', backref='test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Test {self.test_name}>'

    teacher = db.relationship('Teacher', backref='tests', lazy=True)

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    grade = db.Column(db.Float)  # Actual points earned (can be null if not graded yet)
    absent = db.Column(db.Boolean, default=False, nullable=False)  # Track if student was absent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique combination of test and student
    __table_args__ = (db.UniqueConstraint('test_id', 'student_id', name='unique_test_student'),)
    
    def __repr__(self):
        return f'<Grade test_id={self.test_id} student_id={self.student_id} grade={self.grade}>'

class ClassroomLayout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    layout_data = db.Column(db.Text, nullable=False)  # JSON string of desk positions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique combination of teacher and classroom
    __table_args__ = (db.UniqueConstraint('teacher_id', 'classroom_id', name='unique_teacher_classroom_layout'),)
    
    teacher = db.relationship('Teacher', backref='classroom_layouts', lazy=True)
    classroom = db.relationship('Classroom', backref='layout', lazy=True)
    
    def __repr__(self):
        return f'<ClassroomLayout teacher_id={self.teacher_id} classroom_id={self.classroom_id}>'
