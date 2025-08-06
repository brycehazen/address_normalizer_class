from address_normalizer import AddressNormalizer

def test_comprehensive_logic():
    normalizer = AddressNormalizer()
    
    test_cases = [
        # Original suffix tests
        "7921 Canyon Lake Cir",
        "7921 Canyon Lk Cir", 
        "123 Canyon Lake Circle",
        "456 Oak Street",
        
        # Directional tests (both full and abbreviated)
        "123 Main St NE",
        "123 Main St Northeast", 
        "456 Oak Ave SW",
        "456 Oak Ave Southwest",
        "789 Pine Dr N",
        "789 Pine Dr North",
        
        # Character tests (comma, hash)
        "123 Main St, Apt 4",
        "456 Oak Ave #5",
        "789 Pine Dr, Unit #3",
        "321 Elm St #2B",
        "654 Maple Ave, Suite 100",
        
        # Ignore list words (Unit, Apartment, Suite, etc.)
        "123 Main St Unit 5",
        "456 Oak Ave Apartment 3A",
        "789 Pine Dr Suite 200",
        "321 Elm St Apt B",
        "654 Maple Ave Office 12",
        "987 Cedar Ln Building C",
        "147 Birch Rd Floor 2",
        
        # Complex combinations
        "123 Canyon Lake Cir NE Unit 5",
        "456 Oak Street #3B Southwest",
        "789 Pine Lake Drive Apt 4A",
        "321 Maple Hill Circle Suite 100 NE",
        
        # Edge cases
        "123 Lake Shore Drive",
        "456 Hill Top Lane",
        "789 Mountain View Circle",
        "321 River Canyon Road",
        "50 Lake Dr #1/2"
    ]
    
    print("=== COMPREHENSIVE ADDRESS NORMALIZATION TEST ===")
    print("Rule: Only LAST suffix abbreviated, others spelled out")
    print("Directionals: Always abbreviated")
    print("Ignore words: Pass through unchanged")
    print("=" * 60)
    
    for i, address in enumerate(test_cases, 1):
        print(f"\n{i:2d}. Original:   {address}")
        normalized = normalizer.normalize_address(address)
        print(f"    Normalized: {normalized}")
        
        # Debug: show detection
        words = address.split()
        suffix_indices = []
        directional_indices = []
        ignore_indices = []
        
        for j, word in enumerate(words):
            if (word.title() in normalizer.street_suffix_mapping or 
                word.title() in normalizer.reverse_mapping):
                suffix_indices.append(j)
            if word.upper() in normalizer.directional:
                directional_indices.append(j)
            if word.title() in normalizer.ignore_list:
                ignore_indices.append(j)
        
        if suffix_indices:
            suffix_words = [words[j] for j in suffix_indices]
            print(f"    Suffixes:   {suffix_words} at indices {suffix_indices}")
            if suffix_indices:
                last_suffix = words[max(suffix_indices)]
                print(f"    Last suffix: '{last_suffix}' (should be abbreviated)")
        
        if directional_indices:
            directional_words = [words[j] for j in directional_indices]
            print(f"    Directionals: {directional_words} at indices {directional_indices}")
            
        if ignore_indices:
            ignore_words = [words[j] for j in ignore_indices]
            print(f"    Ignore words: {ignore_words} at indices {ignore_indices}")

def test_specific_address():
    """Test a specific address interactively"""
    normalizer = AddressNormalizer()
    
    print("\n" + "=" * 60)
    print("INTERACTIVE TEST - Enter your own address:")
    print("=" * 60)
    
    while True:
        try:
            address = input("\nEnter address (or 'quit' to exit): ").strip()
            if address.lower() in ['quit', 'exit', 'q']:
                break
                
            if not address:
                continue
                
            print(f"Original:   {address}")
            normalized = normalizer.normalize_address(address)
            print(f"Normalized: {normalized}")
            
            # Show what was detected
            words = address.split()
            suffix_indices = []
            directional_indices = []
            ignore_indices = []
            
            for j, word in enumerate(words):
                if (word.title() in normalizer.street_suffix_mapping or 
                    word.title() in normalizer.reverse_mapping):
                    suffix_indices.append(j)
                if word.upper() in normalizer.directional:
                    directional_indices.append(j)
                if word.title() in normalizer.ignore_list:
                    ignore_indices.append(j)
            
            print(f"Detection - Suffixes: {suffix_indices}, Directionals: {directional_indices}, Ignore: {ignore_indices}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    test_comprehensive_logic()
    test_specific_address()