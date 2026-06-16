from app.models.procurementRequest_model import ProcurementRequestModel
from app.services import scoring_service


def procurement_request_ranking(procurement_request: ProcurementRequestModel):
    return scoring_service.rank_vendors(procurement_request)

