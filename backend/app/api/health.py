from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.guild import Guild

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check service health and database status"""
    try:
        # Check if database has guilds (indicating warmup is complete)
        guild_count = db.query(Guild).count()
        return {
            "status": "healthy",
            "database": {
                "status": "warmed" if guild_count > 0 else "initializing",
                "guild_count": guild_count
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 