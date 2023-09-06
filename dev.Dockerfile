FROM tensorflow/tensorflow:2.11.0-gpu

WORKDIR /flask-docker

RUN pip install --no-cache --upgrade pip setuptools

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN apt update && apt install tzdata -y
ENV TZ=Asia/Bangkok

RUN pip install Flask

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt

COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Install Gunicorn
RUN pip install gunicorn

# Expose the port the app runs on
EXPOSE 80

# Start the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
