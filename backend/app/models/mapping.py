from sqlalchemy import Column, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from .base import Base


class ControlRegulatoryRequirement(Base):
    __tablename__ = "controls_regulatory_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    control_id = Column(
        UUID(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), nullable=False
    )
    regulatory_requirement_id = Column(
        UUID(as_uuid=True),
        ForeignKey("regulatory_requirements.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    control = relationship("Control", back_populates="regulatory_mappings")
    regulatory_requirement = relationship(
        "RegulatoryRequirement", back_populates="control_mappings"
    )

    __table_args__ = (
        UniqueConstraint(
            "control_id",
            "regulatory_requirement_id",
            "tenant_id",
            name="unique_control_requirement_per_tenant",
        ),
    )
