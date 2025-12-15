from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from app.models.guid import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base


class BusinessProcess(Base):
    __tablename__ = "business_processes"

    id = Column(GUID, primary_key=True, default=uuid4)
    tenant_id = Column(GUID, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    risks = relationship("Risk", back_populates="process", cascade="all, delete-orphan")
    controls = relationship("Control", back_populates="process", cascade="all, delete-orphan")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(GUID, primary_key=True, default=uuid4)
    tenant_id = Column(GUID, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    owner_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    process_id = Column(GUID, ForeignKey("business_processes.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    process = relationship("BusinessProcess", back_populates="risks")


class Control(Base):
    __tablename__ = "controls"

    id = Column(GUID, primary_key=True, default=uuid4)
    tenant_id = Column(GUID, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(100), nullable=True)  # e.g., Preventive, Detective
    owner_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    process_id = Column(GUID, ForeignKey("business_processes.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    process = relationship("BusinessProcess", back_populates="controls")
    regulatory_mappings = relationship(
        "ControlRegulatoryRequirement", back_populates="control", cascade="all, delete-orphan"
    )


class RegulatoryFramework(Base):
    __tablename__ = "regulatory_frameworks"

    id = Column(GUID, primary_key=True, default=uuid4)
    tenant_id = Column(GUID, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String(50), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    requirements = relationship(
        "RegulatoryRequirement", back_populates="framework", cascade="all, delete-orphan"
    )
    document_id = Column(GUID, ForeignKey("documents.id"), nullable=True)
    document = relationship("Document", back_populates="regulatory_framework")


class RegulatoryRequirement(Base):
    __tablename__ = "regulatory_requirements"

    id = Column(GUID, primary_key=True, default=uuid4)
    tenant_id = Column(GUID, nullable=False)
    framework_id = Column(
        GUID, ForeignKey("regulatory_frameworks.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)  # e.g., "Article 5.1"
    description = Column(Text, nullable=True)  # e.g., "Requirement text..."
    document_id = Column(GUID, ForeignKey("documents.id"), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    framework = relationship("RegulatoryFramework", back_populates="requirements")
    document = relationship("Document", back_populates="regulatory_requirement")
    control_mappings = relationship(
        "ControlRegulatoryRequirement", back_populates="regulatory_requirement", cascade="all, delete-orphan"
    )