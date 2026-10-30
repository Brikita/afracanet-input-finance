from fastapi import APIRouter, Depends

from ..auth import actor
from ..contracts.catalogue import ProductEdit
from ..contracts.requests import AssistantRequest
from ..services import catalogue

router = APIRouter(prefix="/api", tags=["catalogue"])


@router.put("/products/{product_id}")
def product_save(product_id: str, body: ProductEdit, user=Depends(actor)):
    return catalogue.product_save(product_id, body, user)


@router.post("/assistant")
def interpret_request(body: AssistantRequest, user=Depends(actor)):
    return catalogue.interpret_request(body, user)
