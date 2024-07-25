# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m myuser

# Set the working directory
WORKDIR /home/myuser

# Copy the current directory contents into the container at /app
COPY . /home/myuser

# Change the ownership of the application to the created user
RUN chown -R myuser:myuser /home/myuser

# Change the user to the created user
USER myuser

# Create a virtual environment
RUN python -m venv /home/myuser/venv

# Set the virtual environment as the current source
ENV PATH="/home/myuser/venv/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV MONGO_URL=mongodb://mongo

# Run app.py when the container launches
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]
