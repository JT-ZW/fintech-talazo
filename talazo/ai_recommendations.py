# talazo/ml/ai_recommendations.py
import requests
import os
import json
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIRecommendationSystem:
    """
    AI-powered recommendation system for agricultural advice
    Uses the Groq API to generate contextual recommendations based on soil data
    """
    
    def __init__(self, cache_expiry=3600):
        """
        Initialize the AI Recommendation System
        
        Args:
            cache_expiry (int, optional): Cache expiry time in seconds. Defaults to 3600 (1 hour).
        """
        self.api_key = os.environ.get('GROQ_API_KEY')
        self.api_url = 'https://api.groq.com/openai/v1/chat/completions'
        self.model = 'llama3-8b-8192'  # or 'mixtral-8x7b-32768' depending on needs
        self.cache_expiry = cache_expiry
        
        # Initialize request session for connection pooling
        self.session = requests.Session()
        
        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured. AI recommendations will use fallback system.")
    
    def generate_recommendations(self, soil_data, farmer_info=None, region=None, crop=None):
        """
        Generate AI-driven recommendations based on soil data
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            farmer_info (dict, optional): Farmer details for contextual recommendations
            region (str, optional): Geographic region in Zimbabwe
            crop (str, optional): Current or planned crop
            
        Returns:
            dict: Dictionary containing recommendations and metadata
        """
        # Check if API key is available
        if not self.api_key:
            logger.warning("Using fallback recommendations due to missing API key")
            return {
                'status': 'fallback',
                'recommendations': self._fallback_recommendations(soil_data, crop),
                'metadata': {
                    'source': 'fallback',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
        
        # Try to get cached recommendations if parameters are similar
        cache_key = self._generate_cache_key(soil_data, region, crop)
        cached_result = self._get_cached_recommendation(cache_key)
        if cached_result:
            logger.info("Returning cached recommendation")
            return cached_result
        
        # Create prompt with soil data
        prompt = self._create_prompt(soil_data, farmer_info, region, crop)
        
        try:
            # Call Groq LLM API
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': self.model,
                'messages': [
                    {'role': 'system', 'content': 'You are an expert agricultural advisor specializing in Zimbabwean farming conditions. Provide practical, actionable recommendations based on soil health data that are appropriate for small-scale farmers in Zimbabwe.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.2,  # Lower temperature for more consistent outputs
                'max_tokens': 1024
            }
            
            logger.debug(f"Sending request to Groq API for soil data: {json.dumps(soil_data)}")
            response = self.session.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                timeout=30  # Add timeout to prevent hanging
            )
            
            if response.status_code == 200:
                response_data = response.json()
                recommendations_text = response_data['choices'][0]['message']['content']
                
                # Parse the recommendations
                parsed_recommendations = self._parse_recommendations(recommendations_text)
                
                result = {
                    'status': 'success',
                    'recommendations': parsed_recommendations,
                    'raw_response': recommendations_text,
                    'metadata': {
                        'source': 'groq',
                        'model': self.model,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                
                # Cache the result
                self._cache_recommendation(cache_key, result)
                return result
            else:
                logger.error(f"Groq API request failed with status {response.status_code}: {response.text}")
                # API call failed, use fallback
                return {
                    'status': 'error',
                    'error': f'API call failed with status {response.status_code}',
                    'recommendations': self._fallback_recommendations(soil_data, crop),
                    'metadata': {
                        'source': 'fallback',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }
                
        except Exception as e:
            logger.exception(f"Error in AI recommendation generation: {str(e)}")
            # Error occurred, use fallback
            return {
                'status': 'error',
                'error': str(e),
                'recommendations': self._fallback_recommendations(soil_data, crop),
                'metadata': {
                    'source': 'fallback',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def _create_prompt(self, soil_data, farmer_info=None, region=None, crop=None):
        """
        Create a detailed prompt for the LLM based on soil data
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            farmer_info (dict, optional): Farmer details for contextual recommendations
            region (str, optional): Geographic region in Zimbabwe
            crop (str, optional): Current or planned crop
            
        Returns:
            str: Formatted prompt for the LLM
        """
        # Format soil data
        soil_info = '\n'.join([f'- {k.replace("_", " ").title()}: {v}' for k, v in soil_data.items()])
        
        # Get current season
        current_month = datetime.now().month
        season = self._determine_season(current_month)
        
        # Build the prompt
        prompt = f"""
        Analyze the following soil health data from a farm in {region or 'Zimbabwe'} and provide detailed recommendations:

        SOIL DATA:
        {soil_info}

        CONTEXT:
        - Current season: {season}
        - Region: {region or 'Zimbabwe'}
        """
        
        if crop:
            prompt += f"\n- Current/planned crop: {crop}"
        
        if farmer_info:
            farmer_context = '\n'.join([f'- {k.replace("_", " ").title()}: {v}' for k, v in farmer_info.items()])
            prompt += f"\n\nFARMER INFORMATION:\n{farmer_context}"
        
        prompt += """
        
        Please provide the following in a structured format:
        
        1. SOIL HEALTH ANALYSIS: Explain what these soil readings indicate about soil health.
        
        2. PRIORITY RECOMMENDATIONS: List 3-5 specific actions the farmer should take to improve soil health, in priority order. For each recommendation, include:
           - ACTION: The specific action to take
           - REASON: Why it's needed based on the soil data
           - COST: Estimated cost (low/medium/high)
           - TIMEFRAME: Expected timeframe for results
           - LOCAL CONSIDERATIONS: Any Zimbabwe-specific factors
        
        3. CROP RECOMMENDATIONS: Suggest 2-3 crops that would be suitable for these soil conditions, explaining why each is appropriate.
        
        4. SUSTAINABLE PRACTICES: Recommend 1-2 sustainable farming practices that would improve long-term soil health.
        
        Format each recommendation as a clear section with the headings above. Be practical, specific, and consider the constraints of small-scale farmers in Zimbabwe.
        """
        
        return prompt
    
    def _parse_recommendations(self, recommendations_text):
        """
        Parse the LLM response into structured recommendations
        
        Args:
            recommendations_text (str): Raw text response from the LLM
            
        Returns:
            list: List of structured recommendation dictionaries
        """
        # Split the text into sections
        sections = []
        current_section = ""
        current_heading = None
        
        for line in recommendations_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a new section heading
            if line.upper() == "SOIL HEALTH ANALYSIS:" or "SOIL HEALTH ANALYSIS" in line.upper():
                if current_heading:
                    sections.append({"type": current_heading, "content": current_section.strip()})
                current_heading = "soil_analysis"
                current_section = ""
            elif line.upper() == "PRIORITY RECOMMENDATIONS:" or "PRIORITY RECOMMENDATIONS" in line.upper():
                if current_heading:
                    sections.append({"type": current_heading, "content": current_section.strip()})
                current_heading = "recommendations"
                current_section = ""
            elif line.upper() == "CROP RECOMMENDATIONS:" or "CROP RECOMMENDATIONS" in line.upper():
                if current_heading:
                    sections.append({"type": current_heading, "content": current_section.strip()})
                current_heading = "crops"
                current_section = ""
            elif line.upper() == "SUSTAINABLE PRACTICES:" or "SUSTAINABLE PRACTICES" in line.upper():
                if current_heading:
                    sections.append({"type": current_heading, "content": current_section.strip()})
                current_heading = "sustainable_practices"
                current_section = ""
            else:
                current_section += line + "\n"
        
        # Add the last section
        if current_heading and current_section:
            sections.append({"type": current_heading, "content": current_section.strip()})
        
        # Process the recommendations section into structured format
        structured_recommendations = []
        
        for section in sections:
            if section["type"] == "recommendations":
                recommendations_text = section["content"]
                recommendation_blocks = recommendations_text.split("\n\n")
                
                for block in recommendation_blocks:
                    if not block.strip():
                        continue
                        
                    rec = {"type": "recommendation"}
                    
                    # Extract title
                    if ":" in block.split("\n")[0]:
                        title_parts = block.split("\n")[0].split(":", 1)
                        rec["title"] = title_parts[1].strip() if len(title_parts) > 1 else title_parts[0].strip()
                    else:
                        rec["title"] = block.split("\n")[0].strip()
                    
                    # Extract other fields
                    for line in block.split("\n"):
                        line = line.strip()
                        if not line or ":" not in line:
                            continue
                            
                        key, value = line.split(":", 1)
                        key = key.strip().upper()
                        
                        if "ACTION" in key:
                            rec["action"] = value.strip()
                        elif "REASON" in key or "WHY" in key:
                            rec["reason"] = value.strip()
                        elif "COST" in key:
                            rec["cost_estimate"] = value.strip()
                        elif "TIMEFRAME" in key or "TIME" in key:
                            rec["timeframe"] = value.strip()
                        elif "LOCAL" in key or "CONSIDERATION" in key:
                            rec["local_context"] = value.strip()
                    
                    if len(rec) > 1:  # Only add if we have more than just the title
                        structured_recommendations.append(rec)
        
        # If we couldn't parse properly, create a simple recommendation
        if not structured_recommendations and recommendations_text:
            structured_recommendations.append({
                "title": "Soil Improvement",
                "action": "Refer to the detailed text analysis",
                "content": recommendations_text
            })
        
        return structured_recommendations
    
    def _determine_season(self, month):
        """
        Determine current agricultural season in Zimbabwe based on month
        
        Args:
            month (int): Month as integer (1-12)
            
        Returns:
            str: Current agricultural season
        """
        if month in [11, 12, 1, 2, 3]:
            return "Rainy Season (Summer)"
        elif month in [5, 6, 7, 8]:
            return "Dry Season (Winter)"
        elif month in [4, 9, 10]:
            return "Transition Season"
    
    def _fallback_recommendations(self, soil_data, crop=None):
        """
        Provide fallback recommendations if API call fails
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            crop (str, optional): Current or planned crop
            
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        # Check pH level
        try:
            ph = float(soil_data.get('ph_level', 0))
            if ph < 6.0:
                recommendations.append({
                    'title': 'Correct Soil pH',
                    'action': 'Apply agricultural lime at 2-4 tons per hectare',
                    'reason': 'Soil is too acidic, which limits nutrient availability',
                    'cost_estimate': 'Medium',
                    'timeframe': '3-6 months',
                    'local_context': 'Locally available agricultural lime can be sourced from most agricultural supply stores in Zimbabwe'
                })
            elif ph > 7.0:
                recommendations.append({
                    'title': 'Reduce Soil pH',
                    'action': 'Apply organic matter such as compost or manure',
                    'reason': 'Soil is too alkaline, which can limit certain nutrient uptake',
                    'cost_estimate': 'Low to Medium',
                    'timeframe': '3-6 months',
                    'local_context': 'Manure from local livestock can be an affordable option'
                })
        except (ValueError, TypeError):
            pass
        
        # Check nitrogen level
        try:
            nitrogen = float(soil_data.get('nitrogen_level', 0))
            if nitrogen < 20:
                recommendations.append({
                    'title': 'Increase Nitrogen Levels',
                    'action': 'Apply nitrogen fertilizer (Ammonium Nitrate) at 100-150 kg/ha',
                    'reason': 'Nitrogen deficiency will limit plant growth and yield',
                    'cost_estimate': 'Medium',
                    'timeframe': '2-4 weeks',
                    'local_context': 'Consider split application during the growing season for better efficiency in Zimbabwe\'s climate'
                })
        except (ValueError, TypeError):
            pass
        
        # Check organic matter
        try:
            organic_matter = float(soil_data.get('organic_matter', 0))
            if organic_matter < 3.0:
                recommendations.append({
                    'title': 'Increase Organic Matter',
                    'action': 'Apply compost or incorporate crop residues into the soil',
                    'reason': 'Low organic matter reduces soil structure, water retention, and nutrient availability',
                    'cost_estimate': 'Low',
                    'timeframe': '6-12 months',
                    'local_context': 'Conservation agriculture techniques are being promoted in Zimbabwe and can help build organic matter over time'
                })
        except (ValueError, TypeError):
            pass
        
        # Check moisture content
        try:
            moisture = float(soil_data.get('moisture_content', 0))
            if moisture < 20:
                recommendations.append({
                    'title': 'Improve Water Management',
                    'action': 'Apply mulch and implement water conservation practices',
                    'reason': 'Low soil moisture will stress plants and reduce yields',
                    'cost_estimate': 'Low to Medium',
                    'timeframe': 'Immediate benefits',
                    'local_context': 'Given Zimbabwe\'s drought-prone regions, water conservation is critical'
                })
        except (ValueError, TypeError):
            pass
        
        # Add crop-specific recommendation if crop is provided
        if crop:
            crop = crop.lower()
            if crop == 'maize':
                recommendations.append({
                    'title': 'Maize-Specific Management',
                    'action': 'Ensure proper spacing at 75cm between rows and 25cm between plants',
                    'reason': 'Proper spacing optimizes resource use and yield potential',
                    'cost_estimate': 'Low',
                    'timeframe': 'Planting time',
                    'local_context': 'Maize is a staple crop in Zimbabwe, and proper spacing is essential for good yields'
                })
            elif crop == 'groundnuts' or crop == 'peanuts':
                recommendations.append({
                    'title': 'Groundnut Management',
                    'action': 'Ensure calcium levels are adequate with gypsum application if needed',
                    'reason': 'Calcium is essential for pod development in groundnuts',
                    'cost_estimate': 'Medium',
                    'timeframe': 'Apply at flowering',
                    'local_context': 'Groundnuts are an important cash and food security crop in Zimbabwe'
                })
        
        return recommendations
    
    def _generate_cache_key(self, soil_data, region=None, crop=None):
        """
        Generate a cache key based on input parameters
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            region (str, optional): Geographic region
            crop (str, optional): Current/planned crop
            
        Returns:
            str: Cache key
        """
        # Round numerical values to reduce cache variations
        rounded_data = {}
        for key, value in soil_data.items():
            try:
                if isinstance(value, (int, float)):
                    rounded_data[key] = round(float(value), 1)
                else:
                    rounded_data[key] = value
            except (ValueError, TypeError):
                rounded_data[key] = value
        
        # Create a string representation for hashing
        key_parts = [
            json.dumps(rounded_data, sort_keys=True),
            region or '',
            crop or ''
        ]
        
        return '_'.join(key_parts)
    
    # Use LRU cache for storing recommendations
    @lru_cache(maxsize=100)
    def _get_cached_recommendation(self, cache_key):
        """Placeholder for retrieving cached recommendations"""
        # In a real implementation, this would check a persistent cache
        return None
    
    def _cache_recommendation(self, cache_key, result):
        """Placeholder for storing recommendations in cache"""
        # In a real implementation, this would store in a persistent cache
        pass