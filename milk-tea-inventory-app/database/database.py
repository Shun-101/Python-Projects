"""
BrewMetric Database Module
SQLAlchemy ORM models and database operations.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import DATABASE_URL, DATABASE_ECHO, ROLE_ADMIN, ROLE_STAFF

Base = declarative_base()

# ============================================================================
# Database Models
# ============================================================================

class User(Base):
    """User model for authentication and role-based access control."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(20), default=ROLE_STAFF, nullable=False)  # 'admin' or 'staff'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    audit_trails = relationship("AuditTrail", back_populates="user")
    waste_logs = relationship("WasteLog", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username}>"


class InventoryItem(Base):
    """Inventory item model for tracking stock."""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    quantity = Column(Float, default=0, nullable=False)
    unit = Column(String(20), default="unit", nullable=False)  # e.g., "kg", "L", "box"
    min_threshold = Column(Float, default=10, nullable=False)
    unit_cost = Column(Float, default=0.0, nullable=False)
    expiration_date = Column(DateTime, nullable=True)
    location = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    waste_logs = relationship("WasteLog", back_populates="inventory_item")
    audit_trails = relationship("AuditTrail", back_populates="inventory_item")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_category', 'category'),
        Index('idx_expiration', 'expiration_date'),
        Index('idx_deleted', 'is_deleted'),
    )
    
    def is_below_threshold(self) -> bool:
        """Check if item is below minimum threshold."""
        return self.quantity < self.min_threshold
    
    def is_expiring_soon(self, days: int = 7) -> bool:
        """Check if item is expiring within specified days."""
        if not self.expiration_date:
            return False
        days_until_expiration = (self.expiration_date - datetime.utcnow()).days
        return 0 <= days_until_expiration <= days
    
    def is_expired(self) -> bool:
        """Check if item is expired."""
        if not self.expiration_date:
            return False
        return self.expiration_date < datetime.utcnow()
    
    def get_stock_value(self) -> float:
        """Calculate total stock value."""
        return self.quantity * self.unit_cost
    
    def __repr__(self):
        return f"<InventoryItem {self.name}>"


class WasteLog(Base):
    """Waste log model for tracking spoilage and waste."""
    __tablename__ = "waste_logs"
    
    id = Column(Integer, primary_key=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    reason = Column(String(50), nullable=False)  # 'spill', 'expired', 'quality', etc.
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="waste_logs")
    user = relationship("User", back_populates="waste_logs")
    
    __table_args__ = (
        Index('idx_user_waste', 'user_id'),
        Index('idx_item_waste', 'inventory_item_id'),
    )
    
    def __repr__(self):
        return f"<WasteLog {self.inventory_item.name} - {self.quantity}>"


class AuditTrail(Base):
    """Audit trail model for compliance and security logging."""
    __tablename__ = "audit_trails"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    action = Column(String(50), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT'
    entity_type = Column(String(50), nullable=False)  # 'User', 'InventoryItem', 'WasteLog'
    entity_id = Column(Integer, nullable=False)
    old_values = Column(Text, nullable=True)  # JSON string
    new_values = Column(Text, nullable=True)  # JSON string
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    session_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_trails")
    inventory_item = relationship("InventoryItem", back_populates="audit_trails")
    
    __table_args__ = (
        Index('idx_user_audit', 'user_id'),
        Index('idx_action_audit', 'action'),
        Index('idx_created_audit', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AuditTrail {self.action} by {self.user.username}>"


class ActivityFeed(Base):
    """Activity feed model for recent actions display."""
    __tablename__ = "activity_feed"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    action = Column(String(100), nullable=False)  # e.g., "Added 50 units of Pearl Tea"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    __table_args__ = (
        Index('idx_created_feed', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ActivityFeed {self.action}>"


# ============================================================================
# Database Engine and Session Setup
# ============================================================================

class DatabaseManager:
    """Manager for database operations and session handling."""
    
    def __init__(self):
        """Initialize database engine and session factory."""
        self.engine = create_engine(
            DATABASE_URL,
            echo=DATABASE_ECHO,
            connect_args={"timeout": 30}  # SQLite timeout
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all database tables (for testing/reset)."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def init_db(self):
        """Initialize database with schema."""
        self.create_tables()
    
    def close_all(self):
        """Close all connections."""
        self.engine.dispose()


# ============================================================================
# Query Helpers
# ============================================================================

class InventoryQueries:
    """Queries for inventory operations."""
    
    @staticmethod
    def get_low_stock_items(session, limit: int = 10):
        """Get items below threshold."""
        return session.query(InventoryItem)\
            .filter(InventoryItem.quantity < InventoryItem.min_threshold)\
            .filter(InventoryItem.is_deleted == False)\
            .order_by(InventoryItem.quantity.asc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_expiring_items(session, days: int = 7):
        """Get items expiring within specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        return session.query(InventoryItem)\
            .filter(InventoryItem.expiration_date <= cutoff_date)\
            .filter(InventoryItem.expiration_date >= datetime.utcnow())\
            .filter(InventoryItem.is_deleted == False)\
            .order_by(InventoryItem.expiration_date.asc())\
            .all()
    
    @staticmethod
    def get_all_items(session, exclude_deleted: bool = True):
        """Get all inventory items."""
        query = session.query(InventoryItem)
        if exclude_deleted:
            query = query.filter(InventoryItem.is_deleted == False)
        return query.order_by(InventoryItem.name.asc()).all()
    
    @staticmethod
    def get_by_category(session, category: str):
        """Get items by category."""
        return session.query(InventoryItem)\
            .filter(InventoryItem.category == category)\
            .filter(InventoryItem.is_deleted == False)\
            .order_by(InventoryItem.name.asc())\
            .all()
    
    @staticmethod
    def get_total_inventory_value(session):
        """Calculate total inventory value."""
        items = session.query(InventoryItem)\
            .filter(InventoryItem.is_deleted == False)\
            .all()
        return sum(item.get_stock_value() for item in items)


class WasteQueries:
    """Queries for waste log operations."""
    
    @staticmethod
    def get_recent_waste(session, limit: int = 50):
        """Get recent waste entries."""
        return session.query(WasteLog)\
            .order_by(WasteLog.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_waste_by_date_range(session, start_date: datetime, end_date: datetime):
        """Get waste entries within date range."""
        return session.query(WasteLog)\
            .filter(WasteLog.created_at >= start_date)\
            .filter(WasteLog.created_at <= end_date)\
            .order_by(WasteLog.created_at.desc())\
            .all()
    
    @staticmethod
    def get_monthly_waste_summary(session):
        """Get waste summary for current month."""
        from datetime import timedelta
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
        return session.query(WasteLog)\
            .filter(WasteLog.created_at >= start_of_month)\
            .all()


class AuditQueries:
    """Queries for audit trail operations."""
    
    @staticmethod
    def get_recent_actions(session, limit: int = 100):
        """Get recent audit actions."""
        return session.query(AuditTrail)\
            .order_by(AuditTrail.created_at.desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_actions_by_user(session, user_id: int):
        """Get all actions by a user."""
        return session.query(AuditTrail)\
            .filter(AuditTrail.user_id == user_id)\
            .order_by(AuditTrail.created_at.desc())\
            .all()
    
    @staticmethod
    def get_actions_by_type(session, action_type: str):
        """Get actions by type."""
        return session.query(AuditTrail)\
            .filter(AuditTrail.action == action_type)\
            .order_by(AuditTrail.created_at.desc())\
            .all()
