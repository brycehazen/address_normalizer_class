# Address Normalization for Record Matching

This suite of Python scripts provides address normalization functionality specifically designed for **duplicate detection and record matching**, not address correction or validation.

## ⚠️ Important Notice

**Purpose**: These tools normalize addresses to create consistent formats for comparing and matching records. They are **NOT** intended to fix or validate actual address data.

## 📁 Files Overview

### Core Files

#### `address_normalizer.py`
The main normalization engine containing the `AddressNormalizer` class.

**Key Features:**
- Handles special characters (`#`, `,`, `/n` patterns)
- Normalizes directionals (Northeast → NE, Southwest → SW)
- Applies USPS-style suffix abbreviation rules
- **Rule**: Only the LAST suffix gets abbreviated, others remain spelled out
- Processes unit designators (Apt, Suite, Unit, etc.)
- Preserves fractions (1/2, 1/3, etc.)

#### `normalize_addresses.py`
Main script for processing CSV files with address normalization.

**Features:**
- Interactive file selection from current directory
- Automatic encoding detection for CSV files
- Auto-detects address columns using configurable patterns
- Creates normalized columns with `n_` prefix next to original columns
- Supports both automatic detection and manual column specification

#### `test_address_logic.py`
Comprehensive test suite for validating normalization logic.

**Test Coverage:**
- Suffix handling (Canyon Lake Circle → Canyon Lake Cir)
- Directional normalization (Northeast → NE)
- Special characters (commas, hash symbols)
- Unit designators (Apt, Suite, Unit)
- Complex address combinations
- Interactive testing for custom addresses

## Quick Start

### 1. Normalize CSV Files
```bash
python normalize_addresses.py
```
- Select from available CSV files in current directory
- Address columns automatically detected and normalized
- Output saved as `filename_proc.csv`

### 2. Test Normalization Rules
```bash
python test_address_logic.py
```
- Runs comprehensive test suite
- Interactive mode for testing custom addresses

### 3. Use in Your Code
```python
from address_normalizer import AddressNormalizer

normalizer = AddressNormalizer()
normalized = normalizer.normalize_address("123 Canyon Lake Circle NE Apt 5")
# Result: "123 Canyon Lake Cir NE Apt 5"
```

## Normalization Rules

### Suffix Rules
- **Only the LAST suffix is abbreviated**
- Example: `Canyon Lake Circle` → `Canyon Lake Cir`
- Canyon and Lake remain spelled out, Circle becomes Cir

### Directional Rules
- **Always abbreviated**: `Northeast` → `NE`, `Southwest` → `SW`
- Applied to: N, S, E, W, NE, NW, SE, SW

### Unit Designator Rules
- **Pass through unchanged**: Apartment, Suite, Unit, Apt, Office, etc.
- These words are preserved as-is for record matching

### Special Character Handling
- **Hash symbols (`#`)**: Converted to "Unit" unless adjacent to unit words
- **Commas**: Removed during processing
- **Fractions**: Preserved (1/2, 1/3, etc.)

## Column Detection

### Automatic Detection
The script automatically identifies address columns using:

**Exact Matches:**
```
'PRIMARY_ADDRESS', 'Address1', 'Addrline', 'AddrLines', 
'CnAdrPrf_Addrline1', 'CnAdrAdrProc_Addrline1'
```

**Pattern Matches:**
```
'^CnAdrAll_1_\d+_Addrline1$'
'^CnRelInd_1_\d+_Adr_Addrline1$'
```

### Manual Column Specification
```python
from normalize_addresses import normalize_specific_addresses

# Normalize specific columns
df_normalized = normalize_specific_addresses(df, ['PRIMARY_ADDRESS', 'Address1'])

# Single column
df_normalized = normalize_specific_addresses(df, 'PRIMARY_ADDRESS')
```

## Output Format

Original columns remain unchanged. Normalized columns are added with `n_` prefix:

| Original Column | Normalized Column |
|----------------|-------------------|
| `PRIMARY_ADDRESS` | `n_PRIMARY_ADDRESS` |
| `CnAdrAll_1_01_Addrline1` | `n_CnAdrAll_1_01_Addrline1` |

**Example Output:**
```
PRIMARY_ADDRESS              | n_PRIMARY_ADDRESS
7921 Canyon Lake Circle      | 7921 Canyon Lake Cir
123 Main Street Northeast    | 123 Main St NE  
456 Oak Ave #5              | 456 Oak Ave Unit 5
```

## Requirements

```python
pandas
chardet  # Optional: for better encoding detection
```

Install dependencies:
```bash
pip install pandas chardet
```

## Example Usage Scenarios

### 1. Data Deduplication
```python
# Before normalization - these appear different:
"123 Canyon Lake Circle"
"123 Canyon Lake Cir"

# After normalization - both become:
"123 Canyon Lake Cir"
```

### 2. Record Matching
```python
# Different formats of same address:
"456 Main Street Northeast Apartment 3"  → "456 Main St NE Apartment 3"
"456 Main St NE Apt 3"                   → "456 Main St NE Apt 3"
```

### 3. Batch Processing
```python
# Process entire CSV file
python normalize_addresses.py

# Select file from menu:
# 1. customer_data.csv
# 2. member_records.csv
# Select: 1

# Output: customer_data_proc.csv with normalized columns
```

## Performance Notes

- **Encoding Detection**: Automatically handles UTF-8, Latin-1, CP1252, ISO-8859-1
- **Memory Efficient**: Processes data in chunks for large files
- **Preserves Data**: Original columns remain unchanged

## Technical Details

### Address Processing Pipeline
1. **Clean special characters** (`/n`, commas, etc.)
2. **Handle hash symbols** (convert to "Unit" appropriately)
3. **Preserve fractions** (1/2, 1/3, etc.)
4. **Normalize directionals** (Northeast → NE)
5. **Apply suffix rules** (only last suffix abbreviated)
6. **Proper capitalization** (maintain consistent formatting)

### Suffix Mapping Examples
```python
# Full form → Abbreviation
'Circle': 'Cir', 'Street': 'St', 'Avenue': 'Ave'
'Lake': 'Lk', 'Canyon': 'Cyn', 'Drive': 'Dr'
```

---

**Note**: This normalization is optimized for record matching accuracy, not address postal compliance.
