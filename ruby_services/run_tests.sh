#!/bin/bash

# Run Ruby tests
echo "?? Running Ruby tests..."

# Check if bundler is installed
if ! command -v bundle &> /dev/null; then
    echo "? Bundler not found. Installing..."
    gem install bundler
fi

# Install dependencies
echo "?? Installing dependencies..."
bundle install

# Run RSpec tests
echo "?? Running RSpec..."
bundle exec rspec spec/ --format documentation --color

# Get exit code
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "? All tests passed!"
else
    echo "? Some tests failed"
fi

exit $exit_code
