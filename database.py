"""
Database operations for the Task Tracker application.
"""
import sqlite3
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading
from sqlmodel import SQLModel, create_engine, Session, select
from models import Task, Project, TaskHistory, TaskStatus, TaskPriority
from config import DATABASE_PATH, BATCH_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations with connection pooling."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._engine = None
        self._init_database()
    
    def _init_database(self):
        """Initialize the database and create tables."""
        try:
            self._engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
            
            # Check if database exists
            import os
            db_exists = os.path.exists(self.db_path)
            
            if db_exists:
                # Check if we need to migrate the schema
                try:
                    # Try to connect and check if tables exist
                    with Session(self._engine) as session:
                        # Check if Task table exists by trying to query it
                        session.exec(select(Task).limit(1))
                    logger.info(f"Database exists and schema is up to date at {self.db_path}")
                except Exception as e:
                    # Schema needs migration - backup and recreate
                    logger.info("Database schema needs migration")
                    backup_path = self.db_path + '.backup'
                    if not os.path.exists(backup_path):
                        import shutil
                        shutil.copy2(self.db_path, backup_path)
                        logger.info(f"Backed up old database to {backup_path}")
                    
                    # Drop and recreate tables to ensure new schema
                    SQLModel.metadata.drop_all(self._engine)
                    logger.info("Dropped old database schema")
                    SQLModel.metadata.create_all(self._engine)
                    logger.info("Created new database schema")
            else:
                # Create new database
                SQLModel.metadata.create_all(self._engine)
                logger.info(f"Created new database at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = Session(self._engine)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def add_task(self, task_data: Dict[str, Any]) -> Optional[int]:
        """Add a new task to the database."""
        try:
            with self.get_session() as session:
                task = Task(**task_data)
                session.add(task)
                session.commit()
                session.refresh(task)
                logger.info(f"Task added with ID: {task.id}")
                return task.id
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return None
    
    def get_tasks(self, project: Optional[str] = None, 
                  status: Optional[str] = None,
                  owner: Optional[str] = None,
                  limit: int = BATCH_SIZE,
                  offset: int = 0) -> List[Dict[str, Any]]:
        """Get tasks with optional filtering and pagination."""
        try:
            with self.get_session() as session:
                query = select(Task)
                
                if project:
                    query = query.where(Task.project == project)
                if status:
                    query = query.where(Task.status == status)
                if owner:
                    query = query.where(Task.owner == owner)
                
                query = query.order_by(Task.created_date.desc())
                query = query.offset(offset).limit(limit)
                
                tasks = session.exec(query).all()
                # Sanitize task data to ensure proper types
                sanitized_tasks = []
                for task in tasks:
                    task_dict = task.dict()
                    # Ensure due_date is a string or None
                    if task_dict.get('due_date') is not None:
                        task_dict['due_date'] = str(task_dict['due_date'])
                    # Ensure estimated_hours is a number or None
                    if task_dict.get('estimated_hours') is not None:
                        try:
                            task_dict['estimated_hours'] = float(task_dict['estimated_hours'])
                        except (ValueError, TypeError):
                            task_dict['estimated_hours'] = None
                    sanitized_tasks.append(task_dict)
                return sanitized_tasks
        except Exception as e:
            logger.error(f"Failed to get tasks: {e}")
            return []
    
    def search_tasks(self, search_term: str, project: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search tasks by title, description, or notes."""
        try:
            with self.get_session() as session:
                query = select(Task).where(
                    (Task.title.contains(search_term)) |
                    (Task.description.contains(search_term)) |
                    (Task.notes.contains(search_term))
                )
                
                if project:
                    query = query.where(Task.project == project)
                
                query = query.order_by(Task.created_date.desc())
                tasks = session.exec(query).all()
                # Sanitize task data to ensure proper types
                sanitized_tasks = []
                for task in tasks:
                    task_dict = task.dict()
                    # Ensure due_date is a string or None
                    if task_dict.get('due_date') is not None:
                        task_dict['due_date'] = str(task_dict['due_date'])
                    # Ensure estimated_hours is a number or None
                    if task_dict.get('estimated_hours') is not None:
                        try:
                            task_dict['estimated_hours'] = float(task_dict['estimated_hours'])
                        except (ValueError, TypeError):
                            task_dict['estimated_hours'] = None
                    sanitized_tasks.append(task_dict)
                return sanitized_tasks
        except Exception as e:
            logger.error(f"Failed to search tasks: {e}")
            return []
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID."""
        try:
            with self.get_session() as session:
                task = session.get(Task, task_id)
                if task:
                    task_dict = task.dict()
                    # Ensure due_date is a string or None
                    if task_dict.get('due_date') is not None:
                        task_dict['due_date'] = str(task_dict['due_date'])
                    # Ensure estimated_hours is a number or None
                    if task_dict.get('estimated_hours') is not None:
                        try:
                            task_dict['estimated_hours'] = float(task_dict['estimated_hours'])
                        except (ValueError, TypeError):
                            task_dict['estimated_hours'] = None
                    return task_dict
                return None
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return None
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """Update a task with change tracking."""
        try:
            with self.get_session() as session:
                task = session.get(Task, task_id)
                if not task:
                    return False
                
                # Track changes for history
                changes = []
                for field, new_value in kwargs.items():
                    if hasattr(task, field) and getattr(task, field) != new_value:
                        old_value = getattr(task, field)
                        setattr(task, field, new_value)
                        
                        # Record change in history
                        history = TaskHistory(
                            task_id=task_id,
                            field_name=field,
                            old_value=str(old_value) if old_value is not None else None,
                            new_value=str(new_value) if new_value is not None else None,
                            changed_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        )
                        session.add(history)
                        changes.append(field)
                
                if changes:
                    logger.info(f"Task {task_id} updated: {', '.join(changes)}")
                
                return True
        except Exception as e:
            logger.error(f"Failed to update task {task_id}: {e}")
            return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task and its history."""
        try:
            with self.get_session() as session:
                task = session.get(Task, task_id)
                if not task:
                    return False
                
                # Delete associated history first
                history_query = select(TaskHistory).where(TaskHistory.task_id == task_id)
                history_records = session.exec(history_query).all()
                for history_record in history_records:
                    session.delete(history_record)
                
                # Delete the task
                session.delete(task)
                session.commit()
                logger.info(f"Task {task_id} deleted")
                return True
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return False
    
    def get_task_statistics(self, project: Optional[str] = None) -> Dict[str, Any]:
        """Get task statistics for dashboard."""
        try:
            with self.get_session() as session:
                query = select(Task)
                if project:
                    query = query.where(Task.project == project)
                
                tasks = session.exec(query).all()
                
                total = len(tasks)
                completed = len([t for t in tasks if t.completed])
                overdue = len([t for t in tasks if t.due_date and 
                             datetime.strptime(t.due_date, "%Y-%m-%d") < datetime.now() and 
                             not t.completed])
                
                status_counts = {}
                for status in TaskStatus:
                    status_counts[status.value] = len([t for t in tasks if t.status == status])
                
                return {
                    "total": total,
                    "completed": completed,
                    "overdue": overdue,
                    "status_counts": status_counts,
                    "completion_rate": (completed / total * 100) if total > 0 else 0
                }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {"total": 0, "completed": 0, "overdue": 0, "status_counts": {}, "completion_rate": 0}
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        try:
            with self.get_session() as session:
                projects = session.exec(select(Project).where(Project.is_active == True)).all()
                return [project.dict() for project in projects]
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []
    
    def add_project(self, project_data: Dict[str, Any]) -> Optional[int]:
        """Add a new project."""
        try:
            with self.get_session() as session:
                project = Project(**project_data)
                session.add(project)
                session.commit()
                session.refresh(project)
                return project.id
        except Exception as e:
            logger.error(f"Failed to add project: {e}")
            return None
    
    def delete_project(self, project_name: str) -> bool:
        """Deactivate (soft-delete) a project by name."""
        try:
            with self.get_session() as session:
                project = session.exec(select(Project).where(Project.name == project_name)).first()
                if project:
                    project.is_active = False
                    session.add(project)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete project: {e}")
            return False
    
    def delete_project_permanently(self, project_name: str) -> bool:
        """Permanently delete a project and all its tasks from the database."""
        try:
            with self.get_session() as session:
                # Delete tasks associated with the project
                tasks = session.exec(select(Task).where(Task.project == project_name)).all()
                for task in tasks:
                    session.delete(task)
                # Delete the project itself
                project = session.exec(select(Project).where(Project.name == project_name)).first()
                if project:
                    session.delete(project)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to permanently delete project: {e}")
            return False
    
    def get_overdue_tasks(self) -> List[Dict[str, Any]]:
        """Get tasks that are overdue."""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            with self.get_session() as session:
                query = select(Task).where(
                    (Task.due_date < today) & 
                    (Task.completed == False)
                )
                tasks = session.exec(query).all()
                # Sanitize task data to ensure proper types
                sanitized_tasks = []
                for task in tasks:
                    task_dict = task.dict()
                    # Ensure due_date is a string or None
                    if task_dict.get('due_date') is not None:
                        task_dict['due_date'] = str(task_dict['due_date'])
                    # Ensure estimated_hours is a number or None
                    if task_dict.get('estimated_hours') is not None:
                        try:
                            task_dict['estimated_hours'] = float(task_dict['estimated_hours'])
                        except (ValueError, TypeError):
                            task_dict['estimated_hours'] = None
                    sanitized_tasks.append(task_dict)
                return sanitized_tasks
        except Exception as e:
            logger.error(f"Failed to get overdue tasks: {e}")
            return []
    
    def get_task_history(self, task_id: int) -> List[Dict[str, Any]]:
        """Get change history for a task."""
        try:
            with self.get_session() as session:
                history = session.exec(
                    select(TaskHistory)
                    .where(TaskHistory.task_id == task_id)
                    .order_by(TaskHistory.changed_date.desc())
                ).all()
                return [h.dict() for h in history]
        except Exception as e:
            logger.error(f"Failed to get task history: {e}")
            return []

    def delete_orphan_learning_tasks(self):
        """Delete all tasks with project='learning' (case-insensitive) if the project does not exist in the Project table."""
        try:
            with self.get_session() as session:
                # Check if 'learning' project exists (case-insensitive)
                project = session.exec(select(Project).where(Project.name.ilike('learning'))).first()
                if not project:
                    # Delete all tasks with project='learning' (case-insensitive)
                    tasks = session.exec(select(Task).where(Task.project.ilike('learning'))).all()
                    for task in tasks:
                        session.delete(task)
                    session.commit()
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to delete orphan learning tasks: {e}")
            return False

# Global database manager instance
db_manager = DatabaseManager() 