from pydantic import BaseModel, Field

class VendorDetailsRequestModel(BaseModel):
    vendor_ids: list[str] = Field(..., description="List of vendor IDs", min_length=1, max_length=100)


class VendorByCategoryNamesRequestModel(BaseModel):
    category_names: list[str] = Field(..., description="List of category names", min_length=1, max_length=100)