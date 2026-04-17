from datetime import date
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# class TeachersRolesRequest(str, Enum):
#     r_manager = "班主任"
#     r_teacher = "授课老师"
from app.model.classes import Classes


class TeachersRegisterRequest(BaseModel):
    t_name: str = Field(..., min_length=1, max_length=50, description="教师姓名")
    t_gender: str = Field(..., max_length=1, pattern="^男|女$", description="教师性别")
    # roles: List[TeachersRolesRequest] = Field(..., description="教师多选角色，班主任|授课老师")
    t_hire_date: Optional[date] = Field(None, description="入职日期")


class TeacherUpdateRequest(BaseModel):
    t_name: Optional[str] = Field(None, min_length=1, max_length=50, description="教师姓名")
    t_gender: Optional[str] = Field(None, max_length=1, pattern="^男|女$", description="教师性别")
    # roles: Optional[List[TeachersRolesRequest]] = Field(None, description="教师多选角色，班主任|授课老师")
    t_hire_date: Optional[date] = Field(None, description="入职日期")


# class TeachersRolesResponse(BaseModel):
#     r_id: int
#     r_name: str

class ClassesResponse(BaseModel):
    c_id: int
    c_name: str


class TeachersDB(BaseModel):
    t_id: int
    t_name: str
    t_gender: str
    # roles: list[TeachersRolesResponse]
    t_home_classes: List[ClassesResponse]
    t_lead_classes: List[ClassesResponse]
    t_hire_date: date


class TeachersResponse(BaseModel):
    code: int
    message: str
    data: list[TeachersDB]


class TeachersRegisterResponse(BaseModel):
    code: int
    message: str
    data: TeachersDB


class TeachersSearchRequest(BaseModel):
    t_name: Optional[str] = Field(None, min_length=1, max_length=50, description="教师姓名")
    t_gender: Optional[str] = Field(None, max_length=1, pattern="^男|女$", description="教师性别")
    # roles: Optional[List[TeachersRolesRequest]] = Field(None, description="教师多选角色，班主任|授课老师")
    t_class_name: Optional[str] = Field(None, description="班主任-带班编号")
    t_start_hire_date: Optional[date] = Field(None, description="最早入职日期")
    t_end_hire_date: Optional[date] = Field(None, description="最晚入职日期")


class TeachersSearchResponse(BaseModel):
    code: int
    message: str
    data: list[TeachersDB]
