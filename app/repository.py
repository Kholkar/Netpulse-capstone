from app.models import OrderItem, OrderRequest, OrderResponse


class OrderRepository:
    def __init__(self) -> None:
        self._orders: list[OrderResponse] = []
        self._next_order_id = 1

    def save(self, order: OrderRequest, total: float) -> OrderResponse:
        saved_order = OrderResponse(
            order_id=self._next_order_id,
            customer_name=order.customer_name,
            items=[OrderItem.model_validate(item) for item in order.items],
            total=total,
        )
        self._orders.append(saved_order)
        self._next_order_id += 1
        return saved_order

    def list_all(self) -> list[OrderResponse]:
        return [order.model_copy(deep=True) for order in self._orders]

    def clear(self) -> None:
        self._orders.clear()
        self._next_order_id = 1