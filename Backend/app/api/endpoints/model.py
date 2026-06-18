from fastapi import APIRouter

from app.models.procurement_request import ProcurementRequest
from app.services.scoring import orchestrator as scoring_service

router = APIRouter(tags=["scoring"])


@router.get("/model/status")
def get_model_status():
    return scoring_service.get_model_status()


@router.post("/model/train")
def train_xgboost_model():
    return scoring_service.train_xgboost_model()


@router.post("/rank")
def rank_vendors(procurement_request: ProcurementRequest):
    """Merged rule-engine + ML vendor ranking."""
    return scoring_service.rank_vendors(procurement_request)


@router.post("/predict")
def predict_vendors(procurement_request: ProcurementRequest):
    """ML-heavy vendor ranking (70% ML by default)."""
    return scoring_service.predict_vendors(procurement_request)
