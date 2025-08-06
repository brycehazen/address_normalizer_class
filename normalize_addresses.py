import pandas as pd
import re
import os
import glob
from address_normalizer import AddressNormalizer

try:
    import chardet
    CHARDET_AVAILABLE = True
except ImportError:
    CHARDET_AVAILABLE = False
    print("Note: chardet not available. Using fallback encoding detection.")

# Column mapping for address line identification
COLUMN_MAPPING = {
    'Address line 1': ['Gf_CnAdrPrf_Addrline1', 'Addrline', 'AddrLines', 'AddrLine1', 'Address1', 'CnAdrAdrProc_Addrline1', 'Address Line 1', 'CnAdrPrf_Addrline1', 'PRIMARY_ADDRESS'],
    'Address line 2': ['Gf_CnAdrPrf_Addrline2', 'Addrline2', 'AddrLine2', 'Address2', 'CnAdrAdrProc_Addrline2', 'Address Line 2', 'CnAdrPrf_Addrline2'],
}

COLUMN_PATTERNS = {
    'Address line 1': [
        r'^CnAdrAll_1_\d+_Addrline1$',      
        r'^CnRelInd_1_\d+_Adr_Addrline1$',  
    ],
    'Address line 2': [
        r'^CnAdrAll_1_\d+_Addrline2$',      
        r'^CnRelInd_1_\d+_Adr_Addrline2$',  
    ],
    'City': [
        r'^CnAdrAll_1_\d+_City$',          
        r'^CnRelInd_1_\d+_Adr_City$',       
    ],
    'State': [
        r'^CnAdrAll_1_\d+_State$',         
        r'^CnRelInd_1_\d+_Adr_State$',      
    ],
    'ZIP Code': [
        r'^CnAdrAll_1_\d+_ZIP$',            
        r'^CnRelInd_1_\d+_Adr_ZIP$',        
    ],
}

def create_enhanced_reverse_mapping(dataframe_columns):
    """Create a reverse mapping from actual column names to standard names."""
    reverse_mapping = {}
    
    # Map exact matches from COLUMN_MAPPING - only if they exist in the DataFrame
    for standard_name, variations in COLUMN_MAPPING.items():
        for variation in variations:
            if variation in dataframe_columns:
                reverse_mapping[variation] = standard_name
    
    # Map pattern matches from COLUMN_PATTERNS
    for col in dataframe_columns:
        if col not in reverse_mapping:  
            for standard_name, patterns in COLUMN_PATTERNS.items():
                for pattern in patterns:
                    if re.match(pattern, col):
                        reverse_mapping[col] = standard_name
                        break  
                if col in reverse_mapping:  
                    break
    
    return reverse_mapping

def detect_file_encoding(file_path):
    """
    Detect the encoding of a file using chardet or fallback methods.
    
    Parameters:
    -----------
    file_path : str
        Path to the file to detect encoding for
        
    Returns:
    --------
    str
        Detected encoding string
    """
    if CHARDET_AVAILABLE:
        # Use chardet for accurate detection
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            confidence = result['confidence']
            print(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
            return encoding
    else:
        # Fallback: try common encodings
        common_encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        
        for encoding in common_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    file.read(1000)  # Try to read first 1000 characters
                print(f"Successfully detected encoding: {encoding}")
                return encoding
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        # If all fail, return utf-8 as default
        print("Could not detect encoding, defaulting to utf-8")
        return 'utf-8'

def read_csv_with_encoding(file_path):
    """
    Read CSV file with automatic encoding detection.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file
        
    Returns:
    --------
    pandas.DataFrame
        Loaded DataFrame
    """
    encoding = detect_file_encoding(file_path)
    
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        return df
    except UnicodeDecodeError:
        # If detected encoding fails, try other common encodings
        fallback_encodings = ['latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        
        for fallback_encoding in fallback_encodings:
            if fallback_encoding != encoding:  # Skip the one we already tried
                try:
                    print(f"Trying fallback encoding: {fallback_encoding}")
                    df = pd.read_csv(file_path, encoding=fallback_encoding)
                    print(f"Successfully loaded with encoding: {fallback_encoding}")
                    return df
                except UnicodeDecodeError:
                    continue
        
        # If all encodings fail, raise the original error
        raise

def identify_address_columns(df):
    """Identify all address line columns in the DataFrame."""
    reverse_mapping = create_enhanced_reverse_mapping(df.columns)
    address_columns = {}
    
    for col, standard_name in reverse_mapping.items():
        if 'Address line' in standard_name:
            address_columns[col] = standard_name
    
    return address_columns

def normalize_address_columns(df, specific_columns=None):
    """
    Normalize address columns in a DataFrame.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing address columns to normalize
    specific_columns : list, optional
        Specific column names to normalize. If None, will auto-detect address columns.
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with normalized address columns added (prefixed with 'n_')
    """
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    # Initialize the address normalizer
    normalizer = AddressNormalizer()
    
    # Determine which columns to normalize
    if specific_columns is not None:
        # Use specific columns provided by user
        columns_to_normalize = {}
        for col in specific_columns:
            if col in df_copy.columns:
                columns_to_normalize[col] = col  # Use the column name as is
            else:
                print(f"Warning: Column '{col}' not found in DataFrame")
    else:
        # Auto-detect address columns
        columns_to_normalize = identify_address_columns(df_copy)
    
    if not columns_to_normalize:
        print("No address columns found to normalize")
        return df_copy
    
    # Normalize each identified address column
    for original_col, standard_name in columns_to_normalize.items():
        normalized_col_name = f'n_{original_col}'
        
        print(f"Normalizing column: {original_col} -> {normalized_col_name}")
        
        # Apply normalization to the column
        normalized_data = df_copy[original_col].apply(
            lambda x: normalizer.normalize_address(x) if pd.notna(x) else x
        )
        
        # Find the position of the original column
        original_col_position = df_copy.columns.get_loc(original_col)
        
        # Insert the normalized column right after the original column
        df_copy.insert(original_col_position + 1, normalized_col_name, normalized_data)
    
    return df_copy

def normalize_specific_addresses(df, column_names):
    """
    Normalize specific address columns by name.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing address columns
    column_names : str or list
        Column name(s) to normalize
    
    Returns:
    --------
    pandas.DataFrame
        DataFrame with normalized address columns added
    """
    if isinstance(column_names, str):
        column_names = [column_names]
    
    return normalize_address_columns(df, specific_columns=column_names)

def main():
    """
    Interactive address normalization - select CSV file from current directory.
    """
    try:
        # Find all CSV files in current directory
        csv_files = glob.glob("*.csv")
        
        if not csv_files:
            print("No CSV files found in the current directory.")
            return
        
        # Display available CSV files
        print("Available CSV files to normalize:")
        print("-" * 50)
        for i, filename in enumerate(csv_files, 1):
            print(f"{i}. {filename}")
        
        # Get user selection
        while True:
            try:
                choice = input(f"\nSelect a file to normalize (1-{len(csv_files)}): ").strip()
                file_index = int(choice) - 1
                
                if 0 <= file_index < len(csv_files):
                    input_file = csv_files[file_index]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(csv_files)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                return
        
        print(f"\nSelected file: {input_file}")
        print("Loading data...")
        
        # Load the selected DataFrame with encoding detection
        df = read_csv_with_encoding(input_file)
        print(f"Loaded DataFrame with {len(df)} rows and {len(df.columns)} columns")
        
        # Check for address columns first
        address_cols = identify_address_columns(df)
        if address_cols:
            print(f"Found address columns: {list(address_cols.keys())}")
        else:
            print("No address columns detected in this file.")
            return
        
        # Auto-detect and normalize all address columns
        print("\nNormalizing address columns...")
        normalized_df = normalize_address_columns(df)
        
        # Generate output filename by adding '_proc' to the original filename
        if input_file.endswith('.csv'):
            output_file = input_file[:-4] + '_proc.csv'
        else:
            output_file = input_file + '_proc'
        
        # Save the result
        normalized_df.to_csv(output_file, index=False)
        print(f"\nSuccessfully saved normalized data to: {output_file}")
        
        # Show summary
        new_cols = [col for col in normalized_df.columns if col.startswith('n_')]
        print(f"Added {len(new_cols)} normalized columns: {new_cols}")
        
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except pd.errors.EmptyDataError:
        print("The selected file is empty or corrupted.")
    except Exception as e:
        print(f"Error: {e}")
        print("Please check the file format and try again.")

if __name__ == "__main__":
    main()