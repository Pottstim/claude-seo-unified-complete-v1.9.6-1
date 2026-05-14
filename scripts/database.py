#!/usr/bin/env python3
"""
Database models and connection management for claude-seo-unified
Supports PostgreSQL, MySQL, SQLite, and Redis caching
"""

import os
import json
import hashlib
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from contextlib import contextmanager
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Try to import database libraries
try:
    from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, JSON, Boolean, Index
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import QueuePool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# ========================================
# Configuration
# ========================================

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///seo_unified.db")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.environ.get("CACHE_TTL", "3600"))  # 1 hour default


# ========================================
# SQLAlchemy Models
# ========================================

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()
    
    class AnalysisRecord(Base):
        """Stores SEO analysis results"""
        __tablename__ = "analyses"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        report_id = Column(String(36), unique=True, nullable=False, index=True)
        url = Column(String(2048), nullable=False, index=True)
        url_hash = Column(String(32), nullable=False, index=True)
        domain = Column(String(255), index=True)
        
        # Scores
        overall_score = Column(Integer)
        technical_score = Column(Integer)
        content_score = Column(Integer)
        performance_score = Column(Integer)
        schema_score = Column(Integer)
        ai_readiness_score = Column(Integer)
        
        # Full analysis JSON
        analysis_data = Column(JSON, nullable=False)
        
        # Metadata
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
        expires_at = Column(DateTime, index=True)
        
        # Status
        status = Column(String(20), default="completed", index=True)  # pending, completed, failed
        error_message = Column(Text)
        
        # Request info
        ip_address = Column(String(45))
        user_agent = Column(String(500))
        request_duration_ms = Column(Integer)
        
        __table_args__ = (
            Index('idx_url_hash_created', 'url_hash', 'created_at'),
            Index('idx_domain_created', 'domain', 'created_at'),
        )
    
    class APIKeyRecord(Base):
        """Stores API keys and usage"""
        __tablename__ = "api_keys"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        api_key = Column(String(64), unique=True, nullable=False, index=True)
        name = Column(String(100), nullable=False)
        email = Column(String(255))
        
        # Usage tracking
        total_requests = Column(Integer, default=0)
        last_request_at = Column(DateTime)
        
        # Limits
        daily_limit = Column(Integer, default=1000)
        monthly_limit = Column(Integer, default=10000)
        
        # Status
        is_active = Column(Boolean, default=True, index=True)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        expires_at = Column(DateTime)
        
        # Admin
        is_admin = Column(Boolean, default=False)
        notes = Column(Text)
    
    class RequestLog(Base):
        """Stores request logs for analytics"""
        __tablename__ = "request_logs"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        request_id = Column(String(36), unique=True, index=True)
        api_key_id = Column(Integer, index=True)
        
        # Request details
        method = Column(String(10))
        path = Column(String(500), index=True)
        query_params = Column(JSON)
        
        # Response
        status_code = Column(Integer, index=True)
        response_time_ms = Column(Integer)
        
        # Client info
        ip_address = Column(String(45), index=True)
        user_agent = Column(String(500))
        
        # Timing
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
        
        __table_args__ = (
            Index('idx_created_status', 'created_at', 'status_code'),
        )
    
    class CachedResult(Base):
        """Stores cached analysis results"""
        __tablename__ = "cache"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        cache_key = Column(String(64), unique=True, nullable=False, index=True)
        data = Column(JSON, nullable=False)
        created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
        expires_at = Column(DateTime, index=True)
        hits = Column(Integer, default=0)
    
    class CircuitBreakerState(Base):
        """Stores circuit breaker state for distributed systems"""
        __tablename__ = "circuit_breakers"
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        service_name = Column(String(100), unique=True, nullable=False, index=True)
        state = Column(String(20), default="closed")  # closed, open, half-open
        failure_count = Column(Integer, default=0)
        last_failure_at = Column(DateTime)
        opened_at = Column(DateTime)
        updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# ========================================
# Database Manager
# ========================================

class DatabaseManager:
    """Manages database connections and sessions"""
    
    def __init__(self, database_url: str = None):
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError("SQLAlchemy not installed. Run: pip install sqlalchemy psycopg2-binary")
        
        self.database_url = database_url or DATABASE_URL
        self._engine = None
        self._session_factory = None
        self._lock = threading.Lock()
    
    @property
    def engine(self):
        if self._engine is None:
            with self._lock:
                if self._engine is None:
                    # Configure pool based on database type
                    pool_kwargs = {}
                    if "postgresql" in self.database_url or "mysql" in self.database_url:
                        pool_kwargs = {
                            "poolclass": QueuePool,
                            "pool_size": 10,
                            "max_overflow": 20,
                            "pool_timeout": 30,
                            "pool_recycle": 3600
                        }
                    
                    self._engine = create_engine(
                        self.database_url,
                        echo=os.environ.get("SQL_ECHO", "").lower() == "true",
                        **pool_kwargs
                    )
        return self._engine
    
    @property
    def session_factory(self):
        if self._session_factory is None:
            with self._lock:
                if self._session_factory is None:
                    self._session_factory = sessionmaker(bind=self.engine)
        return self._session_factory
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
        logger.warning("Database tables dropped")
    
    @contextmanager
    def session(self) -> Session:
        """Get a database session with automatic cleanup"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """Get a database session (caller responsible for cleanup)"""
        return self.session_factory()


# ========================================
# Redis Cache Manager
# ========================================

class RedisCacheManager:
    """Manages Redis caching"""
    
    def __init__(self, redis_url: str = None):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library not installed. Run: pip install redis")
        
        self.redis_url = redis_url or REDIS_URL
        self._client = None
        self._lock = threading.Lock()
        self._local_cache: Dict[str, Any] = {}  # Fallback local cache
        self._connected = False
    
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            with self._lock:
                if self._client is None:
                    try:
                        self._client = redis.from_url(self.redis_url)
                        # Test connection
                        self._client.ping()
                        self._connected = True
                        logger.info(f"Redis connected: {self.redis_url}")
                    except redis.ConnectionError as e:
                        logger.warning(f"Redis connection failed: {e}. Using local cache fallback.")
                        self._client = None
                        self._connected = False
        return self._client
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            if self._connected and self.client:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
            else:
                # Local cache fallback
                return self._local_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cached value with TTL"""
        ttl = ttl or CACHE_TTL
        try:
            if self._connected and self.client:
                self.client.setex(key, ttl, json.dumps(value))
            else:
                # Local cache fallback (no TTL support)
                self._local_cache[key] = value
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            if self._connected and self.client:
                self.client.delete(key)
            else:
                self._local_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        count = 0
        try:
            if self._connected and self.client:
                for key in self.client.scan_iter(pattern):
                    self.client.delete(key)
                    count += 1
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        return count
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            if self._connected and self.client:
                return self.client.incrby(key, amount)
            else:
                self._local_cache[key] = self._local_cache.get(key, 0) + amount
                return self._local_cache[key]
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0


# ========================================
# Retry Logic
# ========================================

def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_backoff: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_retries: Maximum number of retries
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_backoff: Use exponential backoff
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} retries",
                            extra={"error": str(e), "attempt": attempt}
                        )
                        raise
                    
                    # Calculate delay
                    if exponential_backoff:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay
                    
                    logger.warning(
                        f"Function {func.__name__} failed, retrying in {delay}s",
                        extra={"error": str(e), "attempt": attempt, "delay": delay}
                    )
                    
                    time.sleep(delay)
        
        return wrapper
    return decorator


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_backoff: bool = True,
    exceptions: tuple = (Exception,)
):
    """
    Async retry decorator with exponential backoff
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            import asyncio
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"Async function {func.__name__} failed after {max_retries} retries",
                            extra={"error": str(e), "attempt": attempt}
                        )
                        raise
                    
                    # Calculate delay
                    if exponential_backoff:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay
                    
                    logger.warning(
                        f"Async function {func.__name__} failed, retrying in {delay}s",
                        extra={"error": str(e), "attempt": attempt, "delay": delay}
                    )
                    
                    await asyncio.sleep(delay)
        
        return wrapper
    return decorator


# ========================================
# Global instances
# ========================================

_db_manager: Optional[DatabaseManager] = None
_cache_manager: Optional[RedisCacheManager] = None


def get_db() -> DatabaseManager:
    """Get or create database manager"""
    global _db_manager
    if _db_manager is None:
        try:
            _db_manager = DatabaseManager()
        except ImportError:
            pass
    return _db_manager


def get_cache() -> Optional[RedisCacheManager]:
    """Get or create cache manager"""
    global _cache_manager
    if _cache_manager is None:
        try:
            _cache_manager = RedisCacheManager()
        except ImportError:
            pass
    return _cache_manager


def init_database(create_tables: bool = True):
    """Initialize database"""
    db = get_db()
    if db and create_tables:
        db.create_tables()
    return db


def init_cache():
    """Initialize cache"""
    return get_cache()


# ========================================
# Helper Functions
# ========================================

def save_analysis(
    url: str,
    analysis_data: Dict,
    report_id: str = None,
    ip_address: str = None,
    user_agent: str = None,
    duration_ms: int = None
) -> str:
    """Save analysis to database and cache"""
    from urllib.parse import urlparse
    
    report_id = report_id or os.urandom(16).hex()
    url_hash = hashlib.md5(url.encode()).hexdigest()
    domain = urlparse(url).netloc
    
    scores = analysis_data.get("scores", {})
    
    record_data = {
        "report_id": report_id,
        "url": url,
        "url_hash": url_hash,
        "domain": domain,
        "overall_score": analysis_data.get("health_score"),
        "technical_score": scores.get("technical"),
        "content_score": scores.get("content"),
        "performance_score": scores.get("performance"),
        "schema_score": scores.get("schema"),
        "ai_readiness_score": scores.get("ai_readiness"),
        "analysis_data": analysis_data,
        "status": "completed",
        "ip_address": ip_address,
        "user_agent": user_agent,
        "request_duration_ms": duration_ms,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=30)
    }
    
    # Save to database
    db = get_db()
    if db:
        try:
            with db.session() as session:
                record = AnalysisRecord(**record_data)
                session.add(record)
        except Exception as e:
            logger.error(f"Failed to save analysis to database: {e}")
    
    # Save to cache
    cache = get_cache()
    if cache:
        cache.set(f"analysis:{url_hash}", analysis_data, ttl=CACHE_TTL)
        cache.set(f"report:{report_id}", analysis_data, ttl=CACHE_TTL)
    
    return report_id


def get_cached_analysis(url: str = None, report_id: str = None) -> Optional[Dict]:
    """Get cached analysis"""
    cache = get_cache()
    if not cache:
        return None
    
    if url:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return cache.get(f"analysis:{url_hash}")
    
    if report_id:
        return cache.get(f"report:{report_id}")
    
    return None


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    
    try:
        db = init_database()
        print(f"✅ Database initialized: {db.database_url}")
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    try:
        cache = init_cache()
        if cache and cache._connected:
            print(f"✅ Redis cache connected")
        else:
            print("⚠️  Redis not connected (using local cache fallback)")
    except Exception as e:
        print(f"❌ Cache error: {e}")
