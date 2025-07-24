// soil_health_algorithm.js - Complete soil health scoring algorithm for Talazo AgriFinance

class SoilHealthAlgorithm {
    constructor() {
        this.optimalRanges = {
            ph_level: { min: 6.0, max: 7.0 },
            nitrogen_level: { min: 20, max: 40 },
            phosphorus_level: { min: 20, max: 30 },
            potassium_level: { min: 150, max: 250 },
            organic_matter: { min: 3, max: 5 },
            cation_exchange_capacity: { min: 10, max: 20 },
            moisture_content: { min: 20, max: 30 }
        };
        
        // Weight factors for different soil parameters
        this.weights = {
            ph_level: 0.20,
            nitrogen_level: 0.18,
            phosphorus_level: 0.15,
            potassium_level: 0.15,
            organic_matter: 0.17,
            cation_exchange_capacity: 0.08,
            moisture_content: 0.07
        };
        
        // Crop-specific requirements for Zimbabwe
        this.cropRequirements = {
            maize: {
                ph_range: [5.5, 7.0],
                nitrogen_need: 'high',
                water_requirement: 'medium-high'
            },
            groundnuts: {
                ph_range: [5.0, 7.0],
                nitrogen_need: 'low', // fixes nitrogen
                water_requirement: 'medium'
            },
            sorghum: {
                ph_range: [5.5, 8.0],
                nitrogen_need: 'medium',
                water_requirement: 'low'
            },
            cotton: {
                ph_range: [5.8, 8.0],
                nitrogen_need: 'high',
                water_requirement: 'medium'
            },
            soybeans: {
                ph_range: [6.0, 7.0],
                nitrogen_need: 'low', // fixes nitrogen
                water_requirement: 'medium'
            },
            sweet_potatoes: {
                ph_range: [5.5, 6.5],
                nitrogen_need: 'medium',
                water_requirement: 'medium'
            }
        };
    }
    
    /**
     * Calculate overall soil health score
     * @param {Object} soilData - Soil parameter measurements
     * @returns {number} Score between 0-100
     */
    calculateScore(soilData) {
        if (!soilData || Object.keys(soilData).length === 0) {
            return 50; // Default score when no data available
        }
        
        let totalScore = 0;
        let totalWeight = 0;
        
        // Calculate weighted score for each parameter
        for (const [param, value] of Object.entries(soilData)) {
            if (param === 'timestamp' || param === 'sample_id') continue;
            
            const range = this.optimalRanges[param];
            const weight = this.weights[param];
            
            if (range && weight && typeof value === 'number') {
                const paramScore = this.calculateParameterScore(param, value);
                totalScore += paramScore * weight;
                totalWeight += weight;
            }
        }
        
        // Normalize to 0-100 scale
        const finalScore = totalWeight > 0 ? (totalScore / totalWeight) * 100 : 50;
        return Math.max(0, Math.min(100, finalScore));
    }
    
    /**
     * Calculate score for individual soil parameter
     * @param {string} parameter - Parameter name
     * @param {number} value - Measured value
     * @returns {number} Score between 0-1
     */
    calculateParameterScore(parameter, value) {
        const range = this.optimalRanges[parameter];
        if (!range) return 0.5; // Default score for unknown parameters
        
        const { min, max } = range;
        
        if (value >= min && value <= max) {
            // Value is within optimal range
            return 1.0;
        } else if (value < min) {
            // Value is below optimal range
            const deviation = (min - value) / min;
            return Math.max(0, 1 - deviation);
        } else {
            // Value is above optimal range
            const deviation = (value - max) / max;
            // Some parameters are more tolerant of high values
            const tolerance = this.getHighValueTolerance(parameter);
            return Math.max(0, 1 - (deviation / tolerance));
        }
    }
    
    /**
     * Get tolerance factor for high values
     * @param {string} parameter - Parameter name
     * @returns {number} Tolerance factor
     */
    getHighValueTolerance(parameter) {
        const tolerances = {
            ph_level: 1.5,           // pH deviations are more serious
            nitrogen_level: 2.0,     // High nitrogen is less problematic
            phosphorus_level: 2.0,   // High phosphorus is manageable
            potassium_level: 1.5,    // High potassium can cause imbalances
            organic_matter: 3.0,     // High organic matter is generally good
            cation_exchange_capacity: 2.0,
            moisture_content: 1.3    // High moisture can cause problems
        };
        
        return tolerances[parameter] || 1.5;
    }
    
    /**
     * Determine risk level based on soil health score
     * @param {number} score - Health score (0-100)
     * @returns {string} Risk level description
     */
    determineRiskLevel(score) {
        if (score >= 80) return "Low Risk";
        if (score >= 65) return "Medium-Low Risk";
        if (score >= 50) return "Medium Risk";
        if (score >= 35) return "Medium-High Risk";
        return "High Risk";
    }
    
    /**
     * Calculate insurance premium based on soil health
     * @param {number} score - Health score (0-100)
     * @returns {number} Premium amount
     */
    calculatePremium(score) {
        // Base premium of $100, adjusted by risk
        const basePremium = 100;
        const riskMultiplier = Math.max(0.5, (100 - score) / 50);
        return Math.round(basePremium * riskMultiplier);
    }
    
    /**
     * Recommend suitable crops based on soil conditions
     * @param {Object} soilData - Soil measurements
     * @returns {Array} Array of recommended crop names
     */
    recommendSuitableCrops(soilData) {
        const cropScores = [];
        
        for (const [cropName, requirements] of Object.entries(this.cropRequirements)) {
            const suitabilityScore = this.calculateCropSuitability(soilData, cropName);
            cropScores.push({
                name: this.formatCropName(cropName),
                score: suitabilityScore
            });
        }
        
        // Sort by suitability score and return top crops
        return cropScores
            .sort((a, b) => b.score - a.score)
            .slice(0, 4)
            .map(crop => crop.name);
    }
    
    /**
     * Calculate suitability score for specific crop
     * @param {Object} soilData - Soil measurements
     * @param {string} cropType - Type of crop
     * @returns {number} Suitability score (0-100)
     */
    calculateCropSuitability(soilData, cropType) {
        const requirements = this.cropRequirements[cropType];
        if (!requirements) return 50;
        
        let score = 100;
        
        // Check pH suitability
        if (soilData.ph_level) {
            const ph = soilData.ph_level;
            const [minPh, maxPh] = requirements.ph_range;
            
            if (ph < minPh || ph > maxPh) {
                const deviation = Math.min(
                    Math.abs(ph - minPh),
                    Math.abs(ph - maxPh)
                );
                score -= deviation * 15; // Penalize pH deviation
            }
        }
        
        // Check nitrogen requirements
        if (soilData.nitrogen_level) {
            const nitrogen = soilData.nitrogen_level;
            const nitrogenNeed = requirements.nitrogen_need;
            
            if (nitrogenNeed === 'high' && nitrogen < 25) {
                score -= 20;
            } else if (nitrogenNeed === 'low' && nitrogen > 35) {
                score -= 10; // High nitrogen can inhibit nitrogen fixation
            }
        }
        
        // Check organic matter (generally beneficial for all crops)
        if (soilData.organic_matter && soilData.organic_matter < 2.5) {
            score -= 15;
        }
        
        // Check moisture content based on water requirements
        if (soilData.moisture_content) {
            const moisture = soilData.moisture_content;
            const waterReq = requirements.water_requirement;
            
            if (waterReq === 'high' && moisture < 25) {
                score -= 15;
            } else if (waterReq === 'low' && moisture > 35) {
                score -= 10;
            }
        }
        
        return Math.max(20, Math.min(100, score));
    }
    
    /**
     * Generate soil management recommendations
     * @param {Object} soilData - Soil measurements
     * @param {string} region - Geographic region
     * @param {string} crop - Primary crop type
     * @returns {Array} Array of recommendation objects
     */
    getRecommendations(soilData, region = 'Zimbabwe', crop = 'Maize') {
        const recommendations = [];
        
        if (!soilData) return recommendations;
        
        // pH recommendations
        if (soilData.ph_level < 5.5) {
            recommendations.push({
                title: 'Critical pH Correction',
                action: `Apply 3-4 tons of agricultural lime per hectare immediately`,
                reason: `Soil pH is severely acidic at ${soilData.ph_level.toFixed(1)}, severely limiting nutrient availability`,
                cost_estimate: 'High ($200-300 per hectare)',
                timeframe: '3-6 months for full effect',
                local_context: 'Agricultural lime is available from most agricultural suppliers in Zimbabwe. Consider community purchasing for bulk discounts.'
            });
        } else if (soilData.ph_level < 6.0) {
            recommendations.push({
                title: 'Improve Soil pH',
                action: `Apply 2-3 tons of agricultural lime per hectare`,
                reason: `Current pH of ${soilData.ph_level.toFixed(1)} is limiting optimal nutrient availability`,
                cost_estimate: 'Medium ($150-200 per hectare)',
                timeframe: '2-4 months',
                local_context: 'Time application for the beginning of the rainy season for better incorporation.'
            });
        } else if (soilData.ph_level > 7.5) {
            recommendations.push({
                title: 'Reduce Soil Alkalinity',
                action: 'Apply organic matter (compost, manure) and consider sulfur application',
                reason: `High pH of ${soilData.ph_level.toFixed(1)} may limit micronutrient availability`,
                cost_estimate: 'Medium ($100-150 per hectare)',
                timeframe: '6-12 months',
                local_context: 'Use locally available cattle or chicken manure. Avoid lime-based fertilizers.'
            });
        }
        
        // Nitrogen recommendations
        if (soilData.nitrogen_level < 15) {
            recommendations.push({
                title: 'Critical Nitrogen Supplementation',
                action: `Apply ${Math.round(40 - soilData.nitrogen_level)} kg/ha of nitrogen fertilizer (Urea or AN) in split applications`,
                reason: 'Severe nitrogen deficiency will dramatically reduce yields',
                cost_estimate: 'High ($120-180 per hectare)',
                timeframe: '2-4 weeks, split applications throughout season',
                local_context: 'Apply 1/3 at planting, 1/3 at 4-6 weeks, 1/3 at tasseling for maize.'
            });
        } else if (soilData.nitrogen_level < 20) {
            recommendations.push({
                title: 'Increase Nitrogen Levels',
                action: `Apply ${Math.round(30 - soilData.nitrogen_level)} kg/ha of nitrogen fertilizer`,
                reason: 'Nitrogen levels are below optimal for good crop performance',
                cost_estimate: 'Medium ($80-120 per hectare)',
                timeframe: '2-4 weeks',
                local_context: 'Consider incorporating legume crops in rotation to reduce future nitrogen needs.'
            });
        }
        
        // Phosphorus recommendations
        if (soilData.phosphorus_level < 15) {
            recommendations.push({
                title: 'Phosphorus Supplementation',
                action: `Apply ${Math.round((20 - soilData.phosphorus_level) * 2)} kg/ha of phosphorus fertilizer (TSP or DAP)`,
                reason: 'Low phosphorus limits root development and early plant growth',
                cost_estimate: 'Medium ($60-100 per hectare)',
                timeframe: 'Apply at planting for best results',
                local_context: 'Phosphorus should be placed near seeds/seedlings as it doesn\'t move much in soil.'
            });
        }
        
        // Potassium recommendations
        if (soilData.potassium_level < 120) {
            recommendations.push({
                title: 'Potassium Enhancement',
                action: `Apply ${Math.round((180 - soilData.potassium_level) / 10)} kg/ha of potassium fertilizer (Muriate of Potash)`,
                reason: 'Low potassium reduces plant stress tolerance and water use efficiency',
                cost_estimate: 'Medium ($70-110 per hectare)',
                timeframe: 'Apply before planting or early in season',
                local_context: 'Potassium is especially important during drought periods common in Zimbabwe.'
            });
        }
        
        // Organic matter recommendations
        if (soilData.organic_matter < 2.0) {
            recommendations.push({
                title: 'Critical Organic Matter Improvement',
                action: 'Apply 10-15 tons per hectare of well-composted organic matter',
                reason: `Extremely low organic matter at ${soilData.organic_matter.toFixed(1)}% severely impacts soil structure and water retention`,
                cost_estimate: 'Low-Medium ($50-120 per hectare)',
                timeframe: '6-12 months for significant improvement',
                local_context: 'Use local resources: cattle manure, crop residues, or start composting program. Critical for Zimbabwe\'s climate.'
            });
        } else if (soilData.organic_matter < 3.0) {
            recommendations.push({
                title: 'Increase Organic Matter',
                action: 'Apply 5-8 tons per hectare of compost or well-rotted manure',
                reason: 'Increasing organic matter will improve soil structure and nutrient retention',
                cost_estimate: 'Low ($30-80 per hectare)',
                timeframe: '3-6 months',
                local_context: 'Consider cover crops during off-season to build organic matter naturally.'
            });
        }
        
        // Moisture management recommendations
        const currentMonth = new Date().getMonth() + 1;
        const isDrySeason = [5, 6, 7, 8, 9].includes(currentMonth);
        
        if (soilData.moisture_content < 15 && isDrySeason) {
            recommendations.push({
                title: 'Emergency Water Conservation',
                action: 'Implement immediate water conservation: mulching, basin planting, and reduce plant density',
                reason: `Critical soil moisture shortage during dry season at ${soilData.moisture_content.toFixed(1)}%`,
                cost_estimate: 'Low-Medium ($20-60 per hectare)',
                timeframe: 'Immediate implementation required',
                local_context: 'Use available crop residues for mulch. Consider drought-tolerant varieties for next season.'
            });
        } else if (soilData.moisture_content < 20) {
            recommendations.push({
                title: 'Improve Water Management',
                action: 'Install water conservation measures: tied ridges, mulching, or drip irrigation if possible',
                reason: 'Low soil moisture may limit plant productivity and stress tolerance',
                cost_estimate: 'Medium ($60-200 per hectare depending on method)',
                timeframe: '1-3 months',
                local_context: 'Rainwater harvesting techniques are well-suited to Zimbabwe\'s rainfall patterns.'
            });
        } else if (soilData.moisture_content > 35) {
            recommendations.push({
                title: 'Improve Drainage',
                action: 'Create drainage channels or raised beds to prevent waterlogging',
                reason: `High moisture content at ${soilData.moisture_content.toFixed(1)}% may cause root rot and nutrient leaching`,
                cost_estimate: 'Medium ($40-100 per hectare)',
                timeframe: '2-4 weeks',
                local_context: 'Important during Zimbabwe\'s rainy season (November-March) to prevent crop damage.'
            });
        }
        
        // Cation Exchange Capacity recommendations
        if (soilData.cation_exchange_capacity < 8) {
            recommendations.push({
                title: 'Improve Nutrient Retention Capacity',
                action: 'Add clay-rich soil amendments and increase organic matter significantly',
                reason: 'Low CEC means poor nutrient retention and higher fertilizer requirements',
                cost_estimate: 'Medium ($80-150 per hectare)',
                timeframe: '6-18 months for measurable improvement',
                local_context: 'Focus on long-term soil building. Consider adding local clay deposits if available.'
            });
        }
        
        // Regional and crop-specific recommendations
        if (crop.toLowerCase() === 'maize') {
            if (soilData.nitrogen_level < 25) {
                recommendations.push({
                    title: 'Maize-Specific Nitrogen Management',
                    action: 'Use split nitrogen application: 30% at planting, 40% at 6 weeks, 30% at tasseling',
                    reason: 'Maize has high nitrogen demands throughout growing season',
                    cost_estimate: 'Medium ($100-150 per hectare)',
                    timeframe: 'Throughout growing season',
                    local_context: 'Critical for maize production in Zimbabwe. Time applications with rainfall.'
                });
            }
        }
        
        // Add general conservation agriculture recommendation
        recommendations.push({
            title: 'Adopt Conservation Agriculture',
            action: 'Implement minimum tillage, crop rotation, and permanent soil cover',
            reason: 'Long-term soil health improvement and climate resilience',
            cost_estimate: 'Low (mainly labor and management changes)',
            timeframe: '2-3 seasons for full benefits',
            local_context: 'Widely promoted in Zimbabwe. Join local conservation agriculture groups for support and training.'
        });
        
        // Limit to most important recommendations (top 5)
        return recommendations.slice(0, 5);
    }
    
    /**
     * Format crop name for display
     * @param {string} cropName - Internal crop name
     * @returns {string} Formatted crop name
     */
    formatCropName(cropName) {
        const nameMap = {
            'maize': 'Maize',
            'groundnuts': 'Groundnuts',
            'sorghum': 'Sorghum',
            'cotton': 'Cotton',
            'soybeans': 'Soybeans',
            'sweet_potatoes': 'Sweet Potatoes'
        };
        
        return nameMap[cropName] || cropName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    /**
     * Get detailed analysis of soil health
     * @param {Object} soilData - Soil measurements
     * @returns {Object} Detailed analysis object
     */
    getDetailedAnalysis(soilData) {
        const overallScore = this.calculateScore(soilData);
        const parameterScores = {};
        
        // Calculate individual parameter scores
        for (const [param, value] of Object.entries(soilData)) {
            if (param === 'timestamp' || param === 'sample_id') continue;
            
            if (this.optimalRanges[param] && typeof value === 'number') {
                parameterScores[param] = {
                    value: value,
                    score: this.calculateParameterScore(param, value) * 100,
                    status: this.getParameterStatus(param, value),
                    optimal_range: this.optimalRanges[param]
                };
            }
        }
        
        return {
            overall_score: overallScore,
            risk_level: this.determineRiskLevel(overallScore),
            parameter_analysis: parameterScores,
            recommended_crops: this.recommendSuitableCrops(soilData),
            recommendations: this.getRecommendations(soilData),
            analysis_date: new Date().toISOString()
        };
    }
    
    /**
     * Get status description for parameter
     * @param {string} parameter - Parameter name
     * @param {number} value - Parameter value
     * @returns {string} Status description
     */
    getParameterStatus(parameter, value) {
        const score = this.calculateParameterScore(parameter, value) * 100;
        
        if (score >= 80) return 'Optimal';
        if (score >= 60) return 'Good';
        if (score >= 40) return 'Fair';
        if (score >= 20) return 'Poor';
        return 'Critical';
    }
}

// Make the class available globally
if (typeof window !== 'undefined') {
    window.SoilHealthAlgorithm = SoilHealthAlgorithm;
}