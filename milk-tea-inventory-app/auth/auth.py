"""
BrewMetric Authentication Module
Secure password handling and user authentication.
"""

import re
import bcrypt
from sqlalchemy.orm import Session
from database import User, ROLE_ADMIN, ROLE_STAFF
from config import PASSWORD_MIN_LENGTH, BCRYPT_ROUNDS


class AuthManager:
    """Authentication and authorization manager."""
    
    # Current session user (maintained in memory)
    current_user: User = None
    current_session: Session = None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """
        Validate password strength requirements.
        
        Requirements:
        - Minimum 8 characters
        - At least 1 lowercase letter
        - At least 1 uppercase letter
        - At least 1 digit
        - At least 1 special character (!@#$%^&*)
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*]', password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        return True, "Password is strong"
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username format.
        
        Requirements:
        - 3-50 characters
        - Alphanumeric and underscores only
        - Cannot start with number
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(username) < 3 or len(username) > 50:
            return False, "Username must be between 3 and 50 characters"
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', username):
            return False, "Username can only contain letters, numbers, and underscores (must start with letter or underscore)"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        return True, "Email is valid"
    
    @staticmethod
    def authenticate_user(session: Session, username: str, password: str) -> User | None:
        """
        Authenticate a user with username and password.
        
        Args:
            session: Database session
            username: Username
            password: Plain text password
            
        Returns:
            User object if authenticated, None otherwise
        """
        try:
            user = session.query(User).filter(User.username == username).first()
            
            if not user:
                return None
            
            if not user.is_active:
                return None
            
            if not AuthManager.verify_password(password, user.password_hash):
                return None
            
            return user
        except Exception as e:
            print(f"[v0] Authentication error: {e}")
            return None
    
    @staticmethod
    def create_user(
        session: Session,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: str = ROLE_STAFF
    ) -> tuple[bool, str, User | None]:
        """
        Create a new user.
        
        Args:
            session: Database session
            username: Username
            email: Email address
            password: Plain text password
            full_name: User's full name
            role: User role (admin or staff)
            
        Returns:
            Tuple of (success, message, user_object)
        """
        # Validate username
        is_valid, msg = AuthManager.validate_username(username)
        if not is_valid:
            return False, f"Invalid username: {msg}", None
        
        # Validate email
        is_valid, msg = AuthManager.validate_email(email)
        if not is_valid:
            return False, f"Invalid email: {msg}", None
        
        # Validate password
        is_valid, msg = AuthManager.validate_password_strength(password)
        if not is_valid:
            return False, f"Weak password: {msg}", None
        
        # Check if username already exists
        existing_user = session.query(User).filter(User.username == username).first()
        if existing_user:
            return False, "Username already exists", None
        
        # Check if email already exists
        existing_email = session.query(User).filter(User.email == email).first()
        if existing_email:
            return False, "Email already exists", None
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=AuthManager.hash_password(password),
                full_name=full_name,
                role=role,
                is_active=True
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return True, "User created successfully", new_user
        except Exception as e:
            session.rollback()
            return False, f"Error creating user: {str(e)}", None
    
    @staticmethod
    def create_default_admin(session: Session) -> User | None:
        """
        Create default admin account if none exists.
        
        Default credentials:
        - Username: admin
        - Password: Admin@123456
        - Email: admin@brewmetric.local
        
        Args:
            session: Database session
            
        Returns:
            Admin user object if created or already exists, None on error
        """
        # Check if any admin already exists
        existing_admin = session.query(User).filter(User.role == ROLE_ADMIN).first()
        if existing_admin:
            return existing_admin
        
        # Create default admin
        success, msg, admin = AuthManager.create_user(
            session=session,
            username="admin",
            email="admin@brewmetric.local",
            password="Admin@123456",
            full_name="Administrator",
            role=ROLE_ADMIN
        )
        
        if success:
            return admin
        else:
            print(f"[v0] Failed to create default admin: {msg}")
            return None
    
    @staticmethod
    def has_permission(user: User, action: str) -> bool:
        """
        Check if user has permission for an action.
        
        Admin permissions:
        - All actions (create, update, delete, audit_view, etc.)
        
        Staff permissions:
        - Add and view inventory items
        - Record waste entries
        - View own activity only
        - Export limited reports (inventory only)
        
        Args:
            user: User object
            action: Action to check (e.g., 'delete_item', 'view_audit', 'create_user')
            
        Returns:
            True if user has permission, False otherwise
        """
        if not user:
            return False
        
        if user.role == ROLE_ADMIN:
            return True
        
        if user.role == ROLE_STAFF:
            staff_allowed = [
                'view_inventory',
                'add_item',
                'adjust_stock',
                'record_waste',
                'view_activity',
                'export_inventory',
            ]
            return action in staff_allowed
        
        return False
    
    @staticmethod
    def set_current_user(user: User, session: Session):
        """
        Set the current logged-in user.
        
        Args:
            user: User object
            session: Database session
        """
        AuthManager.current_user = user
        AuthManager.current_session = session
    
    @staticmethod
    def get_current_user() -> User | None:
        """Get the current logged-in user."""
        return AuthManager.current_user
    
    @staticmethod
    def get_current_session() -> Session | None:
        """Get the current database session."""
        return AuthManager.current_session
    
    @staticmethod
    def logout():
        """Log out the current user."""
        AuthManager.current_user = None
        AuthManager.current_session = None
