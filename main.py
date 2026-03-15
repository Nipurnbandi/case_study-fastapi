from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel,create_model,Field
from typing import Any, Dict, Type, List, Literal
from datetime import date

app=FastAPI()


CATEGORY_DEFINITIONS = {
    1: {"name": "Laptop",
        "fields": {"cpu_type": (str, ...), "ram_gb": (int, ...)}},
    2: {"name": "T-Shirt",
        "fields": {"color": (str, ...), "size": (Literal['S','M','L','XL'], ...)}},
    3: {"name": "Equipment",
        "fields": {"voltage": (int, 220), "warranty_expires_on": (date, ...)}}
}


def get_product_model(category_id:int)->Type[BaseModel]:
    category=CATEGORY_DEFINITIONS.get(category_id)
    if not category:
        raise HTTPException(status_code=404)
    

    base_fields={'sku':(str,...),
                'price': (float, Field(..., gt=0))
                }


    all_fields = {**base_fields, **category["fields"]}

    ProductModel = create_model(
        f'Dynamic{category["name"]}Model',
        **all_fields
    )
    return ProductModel


# post request
@app.post("/products/{category_id}")
async def create_dynamic_product(
        category_id: int,
        request_body: Dict[str, Any]
):
    Model = get_product_model(category_id)
    try:
        validate_product = Model(**request_body)
    except Exception as error:
        raise HTTPException(status_code=422, detail=error)
    return {
        "message" : "Product created successfully",
        "product": validate_product.model_dump()
        }