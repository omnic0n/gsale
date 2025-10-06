# Security Guidelines for eBay OAuth Configuration

## 🔒 **Important Security Notes**

### **Files with Sensitive Data**
The following files contain sensitive information and should **NEVER** be committed to version control:

- `config.py` - Contains API keys, database credentials, and OAuth secrets
- `test_ebay_oauth.py` - Contains actual OAuth credentials for testing
- Any files with `*_test_*.py` pattern that contain real credentials

### **Git Ignore Configuration**
These files are automatically excluded from Git commits via `.gitignore`:

```
# Configuration files
config.py

# Test scripts with sensitive data
test_ebay_oauth.py
*_test_*.py
test_*.py
```

### **Safe Testing**
To test eBay OAuth configuration safely:

1. **Use the template**: Copy `test_ebay_oauth_template.py` to `test_ebay_oauth.py`
2. **Add your credentials**: Replace placeholder values with actual credentials
3. **Test locally**: Run the test script locally only
4. **Delete after testing**: Remove the file with real credentials after testing
5. **Never commit**: The `.gitignore` will prevent accidental commits

### **Production Deployment**
For production deployment:

1. **Environment variables**: Use environment variables instead of hardcoded secrets
2. **Secure storage**: Store secrets in secure vaults or environment management systems
3. **Access control**: Limit access to production credentials
4. **Monitoring**: Monitor for credential exposure or misuse

### **eBay OAuth Credentials**
Your eBay OAuth credentials are located in:
- **Client ID**: `TheFrisc-Gsale-PRD-389057346-bd79d81f`
- **Client Secret**: Stored securely in `config.py` (not in version control)
- **Redirect URI**: `https://gsale.levimylesllc.com/ebay-callback`

### **Best Practices**
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Use environment variables for production
- ✅ Rotate credentials regularly
- ✅ Monitor for credential exposure
- ❌ Never commit secrets to version control
- ❌ Never share credentials in plain text
- ❌ Never log credentials in application logs

## 🚨 **If Credentials Are Compromised**

If you suspect your eBay credentials have been compromised:

1. **Immediately reset** your Client Secret in eBay Developer Portal
2. **Update** your `config.py` with new credentials
3. **Review** access logs for unauthorized usage
4. **Consider** rotating all related credentials

## 📚 **Additional Resources**

- [eBay Developer Security Guidelines](https://developer.ebay.com/api-docs/static/oauth-guide.html)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/rfc6819)
- [Environment Variable Security](https://12factor.net/config)
