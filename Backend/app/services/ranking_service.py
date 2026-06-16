from app.repositories import vendor_filter
from app.models.procurementRequest_model import ProcurementRequestModel
from app.services import weighted_score



def procurement_request_ranking(procurement_request: ProcurementRequestModel):
    filtered_vendors_data = vendor_filter.get_vendor_products_by_product(procurement_request.product_id)
    filtered_vendors = [vendor["vendor_id"] for vendor in filtered_vendors_data]
    
    vendor_feature_scores = vendor_filter.get_vendor_features_score(filtered_vendors, procurement_request.product_id)
    vendor_with_weighted_scores = weighted_score.calculate_weighted_score(vendor_feature_scores)
    return vendor_with_weighted_scores

