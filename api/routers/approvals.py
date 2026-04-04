from fastapi import APIRouter, Request
from typing import Dict, Any
import uuid

router = APIRouter()

@router.get("/approvals/pending")
async def get_pending_approvals(request: Request):
    """Get all pending approvals"""
    pending = request.app.state.pending_approvals
    return [
        {
            "id": approval_id,
            "tool_name": data["confirmation"].tool_name,
            "description": data["confirmation"].description,
            "params": data["confirmation"].params,
            "is_dangerous": data["confirmation"].is_dangerous,
            "affected_paths": [str(p) for p in data["confirmation"].affected_paths],
            "timestamp": data["timestamp"]
        }
        for approval_id, data in pending.items()
    ]

@router.get("/approvals/status/{approval_id}")
async def get_approval_status(approval_id: str, request: Request):
    """Get status of a specific approval"""
    pending = request.app.state.pending_approvals
    
    if approval_id in pending:
        return {
            "id": approval_id,
            "status": "pending" if pending[approval_id]["approved"] is None else "approved" if pending[approval_id]["approved"] else "rejected",
            "decision": pending[approval_id]["approved"]
        }
    else:
        return {"error": "Approval not found"}, 404
