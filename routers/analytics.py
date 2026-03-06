from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()

REPORT_PATH = "data/rejected_analytics.csv"

@router.get("/analytics/export", tags=["analytics"])
async def export_rejected_analytics():
    """
    Returns the rejected candidates CSV file for download.
    Used for EdTech skill gap analysis.
    """
    if not os.path.exists(REPORT_PATH):
        raise HTTPException(
            status_code=404, 
            detail="Analytics report not found. No candidates have been rejected yet."
        )
    
    return FileResponse(
        path=REPORT_PATH,
        filename="rejected_skill_gaps.csv",
        media_type="text/csv"
    )
