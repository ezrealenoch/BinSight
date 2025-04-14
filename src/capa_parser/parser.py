import json
from collections import defaultdict

def parse_capa_json(file_path):
    """
    Parses a CAPA JSON output file to extract rules and their associated addresses.

    Args:
        file_path (str): The path to the CAPA JSON output file.

    Returns:
        dict: A dictionary where keys are rule names and values are lists of 
              addresses (strings) associated with that rule.
              Returns an empty dictionary if parsing fails or no rules are found.
    
    Raises:
        FileNotFoundError: If the file_path does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        Exception: For other potential errors during processing.
    """
    findings = defaultdict(list)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # CAPA JSON structure can vary slightly, try to handle common patterns
    # Look for 'rules' at the top level
    if "rules" in data:
        for rule_name, rule_data in data["rules"].items():
            if "matches" in rule_data and rule_data["matches"]:
                # Addresses are typically keys in the 'matches' dictionary
                # Convert address keys (which might be integers in JSON) to hex strings
                addresses = [f"0x{addr:X}" if isinstance(addr, int) else str(addr) for addr in rule_data["matches"].keys()]
                if addresses:
                    findings[rule_name].extend(addresses)

    # Alternative structure sometimes seen (e.g., capa explorer format?)
    elif isinstance(data, list): # Check if the root is a list of findings
         for item in data:
             if "rule" in item and "locations" in item and "name" in item["rule"]:
                 rule_name = item["rule"]["name"]
                 # Assuming locations are addresses
                 addresses = [f"0x{loc:X}" if isinstance(loc, int) else str(loc) for loc in item["locations"]]
                 if addresses:
                    findings[rule_name].extend(addresses)

    # TODO: Add more robust parsing for different CAPA versions/formats if needed.
                    
    return dict(findings)

def format_findings_for_display(findings):
    """
    Formats the parsed findings into a simple string for display in the UI.
    """
    if not findings:
        return "No CAPA findings with addresses found in the file."

    output_lines = []
    for rule_name, addresses in findings.items():
        output_lines.append(f"Rule: {rule_name}")
        for addr in addresses:
            output_lines.append(f"  - Address: {addr}")
        output_lines.append("-" * 20) # Separator

    return "\n".join(output_lines)

# Example Usage (for testing)
if __name__ == '__main__':
    # Create a dummy capa_output.json for testing
    dummy_data = {
        "meta": {"analysis": {}, "timestamp": "...", "version": "..."},
        "rules": {
            "Allocate memory": {
                "meta": {"name": "Allocate memory", "namespace": "host-interaction/memory"},
                "matches": {
                    140001000: {}, 
                    140001050: {}
                }
            },
            "Check for debugger": {
                 "meta": {"name": "Check for debugger", "namespace": "anti-analysis/debugger"},
                 "matches": {
                     "0x1400025A0": {} 
                 }
            },
            "Empty Rule": {
                "meta": {"name": "Empty Rule"},
                "matches": {} # Rule with no address matches
            }
        }
    }
    dummy_file = "dummy_capa_output.json"
    with open(dummy_file, 'w') as f:
        json.dump(dummy_data, f, indent=2)

    try:
        parsed_findings = parse_capa_json(dummy_file)
        print("Parsed Findings:")
        print(json.dumps(parsed_findings, indent=2))
        
        formatted_output = format_findings_for_display(parsed_findings)
        print("\nFormatted Output:")
        print(formatted_output)

    except Exception as e:
        print(f"Error parsing dummy file: {e}")
    finally:
        # Clean up the dummy file
        import os
        if os.path.exists(dummy_file):
            os.remove(dummy_file)
