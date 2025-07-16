# 1. Create a common 'base' stage with system libraries and a working directory.
FROM python:3.9-slim as base
# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0 ffmpeg && apt-get clean
# Set the main working directory for the application
WORKDIR /app

# 2. Create the final image for 'stage1'
FROM base as stage1
# Use the new directory name for the WORKDIR
WORKDIR /app/Stage_I_Volleyball
# Copy ONLY the requirements file from the new path to leverage Docker caching
COPY ./VolleyVision/Stage_I_Volleyball/requirements.txt .
# Install dependencies. This layer will be cached unless requirements.txt changes.
RUN pip install --no-cache-dir -r requirements.txt

# 3. Create the final image for 'stage2'
FROM base as stage2
# Use the new directory name for the WORKDIR
WORKDIR /app/Stage_II_Players_and_Actions
# Stage 2 just needs ultralytics
RUN pip install --no-cache-dir ultralytics

# 4. Create the final image for 'stage3'
FROM base as stage3
# Use the new directory name for the WORKDIR
WORKDIR /app/Stage_III_Court_Detection
# Copy ONLY the requirements file from the new path
COPY ./VolleyVision/Stage_III_Court_Detection/requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
