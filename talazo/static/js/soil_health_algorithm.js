// SoilHealthAlgorithm for the Talazo AgriFinance platform
// This class contains the logic for calculating financial indices based on soil health

class SoilHealthAlgorithm {
    constructor() {
        // Ideal ranges for soil parameters specific to Zimbabwe's agricultural conditions
        this.idealRanges = {
            'ph_level': [6.0, 7.0],
            'nitrogen_level': [20.0, 40.0],  // mg/kg
            'phosphorus_level': [15.0, 30.0],  // mg/kg
            'potassium_level': [150.0, 250.0],  // mg/kg
            'organic_matter': [3.0, 5.0],  // percentage
            'cation_exchange_capacity': [10.0, 20.0],  // cmol/kg
            'moisture_content': [20.0, 30.0]  // percentage
        };
        
        // Parameter weights for overall score calculation - adjusted for Zimbabwean context
        this.weights = {
            'ph_level': 0.20,           // Critical for nutrient availability
            'nitrogen_level': 0.18,      // Essential for growth
            'phosphorus_level': 0.15,    // Important for root development and flowering
            'potassium_level': 0.15,     // Key for water regulation and disease resistance
            'organic_matter': 0.17,      // Critical for soil structure and water retention
            'cation_exchange_capacity': 0.08, // Affects nutrient holding capacity
            'moisture_content': 0.07     // Current moisture status
        };
        
        // Define common crops with their requirements
        this.crops = {
            'Maize': {
                idealPh: [5.8, 6.8],
                nitrogenRequirement: 'high',
                droughtTolerance: 'medium',
                suitableRegions: ['Mashonaland', 'Manicaland', 'Midlands']
            },
            'Sorghum': {
                idealPh: [5.5, 7.5],
                nitrogenRequirement: 'medium',
                droughtTolerance: 'high',
                suitableRegions: ['Matabeleland', 'Midlands', 'Masvingo']
            },
            'Groundnuts': {
                idealPh: [5.5, 7.0],
                nitrogenRequirement: 'low',
                droughtTolerance: 'medium',
                suitableRegions: ['Mashonaland', 'Midlands', 'Manicaland']
            },
            'Cotton': {
                idealPh: [5.8, 7.0],
                nitrogenRequirement: 'high',
                droughtTolerance: 'high',
                suitableRegions: ['Midlands', 'Mashonaland West', 'Matabeleland North']
            },
            'Soybeans': {
                idealPh: [6.0, 7.0],
                nitrogenRequirement: 'low',
                droughtTolerance: 'medium',
                suitableRegions: ['Mashonaland', 'Manicaland']
            },
            'Sweet Potatoes': {
                idealPh: [5.6, 6.5],
                nitrogenRequirement: 'medium',
                droughtTolerance: 'high',
                suitableRegions: ['Mashonaland East', 'Manicaland', 'Matabeleland South']
            },
            'Wheat': {
                idealPh: [6.0, 7.5],
                nitrogenRequirement: 'high',
                droughtTolerance: 'low',
                suitableRegions: ['Mashonaland', 'Midlands']
            },
            'Millet': {
                idealPh: [5.5, 7.5],
                nitrogenRequirement: 'low',
                droughtTolerance: 'very high',
                suitableRegions: ['Matabeleland', 'Masvingo', 'Midlands']
            },
            'Tobacco': {
                idealPh: [5.5, 6.5],
                nitrogenRequirement: 'high',
                droughtTolerance: 'low',
                suitableRegions: ['Mashonaland East', 'Mashonaland Central', 'Manicaland']
            },
            'Sunflower': {
                idealPh: [6.0, 7.5],
                nitrogenRequirement: 'medium',
                droughtTolerance: 'high',
                suitableRegions: ['Matabeleland North', 'Midlands', 'Mashonaland West']
            }
        };
        
        // Risk level thresholds
        this.riskLevels = [
            { threshold: 80, level: "Low Risk" },
            { threshold: 65, level: "Medium-Low Risk" },
            { threshold: 50, level: "Medium Risk" },
            { threshold: 35, level: "Medium-High Risk" },
            { threshold: 0, level: "High Risk" }
        ];
        
        // Interest rate model
        this.interestRateModel = [
            { healthScore: 80, rate: 5.75, term: 36 },
            { healthScore: 65, rate: 6.25, term: 30 },
            { healthScore: 50, rate: 7.00, term: 24 },
            { healthScore: 40, rate: 8.25, term: 18 }
        ];
    }
    
    calculateScore(soilData) {
        // Calculate overall soil health score
        let totalScore = 0;
        let totalWeight = 0;
        
        for (const [param, weight] of Object.entries(this.weights)) {
            if (param in soilData && soilData[param] !== null && soilData[param] !== undefined) {
                const value = parseFloat(soilData[param]);
                const paramScore = this.calculateParameterScore(param, value);
                totalScore += paramScore * weight;
                totalWeight += weight;
            }
        }
        
        if (totalWeight === 0) return 0;
        
        // Normalize score to 0-100 range
        return Math.round((totalScore / totalWeight) * 100);
    }
    
    calculateParameterScore(param, value) {
        // Calculate score for individual parameter based on ideal ranges
        if (!this.idealRanges[param]) return 0;
        
        const [min, max] = this.idealRanges[param];
        
        // Perfect score if within ideal range
        if (value >= min && value <= max) {
            return 1.0;
        }
        
        // Calculate deviation from ideal range
        let deviation;
        if (value < min) {
            deviation = (min - value) / min;
        } else { // value > max
            deviation = (value - max) / max;
        }
        
        // Different scoring curves for different parameters
        if (param === 'organic_matter' && value > max) {
            // More organic matter is generally not as bad
            return Math.max(0, 1 - deviation * 0.5);
        } else if (param === 'ph_level') {
            // pH is more sensitive to deviations - critical for nutrient availability
            return Math.max(0, 1 - deviation * 1.5);
        } else if (param === 'nitrogen_level' || param === 'phosphorus_level') {
            // Primary macronutrients are important but with diminishing returns
            if (value > max) {
                return Math.max(0.5, 1 - deviation * 0.8); // Excess isn't as bad as deficiency
            } else {
                return Math.max(0, 1 - deviation * 1.2); // Deficiency is quite bad
            }
        } else {
            // Standard scoring curve
            return Math.max(0, 1 - deviation);
        }
    }
    
    determineRiskLevel(score) {
        /**
         * Determine financial risk level based on soil health score
         */
        for (const { threshold, level } of this.riskLevels) {
            if (score >= threshold) {
                return level;
            }
        }
        return "High Risk"; // Default if no threshold matches
    }
    
    calculatePremium(score, basePremium = 100) {
        /**
         * Calculate insurance premium based on soil health score
         * Lower score = higher risk = higher premium
         */
        // Apply a non-linear relationship for more realistic premiums
        const riskFactor = (100 - score) / 100;
        
        // Make the relationship more pronounced
        const premiumMultiplier = 1 + (riskFactor ** 1.8);
        
        // Calculate the premium with some random variation for realistic demo
        const randomFactor = 0.9 + (Math.random() * 0.2); // 0.9 to 1.1
        const calculatedPremium = basePremium * premiumMultiplier * randomFactor;
        
        // Format to 2 decimal places
        return Math.round(calculatedPremium * 100) / 100;
    }
    
    calculateLoanTerms(score) {
        /**
         * Calculate loan terms based on the soil health score
         */
        // Find the appropriate interest rate and term
        for (const { healthScore, rate, term } of this.interestRateModel) {
            if (score >= healthScore) {
                return {
                    maxAmount: Math.round(score * 50), // $50 per score point
                    interestRate: rate,
                    term: term
                };
            }
        }
        
        // Default for lower scores that don't qualify
        return {
            maxAmount: 0,
            interestRate: 'N/A',
            term: 'N/A'
        };
    }
    
    recommendSuitableCrops(soilData, region = null) {
        /**
         * Recommend suitable crops based on soil parameters
         */
        if (!soilData) return [];
        
        // Extract key soil parameters
        const ph = parseFloat(soilData.ph_level || 0);
        const nitrogen = parseFloat(soilData.nitrogen_level || 0);
        const phosphorus = parseFloat(soilData.phosphorus_level || 0);
        const potassium = parseFloat(soilData.potassium_level || 0);
        const organicMatter = parseFloat(soilData.organic_matter || 0);
        const moisture = parseFloat(soilData.moisture_content || 0);
        
        // Get current season
        const currentMonth = new Date().getMonth() + 1;
        const isWinterSeason = [5, 6, 7, 8].includes(currentMonth);
        
        // Score each crop based on soil suitability
        const cropScores = {};
        
        for (const [cropName, cropData] of Object.entries(this.crops)) {
            // Skip winter crops during summer and vice versa
            if (cropName === 'Wheat' && !isWinterSeason) continue;
            
            // Regional match if region is specified
            let regionScore = 1.0;
            if (region) {
                const regionMatch = cropData.suitableRegions.some(r => 
                    region.toLowerCase().includes(r.toLowerCase())
                );
                regionScore = regionMatch ? 1.0 : 0.7;
            }
            
            // Calculate pH match score
            const [minPh, maxPh] = cropData.idealPh;
            let phScore;
            
            if (minPh <= ph && ph <= maxPh) {
                phScore = 1.0;
            } else {
                const distance = Math.min(Math.abs(ph - minPh), Math.abs(ph - maxPh));
                phScore = Math.max(0, 1 - distance / 2);
            }
            
            // Calculate nitrogen match score
            let nitrogenScore;
            
            if (cropData.nitrogenRequirement === 'low') {
                nitrogenScore = nitrogen < 20 ? 1.0 : (nitrogen > 40 ? 0.7 : 0.9);
            } else if (cropData.nitrogenRequirement === 'medium') {
                nitrogenScore = nitrogen < 20 ? 0.7 : (nitrogen > 40 ? 0.8 : 1.0);
            } else { // high
                nitrogenScore = nitrogen < 20 ? 0.5 : (nitrogen > 40 ? 1.0 : 0.9);
            }
            
            // Calculate drought tolerance vs moisture content match
            let moistureScore;
            
            if (cropData.droughtTolerance === 'very high') {
                moistureScore = moisture < 15 ? 0.9 : (moisture > 35 ? 0.7 : 1.0);
            } else if (cropData.droughtTolerance === 'high') {
                moistureScore = moisture < 15 ? 0.7 : (moisture > 35 ? 0.6 : 1.0);
            } else if (cropData.droughtTolerance === 'medium') {
                moistureScore = moisture < 15 ? 0.5 : (moisture > 35 ? 0.5 : 1.0);
            } else { // low drought tolerance
                moistureScore = moisture < 20 ? 0.3 : (moisture > 35 ? 0.7 : 1.0);
            }
            
            // Calculate overall suitability score with weighted components
            const overallScore = (
                phScore * 0.25 +
                nitrogenScore * 0.2 +
                moistureScore * 0.25 +
                regionScore * 0.3
            );
            
            cropScores[cropName] = overallScore;
        }
        
        // Sort crops by score and return top matches
        const sortedCrops = Object.entries(cropScores)
            .sort((a, b) => b[1] - a[1])
            .filter(([_, score]) => score > 0.65)
            .map(([crop, _]) => crop);
        
        return sortedCrops.slice(0, 5);  // Return top 5 suitable crops
    }
    
    getRecommendations(soilData, region = null, crop = null) {
        /**
         * Generate soil health recommendations based on soil data
         */
        const recommendations = [];
        
        if (!soilData) return recommendations;
        
        // Check pH level
        const ph = parseFloat(soilData.ph_level || 0);
        if (ph < 5.5) {
            recommendations.push({
                title: 'Urgent: Correct Soil Acidity',
                action: `Apply agricultural lime at ${Math.round((6.5 - ph) * 2.5)} tons per hectare`,
                reason: 'Soil is extremely acidic, severely limiting nutrient availability and crop growth',
                cost_estimate: 'Medium to High',
                timeframe: '2-4 weeks before planting',
                local_context: 'Dolomitic lime is recommended for Zimbabwean soils to address both acidity and magnesium deficiency'
            });
        } else if (ph < 6.0) {
            recommendations.push({
                title: 'Correct Soil pH',
                action: `Apply agricultural lime at ${Math.round((6.5 - ph) * 2)} tons per hectare`,
                reason: 'Soil is moderately acidic, which limits nutrient availability',
                cost_estimate: 'Medium',
                timeframe: '1-2 months before planting',
                local_context: 'Locally available agricultural lime can be sourced from most agricultural supply stores in Zimbabwe'
            });
        } else if (ph > 7.5) {
            recommendations.push({
                title: 'Reduce Soil pH',
                action: 'Apply organic matter such as compost or manure at 5-10 tons per hectare',
                reason: 'Soil is too alkaline, which can limit micronutrient uptake',
                cost_estimate: 'Low to Medium',
                timeframe: '3-6 months',
                local_context: 'Manure from local livestock can be an affordable option for small-scale farmers'
            });
        }
        
        // Check nitrogen level
        const nitrogen = parseFloat(soilData.nitrogen_level || 0);
        if (nitrogen < 15) {
            recommendations.push({
                title: 'Critical Nitrogen Deficiency',
                action: `Apply nitrogen fertilizer (Ammonium Nitrate) at ${Math.round(180 - nitrogen * 5)} kg/ha in split application`,
                reason: 'Severe nitrogen deficiency will dramatically reduce plant growth and yield',
                cost_estimate: 'Medium to High',
                timeframe: 'Immediately and follow up in 3-4 weeks',
                local_context: 'Consider applying a portion at planting and the remainder as top dressing during vegetative growth'
            });
        } else if (nitrogen < 20) {
            recommendations.push({
                title: 'Increase Nitrogen Levels',
                action: `Apply nitrogen fertilizer (Ammonium Nitrate) at ${Math.round(120 - nitrogen * 4)} kg/ha`,
                reason: 'Nitrogen deficiency will limit plant growth and yield',
                cost_estimate: 'Medium',
                timeframe: '2-4 weeks before or during early growth',
                local_context: 'Consider split application during the growing season for better efficiency in Zimbabwe\'s climate'
            });
        }
        
        // Check phosphorus level
        const phosphorus = parseFloat(soilData.phosphorus_level || 0);
        if (phosphorus < 10) {
            recommendations.push({
                title: 'Critical Phosphorus Deficiency',
                action: 'Apply phosphate fertilizer (Single Superphosphate) at 200-250 kg/ha',
                reason: 'Severe phosphorus deficiency will inhibit root development and overall plant growth',
                cost_estimate: 'Medium to High',
                timeframe: 'Apply before planting',
                local_context: 'Incorporate into soil near the root zone for best results in Zimbabwean soils'
            });
        } else if (phosphorus < 15) {
            recommendations.push({
                title: 'Increase Phosphorus Levels',
                action: 'Apply phosphate fertilizer at 150-200 kg/ha',
                reason: 'Low phosphorus levels will limit root development, flowering, and seed formation',
                cost_estimate: 'Medium',
                timeframe: 'Apply before planting',
                local_context: 'Most common crops in Zimbabwe respond well to phosphorus at planting time'
            });
        }
        
        // Check potassium level
        const potassium = parseFloat(soilData.potassium_level || 0);
        if (potassium < 100) {
            recommendations.push({
                title: 'Critical Potassium Deficiency',
                action: 'Apply potassium fertilizer (Muriate of Potash) at 150-200 kg/ha',
                reason: 'Severe potassium deficiency will reduce drought tolerance, disease resistance, and yield quality',
                cost_estimate: 'Medium to High',
                timeframe: 'Apply before planting',
                local_context: 'Sandy soils common in parts of Zimbabwe often require potassium supplementation'
            });
        } else if (potassium < 150) {
            recommendations.push({
                title: 'Increase Potassium Levels',
                action: 'Apply potassium fertilizer at 100-150 kg/ha',
                reason: 'Adequate potassium improves drought tolerance, disease resistance, and overall yield',
                cost_estimate: 'Medium',
                timeframe: 'Before planting',
                local_context: 'Important for water efficiency in drought-prone regions of Zimbabwe'
            });
        }
        
        // Check organic matter
        const organicMatter = parseFloat(soilData.organic_matter || 0);
        if (organicMatter < 2.0) {
            recommendations.push({
                title: 'Critical Organic Matter Deficiency',
                action: 'Implement intensive soil building with cover crops, crop residue, and 10+ tons/ha of compost or manure',
                reason: 'Very low organic matter severely impacts soil structure, water retention, and nutrient availability',
                cost_estimate: 'Medium',
                timeframe: 'Long-term strategy over 2-3 growing seasons',
                local_context: 'Conservation agriculture techniques are promoted by Zimbabwe\'s agricultural extension services'
            });
        } else if (organicMatter < 3.0) {
            recommendations.push({
                title: 'Increase Organic Matter',
                action: 'Apply compost or manure at 5-10 tons/ha and incorporate crop residues',
                reason: 'Improved organic matter will enhance soil structure, water retention, and nutrient cycling',
                cost_estimate: 'Low to Medium',
                timeframe: '6-12 months for noticeable benefits',
                local_context: 'Using locally available organic resources reduces dependence on expensive inputs'
            });
        }
        
        // Check moisture content
        const moisture = parseFloat(soilData.moisture_content || 0);
        const currentMonth = new Date().getMonth() + 1;
        const isDrySeason = [5, 6, 7, 8, 9].includes(currentMonth);
        
        if (isDrySeason && moisture < 15) {
            recommendations.push({
                title: 'Critical Drought Risk',
                action: 'Implement water conservation strategies: mulching, tied ridges, and supplemental irrigation if available',
                reason: 'Critically low soil moisture during dry season will cause crop failure without intervention',
                cost_estimate: 'Medium',
                timeframe: 'Immediate action required',
                local_context: 'Water harvesting techniques are essential during Zimbabwe\'s dry season'
            });
        } else if (moisture < 18) {
            recommendations.push({
                title: 'Improve Moisture Management',
                action: 'Apply mulch and implement water conservation practices like tied ridges or basins',
                reason: 'Low soil moisture may lead to plant stress and reduced yields',
                cost_estimate: 'Low to Medium',
                timeframe: 'Implement within 2-3 weeks',
                local_context: 'Critical for rainfed agriculture in Zimbabwe\'s drought-prone regions'
            });
        } else if (moisture > 35) {
            recommendations.push({
                title: 'Address Excess Moisture',
                action: 'Improve drainage through channels or raised beds',
                reason: 'Waterlogging causes root diseases and nutrient leaching',
                cost_estimate: 'Medium',
                timeframe: 'Before next heavy rains',
                local_context: 'Important during Zimbabwe\'s rainy season, especially in low-lying areas'
            });
        }
        
        // Check cation exchange capacity (CEC)
        const cec = parseFloat(soilData.cation_exchange_capacity || 0);
        if (cec < 5) {
            recommendations.push({
                title: 'Improve Nutrient Holding Capacity',
                action: 'Add organic matter and clay materials to improve CEC',
                reason: 'Low CEC soils cannot hold nutrients effectively, leading to leaching and inefficient fertilizer use',
                cost_estimate: 'Medium',
                timeframe: 'Long-term strategy over multiple seasons',
                local_context: 'Sandy soils in Zimbabwe often have this issue and benefit greatly from organic matter addition'
            });
        }
        
        // Add crop-specific recommendation if crop provided
        if (crop) {
            const cropLower = crop.toLowerCase();
            
            if (cropLower === 'maize') {
                recommendations.push({
                    title: 'Maize-Specific Management',
                    action: 'Use appropriate spacing (75cm between rows, 25cm between plants) and consider applying zinc sulfate at 15 kg/ha',
                    reason: 'Proper spacing optimizes resource use and Zimbabwe soils are often zinc deficient for maize',
                    cost_estimate: 'Low',
                    timeframe: 'At planting time',
                    local_context: 'Maize is Zimbabwe\'s staple crop; most extension services provide specific recommendations'
                });
            } else if (cropLower.includes('groundnut') || cropLower.includes('peanut')) {
                recommendations.push({
                    title: 'Groundnut Management',
                    action: 'Apply gypsum (calcium sulfate) at 200-400 kg/ha at flowering stage',
                    reason: 'Calcium is essential for pod development and filling in groundnuts',
                    cost_estimate: 'Medium',
                    timeframe: 'Apply at flowering',
                    local_context: 'Groundnuts are an important crop for both food security and income in Zimbabwe'
                });
            } else if (cropLower === 'cotton') {
                recommendations.push({
                    title: 'Cotton Management',
                    action: 'Implement integrated pest management for bollworm control and consider applying boron at 1-2 kg/ha',
                    reason: 'Pest management is critical for cotton quality and yield; boron deficiency is common in cotton-growing regions',
                    cost_estimate: 'Medium to High',
                    timeframe: 'Throughout growing season',
                    local_context: 'Cotton is a key cash crop in Zimbabwe requiring careful management'
                });
            } else if (cropLower === 'tobacco') {
                recommendations.push({
                    title: 'Tobacco Management',
                    action: 'Monitor and maintain strict soil pH (5.5-6.0) and apply split nitrogen applications',
                    reason: 'Tobacco is very sensitive to soil pH and nitrogen levels, affecting leaf quality',
                    cost_estimate: 'High',
                    timeframe: 'Throughout season',
                    local_context: 'Tobacco is a high-value export crop in Zimbabwe with specific quality requirements'
                });
            } else if (cropLower === 'sorghum' || cropLower === 'millet') {
                recommendations.push({
                    title: 'Drought-Resistant Cereal Management',
                    action: 'Implement moisture conservation and consider wider spacing (up to 100cm between rows for very dry areas)',
                    reason: 'Maximizes limited water resources in drought-prone areas',
                    cost_estimate: 'Low',
                    timeframe: 'At planting',
                    local_context: 'Traditional grains are increasingly important for climate resilience in Zimbabwe'
                });
            }
        }
        
        // If in a specific region, add region-specific advice
        if (region) {
            const regionLower = region.toLowerCase();
            
            if (regionLower.includes('matabeleland')) {
                recommendations.push({
                    title: 'Matabeleland Drought Adaptation',
                    action: 'Implement moisture conservation techniques like deep plowing, mulching, and drought-resistant crop varieties',
                    reason: 'Matabeleland regions are prone to drought conditions and often have shallow soils',
                    cost_estimate: 'Medium',
                    timeframe: 'Before planting season',
                    local_context: 'Conservation agriculture has shown success in similar semi-arid areas of Zimbabwe'
                });
            } else if (regionLower.includes('mashonaland')) {
                if (moisture > 30) {
                    recommendations.push({
                        title: 'Mashonaland Drainage Management',
                        action: 'Create drainage channels to prevent waterlogging during heavy rains',
                        reason: 'Mashonaland regions often receive higher rainfall that can lead to waterlogging',
                        cost_estimate: 'Medium',
                        timeframe: 'Before rainy season',
                        local_context: 'Particularly important for low-lying fields in this region'
                    });
                }
            } else if (regionLower.includes('manicaland')) {
                recommendations.push({
                    title: 'Manicaland Soil Erosion Prevention',
                    action: 'Implement contour ridges and terracing on sloped land',
                    reason: 'The hilly terrain in many parts of Manicaland is prone to soil erosion',
                    cost_estimate: 'Medium to High',
                    timeframe: 'Before rainy season',
                    local_context: 'Soil conservation is critical in this region with varied topography'
                });
            }
        }
        
        return recommendations;
    }
}