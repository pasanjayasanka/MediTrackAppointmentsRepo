FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code to the container
COPY patient_service.py /app

# Install dependencies
RUN pip install flask pymysql

# Expose the port the application will run on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "appointment_service.py"]
