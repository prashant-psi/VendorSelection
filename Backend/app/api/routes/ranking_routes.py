
from fastapi.routing import APIRouter
from app.models.procurementRequest_model import ProcurementRequestModel
from app.services import ranking_service

router = APIRouter()

@router.post("/rank")
def vendor_rank(procurement_request: ProcurementRequestModel):
    return ranking_service.procurement_request_ranking(procurement_request)