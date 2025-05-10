from contextlib import contextmanager
from typing import Generator, Optional, TypeVar, Type, Any, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.db import get_db_session
from database.models import Base
from copy import deepcopy


T = TypeVar('T', bound=Base)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions using session.begin().
    
    Benefits:
    - Explicit transaction management
    - Automatic rollback on exception
    - Clearer intent for transaction handling
    
    Usage:
        with db_session() as session:
            # Use session for database operations
            user = session.query(User).filter(User.id == 1).first()
    
    Yields:
        SQLAlchemy session
        
    Raises:
        SQLAlchemyError: If any database error occurs
    """
    session = get_db_session()
    try:
        with session.begin():
            yield session
    except Exception:
        raise
    finally:
        session.close()


class Repository:
    """Base repository class with session management."""
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository with the model class.
        
        Args:
            model_class: The SQLAlchemy model class this repository will handle
        """
        self.model_class = model_class
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for handling sessions within this repository."""
        with db_session() as session:
            yield session
    
    def create(self, **kwargs) -> T:
        """
        Create a new instance of the model.
        
        Args:
            **kwargs: Model attributes
            
        Returns:
            The created model instance
            
        Raises:
            SQLAlchemyError: If the creation fails
        """
        with self.session_scope() as session:
            instance = self.model_class(**kwargs)
            session.add(instance)
            return instance

    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get a model instance by its ID.
        
        Args:
            id: The ID of the instance to retrieve
            
        Returns:
            Model instance or None if not found
        """
        with self.session_scope() as session:
            return session.query(self.model_class).filter(self.model_class.id == id).first()

    def get_all(self) -> List[T]:
        """
        Get all instances of the model.
        
        Returns:
            List of all model instances
        """
        with self.session_scope() as session:
            return session.query(self.model_class).all()

    def update(self, **kwargs) -> Optional[T]:
        """
        Update a model instance.
        
        Args:
            **kwargs: Attributes to update, must include the primary key field
            
        Returns:
            Updated model instance or None if not found
            
        Raises:
            SQLAlchemyError: If the update fails
        """
        # Extract primary key from kwargs based on model class
        pk_name = None
        # Common primary key names to try
        common_pks = ['id', 'team_id', 'user_id', f'{self.model_class.__name__.lower()}_id']
        
        # Try to find the primary key in kwargs
        for key in common_pks:
            if key in kwargs:
                pk_name = key
                pk_value = kwargs[key]
                # Don't remove from kwargs as it might be needed for the filter
                break
                
        if pk_name is None:
            raise ValueError(f"Primary key not found in kwargs: {kwargs}")
            
        with self.session_scope() as session:
            # Dynamically build the filter using the primary key name
            filter_expr = getattr(self.model_class, pk_name) == pk_value
            instance = session.query(self.model_class).filter(filter_expr).first()
            if not instance:
                return None
                
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                    
            return deepcopy(instance)

    def delete(self, id: Any) -> bool:
        """
        Delete a model instance.
        
        Args:
            id: The ID of the instance to delete
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If the deletion fails
        """
        with self.session_scope() as session:
            instance = session.query(self.model_class).filter(self.model_class.id == id).first()
            if not instance:
                return False
                
            session.delete(instance)
            return True