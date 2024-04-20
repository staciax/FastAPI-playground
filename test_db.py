import re
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, Session, SQLModel as _SQLModel

from app.core.db import engine
from app.utils.uuid7 import uuid7


# https://stackoverflow.com/a/1176023/19394867
def camel_to_snake(name: str):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class SQLModel(_SQLModel):
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        name = camel_to_snake(cls.__name__)
        return name


class BaseUUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        index=True,
        nullable=False,
    )


class TimeStampMixin(SQLModel):
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={'onupdate': datetime.utcnow},
    )


class Department(BaseUUIDModel, TimeStampMixin, table=True):
    name: str
    admins: list['Admin'] = Relationship(back_populates='department')
    trainees: list['Trainee'] = Relationship(back_populates='department')


class UserBase(BaseUUIDModel, TimeStampMixin):
    email: str = Field(unique=True, index=True)
    first_name: str | None = None
    last_name: str | None = None
    phone_number: str | None = None
    is_active: bool = True
    is_admin: bool = False
    is_superuser: bool = False


class User(UserBase):
    hashed_password: str


class Admin(User, table=True):
    department_id: UUID | None = Field(default=None, foreign_key='department.id')
    department: Department | None = Relationship(back_populates='admins')


class Trainner(User, table=True):
    courses: list['Course'] = Relationship(back_populates='author')


class Course(BaseUUIDModel, TimeStampMixin, table=True):
    name: str | None = Field(max_length=150)
    detail: str | None = None
    status: str | None = Field(max_length=50)
    author_id: UUID | None = Field(default=None, foreign_key='trainner.id')
    author: Trainner | None = Relationship(back_populates='courses')


class CourseLog(BaseUUIDModel, table=True):
    action: str | None
    detail: str | None
    action_by_id: UUID | None = Field(default=None, foreign_key='trainner.id')
    action_by: Trainner | None = Relationship()


class CourseAssignment(BaseUUIDModel, table=True):
    course_id: UUID | None = Field(default=None, foreign_key='course.id')
    course: Course | None = Relationship()
    to_department_id: UUID | None = Field(default=None, foreign_key='department.id')
    to_department: Department | None = Relationship()
    assign_by_id: UUID | None = Field(default=None, foreign_key='admin.id')
    assign_by: Admin | None = Relationship()


class CourseVideo(BaseUUIDModel, table=True):
    title: str | None = Field(max_length=150)
    url: str | None
    course_id: UUID | None = Field(default=None, foreign_key='course.id')
    course: Course | None = Relationship()


class CourseDocument(BaseUUIDModel, table=True):
    title: str | None = Field(max_length=150)
    url: str | None
    course_id: UUID | None = Field(default=None, foreign_key='course.id')
    course: Course | None = Relationship()


class CourseTest(BaseUUIDModel, table=True):
    title: str | None = Field(max_length=150)
    url: str | None
    course_id: UUID | None = Field(default=None, foreign_key='course.id')
    course: Course | None = Relationship()


class CourseTestQuestion(BaseUUIDModel, table=True):
    detail: str | None = None
    course_test_id: UUID | None = Field(default=None, foreign_key='course_test.id')
    course_test: CourseTest | None = Relationship()


class CourseTestAnswer(BaseUUIDModel, table=True):
    detail: str | None = None
    is_correct: bool = False
    course_test_question_id: UUID | None = Field(default=None, foreign_key='course_test_question.id')
    course_test_question: CourseTestQuestion | None = Relationship()


class CourseTestAnswerText(BaseUUIDModel, table=True):
    text: str | None = None
    course_test_question_id: UUID | None = Field(default=None, foreign_key='course_test_question.id')
    course_test_question: CourseTestQuestion | None = Relationship()


class Trainee(User, table=True):
    department_id: UUID | None = Field(default=None, foreign_key='department.id')
    department: Department | None = Relationship(back_populates='trainees')
    created_by_id: UUID | None = Field(default=None, foreign_key='admin.id')
    created_by: Admin | None = Relationship()


class TraineeLog(BaseUUIDModel, table=True):
    action: str | None = None
    detail: str | None = None
    action_by_id: UUID | None = Field(default=None, foreign_key='admin.id')
    action_by: Admin | None = Relationship()


class TraineeTest(BaseUUIDModel, table=True):
    answer_text: str | None = None
    answer_choice: str | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    trainee_id: UUID | None = Field(default=None, foreign_key='trainee.id')
    trainee: Trainee | None = Relationship()
    course_test_question_id: UUID | None = Field(default=None, foreign_key='course_test_question.id')
    course_test_question: CourseTestQuestion | None = Relationship()


class TraineeWatchingLog(BaseUUIDModel, table=True):
    content_id: UUID | None = None
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    trainee_id: UUID | None = Field(default=None, foreign_key='trainee.id')
    trainee: Trainee | None = Relationship()


class UserUUID7(BaseUUIDModel, table=True):
    name: str | None = None


def create_db_and_tables():
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def test_uuid7():
    with Session(engine) as session:
        user_1 = UserUUID7(name='User 1')
        user_2 = UserUUID7(name='User 2')
        session.add(user_1)
        session.add(user_2)
        session.commit()
        session.refresh(user_1)
        session.refresh(user_2)

        print(user_1)
        print(user_2)

        assert user_1.id < user_2.id


if __name__ == '__main__':
    create_db_and_tables()
    test_uuid7()
