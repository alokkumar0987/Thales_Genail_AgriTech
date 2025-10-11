import json
from image_agent import analyze_pest_disease  # your @tool function

# Replace with the path to your test image
image_path = r"D:\crop_advisory\Potato\Train\Potato___healthy\Potato_healthy-76-_0_7539.jpg"

# Get raw result from your existing function
raw_result = analyze_pest_disease(image_path)

# Optional: parse it into JSON format
# Assuming your function returns top class and treatment info
# You can modify your original function to return a dict instead of text for cleaner JSON

# Example JSON format
json_output = {
    "image_path": image_path,
    "result": raw_result
}

# Print nicely formatted JSON
print(json.dumps(json_output, indent=4))

