from fastapi import APIRouter, Depends
from ..auth import actor
from ..schemas import OrderRequest, CollectionRequest
from ..services import orders

router = APIRouter(prefix="/api", tags=["orders"])


@router.post('/orders', status_code=201)
def create_order(body: OrderRequest, user=Depends(actor)):
    return orders.create_order(body, user)


@router.post('/orders/{order_id}/approve')
def approve(order_id: int, user=Depends(actor)):
    return orders.approve(order_id, user)


@router.post('/orders/{order_id}/cancel')
def cancel(order_id: int, user=Depends(actor)):
    return orders.cancel(order_id, user)


@router.post('/orders/{order_id}/collect')
def collect(order_id: int, body: CollectionRequest, user=Depends(actor)):
    return orders.collect(order_id, body, user)


@router.get('/orders/{order_id}/timeline')
def timeline(order_id: int, user=Depends(actor)):
    return orders.timeline(order_id, user)


