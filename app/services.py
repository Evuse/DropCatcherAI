import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Domain, Campaign, Attempt
from app.provider_registry import get_active_providers
from app.providers_health import preflight_providers_for_domain

async def execute_campaign(domain_id: int, db: Session):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        return

    # Create campaign
    campaign = Campaign(domain_id=domain.id, status="RUNNING")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Preflight providers
    selected_providers = [p.strip() for p in domain.selected_providers.split(",") if p.strip()]
    active_providers = get_active_providers()
    
    health_status = preflight_providers_for_domain(domain.fqdn)
    
    ready_providers = []
    for p_name in selected_providers:
        if p_name in active_providers and health_status.get(p_name) and health_status[p_name].ready:
            ready_providers.append(active_providers[p_name])

    if not ready_providers:
        campaign.status = "LOST"
        campaign.notes = "No ready providers available"
        campaign.ended_at = datetime.now()
        domain.status = "LOST"
        db.commit()
        return

    end_time = datetime.now().timestamp() + domain.burst_duration_seconds
    success = False
    winner = None

    while datetime.now().timestamp() < end_time and not success:
        tasks = []
        for provider in ready_providers:
            tasks.append(provider.register_domain(domain.fqdn))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                continue
                
            attempt = Attempt(
                campaign_id=campaign.id,
                registrar_name=result.registrar,
                success=result.success,
                latency_ms=result.latency_ms,
                message=result.message,
                raw_response=result.raw
            )
            db.add(attempt)
            
            if result.success:
                success = True
                winner = result.registrar
                break
                
        db.commit()
        
        if success:
            break
            
        await asyncio.sleep(domain.interval_ms / 1000.0)

    campaign.ended_at = datetime.now()
    if success:
        campaign.status = "SUCCESS"
        campaign.winner_registrar = winner
        domain.status = "REGISTERED_BY_US"
    else:
        campaign.status = "LOST"
        domain.status = "LOST"
        
    db.commit()
