from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Domain, Campaign, Attempt
from app.provider_registry import AVAILABLE_PROVIDER_NAMES
from app.providers_health import preflight_providers_for_domain
from app.nicit_service import NicitService
from app.config import settings
from app.paths import get_env_path
from datetime import datetime
import os
import asyncio
from app.services import execute_campaign

router = APIRouter()

# Setup templates
base_dir = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    domains_count = db.query(Domain).count()
    campaigns_count = db.query(Campaign).count()
    attempts_count = db.query(Attempt).count()
    
    running_campaigns = db.query(Campaign).filter(Campaign.status == "RUNNING").count()
    success_campaigns = db.query(Campaign).filter(Campaign.status == "SUCCESS").count()
    lost_campaigns = db.query(Campaign).filter(Campaign.status == "LOST").count()
    
    recent_domains = db.query(Domain).order_by(Domain.id.desc()).limit(5).all()
    recent_campaigns = db.query(Campaign).order_by(Campaign.id.desc()).limit(5).all()
    recent_attempts = db.query(Attempt).order_by(Attempt.id.desc()).limit(5).all()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "domains_count": domains_count,
        "campaigns_count": campaigns_count,
        "attempts_count": attempts_count,
        "running_campaigns": running_campaigns,
        "success_campaigns": success_campaigns,
        "lost_campaigns": lost_campaigns,
        "recent_domains": recent_domains,
        "recent_campaigns": recent_campaigns,
        "recent_attempts": recent_attempts
    })

@router.get("/domains", response_class=HTMLResponse)
async def domains_list(request: Request, db: Session = Depends(get_db)):
    domains = db.query(Domain).order_by(Domain.id.desc()).all()
    return templates.TemplateResponse("domains.html", {
        "request": request,
        "domains": domains,
        "available_providers": AVAILABLE_PROVIDER_NAMES
    })

@router.post("/domains/create")
async def domain_create(
    fqdn: str = Form(...),
    expected_drop_at: str = Form(...),
    auto_start_window_seconds: int = Form(60),
    burst_duration_seconds: int = Form(120),
    interval_ms: int = Form(500),
    providers: list[str] = Form([]),
    db: Session = Depends(get_db)
):
    dt = datetime.fromisoformat(expected_drop_at)
    domain = Domain(
        fqdn=fqdn,
        expected_drop_at=dt,
        auto_start_window_seconds=auto_start_window_seconds,
        burst_duration_seconds=burst_duration_seconds,
        interval_ms=interval_ms,
        selected_providers=",".join(providers)
    )
    db.add(domain)
    db.commit()
    return RedirectResponse(url="/domains", status_code=303)

@router.get("/domains/{domain_id}/edit", response_class=HTMLResponse)
async def domain_edit(request: Request, domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    selected_providers = domain.selected_providers.split(",") if domain.selected_providers else []
    
    health = preflight_providers_for_domain(domain.fqdn)
    
    return templates.TemplateResponse("domain_edit.html", {
        "request": request,
        "domain": domain,
        "available_providers": AVAILABLE_PROVIDER_NAMES,
        "selected_providers": selected_providers,
        "health": health
    })

@router.post("/domains/{domain_id}/edit")
async def domain_update(
    domain_id: int,
    fqdn: str = Form(...),
    expected_drop_at: str = Form(...),
    auto_start_window_seconds: int = Form(60),
    burst_duration_seconds: int = Form(120),
    interval_ms: int = Form(500),
    providers: list[str] = Form([]),
    db: Session = Depends(get_db)
):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if domain:
        domain.fqdn = fqdn
        domain.expected_drop_at = datetime.fromisoformat(expected_drop_at)
        domain.auto_start_window_seconds = auto_start_window_seconds
        domain.burst_duration_seconds = burst_duration_seconds
        domain.interval_ms = interval_ms
        domain.selected_providers = ",".join(providers)
        db.commit()
    return RedirectResponse(url="/domains", status_code=303)

@router.post("/domains/{domain_id}/start")
async def domain_start(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if domain and domain.status in ["SCHEDULED", "LOST"]:
        domain.status = "DROP_WINDOW"
        db.commit()
        from app.scheduler import running_domain_ids
        running_domain_ids.add(domain_id)
        asyncio.create_task(execute_campaign_bg(domain_id))
    return RedirectResponse(url="/campaigns", status_code=303)

async def execute_campaign_bg(domain_id: int):
    from app.database import SessionLocal
    from app.scheduler import running_domain_ids
    db = SessionLocal()
    try:
        await execute_campaign(domain_id, db)
    finally:
        db.close()
        if domain_id in running_domain_ids:
            running_domain_ids.remove(domain_id)

@router.get("/campaigns", response_class=HTMLResponse)
async def campaigns_list(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.id.desc()).all()
    return templates.TemplateResponse("campaigns.html", {
        "request": request,
        "campaigns": campaigns
    })

@router.get("/attempts", response_class=HTMLResponse)
async def attempts_list(request: Request, db: Session = Depends(get_db)):
    attempts = db.query(Attempt).order_by(Attempt.id.desc()).limit(100).all()
    return templates.TemplateResponse("attempts.html", {
        "request": request,
        "attempts": attempts
    })

@router.get("/nicit", response_class=HTMLResponse)
async def nicit_page(request: Request):
    service = NicitService()
    files = service.get_downloaded_files()
    return templates.TemplateResponse("nicit.html", {
        "request": request,
        "files": files
    })

@router.post("/nicit/download")
async def nicit_download(date_str: str = Form(...), slot: str = Form(...)):
    service = NicitService()
    # date_str comes as YYYY-MM-DD from input type="date"
    formatted_date = date_str.replace("-", "")
    await service.download_file(formatted_date, slot)
    return RedirectResponse(url="/nicit", status_code=303)

@router.post("/nicit/download-today-merged")
async def nicit_download_today_merged():
    service = NicitService()
    await service.download_and_merge_today()
    return RedirectResponse(url="/nicit", status_code=303)

@router.post("/nicit/open-folder")
async def nicit_open_folder():
    service = NicitService()
    service.open_download_folder()
    return RedirectResponse(url="/nicit", status_code=303)

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": settings
    })

@router.post("/settings")
async def settings_update(request: Request):
    form_data = await request.form()
    
    # Read current .env
    env_path = get_env_path()
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k] = v

    # Update with form data
    for key, value in form_data.items():
        if value == "on": # Checkbox
            env_vars[key] = "true"
        else:
            env_vars[key] = f'"{value}"' if " " in value or "{" in value else value

    # Handle unchecked checkboxes
    checkboxes = [
        "DYNADOT_ENABLED", "DYNADOT_IT_CONTACT_CONFIRMED",
        "OPENPROVIDER_ENABLED", "OPENPROVIDER_IT_CONTACTS_VERIFIED",
        "GANDI_ENABLED", "GANDI_IT_CONTACT_CONFIRMED"
    ]
    for cb in checkboxes:
        if cb not in form_data:
            env_vars[cb] = "false"

    # Write back to .env
    with open(env_path, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")
            
    # Note: Settings require app restart to take effect fully
    return RedirectResponse(url="/settings", status_code=303)

@router.get("/preflight", response_class=HTMLResponse)
async def preflight_page(request: Request, domain: str = ""):
    health = {}
    if domain:
        health = preflight_providers_for_domain(domain)
    return templates.TemplateResponse("providers_preflight.html", {
        "request": request,
        "domain": domain,
        "health": health
    })
