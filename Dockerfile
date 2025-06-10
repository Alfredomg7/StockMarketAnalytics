FROM python:3.11-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY . ./

# Use cache for dependencies installation
RUN pip install -r requirements.txt

# Debug step to list files
RUN ls -la /app

# Run the app
CMD ["gunicorn", "--bind", ":8080", "--workers", "1", "--threads", "8", "--timeout", "0", "app:server"]