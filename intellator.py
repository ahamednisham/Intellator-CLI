#!/usr/bin/env python3

import json
import os
import sys
import argparse
import time
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


def translate_json(data, existing_translations, translator, progress_bar=None, verbose=False, max_retries=3):
    """Translate JSON values, maintaining the same structure and order as parent.
    
    Args:
        data: The parent JSON data to translate
        existing_translations: Already translated data from output file (if exists)
        translator: GoogleTranslator instance
        progress_bar: Optional tqdm progress bar
        verbose: Whether to show verbose output
        max_retries: Maximum number of retry attempts for failed translations
    
    Returns:
        Tuple of (translated_data dict, stats dict)
    """
    if not isinstance(data, dict):
        raise ValueError("Error: Input data must be a dictionary.")
    
    translated_data = {}
    total_items = len(data)
    
    if total_items == 0:
        print("Warning: No translation keys found in the JSON file.")
        return data, {}
    
    # Track detailed statistics
    skipped_keys = []
    translated_keys = []
    failed_keys = []
    
    # Process each key-value pair in parent file order
    for key, value in data.items():
        # Check if translation already exists
        if key in existing_translations:
            # Use existing translation
            translated_data[key] = existing_translations[key]
            skipped_keys.append(key)
            if progress_bar:
                progress_bar.update(1)
                if verbose:
                    progress_bar.set_postfix_str(f"Skipped: {key[:30]}..." if len(key) > 30 else f"Skipped: {key}")
        else:
            # Only translate string values
            if isinstance(value, str):
                translation_success = False
                last_error = None
                
                # Retry logic - attempt translation up to max_retries times
                for attempt in range(1, max_retries + 1):
                    try:
                        translated_text = translator.translate(value)
                        translated_data[key] = translated_text
                        translated_keys.append(key)
                        translation_success = True
                        
                        # Update progress bar
                        if progress_bar:
                            progress_bar.update(1)
                            if verbose:
                                progress_bar.set_postfix_str(f"Translated: {key[:30]}..." if len(key) > 30 else f"Translated: {key}")
                        break  # Success, exit retry loop
                        
                    except Exception as e:
                        last_error = e
                        if attempt < max_retries:
                            # Wait before retrying (exponential backoff)
                            time.sleep(1 * attempt)
                            if verbose:
                                progress_bar.set_postfix_str(f"Retry {attempt}/{max_retries}: {key[:20]}...")
                        else:
                            # Final attempt failed
                            if verbose:
                                print(f"\nWarning: Failed to translate '{key}' after {max_retries} attempts: {e}")
                            failed_keys.append(key)
                            # Keep original value if all retries fail
                            translated_data[key] = value
                            if progress_bar:
                                progress_bar.update(1)
            else:
                # Keep non-string values as-is
                translated_data[key] = value
                if progress_bar:
                    progress_bar.update(1)
    
    # Create statistics dictionary
    stats = {
        'total_keys': total_items,
        'skipped': {
            'count': len(skipped_keys),
            'keys': skipped_keys
        },
        'translated': {
            'count': len(translated_keys),
            'keys': translated_keys
        },
        'failed': {
            'count': len(failed_keys),
            'keys': failed_keys
        }
    }
    
    return translated_data, stats


def write_json_file(data, file_path):
    """Write JSON data to file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        raise IOError(f"Error writing to {file_path}: {e}")



def main():
    """Main function to orchestrate the translation process."""
    parser = argparse.ArgumentParser(
        description='Translate JSON files from one language to another',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Positional arguments (simple usage):
  %(prog)s en ar                    # Translate en.json to ar.json
  %(prog)s en ar es de              # Translate en.json to ar.json, es.json, and de.json
  
  # Flag-based arguments (advanced usage):
  %(prog)s -i en.json -o ar.json
  %(prog)s -i en.json -o es.json --source en --target es
  %(prog)s -i en.json -o fr.json -s en -t fr --verbose
        """
    )
    
    parser.add_argument(
        'languages',
        nargs='*',
        help='Language codes: first is source (input), rest are targets (outputs). Example: en ar es'
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        help='Input JSON file path (default: en.json or inferred from source language)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file path (default: auto-generated from target language)'
    )
    
    parser.add_argument(
        '-s', '--source',
        type=str,
        help='Source language code (default: en or first positional argument)'
    )
    
    parser.add_argument(
        '-t', '--target',
        type=str,
        help='Target language code (default: ar or second positional argument)'
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
    
    # Handle positional arguments if provided
    if args.languages:
        if len(args.languages) < 2:
            print("Error: At least two language codes are required (source and target).")
            print("Example: python translator.py en ar")
            sys.exit(1)
        
        # First language is source
        source_lang = args.languages[0]
        # Remaining languages are targets
        target_langs = args.languages[1:]
        
        # If flags were also provided, positional args take precedence
        if not args.source:
            args.source = source_lang
        if not args.input:
            args.input = f"{source_lang}.json"
        
        # Check if input file exists (do this once)
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found.")
            print(f"Current directory: {os.getcwd()}")
            sys.exit(1)
        
        # Read input file once for all targets (optimization)
        print(f"Reading {args.input}...")
        try:
            input_data = read_json_file(args.input)
        except Exception as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)
        
        # Process each target language
        for target_lang in target_langs:
            # Create a copy of args for each target
            target_args = argparse.Namespace(**vars(args))
            target_args.target = target_lang
            if not args.output:
                target_args.output = f"{target_lang}.json"
            else:
                # If output was explicitly set, only use it for the first target
                if target_lang != target_langs[0]:
                    target_args.output = f"{target_lang}.json"
            
            # Process this translation with pre-loaded input data
            _process_translation(target_args, input_data)
        
        return  # Exit after processing all targets
    
    # No positional arguments, use flags or defaults
    if not args.source:
        args.source = 'en'
    if not args.target:
        args.target = 'ar'
    if not args.input:
        args.input = 'en.json'
    
    _process_translation(args)


def _process_translation(args, input_data=None):
    """Process a single translation task.
    
    Args:
        args: Arguments namespace with translation settings
        input_data: Optional pre-loaded input data (optimization for multiple targets)
    """
    
    # Use language codes directly from args
    source_lang = args.source
    target_lang = args.target
    
    # Generate output filename if not provided
    if not args.output:
        # Extract base name and add target language
        base_name = os.path.splitext(args.input)[0]
        args.output = f"{base_name}_{target_lang}.json"
    
    # Check if output file exists
    output_exists = os.path.exists(args.output)
    existing_translations = {}
    
    if output_exists:
        if not args.overwrite:
            # Load existing translations to skip them
            try:
                print(f"Output file '{args.output}' exists. Loading existing translations...")
                existing_translations = read_json_file(args.output)
                print(f"Found {len(existing_translations)} existing translation(s).")
            except Exception as e:
                print(f"Warning: Could not load existing translations: {e}")
                response = input(f"Continue and overwrite '{args.output}'? (y/N): ")
                if response.lower() not in ['y', 'yes']:
                    print("Translation cancelled.")
                    sys.exit(0)
        else:
            # Overwrite mode - still load existing to potentially skip
            try:
                existing_translations = read_json_file(args.output)
                print(f"Loading {len(existing_translations)} existing translation(s) to skip...")
            except Exception:
                pass  # File might not be valid JSON, will overwrite anyway
    
    try:
        # Start timing
        start_time = time.time()
        
        # Read the input JSON file (only if not already provided)
        if input_data is None:
            # Check if input file exists
            if not os.path.exists(args.input):
                print(f"Error: Input file '{args.input}' not found.")
                print(f"Current directory: {os.getcwd()}")
                sys.exit(1)
            
            print(f"Reading {args.input}...")
            input_data = read_json_file(args.input)
        
        # Count total keys
        total_keys = len(input_data) if isinstance(input_data, dict) else 0
        
        if total_keys == 0:
            print("Error: No keys found in the input file.")
            sys.exit(1)
        
        print(f"Found {total_keys} translation key(s) in parent file.")
        
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
            desc="Processing",
            unit="key",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed} <{remaining}, {rate_fmt}]'
        )
        
        # Translate the JSON data
        translated_data, stats = translate_json(input_data, existing_translations, translator, progress_bar, args.verbose)
        
        # Close progress bar
        progress_bar.close()
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Write translated data to output file
        print(f"\nWriting content to {args.output}...")
        write_json_file(translated_data, args.output)
        
        # Display comprehensive statistics
        print(f"\n{'='*80}")
        print(f"✓ TRANSLATION COMPLETE")
        print(f"{'='*80}")
        
        # Time statistics
        hours, remainder = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = ""
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{elapsed_time:.2f}s"
        
        print(f"\n⏱️  Time Elapsed: {time_str}")
        
        # Translation rate
        if elapsed_time > 0:
            rate = stats['total_keys'] / elapsed_time
            print(f"📊 Translation Rate: {rate:.2f} keys/second")
        
        # Overall statistics
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Keys in Parent: {stats['total_keys']}")
        print(f"   ├─ Skipped (existed): {stats['skipped']['count']}")
        print(f"   ├─ Newly Translated:  {stats['translated']['count']}")
        print(f"   └─ Failed:            {stats['failed']['count']}")
        
        # Skipped translations
        if stats['skipped']['count'] > 0:
            print(f"\n⏭️  Skipped Translations ({stats['skipped']['count']}):")
            # Show first 10 skipped keys, or all if less than 10
            display_limit = 10
            for i, key in enumerate(stats['skipped']['keys'][:display_limit]):
                print(f"   {i+1}. {key}")
            if stats['skipped']['count'] > display_limit:
                print(f"   ... and {stats['skipped']['count'] - display_limit} more")
        
        # Newly translated
        if stats['translated']['count'] > 0:
            print(f"\n✨ Newly Translated ({stats['translated']['count']}):")
            # Show first 10 translated keys, or all if less than 10
            display_limit = 10
            for i, key in enumerate(stats['translated']['keys'][:display_limit]):
                print(f"   {i+1}. {key}")
            if stats['translated']['count'] > display_limit:
                print(f"   ... and {stats['translated']['count'] - display_limit} more")
        
        # Failed translations
        if stats['failed']['count'] > 0:
            print(f"\n❌ Failed Translations ({stats['failed']['count']}):")
            for i, key in enumerate(stats['failed']['keys']):
                print(f"   {i+1}. {key}")
            print(f"   Note: Original values have been preserved for failed translations.")
        
        print(f"\n💾 Output File: {args.output}")
        print(f"🌐 Languages: {source_lang.upper()} → {target_lang.upper()}")
        print(f"\n{'='*80}\n")
        
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

