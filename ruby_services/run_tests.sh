#!/bin/bash

# Run Ruby tests
echo "?? Running Ruby tests..."

# Ensure local gem bin directory is on PATH
if command -v ruby &> /dev/null; then
    GEM_BIN_DIR="$(ruby -e 'puts Gem.user_dir')/bin"
    export PATH="$GEM_BIN_DIR:$PATH"
fi

# Check if bundler is installed
if ! command -v bundle &> /dev/null; then
    echo "? Bundler not found. Installing..."
    gem install --user-install bundler
    export PATH="$(ruby -e 'puts Gem.user_dir')/bin:$PATH"
fi

# Install dependencies
echo "?? Installing dependencies..."
bundle config set --local path 'vendor/bundle' >/dev/null 2>&1
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
