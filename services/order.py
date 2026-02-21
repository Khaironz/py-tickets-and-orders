from datetime import datetime
from typing import List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils.dateparse import parse_datetime

from db.models import Order, Ticket

User = get_user_model()


@transaction.atomic
def create_order(
    tickets: List[dict],
    username: str,
    date: Optional[str] = None,
) -> Order:
    user = User.objects.get(username=username)
    order = Order.objects.create(user=user)
    if date is not None:
        if isinstance(date, str):
            parsed_date = parse_datetime(date)
            if parsed_date is None:
                parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M")
        else:
            parsed_date = date
        Order.objects.filter(id=order.id).update(created_at=parsed_date)
        order.refresh_from_db()
    for ticket_data in tickets:
        Ticket.objects.create(
            order=order,
            row=ticket_data["row"],
            seat=ticket_data["seat"],
            movie_session_id=ticket_data["movie_session"],
        )
    return order


def get_orders(username: Optional[str] = None) -> QuerySet[Order]:
    queryset = Order.objects.all()
    if username is not None:
        queryset = queryset.filter(user__username=username)
    return queryset
