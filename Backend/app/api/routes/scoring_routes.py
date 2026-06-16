from fastapi import APIRouter

from app.models.procurementRequest_model import ProcurementRequestModel
from app.services import scoring_service

router = APIRouter()


@router.get("/scoring/weight-configs")
def get_weight_configs():
    return scoring_service.get_weight_configs()


@router.get("/scoring/weight-configs/default")
def get_default_weight_config():
    return scoring_service.get_default_weight_config()


@router.get("/scoring/weight-configs/{config_id}")
def get_weight_config(config_id: str):
    return scoring_service.get_weight_config(config_id)


@router.get("/scoring/vendor-scores/latest")
def get_vendor_latest_scores(vendor_id: str | None = None):
    return scoring_service.get_vendor_latest_scores(vendor_id)


@router.get("/scoring/features/{product_id}")
def get_vendor_features(product_id: str):
    return scoring_service.get_vendor_features(product_id)


@router.get("/scoring/seasonal-demand/{product_id}")
def get_seasonal_demand(product_id: str):
    return scoring_service.get_seasonal_demand(product_id)


@router.get("/scoring/quality/{vendor_id}")
def get_quality_scores(vendor_id: str):
    return scoring_service.get_quality_scores(vendor_id)


@router.get("/scoring/risk/{vendor_id}")
def get_risk_scores(vendor_id: str):
    return scoring_service.get_risk_scores(vendor_id)


@router.get("/scoring/historical-performance/{vendor_id}")
def get_historical_performance(vendor_id: str):
    return scoring_service.get_historical_performance(vendor_id)


@router.get("/scoring/recommendations/{request_id}")
def get_recommendations_by_request(request_id: str):
    return scoring_service.get_recommendations_by_request(request_id)


@router.get("/scoring/model/status")
def get_model_status():
    """Check if XGBoost model is trained and ready for prediction."""
    return scoring_service.get_model_status()


@router.post("/scoring/train")
def train_xgboost_model():
    """Train XGBoost from vendor_historical_performance and save model file."""
    return scoring_service.train_xgboost_model()


@router.post("/scoring/predict")
def predict_vendors(procurement_request: ProcurementRequestModel):
    return scoring_service.predict_vendors(procurement_request)
