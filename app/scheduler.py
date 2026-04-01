import asyncio
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Domain
from app.services import execute_campaign

running_domain_ids = set()

async def scheduler_loop():
    while True:
        try:
            db = SessionLocal()
            now = datetime.now()
            
            # Find domains that are SCHEDULED and within their auto_start_window
            domains = db.query(Domain).filter(Domain.status == "SCHEDULED").all()
            
            for domain in domains:
                if domain.id in running_domain_ids:
                    continue
                    
                if domain.expected_drop_at:
                    time_diff = (domain.expected_drop_at - now).total_seconds()
                    if time_diff <= domain.auto_start_window_seconds:
                        domain.status = "DROP_WINDOW"
                        db.commit()
                        
                        running_domain_ids.add(domain.id)
                        asyncio.create_task(run_campaign_task(domain.id))
                        
        except Exception as e:
            print(f"Scheduler error: {e}")
        finally:
            db.close()
            
        await asyncio.sleep(1)

async def run_campaign_task(domain_id: int):
    db = SessionLocal()
    try:
        await execute_campaign(domain_id, db)
    finally:
        db.close()
        if domain_id in running_domain_ids:
            running_domain_ids.remove(domain_id)
