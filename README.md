🚗 Car Rental Service API
A RESTful API developed with Django and Django REST Framework (DRF) to manage car inventory, handle rental bookings, track user activity, and provide essential backend services for a modern car rental platform.


1. Features
This API supports the following core functionalities:

Inventory Management: Full CRUD operations for cars (make, model, year, price, status).

User Management: Registration and profile management for customers.

Rental System: Dedicated endpoints for booking a car (with start/end dates) and managing returns.

Availability Checks: Logic to prevent double bookings.

History & Status: Retrieval of a user's current rentals and complete rental history.

Search & Filter: Advanced querying of the car list by make, model, year, price, and availability.

Authentication: Secure user authentication and authorization (via DRF).

2. API Endpoints


Resource	HTTP Method	Endpoint	Description
Cars	
GET	/vehicles/	List/Search/Filter all available cars.
POST /vehicles/	Add a new car (requires admin/staff).
PUT	/vehicles/{id}/	Update car details.
DELETE  /vehicles/{id}/	Delete a car.
GET	/vehicles/availability/	Check car availability for given dates.
Rentals	
GET	/rentals/	View all rental transactions (admin) or user's active rentals (user).
POST /rentals/	Book a car rental.
PUT	/rentals/{id}/return/	Mark a car as returned.
GET	/rentals/history/{user_id}/	Retrieve full rental history for a user.
Users
POST /users/register/	Register a new user.
GET/PUT	/users/{id}/	View/Update user profile.

3. Technology Stack
Category	Technology	Purpose
Backend Framework	Django	The primary web framework.
API	Django REST Framework (DRF)	Handles serialization, routing, and RESTful view creation.
Database	PostgreSQL / SQLite	Database management.
Environment	Python 3.10+	Development environment.
Testing	Postman	API validation and testing.




6. Project Structure
The project is modularized into core functional apps:

Car-Rental-Service/
├── CarRentalService/          # Project settings/config (settings.py, urls.py)
├── users/                     # Manages Custom User model and authentication
├── vehicles/                  # Manages the Car model and inventory logic
├── rentals/                   # Manages the Rental model and booking logic
├── manage.py                  # Django's command-line utility
└── venv/                      # Virtual environment
7. Timeline & Status
This project is being developed in a phased approach:

Week	Feature Focus	Status
1	Environment Setup, Model Creation (Car, User, Rental), Initial CRUD (Cars & Users).	[IN PROGRESS]
2	Rental booking logic, Car Return functionality.	[TODO]
3	Availability checks, Advanced Search & Filtering.	[TODO]
4	User Authentication & Authorization (Permissions).	[TODO]
5	Final Testing, Documentation (Swagger/DRF Docs), Deployment.	[TODO]


8. External API Integration
Future iterations will incorporate the following third-party services:

Stripe: Payment processing for rental transactions.

Smartcar API: Integration for real-time vehicle data (location, status).

Google Maps API: Used for location services (pickup/dropoff points) and distance calculation.

OpenWeatherMap API: To provide relevant local weather data for rental logistics.