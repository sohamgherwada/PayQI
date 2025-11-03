# Docker Build Troubleshooting

Common issues and solutions for Docker build failures.

## Issue: pip install fails

### Error
```
ERROR: failed to build: failed to solve: process "/bin/sh -c pip install --no-cache-dir -r requirements.txt" did not complete successfully
```

### Solutions

1. **Missing system dependencies**
   - Ensure `libpq-dev` and `gcc` are installed for psycopg2
   - Ensure `build-essential` is installed for compiling packages

2. **Missing Python dependencies**
   - Add `email-validator` for Pydantic's EmailStr
   - Upgrade pip: `pip install --upgrade pip setuptools wheel`

3. **Version conflicts**
   - Check for duplicate package entries
   - Verify compatible versions

4. **Network issues**
   - Use `--no-cache-dir` flag (already in Dockerfile)
   - Check if behind proxy (configure if needed)

### Fixed Dockerfile

The Dockerfile has been updated with:
- System dependencies: `libpq-dev`, `gcc`, `build-essential`
- pip upgrade before installing packages
- `email-validator` added to requirements.txt

## Testing the Build

```bash
# Build backend
cd backend
docker build -t payqi-backend .

# Build Ruby services
cd ../ruby_services
docker build -t payqi-webhook-service .

# Build everything
cd ..
docker-compose build
```

## Common Build Errors

### psycopg2 installation fails
**Solution**: Ensure `libpq-dev` is in apt-get install list

### email-validator not found
**Solution**: Add `email-validator==2.1.0` to requirements.txt

### Out of memory during build
**Solution**: 
- Increase Docker memory limit
- Remove unnecessary dependencies
- Use multi-stage builds

### Slow builds
**Solution**:
- Use `.dockerignore` to exclude unnecessary files
- Leverage Docker layer caching
- Use build cache: `docker build --cache-from`

## Build Optimization

### Multi-stage build (optional)

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app /app/app
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Still Having Issues?

1. Check Docker logs: `docker-compose logs backend`
2. Build with verbose output: `docker build --progress=plain`
3. Test locally: `pip install -r requirements.txt`
4. Check GitHub Actions logs for CI/CD builds
