"""
Data models for the Task Tracker application.
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    """Enumeration for task status values."""
    NOT_STARTED = "Not Started"
    WORKING_ON_IT = "Working on it"
    STUCK = "Stuck"
    DONE = "Done"

class TaskPriority(str, Enum):
    """Enumeration for task priority levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"

class Task(SQLModel, table=True):
    """Task model representing a single task in the system."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, description="Task title")
    description: Optional[str] = Field(default=None, max_length=500, description="Task description")
    owner: Optional[str] = Field(default=None, max_length=50, description="Task owner")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="Current task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority level")
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD format")
    created_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="Creation date")
    completed_date: Optional[str] = Field(default=None, description="Completion date")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Additional notes")
    completed: bool = Field(default=False, description="Completion status")
    project: str = Field(default="learning", max_length=50, description="Project name")
    tags: Optional[str] = Field(default=None, max_length=200, description="Comma-separated tags")
    estimated_hours: Optional[float] = Field(default=None, ge=0, description="Estimated hours to complete")
    actual_hours: Optional[float] = Field(default=None, ge=0, description="Actual hours spent")
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True

class Project(SQLModel, table=True):
    """Project model for organizing tasks."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, description="Project name")
    description: Optional[str] = Field(default=None, max_length=200, description="Project description")
    created_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    is_active: bool = Field(default=True, description="Project active status")
    color: Optional[str] = Field(default="#2563eb", description="Project color in hex format")

class TaskHistory(SQLModel, table=True):
    """Task history model for tracking changes."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(description="Reference to the task")
    field_name: str = Field(max_length=50, description="Name of the changed field")
    old_value: Optional[str] = Field(default=None, max_length=500, description="Previous value")
    new_value: Optional[str] = Field(default=None, max_length=500, description="New value")
    changed_date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    changed_by: Optional[str] = Field(default=None, max_length=50, description="User who made the change") 