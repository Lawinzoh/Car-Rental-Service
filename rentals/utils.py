from datetime import timedelta, datetime
from decimal import Decimal
from django.db.models import Q
from .models import Rental


def calculate_rental_cost(rental_start, rental_end, rental_rate_per_day):
    """
    Calculate the total cost of a rental based on duration and vehicle rate.
    """
    
    # 1. Ensure the rate is a Decimal object
    rate_decimal = Decimal(rental_rate_per_day) 
    
    duration: timedelta = rental_end - rental_start
    total_seconds = duration.total_seconds() 
    total_days = total_seconds / (60 * 60 * 24) 

    # 2. Robustly determine full days charged
    # Use math.ceil if you want a cleaner way to round up partial days
    import math
    total_days_charged = math.ceil(total_days) 
    
    # 3. Final calculation using Decimals
    total_cost = Decimal(total_days_charged) * rate_decimal
    return total_cost

def is_vehicle_available_for_new_dates(vehicle, start_date, end_date, exclude_rental_id=None):
    """
    Checks if a specific vehicle is available between start_date and end_date, 
    excluding a specified rental ID (for extensions/modifications).
    """
    
    # 1. Start with rentals that are active or confirmed
    conflicting_rentals = Rental.objects.filter(
        vehicle=vehicle,
        status__in=['active', 'confirmed']
    )

    # 2. Exclude the current rental being extended/modified
    if exclude_rental_id:
        conflicting_rentals = conflicting_rentals.exclude(pk=exclude_rental_id)

    # 3. Check for overlaps using Q objects
    # A conflict occurs if:
    #   - The new rental starts before the existing one ends AND
    #   - The new rental ends after the existing one starts.
    overlap_query = Q(rental_start__lt=end_date) & Q(rental_end__gt=start_date)
    
    # If any conflicting rentals match the overlap query, the car is NOT available.
    if conflicting_rentals.filter(overlap_query).exists():
        return False
        
    return True