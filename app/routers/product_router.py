from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_product_handler
from app.handlers.product_handler import ProductHandler
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(
    prefix="/products", tags=["products"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, handler: ProductHandler = Depends(get_product_handler)):
    return handler.create(payload)


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    handler: ProductHandler = Depends(get_product_handler),
):
    return handler.update(product_id, payload)


@router.get("", response_model=list[ProductOut])
def list_products(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: ProductHandler = Depends(get_product_handler),
):
    return handler.list(limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, handler: ProductHandler = Depends(get_product_handler)):
    return handler.get(product_id)
