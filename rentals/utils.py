from datetime import timedelta
from decimal import Decimal


def calculate_rental_cost(rental_start, rental_end, rental_rate_per_day):
    """
    Calculate the total cost of a rental based on duration and vehicle rate.
    """
    duration: timedelta = rental_end - rental_start
    total_days = duration.total_seconds() / (60 * 60 * 24) # Convert duration to days
    total_days_charged = int(total_days) if total_days == int(total_days) else int(total_days) + 1 #ensure a fraction of a day is charged as a full day partial day
    total_cost = Decimal(total_days_charged) * rental_rate_per_day
    return total_cost