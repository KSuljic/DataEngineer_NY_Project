# Use an official Python runtime as a base image
# "normal" python 3.8 didnt work...
FROM python:3.8-slim-bullseye

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run NY_AS_import.py when the container launches
# CMD probably also works
ENTRYPOINT ["python", "./NY_AS_import.py"]
