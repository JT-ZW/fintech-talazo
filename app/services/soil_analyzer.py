# app/services/soil_analyzer.py
"""
Soil analysis service for Talazo AgriFinance Platform.
"""

from typing import Dict, List
import logging


class SoilAnalyzer:
    """Service for analyzing soil samples and generating recommendations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_financial_index(self, soil_data: Dict) -> float:
        """
        Calculate financial index based on soil parameters.
        
        Args:
            soil_data (dict): Dictionary containing soil parameters
            
        Returns:
            float: Financial index score (0-100)
        """
        try:
            # Extract soil parameters
            ph_level = soil_data.get('ph_level', 6.5)
            nitrogen_level = soil_data.get('nitrogen_level', 50)
            phosphorus_level = soil_data.get('phosphorus_level', 25)
            potassium_level = soil_data.get('potassium_level', 200)
            organic_matter = soil_data.get('organic_matter', 3.0)
            moisture_content = soil_data.get('moisture_content', 25)
            
            # Normalize parameters to 0-100 scale
            ph_score = self._normalize_ph(ph_level)
            nitrogen_score = self._normalize_nitrogen(nitrogen_level)
            phosphorus_score = self._normalize_phosphorus(phosphorus_level)
            potassium_score = self._normalize_potassium(potassium_level)
            organic_score = self._normalize_organic_matter(organic_matter)
            moisture_score = self._normalize_moisture(moisture_content)
            
            # Weighted average (financial focus)
            weights = {
                'ph': 0.15,
                'nitrogen': 0.25,
                'phosphorus': 0.20,
                'potassium': 0.15,
                'organic': 0.15,
                'moisture': 0.10
            }
            
            financial_index = (
                ph_score * weights['ph'] +
                nitrogen_score * weights['nitrogen'] +
                phosphorus_score * weights['phosphorus'] +
                potassium_score * weights['potassium'] +
                organic_score * weights['organic'] +
                moisture_score * weights['moisture']
            )
            
            return round(financial_index, 2)
            
        except Exception as e:
            self.logger.error(f"Financial index calculation failed: {e}")
            return 50.0  # Default middle score
    
    def determine_risk_level(self, financial_index: float) -> str:
        """
        Determine risk level based on financial index.
        
        Args:
            financial_index (float): Financial index score
            
        Returns:
            str: Risk level ('low', 'medium', 'high')
        """
        if financial_index >= 75:
            return 'low'
        elif financial_index >= 50:
            return 'medium'
        else:
            return 'high'
    
    def _normalize_ph(self, ph_level: float) -> float:
        """Normalize pH level to 0-100 score."""
        # Optimal pH range for most crops: 6.0-7.0
        if 6.0 <= ph_level <= 7.0:
            return 100
        elif 5.5 <= ph_level < 6.0 or 7.0 < ph_level <= 7.5:
            return 80
        elif 5.0 <= ph_level < 5.5 or 7.5 < ph_level <= 8.0:
            return 60
        elif 4.5 <= ph_level < 5.0 or 8.0 < ph_level <= 8.5:
            return 40
        else:
            return 20
    
    def _normalize_nitrogen(self, nitrogen_level: float) -> float:
        """Normalize nitrogen level to 0-100 score."""
        # Optimal nitrogen: 40-80 mg/kg
        if 40 <= nitrogen_level <= 80:
            return 100
        elif 30 <= nitrogen_level < 40 or 80 < nitrogen_level <= 100:
            return 80
        elif 20 <= nitrogen_level < 30 or 100 < nitrogen_level <= 120:
            return 60
        elif 10 <= nitrogen_level < 20 or 120 < nitrogen_level <= 150:
            return 40
        else:
            return 20
    
    def _normalize_phosphorus(self, phosphorus_level: float) -> float:
        """Normalize phosphorus level to 0-100 score."""
        # Optimal phosphorus: 20-40 mg/kg
        if 20 <= phosphorus_level <= 40:
            return 100
        elif 15 <= phosphorus_level < 20 or 40 < phosphorus_level <= 50:
            return 80
        elif 10 <= phosphorus_level < 15 or 50 < phosphorus_level <= 60:
            return 60
        elif 5 <= phosphorus_level < 10 or 60 < phosphorus_level <= 80:
            return 40
        else:
            return 20
    
    def _normalize_potassium(self, potassium_level: float) -> float:
        """Normalize potassium level to 0-100 score."""
        # Optimal potassium: 150-300 mg/kg
        if 150 <= potassium_level <= 300:
            return 100
        elif 120 <= potassium_level < 150 or 300 < potassium_level <= 350:
            return 80
        elif 100 <= potassium_level < 120 or 350 < potassium_level <= 400:
            return 60
        elif 80 <= potassium_level < 100 or 400 < potassium_level <= 450:
            return 40
        else:
            return 20
    
    def _normalize_organic_matter(self, organic_matter: float) -> float:
        """Normalize organic matter to 0-100 score."""
        # Optimal organic matter: 2.5-5.0%
        if 2.5 <= organic_matter <= 5.0:
            return 100
        elif 2.0 <= organic_matter < 2.5 or 5.0 < organic_matter <= 6.0:
            return 80
        elif 1.5 <= organic_matter < 2.0 or 6.0 < organic_matter <= 7.0:
            return 60
        elif 1.0 <= organic_matter < 1.5 or 7.0 < organic_matter <= 8.0:
            return 40
        else:
            return 20
    
    def _normalize_moisture(self, moisture_content: float) -> float:
        """Normalize moisture content to 0-100 score."""
        # Optimal moisture: 20-35%
        if 20 <= moisture_content <= 35:
            return 100
        elif 15 <= moisture_content < 20 or 35 < moisture_content <= 40:
            return 80
        elif 10 <= moisture_content < 15 or 40 < moisture_content <= 45:
            return 60
        elif 5 <= moisture_content < 10 or 45 < moisture_content <= 50:
            return 40
        else:
            return 20
    
    def analyze_sample(self, soil_sample) -> Dict:
        """
        Analyze a soil sample and generate recommendations.
        
        Args:
            soil_sample: SoilSample instance
            
        Returns:
            Dict: Analysis results and recommendations
        """
        # TODO: Implement comprehensive soil analysis
        return {
            'health_score': soil_sample.calculate_soil_health_score(),
            'recommendations': self._generate_soil_recommendations(soil_sample),
            'analysis_status': 'completed'
        }
    
    def _generate_soil_recommendations(self, soil_sample) -> List[str]:
        """Generate soil improvement recommendations."""
        recommendations = []
        
        # pH recommendations
        if soil_sample.ph_level < 6.0:
            recommendations.append("Apply lime to increase soil pH")
        elif soil_sample.ph_level > 7.5:
            recommendations.append("Apply sulfur to decrease soil pH")
        
        # Nutrient recommendations
        if soil_sample.nitrogen_level < 25:
            recommendations.append("Apply nitrogen fertilizer")
        
        if soil_sample.phosphorus_level < 15:
            recommendations.append("Apply phosphorus fertilizer")
        
        if soil_sample.potassium_level < 150:
            recommendations.append("Apply potassium fertilizer")
        
        return recommendations
