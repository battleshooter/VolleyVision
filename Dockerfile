# 1. Create a common 'base' stage with all the shared components
FROM python:3.9-slim as base

WORKDIR /app
RUN apt-get update && apt-get install -y git libgl1-mesa-glx libglib2.0-0
RUN git clone https://github.com/battleshooter/VolleyVision.git .

# 2. Create the final image for 'stage1'
FROM base as stage1
WORKDIR /app/Stage I - Volleyball
RUN pip install --no-cache-dir -r requirements.txt

# 3. Create the final image for 'stage2'
FROM base as stage2
WORKDIR /app/Stage II - Players & Actions
RUN pip install --no-cache-dir ultralytics

# 4. Create the final image for 'stage3'
FROM base as stage3
WORKDIR /app/Stage III - Court Detection
RUN pip install --no-cache-dir -r requirements.txt
