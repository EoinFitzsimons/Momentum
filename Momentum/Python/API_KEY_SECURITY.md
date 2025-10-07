# 🔒 Security & Data Management

## ✅ No API Keys Required!

**Good News:** This project now uses the Faker library for name generation, which works completely offline with no API keys needed!

## 🛡️ Protected Files

The following files are automatically ignored by Git and should **NEVER** be committed:

### Environment Files
- `.env` - May contain future API keys or configuration secrets
- `.env.*` - Any environment files with secrets
- `*.key` - Any key files
- `*.secret` - Any secret files
- `credentials.json` - Credential files

### Databases & Data
- `data/used_names.db` - Name tracking database (auto-generated)
- `database/*.db` - All database files (contains generated game data)
- `logs/` - Log files may contain sensitive info

## ✅ Safe to Commit

These files are safe and should be committed:

- `.env.example` - Template with placeholder values (if needed for future features)
- `.gitignore` - Protects sensitive files
- All source code files (`.py`, `.md`, etc.)
- Configuration templates
- Documentation

## 🚀 Setup for New Developers

If someone else works on this project:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd FinalProject/Momentum/Python
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate initial database:**
   ```bash
   python generate_initial_database.py
   ```

That's it! No API keys, no downloads, no external services required.

## 🔍 How to Check if Files are Protected

Run this command to verify sensitive files are ignored:

```bash
git status --ignored
```

You should see `*.db` files and `data/` directory listed under "Ignored files".

## � Name Generation System

The project uses an **Intelligent Name Generator** with:

- **Faker library**: 24 different locales for culturally-appropriate names
- **SQLite tracking**: Ensures 100% unique names (no duplicates)
- **Offline operation**: No internet connection required
- **80+ countries**: Comprehensive mapping with regional fallbacks
- **Multilingual**: Supports Cyrillic, Chinese, Japanese, Arabic, diacritics, etc.

### Example Names Generated

| Country | Example Name | Locale Used |
|---------|--------------|-------------|
| Ukraine | Наталья Константинов | Russian (ru_RU) |
| Japan | 聡太郎 石川 | Japanese (ja_JP) |
| Brazil | Isadora Peixoto | Portuguese (pt_BR) |
| Germany | Oswin Ziegert | German (de_DE) |
| Finland | Tapio Nieminen | Finnish (fi_FI) |

See `docs/NAME_GENERATION_SOLUTION.md` for complete technical details.

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