from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import apaginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import User, get_async_session
from app.models.compliance import Control, Risk, BusinessProcess, RegulatoryFramework, RegulatoryRequirement
from app.schemas import (
    ControlCreate,
    ControlUpdate,
    ControlRead,
    RiskCreate,
    RiskUpdate,
    RiskRead,
    BusinessProcessCreate,
    BusinessProcessUpdate,
    BusinessProcessRead,
    RegulatoryFrameworkCreate,
    RegulatoryFrameworkUpdate,
    RegulatoryFrameworkRead,
    RegulatoryRequirementCreate,
    RegulatoryRequirementUpdate,
    RegulatoryRequirementRead,
)
from app.core.deps import get_current_active_user as current_active_user

router = APIRouter()

# --- Controls ---


@router.post(
    "/controls", response_model=ControlRead, tags=["controls"], status_code=201
)
async def create_control(
    control: ControlCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id

    db_control = Control(**control.model_dump(), tenant_id=tenant_id, owner_id=user.id)
    db.add(db_control)
    await db.commit()
    await db.refresh(db_control)
    return db_control


@router.get("/controls", response_model=Page[ControlRead], tags=["controls"])
async def read_controls(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    tenant_id = user.tenant_id
    params = Params(page=page, size=size)
    query = select(Control).filter(Control.tenant_id == tenant_id)
    return await apaginate(db, query, params)


@router.get("/controls/{control_id}", response_model=ControlRead, tags=["controls"])
async def read_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Control).filter(Control.id == control_id, Control.tenant_id == tenant_id)
    )
    control = result.scalars().first()
    if not control:
        raise HTTPException(
            status_code=404, detail="Control not found or access denied"
        )
    return control


@router.put("/controls/{control_id}", response_model=ControlRead, tags=["controls"])
async def update_control(
    control_id: UUID,
    control_update: ControlUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Control).filter(Control.id == control_id, Control.tenant_id == tenant_id)
    )
    control = result.scalars().first()
    if not control:
        raise HTTPException(
            status_code=404, detail="Control not found or access denied"
        )

    for key, value in control_update.model_dump(exclude_unset=True).items():
        setattr(control, key, value)

    await db.commit()
    await db.refresh(control)
    return control


@router.delete("/controls/{control_id}", status_code=204, tags=["controls"])
async def delete_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Control).filter(Control.id == control_id, Control.tenant_id == tenant_id)
    )
    control = result.scalars().first()
    if not control:
        raise HTTPException(
            status_code=404, detail="Control not found or access denied"
        )

    await db.delete(control)
    await db.commit()
    return


# --- Risks ---


@router.post("/risks", response_model=RiskRead, tags=["risks"], status_code=201)
async def create_risk(
    risk: RiskCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    db_risk = Risk(**risk.model_dump(), tenant_id=tenant_id, owner_id=user.id)
    db.add(db_risk)
    await db.commit()
    await db.refresh(db_risk)
    return db_risk


@router.get("/risks", response_model=Page[RiskRead], tags=["risks"])
async def read_risks(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    tenant_id = user.tenant_id
    params = Params(page=page, size=size)
    query = select(Risk).filter(Risk.tenant_id == tenant_id)
    return await apaginate(db, query, params)


@router.get("/risks/{risk_id}", response_model=RiskRead, tags=["risks"])
async def read_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Risk).filter(Risk.id == risk_id, Risk.tenant_id == tenant_id)
    )
    risk = result.scalars().first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found or access denied")
    return risk


@router.put("/risks/{risk_id}", response_model=RiskRead, tags=["risks"])
async def update_risk(
    risk_id: UUID,
    risk_update: RiskUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Risk).filter(Risk.id == risk_id, Risk.tenant_id == tenant_id)
    )
    risk = result.scalars().first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found or access denied")

    for key, value in risk_update.model_dump(exclude_unset=True).items():
        setattr(risk, key, value)

    await db.commit()
    await db.refresh(risk)
    return risk


@router.delete("/risks/{risk_id}", status_code=204, tags=["risks"])
async def delete_risk(
    risk_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(Risk).filter(Risk.id == risk_id, Risk.tenant_id == tenant_id)
    )
    risk = result.scalars().first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found or access denied")

    await db.delete(risk)
    await db.commit()
    return


# --- Business Processes ---


@router.post(
    "/business-processes",
    response_model=BusinessProcessRead,
    tags=["business-processes"],
    status_code=201,
)
async def create_business_process(
    process: BusinessProcessCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    db_process = BusinessProcess(
        **process.model_dump(), tenant_id=tenant_id, owner_id=user.id
    )
    db.add(db_process)
    await db.commit()
    await db.refresh(db_process)
    return db_process


@router.get(
    "/business-processes",
    response_model=Page[BusinessProcessRead],
    tags=["business-processes"],
)
async def read_business_processes(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    tenant_id = user.tenant_id
    params = Params(page=page, size=size)
    query = select(BusinessProcess).filter(BusinessProcess.tenant_id == tenant_id)
    return await apaginate(db, query, params)


@router.get(
    "/business-processes/{process_id}",
    response_model=BusinessProcessRead,
    tags=["business-processes"],
)
async def read_business_process(
    process_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(BusinessProcess).filter(
            BusinessProcess.id == process_id, BusinessProcess.tenant_id == tenant_id
        )
    )
    process = result.scalars().first()
    if not process:
        raise HTTPException(
            status_code=404, detail="Business Process not found or access denied"
        )
    return process


@router.put(
    "/business-processes/{process_id}",
    response_model=BusinessProcessRead,
    tags=["business-processes"],
)
async def update_business_process(
    process_id: UUID,
    process_update: BusinessProcessUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(BusinessProcess).filter(
            BusinessProcess.id == process_id, BusinessProcess.tenant_id == tenant_id
        )
    )
    process = result.scalars().first()
    if not process:
        raise HTTPException(
            status_code=404, detail="Business Process not found or access denied"
        )

    for key, value in process_update.model_dump(exclude_unset=True).items():
        setattr(process, key, value)

    await db.commit()
    await db.refresh(process)
    return process


@router.delete(
    "/business-processes/{process_id}", status_code=204, tags=["business-processes"]
)
async def delete_business_process(
    process_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(BusinessProcess).filter(
            BusinessProcess.id == process_id, BusinessProcess.tenant_id == tenant_id
        )
    )
    process = result.scalars().first()
    if not process:
        raise HTTPException(
            status_code=404, detail="Business Process not found or access denied"
        )

    await db.delete(process)
    await db.commit()
    return


# --- Regulatory Frameworks ---


@router.post(
    "/regulatory-frameworks",
    response_model=RegulatoryFrameworkRead,
    tags=["regulatory-frameworks"],
    status_code=201,
)
async def create_regulatory_framework(
    framework: RegulatoryFrameworkCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    db_framework = RegulatoryFramework(**framework.model_dump(), tenant_id=tenant_id)
    db.add(db_framework)
    await db.commit()
    await db.refresh(db_framework)
    return db_framework


@router.get(
    "/regulatory-frameworks",
    response_model=Page[RegulatoryFrameworkRead],
    tags=["regulatory-frameworks"],
)
async def read_regulatory_frameworks(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    tenant_id = user.tenant_id
    params = Params(page=page, size=size)
    query = select(RegulatoryFramework).filter(
        RegulatoryFramework.tenant_id == tenant_id
    )
    return await apaginate(db, query, params)


@router.get(
    "/regulatory-frameworks/{framework_id}",
    response_model=RegulatoryFrameworkRead,
    tags=["regulatory-frameworks"],
)
async def read_regulatory_framework(
    framework_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryFramework).filter(
            RegulatoryFramework.id == framework_id,
            RegulatoryFramework.tenant_id == tenant_id,
        )
    )
    framework = result.scalars().first()
    if not framework:
        raise HTTPException(
            status_code=404, detail="Regulatory Framework not found or access denied"
        )
    return framework


@router.put(
    "/regulatory-frameworks/{framework_id}",
    response_model=RegulatoryFrameworkRead,
    tags=["regulatory-frameworks"],
)
async def update_regulatory_framework(
    framework_id: UUID,
    framework_update: RegulatoryFrameworkUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryFramework).filter(
            RegulatoryFramework.id == framework_id,
            RegulatoryFramework.tenant_id == tenant_id,
        )
    )
    framework = result.scalars().first()
    if not framework:
        raise HTTPException(
            status_code=404, detail="Regulatory Framework not found or access denied"
        )

    for key, value in framework_update.model_dump(exclude_unset=True).items():
        setattr(framework, key, value)

    await db.commit()
    await db.refresh(framework)
    return framework


@router.delete(
    "/regulatory-frameworks/{framework_id}",
    status_code=204,
    tags=["regulatory-frameworks"],
)
async def delete_regulatory_framework(
    framework_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryFramework).filter(
            RegulatoryFramework.id == framework_id,
            RegulatoryFramework.tenant_id == tenant_id,
        )
    )
    framework = result.scalars().first()
    if not framework:
        raise HTTPException(
            status_code=404, detail="Regulatory Framework not found or access denied"
        )

    await db.delete(framework)
    await db.commit()
    return


# --- Regulatory Requirements ---


@router.post(
    "/regulatory-requirements",
    response_model=RegulatoryRequirementRead,
    tags=["regulatory-requirements"],
    status_code=201,
)
async def create_regulatory_requirement(
    requirement: RegulatoryRequirementCreate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    # Verify framework exists and belongs to tenant
    framework_result = await db.execute(
        select(RegulatoryFramework).filter(
            RegulatoryFramework.id == requirement.framework_id,
            RegulatoryFramework.tenant_id == tenant_id,
        )
    )
    if not framework_result.scalars().first():
        raise HTTPException(
            status_code=404, detail="Regulatory Framework not found or access denied"
        )

    db_requirement = RegulatoryRequirement(**requirement.model_dump(), tenant_id=tenant_id)
    db.add(db_requirement)
    await db.commit()
    await db.refresh(db_requirement)
    return db_requirement


@router.get(
    "/regulatory-requirements",
    response_model=Page[RegulatoryRequirementRead],
    tags=["regulatory-requirements"],
)
async def read_regulatory_requirements(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
    framework_id: UUID | None = Query(None, description="Filter by framework ID"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    tenant_id = user.tenant_id
    params = Params(page=page, size=size)
    query = select(RegulatoryRequirement).filter(
        RegulatoryRequirement.tenant_id == tenant_id
    )
    if framework_id:
        query = query.filter(RegulatoryRequirement.framework_id == framework_id)
    return await apaginate(db, query, params)


@router.get(
    "/regulatory-requirements/{requirement_id}",
    response_model=RegulatoryRequirementRead,
    tags=["regulatory-requirements"],
)
async def read_regulatory_requirement(
    requirement_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryRequirement).filter(
            RegulatoryRequirement.id == requirement_id,
            RegulatoryRequirement.tenant_id == tenant_id,
        )
    )
    requirement = result.scalars().first()
    if not requirement:
        raise HTTPException(
            status_code=404, detail="Regulatory Requirement not found or access denied"
        )
    return requirement


@router.put(
    "/regulatory-requirements/{requirement_id}",
    response_model=RegulatoryRequirementRead,
    tags=["regulatory-requirements"],
)
async def update_regulatory_requirement(
    requirement_id: UUID,
    requirement_update: RegulatoryRequirementUpdate,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryRequirement).filter(
            RegulatoryRequirement.id == requirement_id,
            RegulatoryRequirement.tenant_id == tenant_id,
        )
    )
    requirement = result.scalars().first()
    if not requirement:
        raise HTTPException(
            status_code=404, detail="Regulatory Requirement not found or access denied"
        )

    # If framework_id is being updated, verify new framework exists and belongs to tenant
    if requirement_update.framework_id and requirement_update.framework_id != requirement.framework_id:
        framework_result = await db.execute(
            select(RegulatoryFramework).filter(
                RegulatoryFramework.id == requirement_update.framework_id,
                RegulatoryFramework.tenant_id == tenant_id,
            )
        )
        if not framework_result.scalars().first():
            raise HTTPException(
                status_code=404, detail="Regulatory Framework not found or access denied"
            )

    for key, value in requirement_update.model_dump(exclude_unset=True).items():
        setattr(requirement, key, value)

    await db.commit()
    await db.refresh(requirement)
    return requirement


@router.delete(
    "/regulatory-requirements/{requirement_id}",
    status_code=204,
    tags=["regulatory-requirements"],
)
async def delete_regulatory_requirement(
    requirement_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    tenant_id = user.tenant_id
    result = await db.execute(
        select(RegulatoryRequirement).filter(
            RegulatoryRequirement.id == requirement_id,
            RegulatoryRequirement.tenant_id == tenant_id,
        )
    )
    requirement = result.scalars().first()
    if not requirement:
        raise HTTPException(
            status_code=404, detail="Regulatory Requirement not found or access denied"
        )

    await db.delete(requirement)
    await db.commit()
    return
