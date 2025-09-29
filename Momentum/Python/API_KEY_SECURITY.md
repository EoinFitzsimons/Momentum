# 🔒 API Key Security Notice

## ⚠️ CRITICAL SECURITY INFORMATION

This project uses external APIs that require API keys. **NEVER commit API keys to version control!**

## 🛡️ Protected Files

The following files are automatically ignored by Git and should **NEVER** be committed:

### Environment Files
- `.env` - Contains your actual API keys and secrets
- `.env.*` - Any environment files with secrets
- `*.key` - Any key files
- `*.secret` - Any secret files
- `credentials.json` - Credential files
- `api_keys.txt` - API key files

### Databases & Data
- `data/paranames.tsv` - Large dataset file (download separately)
- `data/paranames.db` - Generated database file
- `database/*.db` - All database files
- `logs/` - Log files may contain sensitive info

## ✅ Safe to Commit

These files are safe and should be committed:

- `.env.example` - Template with placeholder values
- `.gitignore` - Protects sensitive files
- All source code files (`.py`, `.md`, etc.)
- Configuration templates
- Documentation

## 🚀 Setup for New Developers

If someone else works on this project:

1. **Copy the example environment file:**
   ```bash
   cd Momentum/Python
   copy .env.example .env
   ```

2. **Get your own NameAPI key:**
   - Visit: https://www.nameapi.org/
   - Sign up for an account
   - Get your API key
   - Edit `.env` and replace `your-nameapi-key-here` with your actual key

3. **Never commit the `.env` file:**
   - It's already in `.gitignore`
   - Double-check with `git status` before committing

## 🔍 How to Check if Files are Protected

Run this command to verify sensitive files are ignored:

```bash
git status --ignored
```

You should see `.env` and other sensitive files listed under "Ignored files".

## 🚨 What to Do if You Accidentally Commit a Key

If you accidentally commit an API key:

1. **Immediately rotate the key:**
   - Go to NameAPI dashboard
   - Generate a new key
   - Update your `.env` file

2. **Remove from Git history:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
   git push origin --force --all
   ```

3. **Update `.gitignore` if needed**

## 🏆 Best Practices

- ✅ Always use environment variables for secrets
- ✅ Keep `.env.example` updated with new settings (but no real values)
- ✅ Document required environment variables
- ✅ Use meaningful names for environment variables
- ✅ Never hardcode API keys in source code
- ❌ Never commit `.env` files
- ❌ Never put API keys in comments or documentation
- ❌ Never share API keys in chat/email/messages

## 📞 Need Help?

If you're unsure about API key security:
1. Check this file first
2. Verify files are in `.gitignore`
3. Use `git status` to confirm ignored files
4. Ask for help before committing if uncertain

**Remember: Once an API key is committed to version control, consider it compromised and rotate it immediately!**