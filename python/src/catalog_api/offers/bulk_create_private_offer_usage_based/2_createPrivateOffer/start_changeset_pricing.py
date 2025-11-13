# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
"""
Purpose
Shows how to use the AWS SDK for Python (Boto3) to create a private offer
with dynamic pricing based on rate card file for my SaaS product
CAPI-39

This version uses dynamic configuration values from utils/config.py and processes
templates to replace placeholders with actual values including rate cards.
"""

import os
import sys
import tempfile
import json

# Add the parent directory to Python path to access utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils.start_changeset as sc
import utils.stringify_details as sd
import utils.template_processor as tp
import utils.config as config


def load_merged_config_with_rate_cards():
    """
    Load configuration from shared_env.json and merge with config defaults,
    including rate cards from the rate card file
    
    Returns:
        dict: Merged configuration with shared_env.json values taking priority and rate cards
    """
    # Start with default config including rate cards
    merged_config = config.get_config_with_rate_cards()
    
    # Check if PRODUCT_ID was set from command line
    import sys
    product_id_from_cmdline = None
    for arg in sys.argv[1:]:
        if arg.startswith('prod-'):
            product_id_from_cmdline = arg
            break
    
    # Load from shared_env.json if it exists
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared_env.json")
    if os.path.exists(env_file_path):
        try:
            with open(env_file_path, "r") as f:
                env_data = json.load(f)
                # Update config with values from shared_env.json (except RATE_CARDS which is dynamically generated)
                for key in merged_config.keys():
                    if key != "RATE_CARDS" and key in env_data and env_data[key]:
                        # Don't override PRODUCT_ID if it was provided via command line
                        if key == "PRODUCT_ID" and product_id_from_cmdline:
                            continue
                        merged_config[key] = env_data[key]
        except Exception as e:
            print(f"Warning: Could not read shared_env.json: {e}")
    
    return merged_config


def main(change_set=None, rate_card_file=None):
    """
    Main function to create a private offer changeset with dynamic pricing
    
    Args:
        change_set: Optional pre-processed changeset. If None, will process template.
        rate_card_file: Optional path to rate card file. If None, uses default location.
    
    Returns:
        dict: Response from the changeset creation
    """
    if change_set is None:
        # Load merged configuration from shared_env.json and defaults with rate cards
        merged_config = load_merged_config_with_rate_cards()
        
        # Validate that PRODUCT_ID is provided
        if not merged_config.get("PRODUCT_ID"):
            print("\n❌ ERROR: PRODUCT_ID is required but not provided.")
            print("\nPlease provide PRODUCT_ID via one of these methods:")
            print("  1. Command line argument: python start_changeset_pricing.py prod-xxxxx")
            print("  2. Add PRODUCT_ID to shared_env.json file")
            print("\nExample shared_env.json:")
            print('  {')
            print('    "PRODUCT_ID": "prod-xxxxx"')
            print('  }')
            sys.exit(1)
        
        # If custom rate card file specified, reload rate cards
        if rate_card_file:
            rate_cards = config.load_rate_cards(rate_card_file)
            merged_config["RATE_CARDS"] = rate_cards
        
        # Print current configuration
        print("Using configuration:")
        print("=" * 60)
        for key, value in merged_config.items():
            if key == "RATE_CARDS":
                print(f"{key}:")
                for i, card in enumerate(value):
                    print(f"  [{i}] DimensionKey: {card['DimensionKey']}, Price: {card['Price']}")
            else:
                print(f"{key}: {value}")
        print("=" * 60)
        print()
        
        # Use the changeset.json file (which contains rate card template variables)
        template_file = os.path.join(os.path.dirname(__file__), "changeset.json")
        
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Changeset file not found: {template_file}")
        
        try:
            # Process the template with merged configuration
            processed_changeset = tp.process_changeset_template(template_file, merged_config)
            
            # Create a temporary file with the processed changeset
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(processed_changeset, temp_file, indent=2)
                temp_changeset_file = temp_file.name
            
            # Stringify the processed changeset
            stringified_change_set = sd.stringify_changeset(temp_changeset_file)
            
            # Clean up temporary file
            os.unlink(temp_changeset_file)
            
        except Exception as e:
            print(f"Error processing changeset template: {e}")
            raise
    else:
        stringified_change_set = change_set

    # Execute the changeset
    response = sc.usage_demo(
        stringified_change_set,
        "Create private offer with dynamic pricing based on rate card file for my SaaS product",
    )
    
    # If successful, provide helpful information
    if response and 'ChangeSetId' in response:
        print(f"\n✅ Private offer changeset with dynamic pricing created successfully!")
        print(f"ChangeSet ID: {response['ChangeSetId']}")
        print(f"ChangeSet ARN: {response['ChangeSetArn']}")
        
        # Save changeset ID to shared_env.json
        env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "shared_env.json")
        env_data = {}
        if os.path.exists(env_file_path):
            with open(env_file_path, "r") as f:
                env_data = json.load(f)
        env_data["CHANGESET_ID"] = response['ChangeSetId']
        with open(env_file_path, "w") as f:
            json.dump(env_data, f, indent=2)
        print(f"✓ Saved CHANGESET_ID to shared_env.json")
        
        print(f"\nUse describe_changeset.py to monitor progress:")
        print(f"python3 1_publishSaasProcuct/describe_changeset.py {response['ChangeSetId']}")
        
        # Show key configuration values used
        merged_config = load_merged_config_with_rate_cards()
        print(f"\nKey values used in this offer:")
        print(f"  Product ID: {merged_config['PRODUCT_ID']}")
        print(f"  Buyer IDs: {merged_config['BUYER_IDS']}")
        print(f"  Expiry Date: {merged_config['EXPIRY_DATE']}")
        print(f"  Contract Duration: {merged_config['CONTRACT_DURATION_MONTHS']}")
        print(f"  Rate Cards:")
        for card in merged_config['RATE_CARDS']:
            print(f"    - {card['DimensionKey']}: ${card['Price']}")
    
    return response


if __name__ == "__main__":
    # Check if rate card file is provided as command line argument
    rate_card_file = None
    if len(sys.argv) > 1:
        rate_card_file = sys.argv[1]
        print(f"Using custom rate card file: {rate_card_file}")
    
    main(rate_card_file=rate_card_file)