# app/services/risk_assessment.py
"""
Risk Assessment Engine for Talazo AgriFinance Platform.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class RiskAssessmentEngine:
    """Engine for assessing various types of risks in agricultural finance."""
    
    def __init__(self):
        self.risk_factors = {
            'weather': 0.25,
            'soil_health': 0.30,
            'market': 0.20,
            'credit_history': 0.15,
            'farming_experience': 0.10
        }
    
    def assess_overall_risk(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess overall risk for a farmer.
        
        Args:
            farmer_data (dict): Farmer information and metrics
            
        Returns:
            dict: Risk assessment results
        """
        try:
            risk_scores = {}
            
            # Weather risk assessment
            risk_scores['weather'] = self._assess_weather_risk(farmer_data)
            
            # Soil health risk assessment
            risk_scores['soil_health'] = self._assess_soil_risk(farmer_data)
            
            # Market risk assessment
            risk_scores['market'] = self._assess_market_risk(farmer_data)
            
            # Credit history risk assessment
            risk_scores['credit_history'] = self._assess_credit_risk(farmer_data)
            
            # Experience risk assessment
            risk_scores['farming_experience'] = self._assess_experience_risk(farmer_data)
            
            # Calculate weighted overall risk
            overall_risk = sum(
                risk_scores[factor] * weight 
                for factor, weight in self.risk_factors.items()
            )
            
            risk_level = self._categorize_risk(overall_risk)
            
            return {
                'overall_risk_score': round(overall_risk, 2),
                'risk_level': risk_level,
                'individual_risks': risk_scores,
                'risk_factors_weights': self.risk_factors,
                'assessment_date': datetime.utcnow().isoformat(),
                'recommendations': self._generate_recommendations(risk_scores, risk_level)
            }
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return {
                'overall_risk_score': 50.0,
                'risk_level': 'medium',
                'error': str(e)
            }
    
    def _assess_weather_risk(self, farmer_data: Dict[str, Any]) -> float:
        """Assess weather-related risks."""
        location = farmer_data.get('location', {})
        province = location.get('province', '').lower()
        
        # Zimbabwe province weather risk mapping (simplified)
        province_risks = {
            'mashonaland central': 25,
            'mashonaland east': 30,
            'mashonaland west': 35,
            'manicaland': 20,
            'midlands': 45,
            'masvingo': 50,
            'matabeleland north': 60,
            'matabeleland south': 65,
            'bulawayo': 55,
            'harare': 30
        }
        
        base_risk = province_risks.get(province, 40)
        
        # Adjust based on farm size (larger farms may have better resilience)
        farm_size = farmer_data.get('farm_size_hectares', 1)
        if farm_size > 10:
            base_risk -= 5
        elif farm_size > 5:
            base_risk -= 2
        
        return max(0, min(100, base_risk))
    
    def _assess_soil_risk(self, farmer_data: Dict[str, Any]) -> float:
        """Assess soil health related risks."""
        soil_sample = farmer_data.get('latest_soil_sample', {})
        
        if not soil_sample:
            return 60  # High risk if no soil data
        
        soil_score = soil_sample.get('financial_index_score', 50)
        
        # Convert soil health score to risk score (inverse relationship)
        risk_score = 100 - soil_score
        
        return max(0, min(100, risk_score))
    
    def _assess_market_risk(self, farmer_data: Dict[str, Any]) -> float:
        """Assess market-related risks."""
        crop_type = farmer_data.get('crop_type', '').lower()
        
        # Crop market risk mapping (simplified)
        crop_risks = {
            'maize': 35,
            'tobacco': 45,
            'cotton': 50,
            'wheat': 40,
            'barley': 45,
            'soybeans': 30,
            'groundnuts': 35,
            'sunflower': 40
        }
        
        base_risk = crop_risks.get(crop_type, 45)
        
        # Adjust based on farm diversification
        # (This would need more data about crop diversity)
        
        return base_risk
    
    def _assess_credit_risk(self, farmer_data: Dict[str, Any]) -> float:
        """Assess credit history related risks."""
        credit_history = farmer_data.get('credit_history', [])
        
        if not credit_history:
            return 50  # Medium risk for no history
        
        # Calculate based on payment history, defaults, etc.
        total_applications = len(credit_history)
        defaults = sum(1 for record in credit_history if record.get('status') == 'defaulted')
        
        if total_applications == 0:
            return 50
        
        default_rate = defaults / total_applications
        risk_score = default_rate * 80 + 20  # Base risk of 20
        
        return max(0, min(100, risk_score))
    
    def _assess_experience_risk(self, farmer_data: Dict[str, Any]) -> float:
        """Assess farming experience related risks."""
        experience_years = farmer_data.get('farming_experience_years', 0)
        
        if experience_years >= 10:
            return 20  # Low risk
        elif experience_years >= 5:
            return 35  # Medium-low risk
        elif experience_years >= 2:
            return 50  # Medium risk
        else:
            return 70  # High risk
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize overall risk score."""
        if risk_score <= 25:
            return 'low'
        elif risk_score <= 50:
            return 'medium'
        elif risk_score <= 75:
            return 'high'
        else:
            return 'very_high'
    
    def _generate_recommendations(self, risk_scores: Dict[str, float], risk_level: str) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []
        
        if risk_scores.get('soil_health', 0) > 60:
            recommendations.append("Consider soil improvement programs and organic fertilizers")
        
        if risk_scores.get('weather', 0) > 50:
            recommendations.append("Invest in drought-resistant crop varieties and irrigation systems")
        
        if risk_scores.get('market', 0) > 50:
            recommendations.append("Diversify crop portfolio and explore contract farming opportunities")
        
        if risk_scores.get('credit_history', 0) > 60:
            recommendations.append("Focus on building credit history through smaller, manageable loans")
        
        if risk_scores.get('farming_experience', 0) > 50:
            recommendations.append("Participate in agricultural training and extension programs")
        
        if risk_level in ['high', 'very_high']:
            recommendations.append("Consider agricultural insurance products")
            recommendations.append("Start with smaller loan amounts to build track record")
        
        return recommendations
