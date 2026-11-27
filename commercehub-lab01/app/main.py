from fastapi import FastAPI, status

from app.models import OrderRequest, OrderResponse
from app.repository import OrderRepository
from app.service import OrderService

repository = OrderRepository()
service = OrderService(repository)

app = FastAPI(title="CommerceHub Order API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: OrderRequest) -> OrderResponse:
    return service.create_order(order)


@app.get("/orders", response_model=list[OrderResponse])
def list_orders() -> list[OrderResponse]:
    return service.list_orders()