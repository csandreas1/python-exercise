FROM python:3.11.4-buster

WORKDIR /app

# Copy only pyproject.toml and poetry.lock to leverage Docker cache if only dependencies change
COPY pyproject.toml poetry.lock ./

# Install system dependencies and Poetry
RUN set -xe \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install virtualenvwrapper poetry \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project directory
COPY . .

# Install project dependencies
RUN poetry install --no-root

# Set the command to start your application
CMD ["tail", "-f", "/dev/null"]
