# CREATE CONTAINER

docker build --platform=linux/amd64 -t my-python-app .

# RUN CONTAINER

docker run -it --rm \
  --platform=linux/amd64 \
  -v "$(pwd)":/app \
  -w /app \
  my-python-app

# Install

uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
prisma generate
Xvfb :99 -screen 0 1920x1080x24 &