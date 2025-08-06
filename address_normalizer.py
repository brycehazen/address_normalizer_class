import re

class AddressNormalizer:
    def __init__(self):
        # Configurations
        self.ignore_list = {"Apartment", "Apartments","Apt", "Penthouse", "Ph", "Basement", "Bsmt", "Pier", "Building", "Bldg", "Rear", "Department", "Dept", "Room", "Rm","Floor", "Fl", "Side", "Front", "Frnt", "Slip", "Hanger","Hngr", "Space", "Spc", "Key",  "Stop", "Lobby", "Lbby","Suite", "Ste", "Lot", "Trailer", "Trlr", "Lower", "Lowr", "Unit","Office", "Ofc", "Upper", "Uppr"}
        self.directional = {'S', 'W', 'N', 'E', 'SE', 'SW', 'NE', 'NW', 'PO'} 
        self.street_suffix_mapping = {'Alley': 'Aly','Anex': 'Anx','Annex': 'Anx', 'Apartment': 'Apt','Apartments': 'Apt','Arcade': 'Arc','Avenue': 'Ave','Bayou': 'Byu','Beach': 'Bch','Bend': 'Bnd','Bluff': 'Blf','Bluffs': 'Blfs','Bottom': 'Btm','Boulevard': 'Blvd','Branch': 'Br','Bridge': 'Brg','Brook': 'Brk','Brooks': 'Brks','Burg': 'Bg','Burgs': 'Bgs','Bypass': 'Byp','Camp': 'Cp','Canyon': 'Cyn','Cape': 'Cpe','Causeway': 'Cswy','Center': 'Ctr','Centers': 'Ctrs','Circle': 'Cir','Circles': 'Cirs','Cliff': 'Clf','Cliffs': 'Clfs','Club': 'Clb','Common': 'Cmn','Commons': 'Cmns','Corner': 'Cor','Corners': 'Cors','Course': 'Crse','Court': 'Ct','Courts': 'Cts','Cove': 'Cv','Coves': 'Cvs','Creek': 'Crk','Crescent': 'Cres','Crest': 'Crst','Crossing': 'Xing','Crossroad': 'Xrd','Crossroads': 'Xrds','Curve': 'Curv','Dale': 'Dl','Dam': 'Dm','Divide': 'Dv','Drive': 'Dr','Drives': 'Drs','Estate': 'Est','Estates': 'Ests','Expressway': 'Expy','Extension': 'Ext','Extensions': 'Exts','Fall': 'Fall','Falls': 'Fls','Ferry': 'Fry','Field': 'Fld','Fields': 'Flds','Flat': 'Flt','Flats': 'Flts','Ford': 'Frd','Fords': 'Frds','Forest': 'Frst','Forge': 'Frg','Forges': 'Frgs','Fork': 'Frk','Forks': 'Frks','Fort': 'Ft','Freeway': 'Fwy','Garden': 'Gdn','Gardens': 'Gdns','Gateway': 'Gtwy','Glen': 'Gln','Glens': 'Glns','Green': 'Grn','Greens': 'Grns','Grove': 'Grv','Groves': 'Grvs','Harbor': 'Hbr','Harbors': 'Hbrs','Haven': 'Hvn','Heights': 'Hts','Highway': 'Hwy','Hill': 'Hl','Hills': 'Hls','Hollow': 'Holw','Inlet': 'Inlt','Island': 'Is','Islands': 'Iss','Isle': 'Isle','Junction': 'Jct','Junctions': 'Jcts','Key': 'Ky','Keys': 'Kys','Knoll': 'Knl','Knolls': 'Knls','Lake': 'Lk','Lakes': 'Lks','Land': 'Land','Landing': 'Lndg','Lane': 'Ln','Light': 'Lgt','Lights': 'Lgts','Loaf': 'Lf','Lock': 'Lck','Locks': 'Lcks','Lodge': 'Ldg','Loop': 'Lp','Mall': 'Mall','Manor': 'Mnr','Manors': 'Mnrs','Meadow': 'Mdw','Meadows': 'Mdws','Mews': 'Mews','Mill': 'Ml','Mills': 'Mls','Mission': 'Msn','Motorway': 'Mtwy','Mount': 'Mt','Mountain': 'Mtn','Mountains': 'Mtns','Neck': 'Nck','Orchard': 'Orch','Oval': 'Oval','Overpass': 'Opas','Park': 'Park','Parkway': 'Pkwy','Pass': 'Pass','Passage': 'Psge','Path': 'Path','Pike': 'Pike','Pine': 'Pne','Pines': 'Pnes','Place': 'Pl','Plain': 'Pln','Plains': 'Plns','Plaza': 'Plz','Point': 'Pt','Points': 'Pts','Port': 'Prt','Ports': 'Prts','Prairie': 'Pr','Radial': 'Radl','Ranch': 'Rnch','Rapid': 'Rpd','Rapids': 'Rpds','Rest': 'Rst','Ridge': 'Rdg','Ridges': 'Rdgs','River': 'Riv','Road': 'Rd','Roads': 'Rds','Route': 'Rte','Row': 'Row','Rue': 'Rue','Run': 'Run','Shoal': 'Shl','Shoals': 'Shls','Shore': 'Shr','Shores': 'Shrs','Skyway': 'Skyway','Spring': 'Spg','Springs': 'Spgs','Spur': 'Spur','Square': 'Sq','Squares': 'Sqs','Station': 'Sta','Stravenue': 'Stra','Stream': 'Strm','Street': 'St','Streets': 'Sts','Summit': 'Smt','Terrace': 'Ter','Throughway': 'Trwy','Trace': 'Trce','Track': 'Trak','Trafficway': 'Trfy','Trail': 'Trl','Trailer': 'Trlr','Tunnel': 'Tunl','Turnpike': 'Tpke','Underpass': 'Upas','Union': 'Un','Valley': 'Vly','Valleys': 'Vlys','Viaduct': 'Via','View': 'Vw','Views': 'Vws','Village': 'Vlg','Villages': 'Vlgs','Vista': 'Vis','Walk': 'Walk','Way': 'Way','Well': 'Wl','Wells': 'Wls','North': 'N','East': 'E','South': 'S','West': 'W','Northeast': 'NE','Southeast': 'SE','Northwest': 'NW','Southwest': 'SW'}

        
        # Create reverse mapping for abbreviated to full forms
        self.reverse_mapping = {v: k for k, v in self.street_suffix_mapping.items()}
    
    def normalize_address(self, address):
        if not isinstance(address, str) or address.strip() == '':
            return address

        # 1) Fix the erroneous "/n" patterns
        cleaned_address = re.sub(r'(\S*)\s*/\s*n\s*(\S*)', r'\1 \2', address)
        cleaned_address = re.sub(r'(^/\s*n\s*)|(\s*/\s*n\s*$)', ' ', cleaned_address)
        cleaned_address = re.sub(r'(?<!\d)/\s*n\b', ' ', cleaned_address)
        cleaned_address = re.sub(r'(?<!\d)(\s)/(\s+)(?!\d)', r'\1\2', cleaned_address)
        cleaned_address = cleaned_address.replace('\\n', ' ').replace('\n', ' ').strip()

        # 2) Remove common throwaway phrases
        cleaned_address = re.sub(r'See\s+[Mm]ailing(?:\s+[Aa]ddress)?', '', cleaned_address).strip()
        cleaned_address = re.sub(r'\bunlisted\b', '', cleaned_address, flags=re.IGNORECASE).strip()

        # Insert spaces between letters and digits (e.g. "Center25" => "Center 25")
        cleaned_address = re.sub(r'([A-Za-z])(\d+)', r'\1 \2', cleaned_address)

        # Handle multiple slash fraction (e.g. "25/1/2" => "25 1/2")
        cleaned_address = re.sub(r'(\d+)/(?=\d+/)', r'\1 ', cleaned_address)

        # ----------------------------------------------------------------
        # 2.5) SPECIAL STEP FOR '#':
        #
        # If '#' does NOT have an ignore-list word directly to the left
        # or right (ignoring spaces), we replace '#' with "Unit ".
        # Otherwise, we remove '#' entirely.
        #
        # We'll do this by splitting on whitespace, scanning token by token.

        words = cleaned_address.split()
        transformed = []
        for i, token in enumerate(words):
            if '#' not in token:
                transformed.append(token)
                continue

            # If the entire token is just '#' or '#something',
            # we handle them carefully.
            # (1) Check neighbors in the list.
            left_ignore = False
            right_ignore = False

            # See if the left word is in ignore_list (if it exists)
            if i > 0:
                left_word = words[i-1].title()
                if left_word in self.ignore_list:
                    left_ignore = True

            # See if the right word is in ignore_list (if it exists)
            if i < len(words) - 1:
                right_word = words[i+1].title()
                if right_word in self.ignore_list:
                    right_ignore = True

            # If we find an ignore_list neighbor, we remove '#'
            # Otherwise, we replace '#' with 'Unit '
            if left_ignore or right_ignore:
                # Remove '#' from the token. e.g. "#2" => "2"
                no_hash = token.replace('#', '')
                if no_hash.strip():
                    transformed.append(no_hash.strip())
            else:
                # Replace '#' with "Unit "
                # e.g. "#225a" => "Unit 225a"
                replaced = token.replace('#', 'Unit ', 1)
                transformed.append(replaced.strip())

        cleaned_address = ' '.join(transformed)
        # ----------------------------------------------------------------

        # 3) Next, protect numeric fractions like 1/2, 1/3rd, etc.
        fraction_placeholders = {}
        fraction_counter = 0

        # Only match if there's no extra slash after it
        fraction_pattern = r'\b\d+/\d+(?:st|nd|rd|th)?(?!/)\b'
        for fraction_match in re.finditer(fraction_pattern, cleaned_address):
            fraction = fraction_match.group(0)
            placeholder = f"FRACTION_{fraction_counter}"
            fraction_placeholders[placeholder] = fraction
            cleaned_address = cleaned_address.replace(fraction, placeholder, 1)
            fraction_counter += 1

        # 4) Handle hyphens differently - replace them with spaces
        cleaned_address = cleaned_address.replace('-', ' ')
        
        # 5) Now remove other "special" characters except letters, digits, underscores, spaces
        cleaned_address = re.sub(r'[^\w\s]', '', cleaned_address).strip()

        # 6) Restore the fraction placeholders
        for placeholder, fraction in fraction_placeholders.items():
            cleaned_address = cleaned_address.replace(placeholder, fraction)

        if not cleaned_address:
            return address

        words = cleaned_address.split()

        # Normalize spelled-out directionals to abbreviations (Southeast -> SE, etc.)
        normalized_words = []
        for w in words:
            w_stripped = w.upper().rstrip('.')  # remove trailing period
            if w_stripped == "SOUTHEAST":
                normalized_words.append("SE")
            elif w_stripped == "SOUTHWEST":
                normalized_words.append("SW")
            elif w_stripped == "NORTHEAST":
                normalized_words.append("NE")
            elif w_stripped == "NORTHWEST":
                normalized_words.append("NW")
            else:
                normalized_words.append(w)
        words = normalized_words

        # Identify suffixes, directionals, unit designators
        primary_suffix_indices = []
        directional_indices = []
        unit_indices = []

        for i, word in enumerate(words):
            # Check if word is a suffix (either full form or abbreviation)
            if (word.title() in self.street_suffix_mapping or 
                word.title() in self.reverse_mapping):
                primary_suffix_indices.append(i)
            if word.upper() in self.directional:
                directional_indices.append(i)
            if word.title() in self.ignore_list:
                unit_indices.append(i)

        processed_words = []
        for i, word in enumerate(words):
            # Always abbreviate directionals (N, S, E, W, NE, etc.)
            if word.upper() in self.directional:
                processed_words.append(word.upper())
                continue

            # If word is in ignore_list, pass it through (we don't expand or abbreviate)
            if word.title() in self.ignore_list:
                processed_words.append(word)
                continue

            # New simplified rule: Only the LAST suffix gets abbreviated, all others spelled out
            if i in primary_suffix_indices:
                # Find the last suffix index
                last_suffix_index = max(primary_suffix_indices) if primary_suffix_indices else -1
                
                if i == last_suffix_index:
                    # This is the last suffix - abbreviate it
                    # If it's already abbreviated, keep it. If it's full form, abbreviate it.
                    if word.title() in self.street_suffix_mapping:
                        # Full form -> abbreviate
                        processed_words.append(self.street_suffix_mapping[word.title()])
                    else:
                        # Already abbreviated -> keep as is
                        processed_words.append(word)
                else:
                    # Not the last suffix - spell it out
                    if word.title() in self.reverse_mapping:
                        # Abbreviated -> spell out
                        processed_words.append(self.reverse_mapping[word.title()])
                    else:
                        # Already spelled out -> keep as is
                        processed_words.append(word.title())
                continue

            processed_words.append(word)

        # Remove duplicate ignore_list words (e.g. "Unit Unit" if it occurred twice)
        seen_ignore = set()
        final_words = []
        for word in processed_words:
            if word.title() in self.ignore_list:
                if word.title() in seen_ignore:
                    continue
                seen_ignore.add(word.title())
            final_words.append(word)

        # Capitalize properly
        capitalized_words = []
        for word in final_words:
            # e.g. "1st", "2nd": keep them lower for the suffix part
            if re.match(r'^\d+(?:st|nd|rd|th)$', word.lower()):
                capitalized_words.append(word.lower())
            # Keep directionals in uppercase
            elif word.upper() in self.directional:
                capitalized_words.append(word.upper())
            else:
                capitalized_words.append(word.title())

        return ' '.join(capitalized_words)
