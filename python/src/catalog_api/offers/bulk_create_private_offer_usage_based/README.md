# Bulk Create Private Offers with Usage-Based Pricing

This workflow helps you create AWS Marketplace SaaS products and private offers with usage-based pricing at scale.

## Overview

The system provides:
- **Product Creation**: Create SaaS products with metered dimensions
- **Usage-Based Pricing**: Dynamic pricing from CSV rate card files
- **Bulk Operations**: Target multiple buyer accounts
- **Template Processing**: Automatic variable replacement in changesets
- **Configuration Management**: Centralized config with file and programmatic access

## Prerequisites

- Python 3.x installed
- AWS credentials configured
- Virtual environment set up (see [python/README.md](../../README.md))

## Quick Start

### 1. Configure Buyer IDs

Edit `buyer_ids.txt` (one AWS account ID per line):

```
111111111111
123456789012
987654321098
```

### 2. Configure Product ID

Provide your product ID via command line or `shared_env.json`:

```bash
# Option A: Command line
python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx

# Option B: shared_env.json
echo '{"PRODUCT_ID": "prod-xxxxx"}' > shared_env.json
```

### 3. Set Up Rate Cards

Edit `2_createPrivateOffer/rateCard.txt`:

```csv
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,1.0,10
metered_2_id,2.0,15
metered_3_id,3.0,20
```

**Pricing Formula:** `Final Price = Original Price × (1 - Discount% / 100)`

### 4. Run Scripts

```bash
# Navigate to this directory
cd src/catalog_api/offers/bulk_create_private_offer_usage_based

# Step 1: Create SaaS product (if needed)
python 1_publishSaasProcuct/start_changeset.py

# Step 2: Monitor product creation
python 1_publishSaasProcuct/describe_changeset.py <changeset_id>

# Step 3: Create private offers with dynamic pricing
python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx

# Step 4: Monitor offer creation
python 2_createPrivateOffer/describe_changeset.py <changeset_id>
```

## Directory Structure

```
bulk_create_private_offer_usage_based/
├── README.md                    # This file
├── buyer_ids.txt                # Buyer account IDs (one per line)
├── shared_env.json              # Shared configuration
│
├── 1_publishSaasProcuct/        # Product creation
│   ├── changeset.json           # Product creation template
│   ├── start_changeset.py       # Create product
│   ├── describe_changeset.py    # Monitor changeset
│   └── describe_product.py      # Get product details
│
├── 2_createPrivateOffer/        # Offer creation
│   ├── changeset.json           # Offer creation template
│   ├── changeset_with_values.json  # Example with actual values
│   ├── rateCard.txt             # Pricing data (CSV)
│   ├── start_changeset_pricing.py  # Create offer with dynamic pricing
│   ├── describe_changeset.py    # Monitor changeset
│   └── describe_offer.py        # Get offer details
│
└── utils/                       # Shared utilities
    ├── config.py                # Configuration management
    ├── start_changeset.py       # Changeset execution
    ├── stringify_details.py     # JSON stringification
    └── template_processor.py    # Template variable replacement
```

## Configuration Files

### buyer_ids.txt
One buyer AWS account ID per line:
```
111111111111
123456789012
```

**Programmatic Management:**
```python
import utils.config as config

# Add buyer ID
config.add_buyer_id("444444444444")

# Set multiple buyers
config.set_buyer_ids(["111111111111", "222222222222"])

# Save to file
config.save_buyer_ids_to_file()

# Reload from file
config.reload_buyer_ids()
```

### shared_env.json
Shared environment variables:
```json
{
  "PRODUCT_ID": "prod-xxxxx",
  "CHANGESET_ID": "abc123..."
}
```

### rateCard.txt
CSV format pricing data:
```csv
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,1.0,10
metered_2_id,2.0,15
metered_3_id,3.0,20
```

## Available Scripts

### Product Creation (1_publishSaasProcuct/)

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_changeset.py` | Create SaaS product with public offer | `python 1_publishSaasProcuct/start_changeset.py` |
| | | With custom template: `python 1_publishSaasProcuct/start_changeset.py custom.json` |
| `describe_changeset.py` | Monitor changeset status | `python 1_publishSaasProcuct/describe_changeset.py <id>` |
| | | Auto-saves PRODUCT_ID to shared_env.json when successful |
| `describe_product.py` | Get product details | `python 1_publishSaasProcuct/describe_product.py prod-xxxxx` |
| | | Uses shared_env.json if no product ID provided |

**Product Creation Features:**
- Creates SaaS product with 3 metered dimensions (usage-based)
- Creates public offer with usage-based pricing
- Automatically saves CHANGESET_ID to shared_env.json
- Extracts and saves PRODUCT_ID when changeset succeeds
- Supports custom templates via command line

**Product Template Variables:**
- `{{BUYER_IDS}}` - Array of buyer account IDs for targeting

### Offer Creation (2_createPrivateOffer/)

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_changeset_pricing.py` | Create offer with dynamic pricing | `python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx` |
| | | With custom rate card: `python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx /path/to/rates.csv` |
| | | Auto-detects product ID from command line (starts with `prod-`) |
| `describe_changeset.py` | Monitor changeset status | `python 2_createPrivateOffer/describe_changeset.py <id>` |
| | | Uses shared_env.json if no changeset ID provided |
| `describe_offer.py` | Get offer details | `python 2_createPrivateOffer/describe_offer.py offer-xxxxx` |

**Offer Creation Features:**
- Dynamic pricing from CSV rate card files
- Automatic discount calculation
- Template variable replacement
- Command-line product ID detection
- Configuration display before execution
- Saves CHANGESET_ID to shared_env.json

## Customization Examples

### Update Pricing
Edit `2_createPrivateOffer/rateCard.txt`:
```csv
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,5.0,25
metered_2_id,10.0,30
metered_3_id,15.0,35
```

### Update Offer Information
```python
import utils.config as config

# Set offer name and description
config.set_offer_info(
    "Black Friday Deal",
    "Limited time 50% discount on all usage"
)
```

### Manage Buyer IDs
```python
import utils.config as config

# View current buyers
print(config.BUYER_IDS)

# Add a buyer
config.add_buyer_id("555555555555")

# Set multiple buyers
config.set_buyer_ids(["111111111111", "123456789012", "987654321098"])

# Save to file
config.save_buyer_ids_to_file()
```

### Custom Rate Card File
```bash
# Use a custom rate card file
python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx /path/to/custom_rates.csv
```

## Configuration Priority

The system loads configuration from multiple sources with the following priority:

| Configuration | Priority Order |
|---------------|----------------|
| **PRODUCT_ID** | 1. Command line → 2. shared_env.json → 3. **Required** |
| **BUYER_IDS** | 1. buyer_ids.txt → 2. Default: `["111111111111"]` |
| **RATE_CARDS** | 1. Custom file → 2. rateCard.txt → 3. Default values |
| **Other vars** | 1. shared_env.json → 2. config.py defaults |

## Template Variables

Changeset templates use these variables (automatically replaced):

| Variable | Description | Example | Source |
|----------|-------------|---------|--------|
| `{{PRODUCT_ID}}` | Product identifier | `prod-wa4ddxl7e7ktw` | Command line / shared_env.json |
| `{{BUYER_IDS}}` | Buyer account IDs | `["111111111111"]` | buyer_ids.txt |
| `{{OFFER_NAME}}` | Offer name | `Demo Private Offer` | config.py |
| `{{OFFER_DESCRIPTION}}` | Offer description | `Usage-based pricing` | config.py |
| `{{EXPIRY_DATE}}` | Offer expiry | `2025-11-19` | config.py (today + 7 days) |
| `{{CONTRACT_DURATION_DAYS}}` | Contract duration (days) | `P365D` | config.py |
| `{{CONTRACT_DURATION_MONTHS}}` | Contract duration (months) | `P12M` | config.py |
| `{{CUSTOM_EULA_URL}}` | EULA URL | `https://...` | config.py |
| `{{RATE_CARDS}}` | Pricing array | `[{...}]` | rateCard.txt (calculated) |

### Template Processing

The system automatically processes templates and replaces placeholders:

**Usage-Based Pricing Example:**
```json
{
  "Type": "UsageBasedPricingTerm",
  "CurrencyCode": "USD",
  "RateCards": [
    {
      "RateCard": "{{RATE_CARDS}}"
    }
  ]
}
```

**After Processing:**
```json
{
  "Type": "UsageBasedPricingTerm",
  "CurrencyCode": "USD",
  "RateCards": [
    {
      "RateCard": [
        {"DimensionKey": "metered_1_id", "Price": "0.9"},
        {"DimensionKey": "metered_2_id", "Price": "1.7"},
        {"DimensionKey": "metered_3_id", "Price": "2.4"}
      ]
    }
  ]
}
```

## Bulk Operations

This workflow is designed for **bulk creation** of private offers, allowing you to:
- Create private offers for **multiple buyer accounts** simultaneously
- Create private offers for **multiple products** by running the script multiple times
- Use the same pricing configuration across all offers

### How Bulk Operations Work

**Multiple Buyers (Single Product):**
The system automatically creates one private offer that targets all buyer accounts listed in `buyer_ids.txt`. Each buyer will receive the same offer with identical pricing.

**Multiple Products:**
Run the script multiple times with different product IDs to create offers for multiple products:

```bash
# Create offers for Product A
python 2_createPrivateOffer/start_changeset_pricing.py prod-aaaaa

# Create offers for Product B  
python 2_createPrivateOffer/start_changeset_pricing.py prod-bbbbb

# Create offers for Product C
python 2_createPrivateOffer/start_changeset_pricing.py prod-ccccc
```

### Bulk Creation Workflow

#### Scenario 1: Multiple Buyers, Single Product

**Step 1: Configure Multiple Buyers**
```bash
# Add all target buyer account IDs
cat > buyer_ids.txt << EOF
111111111111
123456789012
987654321098
555666777888
444555666777
EOF
```

**Step 2: Set Up Pricing**
```bash
cat > 2_createPrivateOffer/rateCard.txt << EOF
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,1.0,10
metered_2_id,2.0,15
metered_3_id,3.0,20
EOF
```

**Step 3: Create Offer for All Buyers**
```bash
# Single command creates one offer targeting all 5 buyers
python 2_createPrivateOffer/start_changeset_pricing.py prod-xxxxx
```

**Result:** One private offer created, visible to all 5 buyer accounts.

#### Scenario 2: Multiple Products, Multiple Buyers

**Step 1: Configure Buyers (Same as Above)**
```bash
cat > buyer_ids.txt << EOF
111111111111
123456789012
987654321098
EOF
```

**Step 2: Create Offers for Each Product**
```bash
# Product A - Standard pricing
python 2_createPrivateOffer/start_changeset_pricing.py prod-aaaaa

# Product B - Different pricing (update rateCard.txt first)
cat > 2_createPrivateOffer/rateCard.txt << EOF
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,2.0,20
metered_2_id,4.0,25
metered_3_id,6.0,30
EOF
python 2_createPrivateOffer/start_changeset_pricing.py prod-bbbbb

# Product C - Custom rate card file
python 2_createPrivateOffer/start_changeset_pricing.py prod-ccccc /path/to/product_c_rates.csv
```

**Result:** Three separate private offers created (one per product), each targeting all 3 buyers.

#### Scenario 3: Different Buyers for Different Products

**Step 1: Create Offers for Product A (Buyers 1-3)**
```bash
cat > buyer_ids.txt << EOF
111111111111
123456789012
987654321098
EOF
python 2_createPrivateOffer/start_changeset_pricing.py prod-aaaaa
```

**Step 2: Create Offers for Product B (Buyers 4-6)**
```bash
cat > buyer_ids.txt << EOF
444555666777
555666777888
666777888999
EOF
python 2_createPrivateOffer/start_changeset_pricing.py prod-bbbbb
```

**Result:** Two private offers with different buyer targeting.

#### Scenario 4: Programmatic Bulk Creation

For advanced automation, use Python to create offers programmatically:

```python
import utils.config as config
import subprocess

# Define products and their buyer groups
products_config = [
    {
        "product_id": "prod-aaaaa",
        "buyers": ["111111111111", "123456789012"],
        "rate_card": "rates_product_a.csv"
    },
    {
        "product_id": "prod-bbbbb", 
        "buyers": ["987654321098", "444555666777"],
        "rate_card": "rates_product_b.csv"
    },
    {
        "product_id": "prod-ccccc",
        "buyers": ["555666777888", "666777888999"],
        "rate_card": "rates_product_c.csv"
    }
]

# Create offers for each product
for product in products_config:
    print(f"\nCreating offer for {product['product_id']}...")
    
    # Set buyer IDs
    config.set_buyer_ids(product['buyers'])
    config.save_buyer_ids_to_file()
    
    # Run the script
    cmd = [
        "python", 
        "2_createPrivateOffer/start_changeset_pricing.py",
        product['product_id'],
        product['rate_card']
    ]
    subprocess.run(cmd)
    
    print(f"✓ Offer created for {product['product_id']}")
```

### Bulk Operation Best Practices

1. **Test First**: Create offers for a single buyer/product before bulk operations
2. **Monitor Progress**: Check changeset status before creating the next batch
3. **Rate Limits**: Be aware of AWS API rate limits when creating many offers
4. **Backup Configuration**: Save buyer_ids.txt and rateCard.txt for each campaign
5. **Naming Convention**: Use descriptive offer names to track different campaigns
6. **Validation**: Verify pricing calculations before bulk creation
7. **Logging**: Keep track of which offers were created for which products/buyers

## Workflow Example

### Complete Workflow: Product to Offer

```bash
# 1. Set up buyer IDs
cat > buyer_ids.txt << EOF
111111111111
123456789012
EOF

# 2. Create SaaS product
python 1_publishSaasProcuct/start_changeset.py

# 3. Wait for product creation (check status)
python 1_publishSaasProcuct/describe_changeset.py <changeset_id>

# 4. Product ID is automatically saved to shared_env.json
# Or provide it manually:
echo '{"PRODUCT_ID": "prod-xxxxx"}' > shared_env.json

# 5. Configure pricing
cat > 2_createPrivateOffer/rateCard.txt << EOF
DimensionKey,OriginalPrice,DiscountPercent
metered_1_id,1.0,10
metered_2_id,2.0,15
metered_3_id,3.0,20
EOF

# 6. Create private offers
python 2_createPrivateOffer/start_changeset_pricing.py

# 7. Monitor offer creation
python 2_createPrivateOffer/describe_changeset.py <changeset_id>
```

## Error Handling

### Common Issues

**1. Product ID Not Provided**
```
ERROR: No PRODUCT_ID found
```
**Solution:** Provide via command line or shared_env.json

**2. Buyer IDs File Not Found**
```
Warning: buyer_ids.txt not found
```
**Solution:** Create `buyer_ids.txt` with buyer account IDs

**3. Rate Card File Not Found**
```
Warning: Rate card file not found
```
**Solution:** System uses default rate cards; create `rateCard.txt` for custom pricing

**4. AWS Credentials**
```
Unable to locate credentials
```
**Solution:** Configure AWS credentials:
```bash
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_DEFAULT_REGION=us-east-1
```

## Best Practices

1. **Buyer IDs**: Keep `buyer_ids.txt` clean (one ID per line, no extra spaces)
2. **Product ID**: Always provide a valid product ID before creating offers
3. **Rate Cards**: Validate pricing calculations before creating offers
4. **Monitoring**: Use describe_changeset.py to monitor progress
5. **Configuration**: Use shared_env.json for values that persist across runs
6. **Version Control**: Consider tracking buyer_ids.txt and rateCard.txt in git

## Changeset Files

### Product Creation Templates
- `1_publishSaasProcuct/changeset.json` - Usage-based SaaS product with 3 metered dimensions

### Offer Creation Templates
- `2_createPrivateOffer/changeset.json` - Usage-based private offer template
- `2_createPrivateOffer/changeset_with_values.json` - Example with actual values (reference)

## Additional Documentation

- [python/README.md](../../README.md) - Parent Python setup guide
- [AWS Marketplace Catalog API](https://docs.aws.amazon.com/marketplace-catalog/latest/api-reference/) - Official API documentation

## Support

For issues or questions:
- Check the [AWS Marketplace documentation](https://docs.aws.amazon.com/marketplace/)
- Review error messages in changeset descriptions
- Use describe_changeset.py to get detailed error information
