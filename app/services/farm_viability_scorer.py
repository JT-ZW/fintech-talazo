# app/services/farm_viability_scorer.py
"""
Farm Viability Scoring Service for Talazo AgriFinance Platform.

This service calculates comprehensive farm viability scores based on multiple factors
including soil health, climate data, historical performance, and market conditions.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from app.models import SoilSample, Farmer, CreditHistory
from app.core.extensions import db


class FarmViabilityScorer:
    """
    Core scoring engine that calculates farm viability scores.
    
    The scorer evaluates farms across multiple dimensions:
    - Soil health and quality
    - Water access and irrigation
    - Climate resilience
    - Crop suitability
    - Historical performance
    - Market proximity and access
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Weights for different scoring factors
        self.weights = {
            'soil_health': 0.35,        # Most important for agriculture
            'water_access': 0.20,       # Critical in Zimbabwe
            'climate_resilience': 0.15, # Weather risk
            'crop_suitability': 0.10,   # Crop-specific factors
            'historical_performance': 0.10,  # Past track record
            'market_proximity': 0.10    # Access to markets
        }
        
        # Optimal ranges for soil parameters (Zimbabwe-specific)
        self.optimal_ranges = {
            'ph': (6.0, 7.0),
            'nitrogen': (30, 50),       # mg/kg
            'phosphorus': (20, 40),     # mg/kg
            'potassium': (180, 250),    # mg/kg
            'organic_matter': (3.0, 5.0),  # percentage
            'moisture': (20, 30),       # percentage
            'cec': (15, 25)            # cmol/kg
        }
        
        # Zimbabwe-specific crop requirements
        self.crop_requirements = {
            'maize': {
                'min_rainfall': 500,      # mm/year
                'optimal_ph': (5.5, 7.0),
                'nitrogen_need': 'high',
                'season_length': 120,     # days
                'market_demand': 'high'
            },
            'tobacco': {
                'min_rainfall': 600,
                'optimal_ph': (5.0, 6.5),
                'nitrogen_need': 'medium',
                'season_length': 150,
                'market_demand': 'medium'
            },
            'cotton': {
                'min_rainfall': 400,
                'optimal_ph': (5.8, 7.2),
                'nitrogen_need': 'medium',
                'season_length': 180,
                'market_demand': 'medium'
            },
            'soybean': {
                'min_rainfall': 450,
                'optimal_ph': (6.0, 7.0),
                'nitrogen_need': 'low',   # Nitrogen-fixing
                'season_length': 100,
                'market_demand': 'high'
            }
        }
        
        # Risk categories and thresholds
        self.risk_thresholds = {
            'low': 80,      # Score >= 80
            'medium_low': 65,   # Score 65-79
            'medium': 50,       # Score 50-64
            'medium_high': 35,  # Score 35-49
            'high': 0          # Score < 35
        }
    
    def calculate_viability_score(self, farm_data: Dict) -> float:
        """
        Calculate farm viability score based on provided farm data.
        
        Args:
            farm_data (dict): Dictionary containing farm information
            
        Returns:
            float: Viability score (0-100)
        """
        try:
            # Extract farm parameters
            soil_health_score = farm_data.get('soil_health_score', 50)
            farm_size = farm_data.get('farm_size', 2.0)
            farming_experience = farm_data.get('farming_experience', 5)
            crop_diversity = farm_data.get('crop_diversity', 1)
            location_risk = farm_data.get('location_risk', 'medium')
            
            # Calculate individual component scores
            soil_component = min(100, soil_health_score)  # 0-100
            
            # Farm size component (optimal around 2-10 hectares)
            if 2 <= farm_size <= 10:
                size_component = 100
            elif 1 <= farm_size < 2 or 10 < farm_size <= 20:
                size_component = 80
            elif 0.5 <= farm_size < 1 or 20 < farm_size <= 50:
                size_component = 60
            else:
                size_component = 40
            
            # Experience component
            if farming_experience >= 10:
                experience_component = 100
            elif farming_experience >= 5:
                experience_component = 80
            elif farming_experience >= 2:
                experience_component = 60
            else:
                experience_component = 40
            
            # Crop diversity component
            diversity_component = min(100, crop_diversity * 25)
            
            # Location risk component
            location_scores = {
                'low': 100,
                'medium': 70,
                'high': 40,
                'very_high': 20
            }
            location_component = location_scores.get(location_risk, 70)
            
            # Weighted calculation
            weights = {
                'soil': 0.30,
                'size': 0.20,
                'experience': 0.20,
                'diversity': 0.15,
                'location': 0.15
            }
            
            viability_score = (
                soil_component * weights['soil'] +
                size_component * weights['size'] +
                experience_component * weights['experience'] +
                diversity_component * weights['diversity'] +
                location_component * weights['location']
            )
            
            return round(viability_score, 2)
            
        except Exception as e:
            self.logger.error(f"Viability score calculation failed: {e}")
            return 50.0  # Default middle score
    
    def calculate_comprehensive_score(self, farmer_id: int, 
                                    additional_data: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive farm viability score for a farmer.
        
        Args:
            farmer_id: ID of the farmer to score
            additional_data: Optional additional data for scoring
            
        Returns:
            Dictionary containing detailed scoring results
        """
        try:
            # Get farmer and related data
            farmer = Farmer.query.get(farmer_id)
            if not farmer:
                raise ValueError(f"Farmer with ID {farmer_id} not found")
            
            # Get latest soil sample
            soil_sample = farmer.get_latest_soil_sample()
            if not soil_sample:
                raise ValueError(f"No soil data available for farmer {farmer_id}")
            
            # Calculate individual component scores
            soil_score = self._calculate_soil_health_score(soil_sample)
            water_score = self._calculate_water_access_score(farmer, additional_data)
            climate_score = self._calculate_climate_resilience_score(farmer, additional_data)
            crop_score = self._calculate_crop_suitability_score(farmer, soil_sample)
            history_score = self._calculate_historical_performance_score(farmer)
            market_score = self._calculate_market_proximity_score(farmer, additional_data)
            
            # Calculate weighted overall score
            overall_score = (
                soil_score * self.weights['soil_health'] +
                water_score * self.weights['water_access'] +
                climate_score * self.weights['climate_resilience'] +
                crop_score * self.weights['crop_suitability'] +
                history_score * self.weights['historical_performance'] +
                market_score * self.weights['market_proximity']
            )
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                farmer, soil_sample, overall_score, {
                    'soil': soil_score,
                    'water': water_score,
                    'climate': climate_score,
                    'crop': crop_score,
                    'history': history_score,
                    'market': market_score
                }
            )
            
            return {
                'farmer_id': farmer_id,
                'overall_score': round(overall_score, 2),
                'risk_level': risk_level,
                'component_scores': {
                    'soil_health': round(soil_score, 2),
                    'water_access': round(water_score, 2),
                    'climate_resilience': round(climate_score, 2),
                    'crop_suitability': round(crop_score, 2),
                    'historical_performance': round(history_score, 2),
                    'market_proximity': round(market_score, 2)
                },
                'weights_used': self.weights,
                'recommendations': recommendations,
                'assessment_date': datetime.utcnow().isoformat(),
                'data_sources': {
                    'soil_sample_id': soil_sample.id,
                    'soil_sample_date': soil_sample.collection_date.isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating comprehensive score: {str(e)}")
            raise
    
    def _calculate_soil_health_score(self, soil_sample: SoilSample) -> float:
        """Calculate soil health score based on soil parameters."""
        if not soil_sample:
            return 0.0
        
        # Use the soil sample's built-in scoring method
        return soil_sample.calculate_soil_health_score() or 0.0
    
    def _calculate_water_access_score(self, farmer: Farmer, 
                                    additional_data: Optional[Dict] = None) -> float:
        """Calculate water access score."""
        score = 50.0  # Base score
        
        # Check for irrigation infrastructure
        if additional_data and additional_data.get('has_irrigation'):
            score += 30
        
        # Check for water sources
        water_sources = additional_data.get('water_sources', []) if additional_data else []
        if 'borehole' in water_sources:
            score += 20
        elif 'well' in water_sources:
            score += 15
        elif 'river' in water_sources:
            score += 10
        
        # Rainfall reliability (if available)
        if additional_data:
            rainfall_reliability = additional_data.get('rainfall_reliability', 0.5)
            score += rainfall_reliability * 20
        
        return min(100.0, score)
    
    def _calculate_climate_resilience_score(self, farmer: Farmer,
                                          additional_data: Optional[Dict] = None) -> float:
        """Calculate climate resilience score."""
        score = 60.0  # Base score for Zimbabwe climate
        
        # Check for climate adaptation practices
        if additional_data:
            adaptations = additional_data.get('climate_adaptations', [])
            if 'drought_resistant_crops' in adaptations:
                score += 15
            if 'conservation_agriculture' in adaptations:
                score += 10
            if 'weather_monitoring' in adaptations:
                score += 10
            if 'diversified_cropping' in adaptations:
                score += 5
        
        # Geographic risk factors
        if farmer.province:
            # Some provinces are more climate-resilient
            high_risk_provinces = ['Matabeleland North', 'Matabeleland South']
            if farmer.province in high_risk_provinces:
                score -= 15
        
        return min(100.0, max(0.0, score))
    
    def _calculate_crop_suitability_score(self, farmer: Farmer, 
                                        soil_sample: SoilSample) -> float:
        """Calculate crop suitability score."""
        if not farmer.primary_crop or not soil_sample:
            return 50.0  # Default score
        
        crop = farmer.primary_crop.lower()
        if crop not in self.crop_requirements:
            return 50.0  # Unknown crop
        
        crop_req = self.crop_requirements[crop]
        score = 0.0
        
        # pH suitability
        optimal_ph = crop_req['optimal_ph']
        if optimal_ph[0] <= soil_sample.ph_level <= optimal_ph[1]:
            score += 40
        elif abs(soil_sample.ph_level - (optimal_ph[0] + optimal_ph[1])/2) <= 0.5:
            score += 20
        
        # Nitrogen requirements
        nitrogen_need = crop_req['nitrogen_need']
        if nitrogen_need == 'high' and soil_sample.nitrogen_level >= 40:
            score += 30
        elif nitrogen_need == 'medium' and soil_sample.nitrogen_level >= 25:
            score += 30
        elif nitrogen_need == 'low':
            score += 30  # Nitrogen-fixing crops
        else:
            score += 15  # Suboptimal but manageable
        
        # Market demand factor
        market_demand = crop_req.get('market_demand', 'medium')
        if market_demand == 'high':
            score += 30
        elif market_demand == 'medium':
            score += 20
        else:
            score += 10
        
        return min(100.0, score)
    
    def _calculate_historical_performance_score(self, farmer: Farmer) -> float:
        """Calculate historical performance score based on credit history."""
        credit_histories = CreditHistory.query.filter_by(farmer_id=farmer.id).all()
        
        if not credit_histories:
            return 60.0  # Neutral score for new farmers
        
        # Calculate average risk score from credit history
        risk_scores = [ch.calculate_risk_score() for ch in credit_histories]
        avg_risk_score = np.mean(risk_scores)
        
        # Check for recent good performance
        recent_histories = [ch for ch in credit_histories 
                          if ch.loan_date and 
                          (datetime.now().date() - ch.loan_date).days <= 365]
        
        if recent_histories:
            recent_performance = np.mean([ch.calculate_risk_score() for ch in recent_histories])
            # Weight recent performance more heavily
            score = 0.7 * recent_performance + 0.3 * avg_risk_score
        else:
            score = avg_risk_score
        
        return score
    
    def _calculate_market_proximity_score(self, farmer: Farmer,
                                        additional_data: Optional[Dict] = None) -> float:
        """Calculate market proximity and access score."""
        score = 50.0  # Base score
        
        # Urban proximity bonus
        if farmer.district:
            major_cities = ['Harare', 'Bulawayo', 'Chitungwiza', 'Mutare', 'Gweru']
            if any(city.lower() in farmer.district.lower() for city in major_cities):
                score += 25
        
        # Transportation access
        if additional_data:
            transport_access = additional_data.get('transport_access', [])
            if 'good_roads' in transport_access:
                score += 15
            if 'public_transport' in transport_access:
                score += 10
            
            # Market infrastructure
            if additional_data.get('has_storage_facilities'):
                score += 10
            if additional_data.get('has_processing_access'):
                score += 10
        
        return min(100.0, score)
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level based on overall score."""
        if score >= self.risk_thresholds['low']:
            return 'LOW'
        elif score >= self.risk_thresholds['medium_low']:
            return 'MEDIUM_LOW'
        elif score >= self.risk_thresholds['medium']:
            return 'MEDIUM'
        elif score >= self.risk_thresholds['medium_high']:
            return 'MEDIUM_HIGH'
        else:
            return 'HIGH'
    
    def _generate_recommendations(self, farmer: Farmer, soil_sample: SoilSample,
                                overall_score: float, component_scores: Dict) -> List[str]:
        """Generate actionable recommendations based on scores."""
        recommendations = []
        
        # Soil health recommendations
        if component_scores['soil'] < 60:
            if soil_sample.ph_level < 6.0:
                recommendations.append("Apply lime to increase soil pH to optimal range (6.0-7.0)")
            elif soil_sample.ph_level > 7.5:
                recommendations.append("Apply sulfur or organic matter to reduce soil pH")
            
            if soil_sample.organic_matter and soil_sample.organic_matter < 2.0:
                recommendations.append("Increase organic matter through compost or manure application")
            
            if soil_sample.nitrogen_level < 25:
                recommendations.append("Apply nitrogen fertilizer or grow nitrogen-fixing crops")
        
        # Water access recommendations  
        if component_scores['water'] < 50:
            recommendations.append("Consider investing in water storage or irrigation infrastructure")
            recommendations.append("Implement water conservation techniques like mulching")
        
        # Climate resilience recommendations
        if component_scores['climate'] < 50:
            recommendations.append("Adopt drought-resistant crop varieties")
            recommendations.append("Implement conservation agriculture practices")
            recommendations.append("Diversify cropping systems to spread climate risk")
        
        # Market access recommendations
        if component_scores['market'] < 50:
            recommendations.append("Form farmer cooperatives to improve market access")
            recommendations.append("Invest in post-harvest storage facilities")
        
        # Overall performance recommendations
        if overall_score < 50:
            recommendations.append("Focus on improving soil health as the foundation for farm productivity")
            recommendations.append("Seek agricultural extension services for technical support")
        
        return recommendations
    
    def calculate_loan_eligibility(self, farmer_id: int) -> Dict:
        """Calculate loan eligibility based on viability score."""
        try:
            viability_result = self.calculate_comprehensive_score(farmer_id)
            score = viability_result['overall_score']
            risk_level = viability_result['risk_level']
            
            # Determine eligibility and loan terms
            if score >= 80:
                eligible = True
                max_amount = score * 150  # Higher multiplier for excellent scores
                interest_rate = 8.0  # Low rate
                term_months = 24
            elif score >= 65:
                eligible = True
                max_amount = score * 100
                interest_rate = 12.0
                term_months = 18
            elif score >= 50:
                eligible = True
                max_amount = score * 75
                interest_rate = 15.0
                term_months = 12
            else:
                eligible = False
                max_amount = 0
                interest_rate = None
                term_months = None
            
            return {
                'eligible': eligible,
                'viability_score': score,
                'risk_level': risk_level,
                'max_loan_amount': max_amount,
                'recommended_interest_rate': interest_rate,
                'max_term_months': term_months,
                'conditions': viability_result['recommendations'][:3]  # Top 3 recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating loan eligibility: {str(e)}")
            return {
                'eligible': False,
                'error': str(e)
            }
