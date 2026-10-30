from fastapi import APIRouter, Depends
from ..auth import actor
from ..schemas import RecoveryRequest
from ..services import payments

router = APIRouter(prefix="/api", tags=["payments"])


@router.post('/orders/{order_id}/invoice')
def invoice(order_id: int, user=Depends(actor)):
    return payments.invoice(order_id, user)


@router.post('/orders/{order_id}/recover-invoice')
def recover_invoice(order_id: int, body: RecoveryRequest, user=Depends(actor)):
    return payments.recover_invoice(order_id, body, user)


@router.post('/orders/{order_id}/demo-pay')
def demo_pay(order_id: int, user=Depends(actor)):
    return payments.demo_pay(order_id, user)


@router.post('/orders/{order_id}/reconcile')
def reconcile(order_id: int, user=Depends(actor)):
    return payments.reconcile(order_id, user)


