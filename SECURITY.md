# Security Policy

## Supported Versions

We actively support and release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest| :x:                |

## Reporting a Vulnerability

We take the security of PayQI seriously. If you discover a security vulnerability, please follow these steps:

### 1. **Do NOT** create a public GitHub issue

Security vulnerabilities should be reported privately to protect users.

### 2. Email us directly

Please email security details to: **[Your GitHub username or create a security advisory]**

Alternatively, you can create a [GitHub Security Advisory](https://github.com/sohamgherwada/PayQI/security/advisories/new) if you have access.

Include the following information:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity (typically 30-90 days)

### 4. What to Expect

- Acknowledgment of your report
- Regular updates on the status of the vulnerability
- Credit in security advisories (if desired)

## Security Best Practices

### For Users

1. **Always use strong secrets**:
   - Generate secure, random JWT secrets (minimum 32 characters)
   - Use unique, strong database passwords
   - Never commit secrets to version control

2. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Use environment variables**:
   - Never hardcode API keys or secrets
   - Use `.env` files (excluded from git)
   - Consider using secrets management services (AWS Secrets Manager, HashiCorp Vault)

4. **Enable HTTPS in production**:
   - Always use TLS/SSL for API endpoints
   - Configure proper CORS settings

5. **Regular security audits**:
   ```bash
   pip install safety
   safety check
   ```

### For Developers

1. **Dependency Scanning**: Regularly scan for vulnerable dependencies
2. **Code Review**: All changes should be code-reviewed
3. **Testing**: Run the full test suite before deployment
4. **Security Headers**: Implement proper security headers
5. **Rate Limiting**: Already implemented, ensure it's properly configured

## Known Security Considerations

### API Keys
- Store API keys in environment variables
- Rotate keys regularly
- Use different keys for development and production

### Webhooks
- Always verify webhook signatures
- Use HTTPS for webhook endpoints
- Implement idempotency checks

### Database
- Use strong database passwords
- Enable SSL connections in production
- Regular backups and access controls

### JWT Tokens
- Use strong JWT secrets (minimum 32 characters)
- Set appropriate token expiration times
- Implement token refresh mechanisms

## Security Updates

We regularly update dependencies and address security vulnerabilities. To stay updated:

1. Watch this repository for security advisories
2. Subscribe to security update notifications
3. Regularly update your dependencies

## Acknowledgments

We appreciate responsible disclosure. Security researchers who help us improve PayQI's security will be acknowledged (with permission) in our security advisories.

---

**Note**: This is a public repository. Do not include sensitive information in issues, pull requests, or discussions.
