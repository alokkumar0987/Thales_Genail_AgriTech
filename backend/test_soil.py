from soil_agent import get_soil_recommendations

def main():
    # Test with crop type + soil data
    result = get_soil_recommendations.invoke({
        "location": "Punjab, India",
        "crop_type": "wheat",
        "soil_data": {"pH": 6.8, "N": "low", "P": "medium", "K": "high"}
    })
    
    print("\n=== Soil Recommendations (Punjab, Wheat) ===\n")
    print(result)

    # Test without soil data
    result2 = get_soil_recommendations.invoke({
        "location": "Maharashtra, India",
        "crop_type": "rice"
    })
    
    print("\n=== Soil Recommendations (Maharashtra, Rice) ===\n")
    print(result2)

if __name__ == "__main__":
    main()
