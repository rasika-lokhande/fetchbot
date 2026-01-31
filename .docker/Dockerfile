FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

COPY vision_service.py . 
CMD ["python", "vision_service.py"]