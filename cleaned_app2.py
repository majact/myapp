
import streamlit as st
import datetime

# Define utility functions from the original notebook

# Function to detect if a name is disallowed
def is_disallowed_name(proposed_name, disallowed_lists):
    for category, names in disallowed_lists.items():
        if proposed_name in names:
            return f"{proposed_name} is disallowed because it matches a {category}."
    return None

# Function to evaluate if a name starts with banned prefixes
def check_banned_name_start(proposed_name, banned_prefixes):
    for prefix in banned_prefixes:
        if proposed_name.startswith(prefix):
            return f"{proposed_name} is disallowed because it starts with the banned prefix '{prefix}'."
    return None

# Function to evaluate word spelling and structure
def evaluate_word(proposed_name, problematic_combinations, ends_with_exceptions):
    for combo in problematic_combinations:
        if combo in proposed_name:
            return "Disapproved", f"Contains problematic combination '{combo}'"
    if proposed_name.endswith(tuple(ends_with_exceptions)):
        return "Approved", "Meets criteria"
    return "Approved", "No issues detected"

# Detect conflicts in GIS data (mock implementation; real implementation would query GIS data)
def detect_conflicts(proposed_name, existing_data):
    conflicts = [row for row in existing_data if proposed_name in row]
    if conflicts:
        return conflicts, {"conflicting_prefixes"}, {"conflicting_ranges"}
    return [], {}, {}

# Streamlit main app logic
st.title("Proposed Street Name Validation")

# Inputs for configuration
disallowed_lists = {
    "business names": ["ACME", "GLOBAL"],
    "city names": ["SPRINGFIELD", "GOTHAM"]
}
banned_prefixes = ["OLD", "NEW"]
problematic_combinations = ["GH", "PH"]
ends_with_exceptions = ["VILLE", "TON"]
existing_data = [{"street_name": "MAIN", "prefix": "N"}]

proposed_name = st.text_input("Enter the proposed street name:", "")

if st.button("Submit"):
    if proposed_name.strip():
        proposed_name = proposed_name.upper().strip()
        
        # Check if disallowed
        disallowed_reason = is_disallowed_name(proposed_name, disallowed_lists)
        if disallowed_reason:
            st.error(disallowed_reason)
        else:
            # Check for banned prefix
            banned_reason = check_banned_name_start(proposed_name, banned_prefixes)
            if banned_reason:
                st.error(banned_reason)
            else:
                # Evaluate spelling and pronunciation
                status, feedback = evaluate_word(proposed_name, problematic_combinations, ends_with_exceptions)
                if status == "Disapproved":
                    st.error(feedback)
                else:
                    # Detect conflicts
                    conflicts, prefixes, ranges = detect_conflicts(proposed_name, existing_data)
                    if conflicts:
                        st.error("Conflicts detected:")
                        st.json(conflicts)
                    else:
                        st.success(f"Proposed name '{proposed_name}' meets all criteria.")
    else:
        st.error("Please enter a valid street name.")
