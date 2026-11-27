from app.models import OrderRequest, OrderResponse
from app.repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create_order(self, order: OrderRequest) -> OrderResponse:
        total = round(
            sum(item.quantity * item.unit_price for item in order.items),
            2,
        )
        return self._repository.save(order, total)

    def list_orders(self) -> list[OrderResponse]:
        return self._repository.list_all()