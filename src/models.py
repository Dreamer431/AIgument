from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()

class Session(db.Model):
    """对话会话模型"""
    __tablename__ = 'session'
    __table_args__ = (
        db.Index('idx_session_type', 'session_type'),
        db.Index('idx_created_at', 'created_at'),
        db.Index('idx_session_type_created', 'session_type', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    session_type = db.Column(db.String(20), nullable=False, index=True)  # debate/chat/qa
    topic = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    settings = db.Column(JSON)  # 存储会话设置（轮次、角色等）
    messages = db.relationship('Message', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'session_type': self.session_type,
            'topic': self.topic,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'settings': self.settings,
            'messages': [msg.to_dict() for msg in self.messages]
        }

class Message(db.Model):
    """消息记录模型"""
    __tablename__ = 'message'
    __table_args__ = (
        db.Index('idx_session_id', 'session_id'),
        db.Index('idx_session_created', 'session_id', 'created_at'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(50), nullable=False)  # positive/negative/user/assistant
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    meta_info = db.Column(JSON)  # 存储额外信息（token统计、模型信息等）

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'meta_info': self.meta_info
        } 