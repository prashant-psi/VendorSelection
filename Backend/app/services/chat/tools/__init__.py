from app.services.chat.tools.vendor_tools import (
    get_categories,
    get_historical_performance,
    get_quality_scores,
    get_risk_scores,
    get_vendor_certifications,
    get_vendor_details,
    get_vendor_latest_scores,
    get_vendor_production_capacity,
    get_vendors_by_category,
    search_vendors,
)
from app.services.chat.tools.product_tools import (
    get_product_detail,
    get_scoring_features,
    get_seasonal_demand,
    search_products,
)
from app.services.chat.tools.ranking_tools import (
    predict_vendors,
    rank_vendors,
)
from app.services.chat.tools.analytics_tools import (
    get_compliance_certifications,
    get_recommendations,
    get_weather_logistics_impact,
    get_weight_configs,
)

CHAT_TOOLS = [
    # vendor
    search_vendors,
    get_vendor_details,
    get_vendor_latest_scores,
    get_quality_scores,
    get_risk_scores,
    get_historical_performance,
    get_vendor_production_capacity,
    get_vendors_by_category,
    get_categories,
    get_vendor_certifications,
    # product
    search_products,
    get_product_detail,
    get_seasonal_demand,
    get_scoring_features,
    # ranking
    rank_vendors,
    predict_vendors,
    # analytics
    get_recommendations,
    get_weather_logistics_impact,
    get_compliance_certifications,
    get_weight_configs,
]
