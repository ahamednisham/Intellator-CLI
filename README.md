# Intellator - Smart JSON Translation Tool

A powerful and intelligent command-line tool for translating JSON files between languages using Google Translate. Built for developers who need to internationalize (i18n) their applications efficiently and reliably.

## ✨ Key Features

- 🚀 **Simple & Intuitive**: Just specify languages - `intellator.py en ar es` translates to multiple languages at once
- 🧠 **Smart Translation**: Automatically skips already translated keys, only translating what's new or changed
- 📊 **Real-time Progress**: Beautiful progress bars with detailed statistics and translation rates
- 🔄 **Retry Logic**: Built-in retry mechanism with exponential backoff for failed translations
- 🛡️ **Robust Error Handling**: Gracefully handles failures while preserving original values
- 🌍 **100+ Languages**: Supports all languages available in Google Translate
- 💾 **Structure Preservation**: Maintains exact JSON structure, key names, and formatting
- 📈 **Comprehensive Stats**: Detailed reports showing skipped, translated, and failed keys
- ⚡ **Blazing Fast**: Efficient batch processing with rate tracking
- 🎯 **Flexible CLI**: Simple positional arguments for common tasks, flags for advanced control

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**

2. **Install dependencies** (one command!):

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install deep-translator tqdm
```

### Basic Usage (Recommended)

The simplest way to use Intellator is with **ISO language codes**:

```bash
# Translate en.json to ar.json
python intellator.py en ar

# Translate to multiple languages at once
python intellator.py en ar es fr de

# Save to a specific directory
python intellator.py en ar es fr -d locales
```

### Flags (Advanced)

```bash
# Custom files
python intellator.py -i input.json -o output.json -s en -t ar

# Verbose + auto-overwrite
python intellator.py en ar -v --overwrite
```

## Command Reference

### Positional Arguments

```
python intellator.py <source> <target1> [target2] [target3] ...
```

- **source**: Source language code (e.g., `en`, `es`, `fr`)
- **target1, target2, ...**: One or more target language codes

### Optional Flags

| Flag           | Short | Description                         | Default                       |
| -------------- | ----- | ----------------------------------- | ----------------------------- |
| `--input`      | `-i`  | Input JSON file path                | `{source}.json`               |
| `--output`     | `-o`  | Output JSON file path               | `{target}.json`               |
| `--output-dir` | `-d`  | Output directory for translations   | Current directory             |
| `--source`     | `-s`  | Source language code                | First positional arg or `en`  |
| `--target`     | `-t`  | Target language code                | Second positional arg or `ar` |
| `--verbose`    | `-v`  | Show detailed output with key names | `False`                       |
| `--overwrite`  |       | Skip overwrite prompts              | `False`                       |

## 🌍 Supported Languages

Intellator supports **100+ languages** via ISO language codes:

| Language              | ISO Code |
| --------------------- | -------- |
| English               | `en`     |
| Arabic                | `ar`     |
| Spanish               | `es`     |
| French                | `fr`     |
| German                | `de`     |
| Italian               | `it`     |
| Portuguese            | `pt`     |
| Russian               | `ru`     |
| Chinese (Simplified)  | `zh-CN`  |
| Chinese (Traditional) | `zh-TW`  |
| Japanese              | `ja`     |
| Korean                | `ko`     |
| Hindi                 | `hi`     |

**Note**: Language codes are case-sensitive (e.g., use `zh-CN`, not `zh-cn`).

[View all supported languages →](https://cloud.google.com/translate/docs/languages)

## 💡 Real-World Examples

### Example 1: Simple Translation

**Input (`en.json`):**

```json
{
  "welcome.title": "Welcome to Intellator",
  "button.submit": "Submit",
  "error.404": "Page not found"
}
```

**Command:**

```bash
python intellator.py en ar
```

**Output (`ar.json`):**

```json
{
  "welcome.title": "مرحبا بك في إنتليتور",
  "button.submit": "إرسال",
  "error.404": "الصفحة غير موجودة"
}
```

**Console Output:**

```
Reading en.json...
Found 3 translation key(s) in parent file.
Initializing Google Translator (en -> ar)...
Processing: 100%|████████████| 3/3 [00:01<00:00, 2.45 keys/s]

================================================================================
✓ TRANSLATION COMPLETE
================================================================================

⏱️  Time Elapsed: 1.22s
📊 Translation Rate: 2.45 keys/second

📈 Overall Statistics:
   Total Keys in Parent: 3
   ├─ Skipped (existed): 0
   ├─ Newly Translated:  3
   └─ Failed:            0

✨ Newly Translated (3):
   1. welcome.title
   2. button.submit
   3. error.404

💾 Output File: ar.json
🌐 Languages: EN → AR

================================================================================
```

### Example 2: Multi-Language Translation

Translate your app to 5 languages with one command:

```bash
# First run: translates all keys
python intellator.py en ar

# Later: only translates NEW keys
python intellator.py en ar  # Auto-skips existing translations
```

### Example 3: Batch Translation Script

Create a reusable script (`translate-all.sh` / `translate-all.bat`):

**Bash (Linux/Mac):**

```bash
#!/bin/bash
python intellator.py en ar es fr de it pt ja ko zh ru hi --overwrite --verbose
```

**Batch (Windows):**

```batch
@echo off
python intellator.py en ar es fr de it pt ja ko zh ru hi --overwrite --verbose
```

### Example 4: CI/CD Integration

```yaml
# .github/workflows/translate.yml
name: Auto Translate
on:
  push:
    paths: ["locales/en.json"]
jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python intellator.py en es fr de --overwrite
      - uses: stefanzweifel/git-auto-commit-action@v4
```

## 🔧 How Intellator Works

1. **📖 Read Input**: Loads your source JSON file (e.g., `en.json`)
2. **🔍 Check Existing**: Loads target file if exists to skip already translated keys
3. **🌐 Initialize Translator**: Sets up Google Translate with source/target languages
4. **⚡ Translate**: Processes each key:
   - Skips if already translated
   - Translates string values
   - Preserves numbers, booleans, null
   - Retries on failure (up to 3 times with exponential backoff)
5. **💾 Save**: Writes translated JSON with proper formatting and UTF-8 encoding
6. **📊 Report**: Shows comprehensive statistics

## 🛡️ Error Handling & Reliability

Intellator is built to be robust:

| Scenario              | Handling                         |
| --------------------- | -------------------------------- |
| File not found        | Clear error with directory path  |
| Invalid JSON          | Detailed parsing error           |
| Network issues        | 3 retries with backoff           |
| Translation fails     | Preserves original, logs warning |
| Existing translations | Auto-skip                        |
| Ctrl+C                | Clean exit                       |

## 📊 What Gets Preserved

- ✅ **JSON key names** (never translated)
- ✅ **JSON structure & nesting**
- ✅ **Non-string values** (numbers, booleans, arrays, null)
- ✅ **Key ordering**
- ✅ **UTF-8 encoding** (supports all languages)

## 🐛 Troubleshooting

**File not found:**

```bash
pwd  # Check directory
ls -la en.json  # Verify file
python intellator.py -i /full/path/to/file.json  # Use absolute path
```

**Slow/failed translations:**

- Check internet connection
- Google may rate-limit - use `--verbose` to see progress
- Failed keys preserve original values

**Encoding issues:**

- Ensure UTF-8 terminal/editor support
- Files auto-save as UTF-8

## Requirements

- **Python**: 3.6 or higher
- **Dependencies**:
  - `deep-translator` (>=1.11.4) - Translation API wrapper
  - `tqdm` (>=4.66.0) - Progress bars
- **Internet**: Required for Google Translate API

## 📄 License

This project is open source and available for use.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests
- 📖 Improve documentation

## 🙏 Credits

Built with:

- [deep-translator](https://github.com/nidhaloff/deep-translator) - Google Translate API wrapper
- [tqdm](https://github.com/tqdm/tqdm) - Progress bars

---

**Made with ❤️ for developers who believe in breaking language barriers**
