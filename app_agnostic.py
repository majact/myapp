# Import necessary libraries
import requests  # HTTP requests library
import pandas as pd  # Data manipulation library
from urllib.parse import urlencode
import streamlit as st
import re

# Define the URL for the feature layer containing street data
api_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0/query"

# Define city-specific search areas
city_search_areas = {
    "TIGARD": ["TIGARD", "HILLSBORO", "SHERWOOD", "TUALATIN", "FOREST GROVE", "CORNELIUS"],
    "HILLSBORO": ["HILLSBORO", "TIGARD", "FOREST GROVE", "CORNELIUS", "BEAVERTON"],
    "SHERWOOD": ["SHERWOOD", "TIGARD", "TUALATIN", "WILSONVILLE"],
    # Add more cities and their respective search areas as needed
}

# Initialize base query parameters
params = {
    "where": "1=1",  # Default where clause to select all records (placeholder)
    "outFields": "*",  # Retrieve all fields
    "f": "json",  # Format the response as JSON
}

# Streamlit UI for user agency selection
st.title("Proposed Name Checker")
# Dropdown for city selection
selected_city = st.selectbox("Select your agency's mailing city:", options=list(city_search_areas.keys()))

# Apply filtering logic based on the selected city
if selected_city:
    search_cities = city_search_areas[selected_city]
    where_clause = " OR ".join([f"MSAGComm_L = '{city}'" for city in search_cities])
    params["where"] = where_clause  # Update the query parameters with the city filter

    # Query the feature layer with the updated filtering parameters
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        features = response.json().get("features", [])
        existing_data = pd.DataFrame([feature["attributes"] for feature in features])
        st.success(f"Loaded {len(existing_data)} records for search area: {', '.join(search_cities)}.")
    else:
        st.error(f"Failed to load data for {selected_city}. Status code: {response.status_code}")

# Input for proposed name
proposed_name = st.text_input("Enter the proposed street name:")
if st.button("Check Name"):
    if proposed_name.strip():
        result = check_proposed_name(proposed_name.upper().strip())
        st.success(result)  # Display the result
    else:
        st.warning("Please enter a valid street name.")



# # Query all data from the feature layer using the REST API
# params = {
#     "where": "1=1",  # Select all records
#     "outFields": "*",  # Retrieve all fields
#     "f": "json"  # Format the response as JSON
# }

response = requests.get(api_url, params=params)  # Send GET request
if response.status_code == 200:
    # Convert response to Pandas DataFrame
    features = response.json().get("features", [])
    existing_data = pd.DataFrame([feature["attributes"] for feature in features])
    print("Street data loaded successfully.")
else:
    print(f"Failed to load data. Status code: {response.status_code}")



# Lists for disallowed names based on category (e.g., business, city, county, arterial)
# These lists will be used later in the script to filter out unwanted names

# Placeholder for disallowed business names (currently empty)
business_names = []

# Cities and counties with restricted names for street data
city_names = ['BEAVERTON', 'TIGARD']
county_names = ['MALHEUR']

# Common arterial street names that should be excluded
arterial_names = [
    "ALLEN", "APIARY", "BALD PEAK", "BANY", "BARBER", "BARBUR", "BARNES", "BASELINE",
    "BEAVERCREEK", "BEEF BEND", "BELMONT", "BERTHA", "BOECKMAN", "BONITA", "BOONE", "BORLAND",
    "BROOKWOOD", "BROADWAY", "BURNSIDE", "CANYON", "CAPITOL", "CHILDS", "CORNELIUS", "CORNELL",
    "COUNTRY CLUB", "DAVIS", "DENVER", "DIVISION", "ELLIGSEN", "EVERGREEN", "FARMINGTON", "FLAVEL",
    "FOSTER", "GAARDE", "GALES", "GERMANTOWN", "GLENCOE", "GLISAN", "GRABHORN", "GRAHAM", "GRAND",
    "GREENBURG", "GREENBERG", "HALL", "HALSEY", "HART", "HAWTHORNE", "HELVETIA", "INTERSTATE",
    "JACKSON", "JENKINS", "JOHNSON CREEK", "KANE", "KAISER", "KILLINGSWORTH", "KRUSE", "LAIDLAW",
    "LARCH MOUNTAIN", "LOMBARD", "MACADAM", "MAIN", "MARINE", "MARKET", "MARTIN LUTHER KING JR",
    "MCDONALD", "MINTER", "MURRAY", "NAITO", "OLESON", "PACIFIC", "POWELL", "REDLAND", "RIVER",
    "RIVERSIDE", "ROSS ISLAND", "SALTZMAN", "SANDY", "SCHOLLS", "SCHOLLS FERRY", "SELLWOOD",
    "SKYLINE", "SPRINGVILLE", "SPRINGWATER", "ST JOHNS", "STAFFORD", "STARK", "SUNNYBROOK",
    "SUNNYSIDE", "TACOMA", "TAYLORS", "THOMPSON", "TONGUE", "TONQUIN", "TOWN CENTER", "WALKER",
    "WATSON", "WEIDLER", "WOODSTOCK", "ZION"
]

# Names that should be avoided if they start with these prefixes
banned_name_starts = ["HILL", "BEAVER", "ALDER", "CEDAR", "MAPLE", "OAK", "HALL", "MAIN", "MT", "PACIFIC", "PARK", "ST ", "WALNUT", "WILLAMETTE"]

# Lists for checking specific name components
cardinal_names = ["NORTH", "SOUTH", "EAST", "WEST"]  # Cardinal directions
usps_names = ["AVENUE", "PLACE", "WAY", "TERRACE", "DRIVE", "STREET"]  # USPS street types

# Common name starts that might be excluded due to duplication or ambiguity
name_starts = ["APPLE",
    "GREEN", "BLUE", "WHITE", "BROWN", "BLACK", "RED", "YELLOW", "PURPLE", "GREY", "GRAY", "ORANGE",
    "ALBERT", "ALEX", "ALTA", "ARCH", "ASH", "BARN", "BASE", "BAY", "BEAVER", "BEEF", "BELL", "BERNARD",
    "BIG", "BOONE", "BOUND", "BOX", "BRAD", "BRAN", "BROWN", "BRIGHT", "BROOK", "BRUN", "BUCK",
    "BUTTER", "CANYON", "CHAT", "CHERRY", "CHURCH", "CLARK", "CLAY", "CLEAR", "CLIFF", "CLOUD",
    "CLOVER", "COLD", "COOL", "COPPER", "CORN", "CROSS", "DALE", "DAWN", "DEEP", "DEER", "DOUBLE",
    "DRAKE", "DRIFT", "DUCK", "EAGLE", "ELDER", "ELK", "END", "EVER", "FAIR", "FARM", "FAVOR",
    "FELD", "FERN", "FIDDLE", "FIRE", "FISH", "FLAG", "FLAT", "FLINT", "FOREST", "FREE", "GARDEN", "GERMAN",
    "GLAD", "GLEN", "GOLD", "GOOD", "GRANT", "GRAPE", "GUM", "HAGGER", "HANDY", "HATCH", "HAY",
    "HIGH", "HITCH", "HOLLY", "IRON", "JACK", "JOY", "KENT", "KIND", "KING", "KIRK",
    "KITTY", "LADY", "LAKE", "LARK", "LEATHER", "LEMON", "LEVEL", "LEWIS", "LIME", "LIVER",
    "LOCK", "LONG", "LOYAL", "MARSH", "MARTIN", "MASON", "MASTER", "MATCH", "MAY", "MORGAN",
    "MORNING", "MOUNTAIN", "NETHER", "NEW", "NIGHT", "OAT", "OLD", "ORCHARD", "OVER", "OX", "PATTER", "PENNY",
    "PEPPER", "PERFECT", "PINE", "PLANT", "PLAY", "QUEEN", "QUICK", "QUIN", "RAMS", "RED", "RENEW",
    "REX", "RICH", "RING", "RIVER", "ROAD", "ROBERT", "ROCK", "ROUND", "SAGE", "SAIL", "SHAKER",
    "SHOW", "SILVER", "SINGLE", "SKY", "SPRING", "STAMP", "STAN", "STAR", "STILL", "STOCK",
    "SUN", "SUNNY", "TOAST", "TOM", "TOWER", "TOWN", "UNDER", "UP", "VALEN", "VANDER", "WALK",
    "WASH", "WATER", "WELL", "WILLIAM", "WILSON", "WINK", "WISE", "WISH", "WOLF", "WONDER", "WOOD",
    "YORK"
]

repeated_letter_exceptions = {"AGREE", "AGREEMENT", "APPLE", "BELL", "BERRY", "BILL", "BOOK", "BROOK", "BUTTER", "CHOPP", "CLAPP", "CLIFF",
 "COMMUNITY", "COOL", "COPPER", "COSTELLO", "CRESS", "CROSS", "DANNER", "DEEP", "DELL", "DUFF", "FALL", "FREE", "GOOD", "GREEN", 
 "GULL", "HAGGER", "HILL", "HOOVER", "HUGG", "JOLLY", "KITTY", "LESS", "MAMMOTH", "MELLOW", "MILL", "MOOSE", 
 "NESS", "PATTER", "PEPPER", "PENNY", "PIONEER", "POOL", "POTTER", "STALL", "STILL", "SUCCESS", "TREE", "VANILLA", 
 "WELL", "WHEEL", "WOOD", "YARNELL", "ZIPPER"}

problematic_combination_exceptions = {"FIELD", "BOUND", "DUCK", "BUCK"}
usps_street_type_exceptions = {"SPARK"}
ends_with_exceptions = {"VALE", "DALE", "SAFARI", "ABLE"}

# Disallowed endings
disallowed_ends_with = ("I", "C", "EL", "LE", "AIRE")

homophones = {
        "AISLE": ["ISLE"], "AIR": ["HEIR"], "AFFECT": ["EFFECT"], "BARE": ["BEAR"], "BLEW": ["BLUE"],
        "BRAKE": ["BREAK"], "CELL": ["SELL"], "CENT": ["SCENT", "SENT"], "COURSE": ["COARSE"],
        "DIE": ["DYE"], "FAIR": ["FARE"], "FORTH": ["FOURTH"], "HEAR": ["HERE"],
        "HOLE": ["WHOLE"], "HOUR": ["OUR"], "KNIGHT": ["NIGHT"], "LEAD": ["LED"], "MAIL": ["MALE"],
        "MEAT": ["MEET"], "PAIR": ["PARE", "PEAR"], "PEACE": ["PIECE"], "PLAIN": ["PLANE"], "PRINCIPAL": ["PRINCIPLE"],
        "RIGHT": ["WRITE", "RITE"], "SEA": ["SEE"], "SIGHT": ["SITE"], "STEAL": ["STEEL"], "STAIR": ["STARE"],
        "TAIL": ["TALE"], "THEIR": ["THERE", "THEY’RE"], "TOE": ["TOW"], "WAIST": ["WASTE"], "WEAK": ["WEEK"],
        "WEATHER": ["WHETHER"], "WHICH": ["WITCH"], "YOUR": ["YOU’RE"], "REED": ["READ"], "SEAS": ["SEES", "CEASE"],
        "SOLE": ["SOUL"], "SOME": ["SUM"], "STALK": ["STOCK"], "THREW": ["THROUGH"], "WEAR": ["WHERE"],
        "WEIGH": ["WAY"], "WHOSE": ["WHO’S"], "VAIN": ["VEIN", "VANE"], "ALLEN": ["ALAN"], "MARY": ["MERRY"],
        "LUKE": ["LOOK"], "CHRIS": ["KRIS"], "MOOR": ["MORE"]
    }



# called by check_proposed_name
def evaluate_word(word, repeated_letter_exceptions, problematic_combination_exceptions,
                  disallowed_ends_with, ends_with_exceptions, homophones):
    issues = []
    word = word.upper()  # Normalize to uppercase for consistent checks

    # Check for special characters
    if re.search(r'[^A-Z\s]', word):
        issues.append("Contains special characters")

    # Check for silent letters
    silent_patterns = ['KN', 'GN', 'PS', 'PH']
    for pattern in silent_patterns:
        if (pattern == 'PS' and word.startswith(pattern)) or (pattern in word and pattern != 'PS'):
            issues.append(f"Contains silent '{pattern}'")

    # Check for problematic vowel/consonant combinations, ignoring exceptions
    problematic_combinations = [] 
    #['IE', 'EI', 'GH', 'AI', 'CK', 'AE', 'OI', 'OU', 'QU', 'EY', 'OE', 'EO', 'UA', 'KN']
    for combo in problematic_combinations:
        if combo in word and not any(exc in word for exc in problematic_combination_exceptions):
            issues.append(f"Contains problematic combination '{combo}'")

    # Check for repeated letters, ignoring exceptions
    if any(word.count(char * 2) > 0 for char in set(word)):
        if not any(exc in word for exc in repeated_letter_exceptions):
            issues.append("Contains repeated letters")

    # Check if word ends in disallowed endings unless in exceptions
    if word.endswith(disallowed_ends_with) and not any(word.endswith(exc) for exc in ends_with_exceptions):
        issues.append("Ends in disallowed suffix")

    # Check word length
    if len(word) > 12:
        issues.append("Exceeds length limit")

    # Check for homophones with specific feedback
    matching_homophones = [f"{key}-{value}" for key, values in homophones.items() for value in values if
                           key in word or value in word]
    if matching_homophones:
        issues.append(f"Contains homophone: {', '.join(matching_homophones)}")

    # Return approval or disapproval based on issues
    feedback = ', '.join(issues)
    return ("Disapproved", feedback[:252] + "...") if issues else ("Approved", "Meets all criteria")



# called by check_proposed_name
def consolidate_ranges(ranges):
    """
    Consolidates a list of numerical ranges by merging overlapping, adjacent, or close ranges within a 500-unit threshold.
    Args:
        ranges (list of tuples): A list of ranges represented as (start, end).
    Returns:
        list of tuples: A sorted list of consolidated ranges.
    """
    # Validate input format
    if not isinstance(ranges, list):
        raise ValueError(f"Expected a list of tuples, but got {type(ranges).__name__}: {ranges}")
    if not all(isinstance(r, tuple) and len(r) == 2 for r in ranges):
        raise ValueError(f"All elements in ranges must be tuples of (start, end), but got: {ranges}")

    # Sort ranges by their start values
    sorted_ranges = sorted(ranges, key=lambda x: x[0])

    # Consolidate ranges based on the 500-unit threshold
    consolidated = []
    for start, end in sorted_ranges:
        if not consolidated:
            consolidated.append((start, end))
        else:
            last_start, last_end = consolidated[-1]
            # Merge if ranges overlap, are adjacent, or within 500 units
            if start <= last_end + 500:
                consolidated[-1] = (last_start, max(last_end, end))
            else:
                consolidated.append((start, end))

    return consolidated



# called by check_proposed_name
# Helper function to identify if a given name starts with any prefix in the name_starts list
def matches_namestart(name, name_starts):
    for start in name_starts:
        if name.startswith(start):  # Check if the name starts with the current prefix
            return start  # Return the matching prefix if found
    return None  # Return None if no match is found

print("Name start matching function defined.")



# called by check_proposed_name
# Function to check if a proposed name starts with any banned prefix from a provided list
def check_banned_name_start(proposed_name, banned_name_starts):
    proposed_name = proposed_name.upper()  # Ensure consistency in case for matching
    for banned_start in banned_name_starts:
        if proposed_name.startswith(banned_start.upper()):  # Match against uppercase prefix
            # print(f"Detected banned prefix '{banned_start}' in '{proposed_name}'")  # Diagnostic print
            return f"Proposed name '{proposed_name}' is disallowed because it starts with '{banned_start}'."
    # print("No banned prefix found")  # Diagnostic print if no match is found
    return None  # No banned prefix found


# called by check_proposed_name 
# Function to check if a proposed name is disallowed based on various lists
def is_disallowed_name(proposed_name):
    # Normalize to uppercase for case-insensitive matching
    proposed_name = proposed_name.upper()

    # Initialize an empty result message
    result = None

    # Check if the name is in any of the exact disallowed lists
    if proposed_name in business_names:
        result = f"{proposed_name} is disallowed because it is a business name."
    elif proposed_name in city_names:
        result = f"{proposed_name} is disallowed because it is a city name."
    elif proposed_name in county_names:
        result = f"{proposed_name} is disallowed because it is a county name."
    elif proposed_name in arterial_names:
        result = f"{proposed_name} is disallowed because it is a major arterial road."

    # Check if any cardinal direction appears as a substring
    for cardinal in cardinal_names:
        if cardinal.upper() in proposed_name:
            result = f"{proposed_name} is disallowed because it contains the cardinal direction '{cardinal}'."
            break  # Stop checking if one match is found

    # Check if any USPS name appears as a substring
    for usps in usps_names:
        if usps.upper() in proposed_name:
            result = f"{proposed_name} is disallowed because it contains the reserved USPS street type '{usps}'."
            break  # Stop checking if one match is found

    # Print and return result if a disallowance is found
    if result:
        print(result)  # Display in Notebook output
        return result

    # Return None if no disallowed condition is met
    return None



# called by check_proposed_name - checks conflicts with existing names
# result provides the input parameters for format_conflict_results
def detect_conflicts(proposed_name, relevant_name_start, api_url):
    # Sanitize inputs
    proposed_name = str(proposed_name).strip()
    relevant_name_start = str(relevant_name_start).strip()

    # Construct query parameters
    query_params = {
        "where": f"LSt_Name='{proposed_name}' OR LSt_Name LIKE '{relevant_name_start}%'",
        "outFields": "MIN_FromAddr_L,MAX_ToAddr_L,LSt_PreDir,LSt_Name,LSt_Typ,MSAGComm_L",
        "f": "json",
    }

    # Debugging: Print URL and params
    print(f"URL: {api_url}")
    print(f"Query Params Before Encoding: {query_params}")

    # Ensure proper encoding
    try:
        response = requests.get(api_url, params=query_params)
        response.raise_for_status()  # Raise an error for HTTP issues
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error during API request: {e}")

    # Parse and process the response
    features = response.json().get("features", [])
    conflicts = []
    disallowed_prefixes = set()
    disallowed_ranges = []  # Change to a list of tuples
    disallowed_types = set()
    disallowed_cities = set()

    for feature in features:
        row = feature["attributes"]
        # Extract start and end values for the range
        try:
            min_addr = int(row["MIN_FromAddr_L"])
            max_addr = int(row["MAX_ToAddr_L"])
        except (ValueError, TypeError):
            raise ValueError(f"Invalid range data in row: {row}")

        existing_prefix = row.get("LSt_PreDir", "")
        existing_name = row["LSt_Name"]
        existing_type = row.get("LSt_Typ", "")
        existing_city = row.get("MSAGComm_L", "")

        if existing_name == proposed_name:
            conflicts.append([f"{min_addr} - {max_addr}", existing_prefix, existing_name, existing_type, existing_city])
            disallowed_types.add(existing_type)
            disallowed_cities.add(existing_city)
            disallowed_ranges.append((min_addr, max_addr))  # Append tuple directly
            disallowed_prefixes.add(existing_prefix)
        elif relevant_name_start and existing_name.startswith(relevant_name_start):
            conflicts.append([f"{min_addr} - {max_addr}", existing_prefix, existing_name, existing_type, existing_city])
            disallowed_prefixes.add(existing_prefix)
            disallowed_types.add(existing_type)
            disallowed_ranges.append((min_addr, max_addr))  # Append tuple directly
            disallowed_cities.add(existing_city)

    return conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities


# called by check_proposed_name, final step
# calls consolidate_ranges
def format_conflict_results(proposed_name, conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types,
                            disallowed_cities):
    """
    Generates formatted conflict results as a Markdown-compatible string.

    Args:
        proposed_name (str): The proposed street name.
        conflicts (list of lists): List of conflicts (e.g., address ranges, prefixes, etc.).
        disallowed_prefixes (set): Disallowed prefixes.
        disallowed_ranges (list of tuples): Disallowed address ranges.
        disallowed_types (set): Disallowed street types.
        disallowed_cities (set): Disallowed mailing cities.

    Returns:
        str: Formatted Markdown-compatible feedback string.
    """
    # Start with naming conditions
    result = f"## Naming Conditions\n\n"
    result += f"Street name **'{proposed_name}'** is allowed as long as it is not assigned with the following elements:\n\n"

    # Add disallowed prefixes
    if disallowed_prefixes:
        result += f"- **Disallowed Prefixes:** {', '.join(sorted(disallowed_prefixes))}  \n"

    # Add disallowed ranges
    if disallowed_ranges:
        consolidated_ranges = consolidate_ranges(disallowed_ranges)
        result += f"- **Disallowed Ranges:** {', '.join(f'{start} - {end}' for start, end in consolidated_ranges)}  \n"

    # Add disallowed types
    if disallowed_types:
        result += f"- **Disallowed Types:** {', '.join(sorted(disallowed_types))}  \n"

    # Add disallowed cities
    if disallowed_cities:
        result += f"- **Disallowed Mailing Cities:** {', '.join(sorted(disallowed_cities))}  \n"

    # Add conflict table for existing assignments
    result += f"\n## Existing Assignment\n\n"
    result += "| Address Range       | Prefix  | Name        | Type   | Mailing City     |\n"
    result += "|---------------------|---------|-------------|--------|------------------|\n"
    for conflict in sorted(conflicts, key=lambda x: (x[4], x[3], int(x[0].split(" - ")[0]))):
        result += f"| {conflict[0]:<20} | {conflict[1]:<7} | {conflict[2]:<11} | {conflict[3]:<6} | {conflict[4]:<16} |\n"
    return result


# called by check_proposed_name
def display_feedback(feedback, status="info", platform="streamlit"):
    """
    Displays feedback based on the platform.
    Args:
        feedback (str): The feedback message to display.
        status (str): The feedback type ("info", "success", "error").
        platform (str): The platform to display on ("streamlit" or "jupyter").
    """
    if platform == "streamlit":

        if status == "success":
            st.success(feedback)
        elif status == "error":
            st.error(feedback)
        else:
            st.markdown(feedback)
    elif platform == "jupyter":
        if status == "success":
            print(f"✅ SUCCESS: {feedback}")
        elif status == "error":
            print(f"❌ ERROR: {feedback}")
        else:
            print(feedback)

# display_feedback("This is an informational message.", status="info", platform="streamlit")
# display_feedback("This is a success message.", status="success", platform="streamlit")
# display_feedback("This is an error message.", status="error", platform="streamlit")



# called by user input
# calls multiple functions to evaluate name, format the results, and display results according to the platform 
def check_proposed_name(proposed_name, platform="streamlit"):
    # called by display_feedback
    # calls 6 functions
    issues = []
    disapproved = False

    # Step 1: Check if the proposed name is disallowed
    disallowed_reason = is_disallowed_name(proposed_name)
    if disallowed_reason:
        issues.append(disallowed_reason)
        disapproved = True

    # Step 2: Check if the name starts with a banned prefix
    banned_start_reason = check_banned_name_start(proposed_name, banned_name_starts)
    if banned_start_reason:
        issues.append(banned_start_reason)
        disapproved = True

    # Step 3: Check spelling and pronunciation
    status, feedback = evaluate_word(proposed_name, repeated_letter_exceptions, problematic_combination_exceptions,
                                     disallowed_ends_with, ends_with_exceptions, homophones)
    if status == "Disapproved":
        issues.append(feedback)
        disapproved = True

    # Step 4: Detect conflicts if no disapproval
    if not disapproved:
        relevant_name_start = matches_namestart(proposed_name, name_starts)
        conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities = detect_conflicts(
            proposed_name, relevant_name_start, api_url
        )
        if conflicts:
            conflict_summary = format_conflict_results(proposed_name, conflicts, disallowed_prefixes,
                                                       disallowed_ranges, disallowed_types, disallowed_cities)
            issues.append(conflict_summary)

    # Step 5: Display results
    if issues:
        full_feedback = "\n\n".join(issues)
        display_feedback(full_feedback, status="error", platform=platform)
        return full_feedback
    else:
        success_message = f"Proposed name '{proposed_name}' meets all criteria."
        display_feedback(success_message, status="success", platform=platform)
        return success_message







# User Input - calls check_proposed_name
# Streamlit UI Integration
st.title("Proposed Name Checker")

proposed_name = st.text_input("Enter the proposed street name:")
if st.button("Check Name"):
    if proposed_name.strip():
        check_proposed_name(proposed_name.upper().strip())
    else:
        st.warning("Please enter a valid street name.")
