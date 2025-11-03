FROM ruby:3.4-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install gems
COPY Gemfile Gemfile.lock* ./
RUN bundle install --jobs 4 --retry 3

# Copy application
COPY . .

# Make CLI executable
RUN chmod +x cli/payqi_cli.rb webhook_service.rb

EXPOSE 4567

# Default to webhook service
CMD ["bundle", "exec", "puma", "-p", "4567", "config.ru"]
