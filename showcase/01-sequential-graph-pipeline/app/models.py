"""Pydantic data models for sequential order pipeline."""

from pydantic import BaseModel, Field


class OrderItem(BaseModel):
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., gt=0, description="Item quantity")
    unit_price: float = Field(..., gt=0, description="Unit price in USD")


class OrderInput(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_email: str = Field(..., min_length=3)
    items: list[OrderItem] = Field(..., min_length=1)
    shipping_city: str = Field(default="New York")


class ValidatedOrder(BaseModel):
    order_id: str
    customer_name: str
    customer_email: str
    items: list[OrderItem]
    subtotal: float


class OrderWithFinancials(BaseModel):
    order_id: str
    customer_name: str
    customer_email: str
    subtotal: float
    tax: float
    shipping_fee: float
    grand_total: float


class OrderConfirmation(BaseModel):
    order_id: str
    invoice_number: str
    customer_name: str
    customer_email: str
    grand_total: float
    status: str
    message: str
