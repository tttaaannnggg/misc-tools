# Security Guidelines

## 🔒 Protecting Sensitive Information

This project handles Zoom API credentials and meeting data. Follow these security guidelines:

### **API Credentials Protection**

#### ✅ **Safe Practices:**
- Use `.env` files for credentials (excluded from git)
- Use `zoom_config*.json.sample` templates (included in git)
- Store actual credentials in `zoom_config.json` (excluded from git)
- Use environment variables in production
- Rotate API keys regularly

#### ❌ **Never Commit:**
- `configs/zoom_config.json` - Contains real API credentials
- `results/` folder - May contain meeting URLs and IDs
- `.env` files - Environment variables with secrets
- Log files - May contain API responses
- Any file with `secret`, `key`, or `token` in the name

### **File Security Status**

#### **✅ Safe to Commit:**
```
✅ configs/*.sample          # Template files only
✅ events/events_sample.*     # Generic sample events
✅ events/igrc_sample_*       # Sample events (no real meetings)
✅ documentation/             # Public documentation
✅ tool/zoom_scheduler.py     # Source code
✅ schedules/                 # Source schedules (no credentials)
```

#### **❌ Never Commit:**
```
❌ configs/zoom_config.json   # Real API credentials
❌ results/                   # Meeting URLs and IDs
❌ .env                       # Environment variables
❌ *.log                      # May contain API responses
❌ *_output.json             # Meeting scheduling results
```

### **Environment Variables**

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

The `.env` file is automatically excluded from git.

### **Multi-Account Security**

When using multiple Zoom accounts:

1. **Separate credentials** for each account
2. **Account-specific permissions** - use least privilege
3. **Regular audit** of which events use which accounts
4. **Backup credentials** stored securely offline

### **Meeting Data Protection**

#### **Scheduled Meeting URLs:**
- Meeting URLs contain meeting IDs and access tokens
- Store results in the excluded `results/` folder
- Do not share meeting URLs in public repositories
- Use `--output` parameter to save to protected locations

#### **Log Data:**
- API responses may contain sensitive meeting information
- Logs are excluded from git by default
- Review logs before sharing for debugging

### **Production Deployment**

For production environments:

1. **Use CI/CD secrets** for API credentials
2. **Environment-specific configurations**
3. **Secure credential storage** (AWS Secrets Manager, etc.)
4. **Network security** for API communications
5. **Regular security audits**

### **Incident Response**

If credentials are accidentally committed:

1. **Immediately rotate** all exposed API keys
2. **Remove credentials** from git history
3. **Check logs** for unauthorized API usage
4. **Update security policies**

### **Compliance Considerations**

When scheduling meetings for organizations:

- **Data residency** requirements for meeting data
- **Privacy policies** for participant information
- **Retention policies** for meeting recordings
- **Access controls** for administrative functions

## 🛡️ Security Checklist

Before committing code:

- [ ] No API credentials in files
- [ ] No meeting URLs or IDs in files
- [ ] `.gitignore` is up to date
- [ ] Sample files contain only dummy data
- [ ] Environment variables used for secrets
- [ ] Results folder is excluded
- [ ] Log files are excluded

## 📞 Security Contact

For security concerns or to report vulnerabilities:
- Review code before committing
- Use secure channels for credential sharing
- Follow principle of least privilege
- Regular security audits

---

*Security is everyone's responsibility. When in doubt, exclude it from git.*