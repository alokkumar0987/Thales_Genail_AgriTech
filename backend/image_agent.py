# image_agent.py

import os
import json
import logging
import base64
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv
from langchain.tools import tool


# --- Configuration and Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Data Structure for Results ---
@dataclass
class DiseaseAnalysisResult:
    """Stores comprehensive disease analysis results."""
    disease_detected: bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms: List[str]
    possible_causes: List[str]
    treatment: List[str]
    analysis_timestamp: str = datetime.now().astimezone().isoformat()


# --- The Core Vision Analysis Class ---


class LeafDiseaseDetector:
    """
    Advanced Leaf Disease Detection System using AI Vision Analysis.

    This class provides comprehensive leaf disease detection capabilities using
    the Groq API with Llama Vision models. It can analyze leaf images to identify
    diseases, assess severity, and provide treatment recommendations. The system
    also validates that uploaded images contain actual plant leaves and rejects
    images of humans, animals, or other non-plant objects.

    The system supports base64 encoded images and returns structured JSON results
    containing disease information, confidence scores, symptoms, causes, and
    treatment suggestions.

    Features:
        - Image validation (ensures uploaded images contain plant leaves)
        - Multi-disease detection (fungal, bacterial, viral, pest, nutrient deficiency)
        - Severity assessment (mild, moderate, severe)
        - Confidence scoring (0-100%)
        - Symptom identification
        - Treatment recommendations
        - Robust error handling and response parsing
        - Invalid image type detection and rejection

    Attributes:
        MODEL_NAME (str): The AI model used for analysis
        DEFAULT_TEMPERATURE (float): Default temperature for response generation
        DEFAULT_MAX_TOKENS (int): Default maximum tokens for responses
        api_key (str): Groq API key for authentication
        client (Groq): Groq API client instance

    Example:
        >>> detector = LeafDiseaseDetector()
        >>> result = detector.analyze_leaf_image_base64(base64_image_data)
        >>> if result['disease_type'] == 'invalid_image':
        ...     print("Please upload a plant leaf image")
        >>> elif result['disease_detected']:
        ...     print(f"Disease detected: {result['disease_name']}")
        >>> else:
        ...     print("Healthy leaf detected")
    """

    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1024

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Leaf Disease Detector with API credentials.

        Sets up the Groq API client and validates the API key from either
        the parameter or environment variables. Initializes logging for
        tracking analysis operations.

        Args:
            api_key (Optional[str]): Groq API key. If None, will attempt to
                                   load from GROQ_API_KEY environment variable.

        Raises:
            ValueError: If no valid API key is found in parameters or environment.

        Note:
            Ensure your .env file contains GROQ_API_KEY or pass it directly.
        """
        load_dotenv()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=self.api_key)
        logger.info("Leaf Disease Detector initialized")



    def create_analysis_prompt(self) -> str:
        """
        Create the standardized analysis prompt for the AI model.

        Generates a comprehensive prompt that instructs the AI model to analyze
        leaf images for diseases and return structured JSON results. The prompt
        specifies the required output format and analysis criteria.

        Returns:
            str: Formatted prompt string with instructions for disease analysis
                 and JSON schema specification.

        Note:
            The prompt ensures consistent output formatting across all analyses
            and includes all necessary fields for comprehensive disease assessment.
        """
        return """IMPORTANT: First determine if this image contains a plant leaf or vegetation. If the image shows humans, animals, objects, buildings, or anything other than plant leaves/vegetation, return the "invalid_image" response format below.

        If this is a valid leaf/plant image, analyze it for diseases and return the results in JSON format.
        
        Please identify:
        1. Whether this is actually a leaf/plant image
        2. Disease name (if any)
        3. Disease type/category or invalid_image
        4. Severity level (mild, moderate, severe)
        5. Confidence score (0-100%)
        6. Symptoms observed
        7. Possible causes
        8. Treatment recommendations

        For NON-LEAF images (humans, animals, objects, or not detected as leaves, etc.), return this format:
        {
            "disease_detected": false,
            "disease_name": null,
            "disease_type": "invalid_image",
            "severity": "none",
            "confidence": 95,
            "symptoms": ["This image does not contain a plant leaf"],
            "possible_causes": ["Invalid image type uploaded"],
            "treatment": ["Please upload an image of a plant leaf for disease analysis"]
            "farmer_advice": {
            "message": "Please upload a clear leaf image showing the affected area."}
  
        }
        
        For VALID LEAF images, return this format:
        {
            "disease_detected": true/false,
            "disease_name": "name of disease or null",
            "disease_type": "fungal/bacterial/viral/pest/nutrient deficiency/healthy",
            "severity": "mild/moderate/severe/none",
            "confidence": 85,
            "symptoms": ["list", "of", "symptoms"],
            "possible_causes": ["list", "of", "causes"],
            "treatment": ["list", "of", "treatments"],
             "farmer_advice": {
  "what_it_means": "This disease is commonly caused by bacteria/fungus/pests. It spreads quickly in humid and wet conditions, and if not treated in time, it can reduce crop yield and quality.",
  "urgency": "immediate|within_2-3_days|monitor",
  "what_to_do": [
    "Carefully remove and destroy the infected leaves so that the infection does not spread further.",
    "Spray a recommended fungicide or bactericide on the affected plants as soon as possible.",
    "Keep the field clean and ensure there is proper air circulation by not planting crops too closely."
  ],
  "prevention": [
    "Do not leave old or infected crop residue in the field as it may carry disease to the next season.",
    "Water plants at the base instead of wetting the leaves, especially during evening hours.",
    "Use resistant seed varieties whenever available to reduce the risk of disease."
  ],
  "recommended_products": [
    "Copper-based fungicide (like Copper Oxychloride or Copper Hydroxide)",
    "For bacterial infections, use products containing Streptomycin + Tetracycline (if allowed in your region)."
  ],
  "organic_remedies": [
    "Spray a solution of neem oil mixed with water (5 ml per liter) on the affected leaves.",
    "Garlic or ginger extract sprays may also help in reducing the spread naturally."
  ]
}

        }"""


    def analyze_leaf_image_base64(self, base64_image: str) -> Dict:
        """Analyzes a base64 encoded image for leaf diseases."""
        try:
            logger.info("Starting analysis for base64 image data")
            if not base64_image: raise ValueError("base64_image cannot be empty")
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]

            completion = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.create_analysis_prompt()},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }],
                temperature=self.DEFAULT_TEMPERATURE, max_tokens=self.DEFAULT_MAX_TOKENS,
                response_format={"type": "json_object"} # Force JSON output
            )
            logger.info("API request completed successfully")
            result = self._parse_response(completion.choices[0].message.content)
            return asdict(result)
        except Exception as e:
            logger.error(f"Analysis failed for base64 image data: {str(e)}")
            # Return a structured error dictionary
            return {"error": True, "message": str(e)}

    def _parse_response(self, response_content: str) -> DiseaseAnalysisResult:
        """Parses and validates the JSON response from the API."""
        try:
            disease_data = json.loads(response_content)
            logger.info("Response parsed successfully as JSON")
            return DiseaseAnalysisResult(
                disease_detected=bool(disease_data.get('disease_detected', False)),
                disease_name=disease_data.get('disease_name'),
                disease_type=disease_data.get('disease_type', 'unknown'),
                severity=disease_data.get('severity', 'unknown'),
                confidence=float(disease_data.get('confidence', 0)),
                symptoms=disease_data.get('symptoms', []),
                possible_causes=disease_data.get('possible_causes', []),
                treatment=disease_data.get('treatment', [])
            )
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Could not parse response as JSON. Error: {e}. Raw response: {response_content}")
            raise ValueError(f"Unable to parse API response as JSON: {response_content[:200]}...")


# --- Bridge to LangChain ---

# 1. Create a single, reusable instance of our detector
try:
    leaf_detector = LeafDiseaseDetector()
except ValueError as e:
    logger.error(f"Failed to initialize LeafDiseaseDetector: {e}")
    leaf_detector = None

@tool
def analyze_plant_health(image_path: str) -> str:
    """
    Analyzes a plant leaf image to identify diseases, their causes, symptoms, and provides detailed treatment recommendations.
    Use this tool when a user uploads an image and asks about plant health.
    The input must be the file path to the saved image.
    """
    if not leaf_detector:
        return "Error: The Leaf Disease Detector is not available due to a configuration error (likely a missing API key)."

    print(f"✔️  Vision Agent: Analyzing image at '{image_path}'")
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        result_dict = leaf_detector.analyze_leaf_image_base64(base64_string)
        
        if result_dict.get("error"):
            return f"An error occurred during analysis: {result_dict.get('message')}"

        # Check for invalid image type
        if result_dict.get('disease_type') == 'invalid_image':
            return "The uploaded image does not appear to be a plant leaf. Please upload a clear photo of a leaf for analysis."

        # Format the successful result into a clean report for the agent
        report_parts = [f"**Plant Health Analysis Report**"]
        if result_dict.get('disease_detected'):
            report_parts.append(f"- **Diagnosis:** The model identified **{result_dict.get('disease_name')}** ({result_dict.get('disease_type')}).")
        else:
            report_parts.append(f"- **Diagnosis:** The leaf appears to be **Healthy**.")

        report_parts.append(f"- **Confidence:** {result_dict.get('confidence'):.2f}%")
        report_parts.append(f"- **Severity:** {result_dict.get('severity').capitalize()}")
        
        if result_dict.get('symptoms'):
            report_parts.append("\n**Symptoms Observed:**\n- " + "\n- ".join(result_dict['symptoms']))
        
        if result_dict.get('possible_causes'):
            report_parts.append("\n**Possible Causes:**\n- " + "\n- ".join(result_dict['possible_causes']))
            
        if result_dict.get('treatment'):
            report_parts.append("\n**💡 Recommended Actions:**\n- " + "\n- ".join(result_dict['treatment']))

        return "\n".join(report_parts)

    except FileNotFoundError:
        return f"Error: The image file was not found at the path '{image_path}'."
    except Exception as e:
        return f"A critical error occurred while analyzing the image: {e}"