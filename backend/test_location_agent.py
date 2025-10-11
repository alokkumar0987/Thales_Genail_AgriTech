# test_location.py
from location_agent import detect_user_location, set_manual_location, get_location_info, detect_user_location_json
import json

print("=== Testing detect_user_location (string) ===")
location_str = detect_user_location.invoke("")
print(location_str)
print("\n")

print("=== Testing set_manual_location ===")
manual_location = set_manual_location.invoke("Delhi, India")
print(manual_location)
print("\n")

print("=== Testing get_location_info (with query) ===")
query_location = get_location_info.invoke("near Mumbai")
print(query_location)
print("\n")

print("=== Testing detect_user_location_json ===")
location_json = detect_user_location_json.invoke("")
print(json.dumps(location_json, indent=4))






