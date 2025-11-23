# Use a lightweight official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production

# Set the working directory
WORKDIR /usr/src/app


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Django project code
COPY . .

# Create staticfiles directory (needed for collectstatic)
RUN mkdir -p staticfiles

# Expose the port Gunicorn will run on
EXPOSE 8000

# Command to run the application using Gunicorn
# Adjust 'CarRentalService.wsgi' to match your project structure
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "CarRentalService.wsgi:application"]