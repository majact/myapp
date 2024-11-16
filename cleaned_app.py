import streamlit as st

# Streamlit App
st.title('Streamlit App Generated from Notebook')
st.write('This app was converted from a Jupyter Notebook.')



# Import core GIS and data manipulation libraries
from arcgis.gis import GIS  # ArcGIS API for Python to work with GIS data and services
from arcgis.features import FeatureLayer  # FeatureLayer class to interact with individual layers
import pandas as pd  # Data manipulation library
import datetime

# Jupyter Notebook display utilities for Markdown and widgets
from IPython.display import display, Markdown
import ipywidgets as widgets

# Initialize GIS object (assuming user is signed into ArcGIS Pro or Online in 'home' mode)
gis = GIS("home")

# Define the URL for the feature layer containing street data
layer_url = "https://services3.arcgis.com/90zScd1lzl2oLYC1/arcgis/rest/services/RCL_AddressAssignment_gdb/FeatureServer/0"
layer = FeatureLayer(layer_url)  # Access the layer through the FeatureLayer class

# Query all data from the feature layer and load it into a Pandas DataFrame
# 'where="1=1"' selects all records, and 'out_fields="*"' retrieves all fields for each feature
features = layer.query(where="1=1", out_fields="*").features
existing_data = pd.DataFrame([f.attributes for f in features])  # Extract attributes to DataFrame

# Confirm setup
print("GIS environment set up and street data loaded.")


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
name_starts = [
    "GREEN", "BLUE", "WHITE", "BROWN", "BLACK", "RED", "YELLOW", "PURPLE", "GREY", "GRAY", "ORANGE",
    "ALBERT", "ALEX", "ALTA", "ARCH", "ASH", "BASE", "BAY", "BEAVER", "BEEF", "BELL", "BERNARD",
    "BIG", "BOONE", "BOUND", "BOX", "BRAD", "BRAN", "BROWN", "BRIGHT", "BROOK", "BRUN", "BUCK",
    "BUTTER", "CANYON", "CHAT", "CHERRY", "CHURCH", "CLARK", "CLAY", "CLEAR", "CLIFF", "CLOUD",
    "CLOVER", "COLD", "COOL", "COPPER", "CORN", "CROSS", "DALE", "DAWN", "DEEP", "DEER", "DOUBLE",
    "DRAKE", "DRIFT", "DUCK", "EAGLE", "ELDER", "ELK", "END", "EVER", "FAIR", "FARM", "FAVOR",
    "FELD", "FERN", "FIDDLE", "FIRE", "FISH", "FLAG", "FLAT", "FLINT", "FREE", "GARDEN", "GERMAN",
    "GLAD", "GLEN", "GOLD", "GOOD", "GRANT", "GRAPE", "GUM", "HAGGER", "HANDY", "HATCH", "HAY",
    "HIGH", "HITCH", "HOLLY", "IRON", "JACK", "JOY", "KENT", "KIND", "KING", "KIRK",
    "KITTY", "LADY", "LAKE", "LARK", "LEATHER", "LEMON", "LEVEL", "LEWIS", "LIME", "LIVER",
    "LOCK", "LONG", "LOYAL", "MARSH", "MARTIN", "MASON", "MASTER", "MATCH", "MAY", "MORGAN",
    "MORNING", "MOUNTAIN", "NETHER", "NEW", "NIGHT", "OAT", "OLD", "OVER", "OX", "PATTER", "PENNY",
    "PEPPER", "PERFECT", "PINE", "PLANT", "PLAY", "QUEEN", "QUICK", "QUIN", "RAMS", "RED", "RENEW",
    "REX", "RICH", "RING", "RIVER", "ROAD", "ROBERT", "ROCK", "ROUND", "SAGE", "SAIL", "SHAKER",
    "SHOW", "SILVER", "SINGLE", "SKY", "SPRING", "STAMP", "STAN", "STAR", "STILL", "STOCK",
    "SUN", "SUNNY", "TOAST", "TOM", "TOWER", "TOWN", "UNDER", "UP", "VALEN", "VANDER", "WALK",
    "WASH", "WATER", "WELL", "WILLIAM", "WILSON", "WINK", "WISE", "WISH", "WOLF", "WONDER", "WOOD",
    "YORK"
]


repeated_letter_exceptions = {"AGREE", "WELL", "BUTTER", "AGREEMENT", "TREE", "WOOD", "BELL", "WHEEL",
                              "PEPPER", "APPLE", "MILL", "CRESS", "STILL", "FALL", "PENNY", "PATTER", "BOOK",
                              "CROSS", "MOOSE", "MELLOW", "MAMMOTH", "POOL", "BERRY", "KITTY", "JOLLY", "HUGG",
                              "HOOVER", "HAGGER", "GULL", "FREE", "DUFF", "BILL", "DEEP", "LESS", "CHOPP", "CLAPP",
                              "CLIFF", "PASS", "COOL", "COPPER", "DELL", "COSTELLO", "BROOK", "DANNER", "NESS",
                              "GOOD", "STALL", "SUCCESS", "VANILLA", "YARNELL", "ZIPPER", "HILL"}
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

import re

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
    problematic_combinations = ['IE', 'EI', 'GH', 'AI', 'CK', 'AE', 'OI', 'OU', 'QU', 'EY', 'OE', 'EO', 'UA', 'KN']
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
    matching_homophones = [f"{key}-{value}" for key, values in homophones.items() for value in values if key in word or value in word]
    if matching_homophones:
        issues.append(f"Contains homophone: {', '.join(matching_homophones)}")

    # Return approval or disapproval based on issues
    feedback = ', '.join(issues)
    return ("Disapproved", feedback[:252] + "...") if issues else ("Approved", "Meets all criteria")


# Helper function to consolidate overlapping or nearby ranges within a specified distance (e.g., 50 units)
def consolidate_ranges(ranges):
    # Return empty list if no ranges are provided
    if not ranges:
        return []
    
    # Sort ranges by their starting values for sequential processing
    sorted_ranges = sorted(ranges, key=lambda r: int(r.split(" - ")[0]))
    consolidated = []  # List to store the consolidated range results
    current_start, current_end = map(int, sorted_ranges[0].split(" - "))  # Initialize with the first range

    # Iterate over the remaining ranges to merge overlapping or nearby ranges
    for r in sorted_ranges[1:]:
        start, end = map(int, r.split(" - "))  # Parse the start and end of each range
        if start <= current_end + 50:
            # Extend the current range if the start of this range is within 50 units of the current end
            current_end = max(current_end, end)
        else:
            # If the ranges are too far apart, finalize the current range and start a new one
            consolidated.append(f"{current_start} - {current_end}")
            current_start, current_end = start, end

    # Append the last consolidated range
    consolidated.append(f"{current_start} - {current_end}")
    return consolidated

print("Helper functions and disallowed name lists defined.")


# Helper function to identify if a given name starts with any prefix in the name_starts list
def matches_namestart(name, name_starts):
    for start in name_starts:
        if name.startswith(start):  # Check if the name starts with the current prefix
            return start  # Return the matching prefix if found
    return None  # Return None if no match is found

print("Name start matching function defined.")


# Function to check if a proposed name starts with any banned prefix from a provided list
def check_banned_name_start(proposed_name, banned_name_starts):
    proposed_name = proposed_name.upper()  # Ensure consistency in case for matching
    for banned_start in banned_name_starts:
        if proposed_name.startswith(banned_start.upper()):  # Match against uppercase prefix
            # print(f"Detected banned prefix '{banned_start}' in '{proposed_name}'")  # Diagnostic print
            return f"Proposed name '{proposed_name}' is disallowed because it starts with '{banned_start}'."
    # print("No banned prefix found")  # Diagnostic print if no match is found
    return None  # No banned prefix found


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
            result = f"{proposed_name} is disallowed because it contains the USPS name '{usps}'."
            break  # Stop checking if one match is found
    
    # Print and return result if a disallowance is found
    if result:
        print(result)  # Display in Notebook output
        return result
    
    # Return None if no disallowed condition is met
    return None


# Function to detect conflicts in existing records based on exact name or name start match
def detect_conflicts(proposed_name, relevant_name_start, existing_data):
    conflicts = []  # List to store records that conflict with the proposed name
    disallowed_prefixes = set()  # Prefixes associated with conflicts
    disallowed_ranges = set()  # Address ranges associated with conflicts
    disallowed_types = set()  # Street types associated with conflicts
    disallowed_cities = set()  # Cities associated with conflicts

    # Iterate over each row in existing data to check for conflicts
    for _, row in existing_data.iterrows():
        existing_range = f"{row['MIN_FromAddr_L']} - {row['MAX_ToAddr_L']}"  # Address range of current record
        existing_prefix = row.get('LSt_PreDir', '')  # Directional prefix (e.g., N, S, E, W)
        existing_name = row['LSt_Name']  # Name of the street in the current record
        existing_type = row.get('LSt_Typ', '')  # Street type (e.g., Avenue, Drive)
        existing_city = row.get('MSAGComm_L', '')  # City or community name

        # Check for an exact name match
        if existing_name == proposed_name:
            conflicts.append([existing_range, existing_prefix, existing_name, existing_type, existing_city])
            disallowed_types.add(existing_type)
            disallowed_cities.add(existing_city)
            disallowed_ranges.add(existing_range)
            disallowed_prefixes.add(existing_prefix)

        # Check for a match based on relevant name start
        elif relevant_name_start and existing_name.startswith(relevant_name_start):
            conflicts.append([existing_range, existing_prefix, existing_name, existing_type, existing_city])
            disallowed_types.add(existing_type)
            disallowed_cities.add(existing_city)

    # Return conflicts and all collected disallowed elements for further processing
    return conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities

print("Conflict detection function defined.")


# Function to format conflict results for a proposed street name
def format_conflict_results(proposed_name, conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities):
    # If there are no conflicts, return a simple acceptance message
    if not conflicts:
        return f"Street name '{proposed_name}' is acceptable with no conflicts."

    # Initialize result message with naming conditions if conflicts exist
    result = f"## Naming Conditions\nStreet name '{proposed_name}' is allowed as long as it is not assigned with the following elements:\n"
    
    # List out disallowed elements by category
    if disallowed_prefixes:
        result += f"- Prefix: {', '.join(disallowed_prefixes)}\n"
    if disallowed_ranges:
        result += f"- Range: {', '.join(disallowed_ranges)}\n"
    if disallowed_types:
        result += f"- Type: {', '.join(disallowed_types)}\n"
    if disallowed_cities:
        result += f"- Mailing City: {', '.join(disallowed_cities)}\n"

    # Add existing assignments in a markdown-style table format for easy readability
    result += f"\n## Existing Assignment\nThe name '{proposed_name}' is already assigned as follows:\n\n"
    result += "| Address Range       | Prefix  | Name        | Type   | Mailing City     |\n"
    result += "|---------------------|---------|-------------|--------|------------------|\n"
    
    # Populate table rows with sorted conflict data for a structured output
    for conflict in sorted(conflicts, key=lambda x: (x[4], x[3], int(x[0].split(" - ")[0]))):
        result += f"| {conflict[0]:<20} | {conflict[1]:<7} | {conflict[2]:<11} | {conflict[3]:<6} | {conflict[4]:<16} |\n"
    
    return result

print("Updated conflict result formatting function defined.")


# def check_proposed_name(proposed_name):
#     result = None
    
#     # Step 1: Check for disallowed names
#     disallowed_reason = is_disallowed_name(proposed_name)
#     if disallowed_reason:
#         return disallowed_reason
    
#     # Step 2: Check for banned name start using the list as a parameter
#     banned_start_reason = check_banned_name_start(proposed_name, banned_name_starts)
#     if banned_start_reason:
#         return banned_start_reason
    
#     # Proceed with further checks if no banned name start is detected
#     relevant_name_start = matches_namestart(proposed_name, name_starts)
#     conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities = detect_conflicts(
#         proposed_name, relevant_name_start, existing_data
#     )
    
#     # Format and display the result
#     result = format_conflict_results(proposed_name, conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities)
#     display(Markdown(result))  # Display markdown-formatted result
#     return result


# # Main function to check a proposed street name for conflicts
# def check_proposed_name(proposed_name):
#     result = None
    
#     # Step 1: Check if the proposed name is disallowed
#     disallowed_reason = is_disallowed_name(proposed_name)
#     if disallowed_reason:
#         return disallowed_reason
    
#     # Step 2: Check if the name starts with a banned prefix
#     banned_start_reason = check_banned_name_start(proposed_name, banned_name_starts)
#     if banned_start_reason:
#         return banned_start_reason
    
#     # Step 3: If no issues are found, check spelling and pronunciation using evaluate_word
#     status, feedback = evaluate_word(proposed_name, repeated_letter_exceptions, problematic_combination_exceptions,
#                                      disallowed_ends_with, ends_with_exceptions, homophones)
#     if status == "Disapproved":
#         # If the name doesn't meet spelling/pronunciation criteria, return the feedback
#         print(feedback)
#         return feedback
    
#     # Step 4: Proceed with further checks if the spelling and pronunciation are approved
#     relevant_name_start = matches_namestart(proposed_name, name_starts)
#     conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities = detect_conflicts(
#         proposed_name, relevant_name_start, existing_data
#     )
    
#     # Format and display the final result
#     result = format_conflict_results(proposed_name, conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities)
#     display(Markdown(result))  # Display markdown-formatted result
#     return result


def check_proposed_name(proposed_name):
    # Initialize a list to accumulate all issues
    issues = []
    disapproved = False  # Flag to indicate if name is disapproved
    
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
    
    # Step 3: Check spelling and pronunciation using evaluate_word
    status, feedback = evaluate_word(proposed_name, repeated_letter_exceptions, problematic_combination_exceptions,
                                     disallowed_ends_with, ends_with_exceptions, homophones)
    if status == "Disapproved":
        issues.append(feedback)
        disapproved = True
    
    # Step 4: Only detect conflicts if name has passed all previous checks
    if not disapproved:
        relevant_name_start = matches_namestart(proposed_name, name_starts)
        conflicts, disallowed_prefixes, disallowed_ranges, disallowed_types, disallowed_cities = detect_conflicts(
            proposed_name, relevant_name_start, existing_data
        )
        
        # Format the conflict results if there are conflicts
        if conflicts:
            conflict_summary = format_conflict_results(proposed_name, conflicts, disallowed_prefixes, 
                                                       disallowed_ranges, disallowed_types, disallowed_cities)
            issues.append(conflict_summary)
    
    # Step 5: Display all issues if any were found
    if issues:
        full_feedback = "\n\n".join(issues)
        print(full_feedback)
        display(Markdown(full_feedback))  # Show in Notebook output
        return full_feedback
    else:
        # If no issues, confirm that the name passed all checks
        success_message = f"Proposed name '{proposed_name}' meets all criteria."
        print(success_message)
        display(Markdown(success_message))
        return success_message






    # Confirm whether the addition was successful
    if add_response['addResults'][0]['success']:


import ipywidgets as widgets
import datetime

# Create a text input widget for entering the proposed street name
street_name_input = widgets.Text(
    value='',  # Default text is empty
    placeholder='Enter proposed street name',  # Placeholder text
    description='Street Name:',  # Label description for the input field
    disabled=False  # Field is enabled for user input
)

# Create a submit button widget
submit_button = widgets.Button(description="Submit", button_style='primary')
output_area = widgets.Output()  # Output area for displaying results

# Event handler for the submit button
def on_submit_clicked(b):
    output_area.clear_output()  # Clear previous output each time the button is clicked
    proposed_name = street_name_input.value.upper().strip()  # Get and format user input
    with output_area:
        # Run the conflict check on the proposed name and display the result
        result = check_proposed_name(proposed_name)
        # Uncomment below line to display result if not already handled in `check_proposed_name`
        # display(Markdown(result))
        

# Connect the submit button to its event handler
submit_button.on_click(on_submit_clicked)

# Display the interface with input, button, and output area vertically aligned
display(widgets.VBox([street_name_input, submit_button, output_area]))
print("User input interface defined.")









