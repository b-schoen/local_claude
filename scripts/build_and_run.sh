#!/bin/bash
set -x

export DOCKER_IMAGE_TAG=bschoen-local-claude

function update_requirements {
    # Echo before activating the virtual environment
    echo "Activating the virtual environment..."

    # Activate the virtual environment
    source /path/to/your/venv/bin/activate

    # Echo after activating the virtual environment
    echo "Virtual environment activated."

    # Echo before capturing the current requirements
    echo "Capturing the current requirements in the virtual environment..."

    # Capture the current requirements in the virtual environment
    pip freeze >requirements.txt

    # Echo after capturing the current requirements
    echo "Current requirements captured in requirements.txt."

    # Echo before deactivating the virtual environment
    echo "Deactivating the virtual environment..."

    # Deactivate the virtual environment
    deactivate

    # Echo after deactivating the virtual environment
    echo "Virtual environment deactivated."
}

function build_docker_image {
    # Echo before building the Docker image
    echo "Building the Docker image..."

    docker build -t $DOCKER_IMAGE_TAG .

    # Echo after building the Docker image
    echo "Docker image built."
}

function run_docker_container {
    # Echo before running the Docker container
    echo "Running the Docker container..."

    docker run -it --rm $DOCKER_IMAGE_TAG

    # Echo after running the Docker container
    echo "Docker container running."
}

update_requirements

build_docker_image

run_docker_container
