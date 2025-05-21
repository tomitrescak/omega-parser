FROM python:3.12-slim

# Install Node.js 22 manually
RUN apt-get update && apt-get install -y curl gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs build-essential

# Set workdir
WORKDIR /app

# Copy everything
COPY . /app

# Install Python deps
RUN pip install -r requirements.txt

# Install Node deps and generate Prisma client
RUN prisma generate

# Expose the app port
EXPOSE 3000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]