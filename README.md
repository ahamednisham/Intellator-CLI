# JSON Translation Tool

A command-line tool for translating JSON files from one language to another using Google Translate. Perfect for internationalization (i18n) workflows where you need to translate translation keys from a source language to multiple target languages.

## Features

- 🌍 **Multi-language Support**: Translate between 100+ languages supported by Google Translate
- 📊 **Progress Tracking**: Real-time progress bar showing translation status
- 🔄 **Structure Preservation**: Maintains the exact JSON structure and key names
- 🛡️ **Error Handling**: Graceful error handling with fallback to original values
- ⚡ **Fast & Efficient**: Batch translation with progress indicators
- 🎯 **Flexible CLI**: Comprehensive command-line interface with multiple options
- 📝 **Verbose Mode**: Optional detailed output for debugging

## Requirements

- Python 3.6+
- Internet connection (for Google Translate API)

## Installation

1. Install the required dependencies:

```bash
pip install deep-translator tqdm
```

## Usage

### Basic Usage

Translate `en.json` to Arabic (default):

```bash
python translator.py
```

This will create `en_ar.json` (or `ar.json` if the input is `en.json`).

### Custom Input/Output Files

```bash
python translator.py -i en.json -o es.json -s en -t es
```

### Translate to Multiple Languages

```bash
# Spanish
python translator.py -i en.json -o es.json -t es

# French
python translator.py -i en.json -o fr.json -t fr

# German
python translator.py -i en.json -o de.json -t de
```

### Verbose Mode

Get detailed output including the current key being translated:

```bash
python translator.py -i en.json -o ar.json -v
```

### Overwrite Existing Files

By default, the tool will prompt before overwriting. Use `--overwrite` to skip the prompt:

```bash
python translator.py -i en.json -o ar.json --overwrite
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | Input JSON file path | `en.json` |
| `--output` | `-o` | Output JSON file path | Auto-generated |
| `--source` | `-s` | Source language code | `en` |
| `--target` | `-t` | Target language code | `ar` |
| `--verbose` | `-v` | Show verbose output | `False` |
| `--overwrite` | | Overwrite output file without prompting | `False` |

## Supported Languages

The tool accepts both language names and ISO codes. Common examples:

- **English**: `en` or `english`
- **Arabic**: `ar` or `arabic`
- **Spanish**: `es` or `spanish`
- **French**: `fr` or `french`
- **German**: `de` or `german`
- **Italian**: `it` or `italian`
- **Portuguese**: `pt` or `portuguese`
- **Chinese**: `zh` or `chinese`
- **Japanese**: `ja` or `japanese`
- **Korean**: `ko` or `korean`
- **Russian**: `ru` or `russian`
- **Hindi**: `hi` or `hindi`

For a complete list of supported languages, refer to [Google Translate supported languages](https://cloud.google.com/translate/docs/languages).

## Examples

### Example 1: Translate English to Arabic

**Input (`en.json`):**
```json
{
  "welcome.message": "Welcome to our application",
  "button.submit": "Submit",
  "error.notFound": "Page not found"
}
```

**Command:**
```bash
python translator.py -i en.json -o ar.json
```

**Output (`ar.json`):**
```json
{
  "welcome.message": "مرحباً بك في تطبيقنا",
  "button.submit": "إرسال",
  "error.notFound": "الصفحة غير موجودة"
}
```

### Example 2: Translate to Spanish with Verbose Output

```bash
python translator.py -i en.json -o es.json -t es -v
```

### Example 3: Batch Translation Script

Create a script to translate to multiple languages:

```bash
#!/bin/bash
languages=("es" "fr" "de" "it" "pt")

for lang in "${languages[@]}"; do
    python translator.py -i en.json -o "${lang}.json" -t "$lang" --overwrite
done
```

## How It Works

1. **Read Input**: Loads the source JSON file
2. **Initialize Translator**: Sets up Google Translator with source and target languages
3. **Translate Values**: Iterates through each key-value pair:
   - Translates string values
   - Preserves non-string values (numbers, booleans, etc.)
   - Maintains the original key structure
4. **Handle Errors**: If translation fails for a key, keeps the original value
5. **Write Output**: Saves the translated JSON with proper formatting

## Error Handling

- **File Not Found**: Clear error message with current directory info
- **Invalid JSON**: Detailed JSON parsing error
- **Translation Failures**: Original values preserved, warnings logged
- **Network Issues**: Graceful handling of API connection problems
- **Keyboard Interrupt**: Clean exit on Ctrl+C

## Output Format

The tool preserves:
- ✅ Original key names (not translated)
- ✅ JSON structure and indentation
- ✅ Non-string values (numbers, booleans, null)
- ✅ UTF-8 encoding for all languages

## Troubleshooting

### "Error: Input file not found"
- Ensure the input file exists in the current directory
- Use absolute paths if needed: `python translator.py -i /path/to/en.json`

### Translation fails for some keys
- Check your internet connection
- Some text may be rate-limited by Google Translate
- Original values are preserved as fallback

### Output file encoding issues
- The tool uses UTF-8 encoding by default
- Ensure your editor supports UTF-8 for viewing translated files

## License

This project is open source and available for use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.
