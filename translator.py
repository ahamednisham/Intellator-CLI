#!/usr/bin/env python3
"""
JSON Translation Tool
Translates JSON files from one language to another using Google Translate.
"""

import json
import os
import sys
import argparse
from deep_translator import GoogleTranslator
from tqdm import tqdm


def read_json_file(file_path):
    """Read and parse JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: {file_path} not found.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error: Invalid JSON format in {file_path}: {e}")


def translate_json(data, translator, progress_bar=None, verbose=False):
    """Translate JSON values, maintaining the same structure."""
    if not isinstance(data, dict):
        raise ValueError("Error: Input data must be a dictionary.")
    
    translated_data = {}
    total_items = len(data)
    
    if total_items == 0:
        print("Warning: No translation keys found in the JSON file.")
        return data
    
    failed_translations = []
    
    # Translate each key-value pair
    for key, value in data.items():
        try:
            # Only translate string values
            if isinstance(value, str):
                translated_text = translator.translate(value)
                translated_data[key] = translated_text
            else:
                # Keep non-string values as-is
                translated_data[key] = value
            
            # Update progress bar
            if progress_bar:
                progress_bar.update(1)
                if verbose:
                    progress_bar.set_postfix_str(f"Key: {key[:30]}..." if len(key) > 30 else f"Key: {key}")
            
        except Exception as e:
            if verbose:
                print(f"\nWarning: Failed to translate '{key}': {e}")
            failed_translations.append(key)
            # Keep original value if translation fails
            translated_data[key] = value
            if progress_bar:
                progress_bar.update(1)
    
    if failed_translations:
        print(f"\nWarning: {len(failed_translations)} translation(s) failed. Original values preserved.")
    
    return translated_data


def write_json_file(data, file_path):
    """Write JSON data to file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        raise IOError(f"Error writing to {file_path}: {e}")


def get_language_code(lang):
    """Get language code from common language names."""
    lang_map = {
        'english': 'en', 'en': 'en',
        'arabic': 'ar', 'ar': 'ar',
        'spanish': 'es', 'es': 'es',
        'french': 'fr', 'fr': 'fr',
        'german': 'de', 'de': 'de',
        'italian': 'it', 'it': 'it',
        'portuguese': 'pt', 'pt': 'pt',
        'chinese': 'zh', 'zh': 'zh',
        'japanese': 'ja', 'ja': 'ja',
        'korean': 'ko', 'ko': 'ko',
        'russian': 'ru', 'ru': 'ru',
        'hindi': 'hi', 'hi': 'hi',
    }
    return lang_map.get(lang.lower(), lang.lower())


def main():
    """Main function to orchestrate the translation process."""
    parser = argparse.ArgumentParser(
        description='Translate JSON files from one language to another',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i en.json -o ar.json
  %(prog)s -i en.json -o es.json --source en --target es
  %(prog)s -i en.json -o fr.json -s en -t fr --verbose
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default='en.json',
        help='Input JSON file path (default: en.json)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path (default: auto-generated from target language)'
    )
    
    parser.add_argument(
        '-s', '--source',
        type=str,
        default='en',
        help='Source language code (default: en)'
    )
    
    parser.add_argument(
        '-t', '--target',
        type=str,
        default='ar',
        help='Target language code (default: ar)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output including current key being translated'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite output file if it exists without prompting'
    )
    
    args = parser.parse_args()
    
    # Normalize language codes
    source_lang = get_language_code(args.source)
    target_lang = get_language_code(args.target)
    
    # Generate output filename if not provided
    if not args.output:
        # Extract base name and add target language
        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}_{target_lang}.json"
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        print(f"Current directory: {os.getcwd()}")
        sys.exit(1)
    
    # Check if output file exists
    if os.path.exists(args.output) and not args.overwrite:
        response = input(f"Output file '{args.output}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Translation cancelled.")
            sys.exit(0)
    
    try:
        # Read the input JSON file
        print(f"Reading {args.input}...")
        input_data = read_json_file(args.input)
        
        # Count total keys
        total_keys = len(input_data) if isinstance(input_data, dict) else 0
        
        if total_keys == 0:
            print("Error: No keys found in the input file.")
            sys.exit(1)
        
        print(f"Found {total_keys} translation key(s).")
        
        # Initialize translator
        print(f"Initializing Google Translator ({source_lang} -> {target_lang})...")
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
        except Exception as e:
            print(f"Error: Failed to initialize translator: {e}")
            sys.exit(1)
        
        # Create progress bar
        progress_bar = tqdm(
            total=total_keys,
            desc="Translating",
            unit="key",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed} <{remaining}, {rate_fmt}]'
        )
        
        # Translate the JSON data
        translated_data = translate_json(input_data, translator, progress_bar, args.verbose)
        
        # Close progress bar
        progress_bar.close()
        
        # Write translated data to output file
        print(f"\nWriting translated content to {args.output}...")
        write_json_file(translated_data, args.output)
        
        print(f"\n✓ Translation complete!")
        print(f"  {total_keys} key(s) translated from {source_lang} to {target_lang}")
        print(f"  Output saved to: {args.output}")
        
    except FileNotFoundError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"\n✗ {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nTranslation interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

