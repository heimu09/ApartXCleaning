# Pull base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /ApartXCleaning

# Install dependencies
COPY Pipfile Pipfile.lock /ApartXCleaning/
RUN pip install pipenv && pipenv install --system

# Copy project
COPY . /ApartXCleaning/
