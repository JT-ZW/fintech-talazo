# talazo/ml/soil_analyzer.py
import logging
import numpy as np
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class SoilHealthIndex:
    """
    Advanced algorithm to calculate financial index based on soil health metrics
    for Zimbabwean small-scale farmers with regional and seasonal context
    """
    
    def __init__(self):
        """Initialize the Soil Health Index calculator"""
        # More comprehensive parameter weights based on Zimbabwean agricultural research
        self.weights = {
            'ph_level': 0.20,
            'nitrogen_level': 0.15,
            'phosphorus_level': 0.15,
            'potassium_level': 0.15,
            'organic_matter': 0.15,
            'cation_exchange_capacity': 0.10,
            'moisture_content': 0.10
        }
        
        # Ideal ranges for soil parameters in Zimbabwe (general)
        self.ideal_ranges = {
            'ph_level': (6.0, 7.0),
            'nitrogen_level': (20.0, 40.0),  # mg/kg
            'phosphorus_level': (15.0, 30.0),  # mg/kg
            'potassium_level': (150.0, 250.0),  # mg/kg
            'organic_matter': (3.0, 5.0),  # percentage
            'cation_exchange_capacity': (10.0, 20.0),  # cmol/kg
            'moisture_content': (20.0, 30.0)  # percentage
        }
        
        # Regional adjustments for different areas of Zimbabwe
        self.regional_adjustments = {
            'mashonaland_central': {
                'ph_level': (0.0, 0.0),  # No adjustment
                'nitrogen_level': (5.0, 5.0),  # Higher nitrogen threshold
                'phosphorus_level': (0.0, 0.0),
                'potassium_level': (0.0, 0.0),
                'organic_matter': (0.5, 0.5),  # Higher organic matter expectations
                'cation_exchange_capacity': (0.0, 0.0),
                'moisture_content': (0.0, 0.0)
            },
            'manicaland': {
                'ph_level': (-0.5, -0.5),  # Slightly more acidic soil is acceptable
                'nitrogen_level': (0.0, 0.0),
                'phosphorus_level': (0.0, 5.0),  # Higher upper threshold for phosphorus
                'potassium_level': (0.0, 0.0),
                'organic_matter': (0.0, 0.0),
                'cation_exchange_capacity': (0.0, 0.0),
                'moisture_content': (5.0, 0.0)  # Higher moisture content lower bound
            },
            'matabeleland': {
                'ph_level': (0.0, 0.5),  # Slightly more alkaline soil is acceptable
                'nitrogen_level': (-5.0, 0.0),  # Lower nitrogen requirements
                'phosphorus_level': (0.0, 0.0),
                'potassium_level': (0.0, 0.0),
                'organic_matter': (-0.5, 0.0),  # Lower organic matter expectations
                'cation_exchange_capacity': (0.0, 0.0),
                'moisture_content': (-5.0, 0.0)  # Lower moisture content lower bound
            }
        }
        
    def calculate_score(self, soil_data, region=None):
        """
        Calculate overall soil health score with regional and seasonal context
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            region (str, optional): Geographic region in Zimbabwe
            
        Returns:
            tuple: (overall_score, parameter_scores)
        """
        # Determine current season
        current_season = self._get_current_season()
        
        # Apply regional and seasonal adjustments to ideal ranges
        adjusted_ranges = self._get_adjusted_ranges(region, current_season)
        
        # Calculate scores for each parameter
        parameter_scores = {}
        total_score = 0
        total_weight = 0
        
        for param, weight in self.weights.items():
            if param in soil_data and soil_data[param] is not None:
                try:
                    # Convert to float and handle potential errors
                    value = float(soil_data[param])
                    
                    # Get the adjusted ideal range
                    min_ideal, max_ideal = adjusted_ranges.get(param, self.ideal_ranges[param])
                    
                    # Calculate parameter score
                    param_score = self._score_parameter(param, value, min_ideal, max_ideal)
                    parameter_scores[param] = param_score
                    
                    # Add weighted score to total
                    total_score += param_score * weight
                    total_weight += weight
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error processing parameter {param}: {e}")
                    continue
        
        # Handle case where no parameters were processed
        if total_weight == 0:
            logger.warning("No valid parameters found in soil data")
            return 0, {}
            
        # Normalize based on actual weights used
        final_score = (total_score / total_weight) * 100
        
        return final_score, parameter_scores
    
    def _score_parameter(self, param, value, min_ideal, max_ideal):
        """
        Calculate score for a single soil parameter with advanced scoring function
        
        Args:
            param (str): Parameter name
            value (float): Parameter value
            min_ideal (float): Minimum ideal value
            max_ideal (float): Maximum ideal value
            
        Returns:
            float: Parameter score (0-1)
        """
        # Perfect score if within ideal range
        if min_ideal <= value <= max_ideal:
            return 1.0
            
        # Calculate score based on distance from ideal range
        if value < min_ideal:
            # For values below ideal range, use a sigmoid function for smooth transition
            # This creates a more gradual penalty for slight deviations
            deviation = (min_ideal - value) / min_ideal
            score = 1.0 / (1.0 + math.exp(5 * deviation - 1.5))
        else:  # value > max_ideal
            # For values above ideal range, use a different function based on parameter
            if param == 'organic_matter':
                # For organic matter, higher values are less problematic
                deviation = (value - max_ideal) / max_ideal
                score = math.exp(-2 * deviation)
            else:
                # For other parameters, use sigmoid for smooth transition
                deviation = (value - max_ideal) / max_ideal
                score = 1.0 / (1.0 + math.exp(5 * deviation - 1.5))
        
        # Ensure score is between 0 and 1
        return max(0, min(1, score))
    
    def _get_current_season(self):
        """
        Determine current agricultural season in Zimbabwe
        
        Returns:
            str: Current season ('rainy', 'dry', or 'transition')
        """
        month = datetime.now().month
        
        if month in [11, 12, 1, 2, 3]:
            return 'rainy'
        elif month in [5, 6, 7, 8]:
            return 'dry'
        else:  # 4, 9, 10
            return 'transition'
    
    def _get_adjusted_ranges(self, region, season):
        """
        Get ideal ranges adjusted for region and season
        
        Args:
            region (str): Geographic region
            season (str): Current season
            
        Returns:
            dict: Adjusted ideal ranges
        """
        # Start with base ranges
        adjusted = {param: range_vals for param, range_vals in self.ideal_ranges.items()}
        
        # Apply regional adjustments if region is specified
        if region:
            # Normalize region name and find the closest match
            region_key = self._normalize_region(region)
            if region_key in self.regional_adjustments:
                regional_adj = self.regional_adjustments[region_key]
                
                for param, (min_adj, max_adj) in regional_adj.items():
                    if param in adjusted:
                        min_val, max_val = adjusted[param]
                        adjusted[param] = (min_val + min_adj, max_val + max_adj)
        
        # Apply seasonal adjustments
        seasonal_adj = self.seasonal_adjustments.get(season, {})
        for param, (min_adj, max_adj) in seasonal_adj.items():
            if param in adjusted:
                min_val, max_val = adjusted[param]
                adjusted[param] = (min_val + min_adj, max_val + max_adj)
        
        return adjusted
    
    def _normalize_region(self, region):
        """
        Normalize region name to match known regions
        
        Args:
            region (str): Region name input
            
        Returns:
            str: Normalized region key
        """
        if not region:
            return None
            
        region = region.lower().strip()
        
        # Simple mapping of common inputs to region keys
        if 'mashonaland' in region:
            return 'mashonaland_central'
        elif 'manicaland' in region:
            return 'manicaland'
        elif 'matabeleland' in region:
            return 'matabeleland'
        
        return None
    
    def determine_risk_level(self, score):
        """
        Determine financial risk level based on soil health score
        
        Args:
            score (float): Soil health score (0-100)
            
        Returns:
            str: Risk level category
        """
        if score >= 80:
            return "Low Risk"
        elif score >= 60:
            return "Medium-Low Risk"
        elif score >= 40:
            return "Medium Risk"
        elif score >= 20:
            return "Medium-High Risk"
        else:
            return "High Risk"
    
    def calculate_premium(self, score, base_premium=1000):
        """
        Calculate insurance premium based on soil health score
        
        Args:
            score (float): Soil health score (0-100)
            base_premium (float, optional): Base premium amount. Defaults to 1000.
            
        Returns:
            float: Calculated premium amount
        """
        # Lower score = higher risk = higher premium
        # Using an exponential model to better reflect risk assessment
        risk_factor = (100 - score) / 100
        
        # Apply a non-linear relationship for more realistic premiums
        premium_multiplier = 1 + (risk_factor ** 1.8)
        
        premium = base_premium * premium_multiplier
        
        # Apply min/max bounds for reasonable premiums
        min_premium = base_premium * 0.7  # Minimum discount: 30%
        max_premium = base_premium * 3.0  # Maximum increase: 300%
        
        return max(min_premium, min(max_premium, premium))
    
    def get_recommendations(self, soil_data, region=None, crop=None):
        """
        Generate soil health recommendations based on soil data
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            region (str, optional): Geographic region in Zimbabwe
            crop (str, optional): Current or planned crop
            
        Returns:
            list: List of recommendation dictionaries
        """
        recommendations = []
        
        # Calculate current score to determine priorities
        score, parameter_scores = self.calculate_score(soil_data, region)
        
        # Find parameters with lowest scores to prioritize
        sorted_params = sorted(
            [(param, score) for param, score in parameter_scores.items()],
            key=lambda x: x[1]
        )
        
        # Generate recommendations for the lowest scoring parameters
        for param, param_score in sorted_params:
            if param_score < 0.7:  # Only recommend for parameters below 70% optimal
                rec = self._generate_recommendation_for_parameter(param, float(soil_data[param]), region, crop)
                if rec:
                    recommendations.append(rec)
        
        # If no specific parameter recommendations, add a general recommendation
        if not recommendations:
            recommendations.append({
                'parameter': 'General soil health',
                'issue': 'Maintain current soil health',
                'action': 'Continue current soil management practices',
                'benefit': 'Sustain soil fertility and productivity',
                'cost_estimate': 'Low',
                'timeframe': 'Ongoing'
            })
        
        # Add crop-specific recommendation if crop is specified
        if crop and len(recommendations) < 5:
            crop_rec = self._generate_crop_recommendation(soil_data, crop, region)
            if crop_rec:
                recommendations.append(crop_rec)
        
        return recommendations
    
    def _generate_recommendation_for_parameter(self, param, value, region=None, crop=None):
        """
        Generate a recommendation for a specific soil parameter
        
        Args:
            param (str): Parameter name
            value (float): Parameter value
            region (str, optional): Geographic region in Zimbabwe
            crop (str, optional): Current or planned crop
            
        Returns:
            dict: Recommendation dictionary or None
        """
        # Get adjusted ideal range for this parameter
        season = self._get_current_season()
        adjusted_ranges = self._get_adjusted_ranges(region, season)
        min_ideal, max_ideal = adjusted_ranges.get(param, self.ideal_ranges[param])
        
        # Default recommendation (will be overridden if specific conditions are met)
        recommendation = None
        
        # Generate recommendation based on parameter
        if param == 'ph_level':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'pH level',
                    'issue': 'Soil is too acidic',
                    'action': f'Apply agricultural lime at {2 + max(0, (min_ideal - value) * 2):.1f}-{4 + max(0, (min_ideal - value) * 3):.1f} tons per hectare',
                    'benefit': 'Improves nutrient availability and microbial activity',
                    'cost_estimate': 'Medium',
                    'timeframe': '3-6 months'
                }
                if region and 'matabeleland' in self._normalize_region(region):
                    recommendation['local_context'] = 'Use dolomitic lime in Matabeleland to address magnesium deficiency'
                else:
                    recommendation['local_context'] = 'Agricultural lime is available from most agricultural supply stores'
            elif value > max_ideal:
                recommendation = {
                    'parameter': 'pH level',
                    'issue': 'Soil is too alkaline',
                    'action': 'Apply organic matter or elemental sulfur to decrease pH',
                    'benefit': 'Prevents micronutrient deficiencies and improves nutrient availability',
                    'cost_estimate': 'Medium',
                    'timeframe': '3-6 months',
                    'local_context': 'Incorporate locally available organic matter like compost or manure'
                }
        
        elif param == 'nitrogen_level':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Nitrogen level',
                    'issue': 'Nitrogen deficiency',
                    'action': f'Apply nitrogen fertilizer (ammonium nitrate or urea) at {100 + max(0, (min_ideal - value) * 5):.0f}-{150 + max(0, (min_ideal - value) * 10):.0f} kg/ha',
                    'benefit': 'Promotes vegetative growth and increases yield potential',
                    'cost_estimate': 'Medium-High',
                    'timeframe': '2-4 weeks',
                    'local_context': 'Split application recommended during the growing season in Zimbabwe'
                }
            elif value > max_ideal:
                recommendation = {
                    'parameter': 'Nitrogen level',
                    'issue': 'Excess nitrogen',
                    'action': 'Reduce nitrogen fertilizer application and consider planting legumes as cover crops',
                    'benefit': 'Prevents excessive vegetative growth and reduces leaching',
                    'cost_estimate': 'Low',
                    'timeframe': 'Next planting season',
                    'local_context': 'Cowpeas and groundnuts are suitable legumes for rotation in Zimbabwe'
                }
        
        elif param == 'phosphorus_level':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Phosphorus level',
                    'issue': 'Phosphorus deficiency',
                    'action': f'Apply phosphate fertilizer (SSP or TSP) at {60 + max(0, (min_ideal - value) * 3):.0f}-{100 + max(0, (min_ideal - value) * 5):.0f} kg/ha',
                    'benefit': 'Improves root development, flowering, and seed formation',
                    'cost_estimate': 'Medium',
                    'timeframe': 'Apply before planting for best results',
                    'local_context': 'Band application near the seed row is most efficient in Zimbabwean soils'
                }
        
        elif param == 'potassium_level':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Potassium level',
                    'issue': 'Potassium deficiency',
                    'action': f'Apply potassium fertilizer (muriate of potash) at {50 + max(0, (min_ideal - value) * 0.2):.0f}-{100 + max(0, (min_ideal - value) * 0.3):.0f} kg/ha',
                    'benefit': 'Enhances drought tolerance, disease resistance, and overall plant vigor',
                    'cost_estimate': 'Medium',
                    'timeframe': 'Apply before or during planting',
                    'local_context': 'Important for drought-prone areas of Zimbabwe'
                }
        
        elif param == 'organic_matter':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Organic matter',
                    'issue': 'Low organic matter content',
                    'action': 'Apply compost or manure at 5-10 tons per hectare and incorporate crop residues',
                    'benefit': 'Improves soil structure, water retention, and nutrient availability',
                    'cost_estimate': 'Low to Medium',
                    'timeframe': '6-12 months for full benefits',
                    'local_context': 'Conservation agriculture practices are promoted in Zimbabwe to build organic matter'
                }
        
        elif param == 'moisture_content':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Soil moisture',
                    'issue': 'Insufficient soil moisture',
                    'action': 'Apply mulch and implement water conservation practices like tied ridges or basins',
                    'benefit': 'Reduces water stress, improves water infiltration, and reduces evaporation',
                    'cost_estimate': 'Low to Medium',
                    'timeframe': 'Immediate benefits',
                    'local_context': 'Critical for rainfed agriculture in Zimbabwe\'s drought-prone regions'
                }
            elif value > max_ideal and season != 'rainy':
                recommendation = {
                    'parameter': 'Soil moisture',
                    'issue': 'Excess soil moisture',
                    'action': 'Improve drainage through channels or raised beds',
                    'benefit': 'Prevents waterlogging, root diseases, and nutrient leaching',
                    'cost_estimate': 'Medium',
                    'timeframe': 'Before next rainy season',
                    'local_context': 'Important in low-lying areas during the rainy season'
                }
        
        elif param == 'cation_exchange_capacity':
            if value < min_ideal:
                recommendation = {
                    'parameter': 'Cation Exchange Capacity',
                    'issue': 'Low nutrient retention capacity',
                    'action': 'Increase organic matter content and apply clay minerals if available',
                    'benefit': 'Improves nutrient retention and reduces fertilizer leaching',
                    'cost_estimate': 'Medium',
                    'timeframe': '1-2 years for significant improvement',
                    'local_context': 'Particularly important for sandy soils in Zimbabwe'
                }
        
        return recommendation
    
    def _generate_crop_recommendation(self, soil_data, crop, region=None):
        """
        Generate crop-specific recommendation based on soil data
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            crop (str): Current or planned crop
            region (str, optional): Geographic region in Zimbabwe
            
        Returns:
            dict: Crop-specific recommendation or None
        """
        crop = crop.lower() if crop else ''
        
        if crop == 'maize':
            return {
                'parameter': 'Crop management - Maize',
                'issue': 'Optimizing maize production',
                'action': 'Ensure proper spacing (75cm between rows, 25cm between plants) and timely weeding',
                'benefit': 'Maximizes yield potential and resource efficiency',
                'cost_estimate': 'Low',
                'timeframe': 'Throughout growing season',
                'local_context': 'Maize is a staple crop in Zimbabwe requiring good management for optimal yields'
            }
        elif crop == 'groundnuts' or crop == 'peanuts':
            return {
                'parameter': 'Crop management - Groundnuts',
                'issue': 'Optimizing groundnut production',
                'action': 'Ensure adequate calcium by applying gypsum (200-400 kg/ha) at flowering',
                'benefit': 'Improves pod filling and reduces empty pods',
                'cost_estimate': 'Medium',
                'timeframe': 'Apply at flowering stage',
                'local_context': 'Groundnuts are an important cash and food security crop in Zimbabwe'
            }
        elif crop == 'cotton':
            return {
                'parameter': 'Crop management - Cotton',
                'issue': 'Optimizing cotton production',
                'action': 'Implement integrated pest management and proper spacing (90cm x 30cm)',
                'benefit': 'Reduces pest damage and optimizes yield',
                'cost_estimate': 'Medium',
                'timeframe': 'Throughout growing season',
                'local_context': 'Cotton is a key cash crop in many parts of Zimbabwe'
            }
        elif crop == 'sorghum':
            return {
                'parameter': 'Crop management - Sorghum',
                'issue': 'Optimizing sorghum production',
                'action': 'Apply bird control measures and ensure proper spacing',
                'benefit': 'Protects yield from bird damage',
                'cost_estimate': 'Low to Medium',
                'timeframe': 'From heading to harvest',
                'local_context': 'Sorghum is well-adapted to drier regions of Zimbabwe'
            }
        
        return None
    
    def recommend_suitable_crops(self, soil_data, region=None):
        """
        Recommend suitable crops based on soil parameters and region
        
        Args:
            soil_data (dict): Dictionary of soil parameters
            region (str, optional): Geographic region in Zimbabwe
            
        Returns:
            list: List of recommended crops in order of suitability
        """
        try:
            # Extract key soil parameters
            ph = float(soil_data.get('ph_level', 0))
            nitrogen = float(soil_data.get('nitrogen_level', 0))
            phosphorus = float(soil_data.get('phosphorus_level', 0))
            potassium = float(soil_data.get('potassium_level', 0))
            moisture = float(soil_data.get('moisture_content', 0))
            
            # Get current season
            current_season = self._get_current_season()
            season_type = 'summer' if current_season == 'rainy' else 'winter'
            
            # Score each crop based on soil suitability
            crop_scores = {}
            for crop_name, crop_data in self.crops.items():
                # Skip crops that don't match the current season
                if crop_data['growing_season'] != season_type and season_type == 'winter':
                    continue
                
                # Calculate pH match score
                min_ph, max_ph = crop_data['ideal_ph']
                if min_ph <= ph <= max_ph:
                    ph_score = 1.0
                else:
                    distance = min(abs(ph - min_ph), abs(ph - max_ph))
                    ph_score = max(0, 1 - distance / 2)
                
                # Calculate nutrient match scores
                n_requirement = crop_data['nitrogen_requirement']
                if n_requirement == 'low':
                    n_score = 1.0 if nitrogen < 30 else max(0, 1 - (nitrogen - 30) / 30)
                elif n_requirement == 'medium':
                    n_score = 1.0 if 20 <= nitrogen <= 40 else max(0, 1 - min(abs(nitrogen - 20), abs(nitrogen - 40)) / 20)
                else:  # high
                    n_score = 1.0 if nitrogen > 30 else max(0, 1 - (30 - nitrogen) / 30)
                
                # Calculate drought tolerance vs moisture content match
                drought_tolerance = crop_data['drought_tolerance']
                if drought_tolerance == 'high':
                    moisture_score = 1.0 if moisture < 25 else max(0.7, 1 - (moisture - 25) / 25)
                elif drought_tolerance == 'medium':
                    moisture_score = 1.0 if 15 <= moisture <= 30 else max(0.6, 1 - min(abs(moisture - 15), abs(moisture - 30)) / 15)
                else:  # low drought tolerance
                    moisture_score = 1.0 if moisture > 20 else max(0.5, moisture / 20)
                
                # Calculate overall suitability score with weighted components
                overall_score = (
                    ph_score * 0.3 +           # pH is very important
                    n_score * 0.2 +            # Nitrogen requirement
                    moisture_score * 0.3 +     # Moisture/drought tolerance match
                    0.2                        # Base score component for other factors
                )
                
                # Regional adjustment
                if region:
                    region_key = self._normalize_region(region)
                    if region_key == 'matabeleland' and drought_tolerance == 'high':
                        # Bonus for drought-tolerant crops in dry regions
                        overall_score += 0.1
                    elif region_key == 'mashonaland_central' and n_requirement == 'high':
                        # Bonus for nitrogen-demanding crops in fertile regions
                        overall_score += 0.05
                
                # Cap at 1.0 maximum
                crop_scores[crop_name] = min(1.0, overall_score)
            
            # Sort crops by score and return top matches
            sorted_crops = sorted(crop_scores.items(), key=lambda x: x[1], reverse=True)
            return [crop for crop, score in sorted_crops if score > 0.65]
            
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Error in crop recommendation: {str(e)}")
            return []
        
        # Seasonal adjustments (applied to ideal ranges based on current season)
        self.seasonal_adjustments = {
            'rainy': {  # November to March
                'moisture_content': (5.0, 10.0)  # Higher moisture expectations
            },
            'dry': {  # May to August
                'moisture_content': (-5.0, -5.0)  # Lower moisture expectations
            },
            'transition': {  # April, September, October
                'moisture_content': (0.0, -5.0)  # Lower upper bound for moisture
            }
        }
        
        # Define typical crops for Zimbabwean small-scale farmers with soil requirements
        self.crops = {
            'maize': {
                'ideal_ph': (5.8, 6.8),
                'nitrogen_requirement': 'high',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'sorghum': {
                'ideal_ph': (5.5, 7.5),
                'nitrogen_requirement': 'medium',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'high',
                'growing_season': 'summer'
            },
            'groundnuts': {
                'ideal_ph': (5.5, 7.0),
                'nitrogen_requirement': 'low',
                'phosphorus_requirement': 'high',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'soybeans': {
                'ideal_ph': (6.0, 7.0),
                'nitrogen_requirement': 'low',  # Nitrogen-fixing
                'phosphorus_requirement': 'high',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'medium',
                'growing_season': 'summer'
            },
            'cotton': {
                'ideal_ph': (5.8, 7.0),
                'nitrogen_requirement': 'high',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'high',
                'drought_tolerance': 'high',
                'growing_season': 'summer'
            },
            'wheat': {
                'ideal_ph': (6.0, 7.5),
                'nitrogen_requirement': 'high',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'medium',
                'drought_tolerance': 'low',
                'growing_season': 'winter'
            },
            'sweet_potato': {
                'ideal_ph': (5.5, 6.5),
                'nitrogen_requirement': 'medium',
                'phosphorus_requirement': 'medium',
                'potassium_requirement': 'high',
                'drought_tolerance': 'high',
                'growing_season': 'summer'
            }
        }