# Use the official Python 3.12 image as the base image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first since that changes less frequently than other files
COPY requirements.txt /app/requirements.txt

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY local_claude /app/local_claude

# By default start in a bash shell
CMD ["/bin/bash"]
