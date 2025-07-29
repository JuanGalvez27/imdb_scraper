FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install inotify-tools for live reload
RUN apt-get update && apt-get install -y inotify-tools && apt-get clean

COPY . .

CMD ["bash"]