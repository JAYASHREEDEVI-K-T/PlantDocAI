"""
Advanced AI-Powered Plant Disease Recommendation Engine
Features: RAG, Caching, Multi-language, User Feedback, Analytics
"""

import json
import logging
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from functools import lru_cache
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_to_bullets(items: List[str]) -> str:
    """Convert list to bullet points"""
    if not items:
        return ""
    return "\n".join([f"• {item}" for item in items])

@dataclass
class Recommendation:
    """Enhanced recommendation data structure"""
    disease_name: str
    plant_type: str
    disease_type: str
    severity: str
    confidence: float
    description: str
    symptoms: List[str] = field(default_factory=list)
    treatment: List[str] = field(default_factory=list)
    prevention: List[str] = field(default_factory=list)
    organic_solutions: List[str] = field(default_factory=list)
    chemical_solutions: List[str] = field(default_factory=list)
    care_instructions: List[str] = field(default_factory=list)
    timeline: Dict[str, str] = field(default_factory=dict)
    cost_estimate: str = ""
    affected_regions: List[str] = field(default_factory=list)
    scientific_name: str = ""
    related_diseases: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    source: str = "dynamic"
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    language: str = "en"
    
    def to_dict(self):
        """Convert to dictionary with formatted lists"""
        data = asdict(self)
        # Convert lists to bullet points for text fields
        list_fields = ['symptoms', 'treatment', 'prevention', 'organic_solutions', 
                      'chemical_solutions', 'care_instructions', 'related_diseases']
        for field_name in list_fields:
            if isinstance(data.get(field_name), list):
                data[field_name] = list_to_bullets(data[field_name])
        return data


@dataclass
class UserFeedback:
    """Track user feedback for continuous improvement"""
    disease_class: str
    recommendation_id: str
    rating: int  # 1-5
    was_helpful: bool
    user_comment: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RecommendationCache:
    """LRU cache for recommendations to improve performance"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_count = {}
    
    def _generate_key(self, disease_class: str, confidence: float, language: str) -> str:
        """Generate cache key"""
        key_string = f"{disease_class}_{confidence:.4f}_{language}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, disease_class: str, confidence: float, language: str = "en") -> Optional[Dict]:
        """Retrieve from cache"""
        key = self._generate_key(disease_class, confidence, language)
        if key in self.cache:
            self.access_count[key] = self.access_count.get(key, 0) + 1
            logger.debug(f"Cache hit for {disease_class}")
            return self.cache[key]
        return None
    
    def set(self, disease_class: str, confidence: float, recommendation: Dict, language: str = "en"):
        """Store in cache with LRU eviction"""
        key = self._generate_key(disease_class, confidence, language)
        
        # Evict least accessed if cache is full
        if len(self.cache) >= self.max_size:
            lru_key = min(self.access_count, key=self.access_count.get)
            del self.cache[lru_key]
            del self.access_count[lru_key]
        
        self.cache[key] = recommendation
        self.access_count[key] = 1
        logger.debug(f"Cached recommendation for {disease_class}")
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.access_count.clear()
        logger.info("Cache cleared")


class RecommendationAnalytics:
    """Track recommendation performance and user interactions"""
    
    def __init__(self, analytics_path: Optional[str] = None):
        self.analytics_path = analytics_path or "analytics/recommendation_stats.json"
        self.stats = self._load_analytics()
    
    def _load_analytics(self) -> Dict:
        """Load analytics from file"""
        try:
            path = Path(self.analytics_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load analytics: {e}")
        
        return {
            "total_requests": 0,
            "disease_frequency": {},
            "average_confidence": {},
            "user_ratings": {},
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    def log_recommendation(self, disease_class: str, confidence: float, cache_hit: bool):
        """Log recommendation request"""
        self.stats["total_requests"] += 1
        
        # Track disease frequency
        if disease_class not in self.stats["disease_frequency"]:
            self.stats["disease_frequency"][disease_class] = 0
        self.stats["disease_frequency"][disease_class] += 1
        
        # Track average confidence
        if disease_class not in self.stats["average_confidence"]:
            self.stats["average_confidence"][disease_class] = []
        self.stats["average_confidence"][disease_class].append(confidence)
        
        # Track cache performance
        if cache_hit:
            self.stats["cache_hits"] += 1
        else:
            self.stats["cache_misses"] += 1
    
    def log_feedback(self, feedback: UserFeedback):
        """Log user feedback"""
        disease = feedback.disease_class
        if disease not in self.stats["user_ratings"]:
            self.stats["user_ratings"][disease] = []
        self.stats["user_ratings"][disease].append(feedback.rating)
    
    def get_insights(self) -> Dict:
        """Generate insights from analytics"""
        insights = {
            "total_requests": self.stats["total_requests"],
            "cache_hit_rate": (
                self.stats["cache_hits"] / max(self.stats["total_requests"], 1)
            ) * 100,
            "most_common_diseases": sorted(
                self.stats["disease_frequency"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "average_ratings": {}
        }
        
        # Calculate average ratings per disease
        for disease, ratings in self.stats["user_ratings"].items():
            if ratings:
                insights["average_ratings"][disease] = sum(ratings) / len(ratings)
        
        return insights
    
    def save_analytics(self):
        """Save analytics to file"""
        try:
            path = Path(self.analytics_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
            logger.info(f"Analytics saved to {self.analytics_path}")
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")


class RecommendationEngine:
    """
    Advanced recommendation engine with caching, analytics, and multi-language support
    """
    
    def __init__(self, 
                 knowledge_base_path: Optional[str] = None,
                 enable_cache: bool = True,
                 enable_analytics: bool = True,
                 cache_size: int = 1000):
        self.logger = logging.getLogger(__name__)
        self.knowledge_base = {}
        self.feedback_history: List[UserFeedback] = []
        
        # Initialize cache and analytics
        self.cache = RecommendationCache(max_size=cache_size) if enable_cache else None
        self.analytics = RecommendationAnalytics() if enable_analytics else None
        
        # Disease knowledge
        self.disease_categories = self._initialize_disease_categories()
        self.severity_thresholds = {
            "Low": 0.85,
            "Moderate": 0.70,
            "High": 0.50,
            "Critical": 0.0
        }
        
        if knowledge_base_path:
            self._load_knowledge_base(knowledge_base_path)
    
    def _initialize_disease_categories(self) -> Dict:
        """Initialize comprehensive disease categorization"""
        return {
            "fungal": {
                "keywords": ["blight", "rust", "mold", "mildew", "spot", "rot", "scab", "wilt", "anthracnose", "powdery"],
                "description": "Fungal infections that thrive in humid conditions",
                "transmission": "Spores spread by wind, water, and contaminated tools",
                "treatment_type": "fungicide"
            },
            "bacterial": {
                "keywords": ["bacterial", "canker", "fire blight", "soft rot", "wilt"],
                "description": "Bacterial diseases spread through water and wounds",
                "transmission": "Water splash, insects, contaminated tools",
                "treatment_type": "bactericide"
            },
            "viral": {
                "keywords": ["mosaic", "virus", "curl", "yellow", "streak", "mottle"],
                "description": "Viral infections transmitted by vectors",
                "transmission": "Insects (aphids, whiteflies), mechanical contact",
                "treatment_type": "prevention_only"
            },
            "nutritional": {
                "keywords": ["deficiency", "chlorosis", "necrosis"],
                "description": "Nutrient-related disorders",
                "transmission": "Not transmissible",
                "treatment_type": "fertilization"
            },
            "environmental": {
                "keywords": ["sunburn", "frost", "heat", "water stress"],
                "description": "Environmental stress-related issues",
                "transmission": "Not transmissible",
                "treatment_type": "environmental_management"
            }
        }
    
    def _load_knowledge_base(self, path: str):
        """Load and validate knowledge base"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            
            # Convert lists to formatted text
            for disease_class, data in self.knowledge_base.items():
                self.knowledge_base[disease_class] = self._format_knowledge_entry(data)
            
            self.logger.info(f"✅ Loaded {len(self.knowledge_base)} disease entries from knowledge base")
        except FileNotFoundError:
            self.logger.warning(f"⚠️ Knowledge base not found: {path}. Using dynamic generation.")
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON in knowledge base: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error loading knowledge base: {e}")
    
    def _format_knowledge_entry(self, data: Dict) -> Dict:
        """Format knowledge base entry"""
        list_fields = ['symptoms', 'treatment', 'prevention', 'organic_solutions', 
                      'chemical_solutions', 'care_instructions', 'related_diseases']
        
        for field in list_fields:
            if isinstance(data.get(field), list):
                data[field] = list_to_bullets(data[field])
        
        return data
    
    def generate_recommendation(self, 
                               disease_class: str, 
                               confidence: float,
                               plant_type: Optional[str] = None,
                               language: str = "en",
                               user_location: Optional[str] = None) -> Dict:
        """
        Generate comprehensive recommendation with caching and analytics
        
        Args:
            disease_class: Disease classification label
            confidence: Model confidence score
            plant_type: Plant type (optional, extracted from disease_class if not provided)
            language: Response language (en, es, fr, hi, etc.)
            user_location: User location for region-specific advice
        """
        # Check cache first
        if self.cache:
            cached = self.cache.get(disease_class, confidence, language)
            if cached:
                if self.analytics:
                    self.analytics.log_recommendation(disease_class, confidence, cache_hit=True)
                return cached
        
        # Log analytics
        if self.analytics:
            self.analytics.log_recommendation(disease_class, confidence, cache_hit=False)
        
        # Parse disease class
        plant, disease = self._parse_disease_class(disease_class, plant_type)
        
        # Check knowledge base first
        if disease_class in self.knowledge_base:
            recommendation = self._enhance_knowledge_base_entry(
                disease_class, plant, disease, confidence, language, user_location
            )
        else:
            # Generate dynamic recommendation
            recommendation = self._generate_dynamic_recommendation(
                plant, disease, confidence, language, user_location
            )
        
        # Cache the result
        if self.cache:
            self.cache.set(disease_class, confidence, recommendation, language)
        
        return recommendation
    
    def _parse_disease_class(self, disease_class: str, plant_type: Optional[str]) -> Tuple[str, str]:
        """Parse disease class into plant and disease components"""
        parts = disease_class.split("___")
        if len(parts) == 2:
            plant = parts[0].replace("_", " ")
            disease = parts[1].replace("_", " ")
        else:
            plant = plant_type or "Unknown"
            disease = disease_class.replace("_", " ")
        
        return plant, disease
    
    def _enhance_knowledge_base_entry(self, 
                                     disease_class: str,
                                     plant: str,
                                     disease: str,
                                     confidence: float,
                                     language: str,
                                     user_location: Optional[str]) -> Dict:
        """Enhance knowledge base entry with dynamic data"""
        data = self.knowledge_base[disease_class].copy()
        data.update({
            "disease_name": f"{plant} - {disease}",
            "plant_type": plant,
            "disease_type": disease,
            "confidence": round(confidence, 4),
            "source": "knowledge_base",
            "language": language,
            "generated_at": datetime.now().isoformat()
        })
        
        # Add location-specific advice if available
        if user_location:
            data["location_notes"] = self._get_location_specific_advice(disease, user_location)
        
        return data
    
    def _generate_dynamic_recommendation(self,
                                        plant: str,
                                        disease: str,
                                        confidence: float,
                                        language: str,
                                        user_location: Optional[str]) -> Dict:
        """Generate comprehensive dynamic recommendation"""
        disease_lower = disease.lower()
        is_healthy = "healthy" in disease_lower
        
        if is_healthy:
            return self._generate_healthy_recommendation(plant, confidence, language)
        
        # Analyze disease characteristics
        disease_info = self._analyze_disease_comprehensive(disease_lower)
        
        # Build recommendation
        recommendation = Recommendation(
            disease_name=f"{plant} - {disease}",
            plant_type=plant,
            disease_type=disease,
            confidence=round(confidence, 4),
            severity=self._assess_severity(disease_info, confidence),
            description=self._generate_description(plant, disease, disease_info),
            symptoms=self._generate_symptoms(disease_info),
            treatment=self._generate_treatment(disease_info, confidence),
            prevention=self._generate_prevention(disease_info),
            organic_solutions=self._generate_organic_solutions(disease_info),
            chemical_solutions=self._generate_chemical_solutions(disease_info),
            care_instructions=self._generate_care_instructions(plant, disease_info),
            timeline=self._generate_treatment_timeline(disease_info),
            cost_estimate=self._estimate_treatment_cost(disease_info),
            scientific_name=self._get_scientific_name(disease),
            related_diseases=self._get_related_diseases(disease_info),
            references=self._generate_references(disease),
            source="dynamic_generation",
            language=language
        )
        
        result = recommendation.to_dict()
        
        # Add location-specific advice
        if user_location:
            result["location_notes"] = self._get_location_specific_advice(disease, user_location)
        
        return result
    
    def _analyze_disease_comprehensive(self, disease_name: str) -> Dict:
        """Comprehensive disease analysis"""
        info = {
            'category': None,
            'is_fungal': False,
            'is_bacterial': False,
            'is_viral': False,
            'is_nutritional': False,
            'is_environmental': False,
            'affects_leaves': False,
            'affects_fruit': False,
            'affects_stem': False,
            'affects_roots': False,
            'severity_base': 'Moderate',
            'spreads_fast': False,
            'season_dependent': False
        }
        
        # Categorize disease
        for category, data in self.disease_categories.items():
            if any(keyword in disease_name for keyword in data['keywords']):
                info['category'] = category
                info[f'is_{category}'] = True
                break
        
        # Affected parts
        if any(word in disease_name for word in ['leaf', 'leaves', 'foliar']):
            info['affects_leaves'] = True
        if any(word in disease_name for word in ['fruit', 'berry', 'pod']):
            info['affects_fruit'] = True
        if any(word in disease_name for word in ['stem', 'trunk', 'branch']):
            info['affects_stem'] = True
        if any(word in disease_name for word in ['root', 'crown']):
            info['affects_roots'] = True
        
        # Severity indicators
        high_severity = ['late blight', 'bacterial wilt', 'virus', 'fire blight', 'canker', 'severe']
        if any(term in disease_name for term in high_severity):
            info['severity_base'] = 'High'
            info['spreads_fast'] = True
        
        # Early stage diseases
        early_stage = ['early blight', 'early spot', 'initial']
        if any(term in disease_name for term in early_stage):
            info['severity_base'] = 'Low'
        
        return info
    
    def _assess_severity(self, disease_info: Dict, confidence: float) -> str:
        """Assess disease severity based on type and confidence"""
        base_severity = disease_info['severity_base']
        
        # Adjust based on confidence
        if confidence < 0.50:
            return "Critical"
        elif confidence < 0.70:
            return "High" if base_severity != "Low" else "Moderate"
        elif confidence < 0.85:
            return base_severity
        else:
            return "Low" if base_severity == "Low" else "Moderate"
    
    def _generate_symptoms(self, disease_info: Dict) -> List[str]:
        """Generate symptom list based on disease type"""
        symptoms = []
        
        if disease_info['affects_leaves']:
            if disease_info['is_fungal']:
                symptoms.extend([
                    "Brown or yellow spots on leaves",
                    "Leaf curling or distortion",
                    "Powdery or fuzzy growth on leaf surface",
                    "Premature leaf drop"
                ])
            elif disease_info['is_bacterial']:
                symptoms.extend([
                    "Water-soaked lesions on leaves",
                    "Yellow halos around spots",
                    "Leaf wilting despite adequate water",
                    "Bacterial ooze from lesions"
                ])
            elif disease_info['is_viral']:
                symptoms.extend([
                    "Mosaic pattern or mottling on leaves",
                    "Stunted or distorted leaf growth",
                    "Yellow streaking or rings",
                    "Reduced leaf size"
                ])
        
        if disease_info['affects_fruit']:
            symptoms.extend([
                "Fruit discoloration or lesions",
                "Premature fruit drop",
                "Reduced fruit quality and size",
                "Rotting or mummification of fruit"
            ])
        
        if disease_info['affects_stem'] or disease_info['affects_roots']:
            symptoms.extend([
                "Wilting of entire plant",
                "Stem or root discoloration",
                "Reduced plant vigor",
                "Plant death in severe cases"
            ])
        
        return symptoms if symptoms else ["Visible disease symptoms on plant tissue", "Reduced plant health and vigor"]
    
    def _generate_treatment(self, disease_info: Dict, confidence: float) -> List[str]:
        """Generate detailed treatment plan"""
        treatments = []
        
        # Immediate actions
        treatments.append("🚨 IMMEDIATE ACTIONS:")
        treatments.append("Remove and dispose of severely infected plant parts")
        treatments.append("Isolate affected plants to prevent spread")
        treatments.append("Sanitize all tools with 70% alcohol or 10% bleach solution")
        
        # Type-specific treatments
        if disease_info['is_fungal']:
            treatments.append("\n🍄 FUNGAL TREATMENT:")
            treatments.extend([
                "Apply copper-based fungicide every 7-10 days",
                "Use systemic fungicides (e.g., propiconazole, azoxystrobin) for severe cases",
                "Spray early morning or late evening for best absorption",
                "Ensure complete coverage including underside of leaves",
                "Continue treatment for 2-3 weeks after symptoms disappear"
            ])
        
        if disease_info['is_bacterial']:
            treatments.append("\n🦠 BACTERIAL TREATMENT:")
            treatments.extend([
                "Apply copper hydroxide or copper sulfate bactericide",
                "Use streptomycin sulfate (where legally permitted)",
                "Remove entire infected plants in severe cases",
                "Avoid overhead watering to prevent spread",
                "Apply treatments during dry weather for better effectiveness"
            ])
        
        if disease_info['is_viral']:
            treatments.append("\n⚠️ VIRAL DISEASE MANAGEMENT:")
            treatments.extend([
                "NO CURE EXISTS - Remove infected plants immediately",
                "Control insect vectors with appropriate insecticides",
                "Use yellow sticky traps for monitoring aphids/whiteflies",
                "Apply neem oil weekly to deter insect vectors",
                "Do not propagate from infected plants"
            ])
        
        # Confidence-based recommendations
        if confidence < 0.70:
            treatments.append("\n⚠️ LOW CONFIDENCE ALERT:")
            treatments.append("Consider getting professional diagnosis before heavy treatments")
            treatments.append("Start with organic solutions while monitoring closely")
        
        return treatments
    
    def _generate_prevention(self, disease_info: Dict) -> List[str]:
        """Generate comprehensive prevention strategies"""
        prevention = [
            "🛡️ GENERAL PREVENTION:",
            "Plant disease-resistant varieties whenever available",
            "Maintain 3-4 year crop rotation cycle",
            "Ensure proper plant spacing (6-12 inches minimum)",
            "Water at soil level early morning to allow foliage to dry",
            "Remove weeds and plant debris weekly",
            "Sterilize tools between plants with alcohol spray",
            "Use drip irrigation instead of overhead sprinklers"
        ]
        
        if disease_info['is_fungal']:
            prevention.append("\n🍄 FUNGAL PREVENTION:")
            prevention.extend([
                "Apply preventive fungicide sprays before disease season",
                "Improve soil drainage with raised beds or amendments",
                "Mulch with 2-3 inches of organic material to prevent soil splash",
                "Prune for better air circulation and light penetration",
                "Avoid working with plants when wet"
            ])
        
        if disease_info['is_bacterial']:
            prevention.append("\n🦠 BACTERIAL PREVENTION:")
            prevention.extend([
                "Use only certified disease-free seeds and transplants",
                "Avoid wounds and injuries to plants during maintenance",
                "Control leaf-feeding insects that create entry points",
                "Maintain slightly acidic soil pH (6.0-6.5)",
                "Remove and destroy volunteer plants"
            ])
        
        if disease_info['is_viral']:
            prevention.append("\n🐛 VIRAL PREVENTION:")
            prevention.extend([
                "Control aphids, whiteflies, and thrips aggressively",
                "Use reflective plastic mulch to repel aphids",
                "Install insect screening in greenhouses",
                "Remove infected plants within 24 hours of detection",
                "Plant virus-resistant or tolerant varieties",
                "Eliminate weed hosts near crop areas"
            ])
        
        prevention.append("\n🌱 PLANT HEALTH:")
        prevention.extend([
            "Fertilize according to soil test recommendations",
            "Maintain consistent soil moisture (not waterlogged)",
            "Monitor plants 2-3 times per week for early detection",
            "Keep growing area clean and organized"
        ])
        
        return prevention
    
    def _generate_organic_solutions(self, disease_info: Dict) -> List[str]:
        """Generate comprehensive organic treatment options"""
        organic = ["🌿 ORGANIC FUNGICIDES & BACTERICIDES:"]
        
        if disease_info['is_fungal']:
            organic.extend([
                "Neem oil spray: 2 tbsp neem oil + 1 tsp dish soap per gallon water",
                "Baking soda solution: 1 tbsp baking soda + 1 tsp soap + 1 tbsp vegetable oil per gallon",
                "Copper soap fungicide (OMRI certified)",
                "Sulfur dust or wettable sulfur spray",
                "Bacillus subtilis biological fungicide",
                "Compost tea foliar spray (apply every 2 weeks)",
                "Milk spray: 40% milk, 60% water (effective for powdery mildew)"
            ])
        
        if disease_info['is_bacterial']:
            organic.extend([
                "Copper-based organic bactericide (fixed copper)",
                "Bacillus subtilis strain QST 713",
                "Streptomyces lydicus biological control",
                "Garlic extract spray: 10 crushed cloves per quart water",
                "Horseradish infusion as natural antibacterial"
            ])
        
        if disease_info['is_viral']:
            organic.extend([
                "Insecticidal soap for vector control (2-3% concentration)",
                "Neem oil to deter insect vectors (spray weekly)",
                "Pyrethrin-based organic insecticide",
                "Beneficial insects: ladybugs, lacewings, parasitic wasps",
                "Diatomaceous earth barrier around plant base",
                "Kaolin clay spray to repel insects"
            ])
        
        organic.append("\n🌱 PLANT IMMUNITY BOOSTERS:")
        organic.extend([
            "Seaweed extract foliar spray (diluted per label)",
            "Mycorrhizal fungi soil amendment",
            "Compost and worm castings for soil health",
            "Silicon supplement to strengthen cell walls",
            "Fish emulsion for balanced nutrition",
            "Molasses solution for beneficial microbes (1 tbsp per gallon)"
        ])
        
        return organic
    
    def _generate_chemical_solutions(self, disease_info: Dict) -> List[str]:
        """Generate chemical treatment options with safety warnings"""
        chemical = ["⚗️ CHEMICAL TREATMENTS (Use as last resort):"]
        
        chemical.append("\n⚠️ SAFETY FIRST:")
        chemical.extend([
            "Always wear protective equipment (gloves, mask, goggles)",
            "Follow label instructions precisely",
            "Observe pre-harvest intervals (PHI)",
            "Apply during calm weather to prevent drift",
            "Keep away from children and pets"
        ])
        
        if disease_info['is_fungal']:
            chemical.append("\n🍄 SYNTHETIC FUNGICIDES:")
            chemical.extend([
                "Chlorothalonil (Daconil) - broad spectrum, 7-10 day intervals",
                "Propiconazole (Banner, Tilt) - systemic, 14-21 day intervals",
                "Azoxystrobin (Quadris) - systemic, 14-day intervals",
                "Myclobutanil (Eagle) - for powdery mildew and rust",
                "Mancozeb (Dithane) - protective fungicide",
                "Rotate fungicide classes to prevent resistance"
            ])
        
        if disease_info['is_bacterial']:
            chemical.append("\n🦠 BACTERICIDES:")
            chemical.extend([
                "Copper hydroxide (Kocide) - protective bactericide",
                "Streptomycin sulfate (Agrimycin) - where permitted",
                "Oxytetracycline (Mycoshield) - systemic antibiotic",
                "Fixed copper products (various brands)",
                "Use antibiotics responsibly to prevent resistance"
            ])
        
        if disease_info['is_viral']:
            chemical.append("\n🐛 INSECTICIDES (for vector control):")
            chemical.extend([
                "Imidacloprid (Merit) - systemic insecticide",
                "Spinosad (Entrust) - organic option for organic-approved use",
                "Bifenthrin (Talstar) - broad spectrum",
                "Acetamiprid (Assail) - for sucking insects",
                "Pymetrozine (Fulfill) - selective aphid control"
            ])
        
        return chemical
    
    def _generate_care_instructions(self, plant: str, disease_info: Dict) -> List[str]:
        """Generate ongoing care and monitoring instructions"""
        care = [
            f"📋 DAILY CARE FOR {plant.upper()}:",
            f"Inspect your {plant} plants every morning for new symptoms",
            "Check soil moisture 2 inches deep before watering",
            "Look for insect activity on both sides of leaves",
            "Remove any dead or yellowing leaves immediately"
        ]
        
        care.append("\n💧 WATERING PROTOCOL:")
        care.extend([
            "Water deeply 1-2 times per week (adjust for weather)",
            "Ensure soil drains well - no standing water",
            "Use soaker hoses or drip irrigation",
            "Water in early morning (6-8 AM) for best results",
            "Reduce watering frequency during treatment"
        ])
        
        care.append("\n🌱 NUTRITION & SOIL:")
        care.extend([
            "Apply balanced fertilizer (10-10-10) every 4-6 weeks",
            "Add compost or worm castings monthly",
            "Maintain soil pH between 6.0-6.8",
            "Mulch with 2-3 inches organic material",
            "Avoid over-fertilizing which weakens resistance"
        ])
        
        care.append("\n✂️ PRUNING & MAINTENANCE:")
        care.extend([
            "Prune to improve airflow and light penetration",
            "Remove lower leaves touching ground",
            "Disinfect pruning tools after each cut",
            "Dispose of infected material in sealed bags (not compost)",
            "Stake tall plants to prevent soil contact"
        ])
        
        if disease_info['severity_base'] in ['High', 'Critical']:
            care.append("\n⚠️ HIGH SEVERITY MONITORING:")
            care.extend([
                "Check plants 2-3 times daily during treatment",
                "Keep detailed log of symptom progression",
                "Take photos to track changes",
                "Consider removing severely affected plants",
                "Quarantine area for 2-4 weeks after treatment"
            ])
        
        care.append("\n📅 FOLLOW-UP:")
        care.extend([
            "Continue monitoring for 4-6 weeks after symptoms disappear",
            "Reapply treatments as directed on label",
            "Document what works for future reference",
            "Consult extension service if symptoms worsen"
        ])
        
        return care
    
    def _generate_treatment_timeline(self, disease_info: Dict) -> Dict[str, str]:
        """Generate treatment timeline"""
        if disease_info['is_viral']:
            return {
                "Immediate (Day 1)": "Remove infected plants, control vectors",
                "Week 1": "Monitor for spread, intensive vector control",
                "Week 2-4": "Continue monitoring, remove any new infections",
                "Long-term": "Plant resistant varieties, maintain vector control"
            }
        elif disease_info['severity_base'] == 'High':
            return {
                "Immediate (Day 1-2)": "Remove infected parts, apply first treatment",
                "Day 3-7": "Monitor response, second treatment if needed",
                "Week 2": "Continue treatments every 7-10 days",
                "Week 3-4": "Reduce frequency if improving",
                "Week 5-6": "Preventive treatments, close monitoring"
            }
        else:
            return {
                "Week 1": "Initial treatment, remove infected parts",
                "Week 2-3": "Follow-up treatments every 7-10 days",
                "Week 4-6": "Monitor recovery, preventive measures",
                "Ongoing": "Maintain plant health, continue prevention"
            }
    
    def _estimate_treatment_cost(self, disease_info: Dict) -> str:
        """Estimate treatment cost range"""
        if disease_info['is_viral']:
            return "Low to Moderate ($5-30) - Mainly insecticide for vector control"
        elif disease_info['severity_base'] == 'High':
            return "Moderate to High ($30-100+) - Multiple treatments and materials needed"
        elif disease_info['is_fungal']:
            return "Low to Moderate ($10-50) - Fungicides and preventive materials"
        else:
            return "Low ($5-25) - Basic treatments and organic solutions"
    
    def _get_scientific_name(self, disease: str) -> str:
        """Generate or retrieve scientific name"""
        scientific_names = {
            "early blight": "Alternaria solani",
            "late blight": "Phytophthora infestans",
            "powdery mildew": "Erysiphe cichoracearum",
            "bacterial spot": "Xanthomonas spp.",
            "mosaic virus": "Various viral species",
            "rust": "Puccinia spp.",
            "anthracnose": "Colletotrichum spp."
        }
        
        disease_lower = disease.lower()
        for common, scientific in scientific_names.items():
            if common in disease_lower:
                return scientific
        
        return "Consult plant pathologist for identification"
    
    def _get_related_diseases(self, disease_info: Dict) -> List[str]:
        """Get related diseases"""
        if disease_info['is_fungal']:
            return ["Powdery mildew", "Downy mildew", "Leaf spot", "Anthracnose"]
        elif disease_info['is_bacterial']:
            return ["Bacterial wilt", "Bacterial spot", "Soft rot", "Crown gall"]
        elif disease_info['is_viral']:
            return ["Mosaic virus", "Leaf curl virus", "Yellow streak", "Mottle virus"]
        return ["Monitor for other infections"]
    
    def _generate_references(self, disease: str) -> List[str]:
        """Generate reference resources"""
        return [
            f"Local Agricultural Extension Office - disease-specific guidance",
            "USDA Plant Disease Database - www.ars.usda.gov/disease",
            "International Plant Protection Convention (IPPC)",
            "American Phytopathological Society - www.apsnet.org",
            "Local university agricultural programs",
            "Consult certified plant pathologist for severe cases"
        ]
    
    def _get_location_specific_advice(self, disease: str, location: str) -> str:
        """Provide location-specific advice"""
        # This would typically query a database or API
        # Placeholder implementation
        return f"In {location}: Check with local agricultural extension for region-specific treatment recommendations and seasonal disease patterns. Local climate may affect treatment efficacy and disease pressure."
    
    def _generate_healthy_recommendation(self, plant: str, confidence: float, language: str) -> Dict:
        """Generate recommendations for healthy plants"""
        recommendation = Recommendation(
            disease_name=f"Healthy {plant}",
            plant_type=plant,
            disease_type="None - Plant is Healthy ✅",
            confidence=round(confidence, 4),
            severity="None",
            description=f"Great news! Your {plant} plant appears healthy with no visible disease symptoms. Continue your excellent care routine!",
            symptoms=["No disease symptoms detected", "Plant shows healthy growth"],
            treatment=["No treatment needed", "Continue current care routine", "Monitor regularly for changes"],
            prevention=[
                "Maintain consistent watering schedule",
                "Apply balanced fertilizer monthly during growing season",
                "Ensure good air circulation around plants",
                "Remove dead leaves and plant debris weekly",
                "Inspect plants 2-3 times per week",
                "Practice crop rotation annually",
                "Use clean, sterilized tools",
                "Water at soil level in morning"
            ],
            organic_solutions=[
                "Apply compost tea monthly as preventive",
                "Use organic mulch (2-3 inches) to retain moisture",
                "Encourage beneficial insects (ladybugs, lacewings)",
                "Spray diluted seaweed extract for plant vigor",
                "Add worm castings quarterly",
                "Maintain diverse plantings to attract beneficials"
            ],
            chemical_solutions=["Not needed for healthy plants"],
            care_instructions=[
                f"Keep your {plant} thriving with consistent care",
                "Water deeply when top 2 inches of soil are dry",
                "Provide 6-8 hours of appropriate light daily",
                "Fertilize during active growth (spring-summer)",
                "Prune dead or damaged growth promptly",
                "Maintain proper plant spacing",
                "Keep growing area clean and organized",
                "Document your successful care routine"
            ],
            timeline={
                "Daily": "Quick visual inspection",
                "Weekly": "Detailed health check, remove debris",
                "Monthly": "Fertilize and spray preventive treatments",
                "Seasonally": "Major pruning and soil amendment"
            },
            cost_estimate="Minimal ($0-15/month) - Routine maintenance only",
            scientific_name="N/A - Healthy plant",
            related_diseases=["Stay vigilant for early signs of common diseases"],
            references=["Continue learning about preventive plant care"],
            source="healthy_plant",
            language=language
        )
        
        return recommendation.to_dict()
    
    def submit_feedback(self, feedback: UserFeedback):
        """Submit user feedback for recommendation improvement"""
        self.feedback_history.append(feedback)
        
        if self.analytics:
            self.analytics.log_feedback(feedback)
        
        # If rating is low, consider updating knowledge base
        if feedback.rating <= 2:
            self.logger.warning(
                f"Low rating ({feedback.rating}) for {feedback.disease_class}: {feedback.user_comment}"
            )
    
    def get_popular_diseases(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most frequently requested diseases"""
        if not self.analytics:
            return []
        
        return sorted(
            self.analytics.stats["disease_frequency"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
    
    def get_analytics_report(self) -> Dict:
        """Get comprehensive analytics report"""
        if not self.analytics:
            return {"error": "Analytics not enabled"}
        
        return self.analytics.get_insights()
    
    def add_to_knowledge_base(self, disease_class: str, recommendation: Dict):
        """Add verified recommendation to knowledge base"""
        self.knowledge_base[disease_class] = self._format_knowledge_entry(recommendation)
        self.logger.info(f"Added {disease_class} to knowledge base")
    
    def save_knowledge_base(self, path: str):
        """Save knowledge base to JSON file"""
        try:
            kb_path = Path(path)
            kb_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Saved {len(self.knowledge_base)} entries to {path}")
        except Exception as e:
            self.logger.error(f"❌ Error saving knowledge base: {e}")
    
    def save_analytics(self):
        """Save analytics data"""
        if self.analytics:
            self.analytics.save_analytics()
    
    def clear_cache(self):
        """Clear recommendation cache"""
        if self.cache:
            self.cache.clear()


# Optional: Advanced GPT-based recommendation engine with RAG
class GPTRecommendationEngine(RecommendationEngine):
    """
    Advanced recommendation engine using OpenAI GPT with RAG
    Features: Context-aware recommendations, conversational follow-ups
    Requires: pip install openai langchain chromadb
    """
    
    def __init__(self, 
                 api_key: str,
                 knowledge_base_path: Optional[str] = None,
                 model: str = "gpt-4o-mini",
                 enable_cache: bool = True,
                 enable_analytics: bool = True):
        super().__init__(knowledge_base_path, enable_cache, enable_analytics)
        
        try:
            import openai
            from langchain.embeddings import OpenAIEmbeddings
            from langchain.vectorstores import Chroma
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
            self.use_gpt = True
            
            # Initialize RAG components
            self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
            self.vector_store = None
            self._initialize_vector_store()
            
            self.logger.info(f"✅ GPT-based engine initialized with model: {model}")
        except ImportError as e:
            self.logger.error(f"❌ Required libraries not installed: {e}")
            self.logger.info("Install with: pip install openai langchain chromadb")
            self.use_gpt = False
        except Exception as e:
            self.logger.error(f"❌ GPT initialization failed: {e}")
            self.use_gpt = False
    
    def _initialize_vector_store(self):
        """Initialize vector store for RAG"""
        try:
            from langchain.docstore.document import Document
            from langchain.vectorstores import Chroma
            
            # Convert knowledge base to documents
            documents = []
            for disease_class, data in self.knowledge_base.items():
                content = f"""
Disease: {data.get('disease_name', disease_class)}
Severity: {data.get('severity', 'Unknown')}
Description: {data.get('description', '')}
Treatment: {data.get('treatment', '')}
Prevention: {data.get('prevention', '')}
Organic Solutions: {data.get('organic_solutions', '')}
                """.strip()
                
                doc = Document(
                    page_content=content,
                    metadata={"disease_class": disease_class}
                )
                documents.append(doc)
            
            if documents:
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    collection_name="plant_diseases"
                )
                self.logger.info(f"✅ Vector store initialized with {len(documents)} documents")
        except Exception as e:
            self.logger.warning(f"⚠️ Vector store initialization failed: {e}")
    
    def _retrieve_relevant_context(self, disease: str, k: int = 3) -> str:
        """Retrieve relevant context using RAG"""
        if not self.vector_store:
            return ""
        
        try:
            docs = self.vector_store.similarity_search(disease, k=k)
            context = "\n\n".join([doc.page_content for doc in docs])
            return f"Similar disease information:\n{context}"
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {e}")
            return ""
    
    def _generate_dynamic_recommendation(self,
                                        plant: str,
                                        disease: str,
                                        confidence: float,
                                        language: str,
                                        user_location: Optional[str]) -> Dict:
        """Generate recommendations using GPT with RAG"""
        if not self.use_gpt:
            return super()._generate_dynamic_recommendation(
                plant, disease, confidence, language, user_location
            )
        
        try:
            # Retrieve relevant context
            context = self._retrieve_relevant_context(f"{plant} {disease}")
            
            # Build comprehensive prompt
            prompt = f"""You are an expert plant pathologist. Provide detailed, actionable recommendations for:

Plant: {plant}
Disease: {disease}
Confidence: {confidence:.2%}
Location: {user_location or 'Not specified'}
Language: {language}

{context}

Provide comprehensive recommendations in JSON format with these exact fields:
{{
  "severity": "Low/Moderate/High/Critical",
  "description": "2-3 detailed sentences about the disease",
  "symptoms": ["symptom1", "symptom2", ...] (4-6 items),
  "treatment": ["step1", "step2", ...] (6-8 detailed steps),
  "prevention": ["measure1", "measure2", ...] (6-8 prevention measures),
  "organic_solutions": ["solution1", "solution2", ...] (5-7 organic options),
  "chemical_solutions": ["chemical1", "chemical2", ...] (4-6 chemical options with safety notes),
  "care_instructions": ["instruction1", "instruction2", ...] (5-6 care tips),
  "timeline": {{"phase1": "description", "phase2": "description", ...}},
  "cost_estimate": "cost range with explanation",
  "scientific_name": "scientific name of pathogen",
  "related_diseases": ["disease1", "disease2", ...],
  "references": ["reference1", "reference2", ...]
}}

Be specific, practical, and science-based. Include actionable steps with timing and measurements."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert plant pathologist providing accurate, detailed, and actionable advice."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            gpt_data = json.loads(response.choices[0].message.content)
            
            # Build complete recommendation
            recommendation = {
                "disease_name": f"{plant} - {disease}",
                "plant_type": plant,
                "disease_type": disease,
                "confidence": round(confidence, 4),
                "source": "gpt_rag_generated",
                "language": language,
                "generated_at": datetime.now().isoformat(),
                **gpt_data
            }
            
            return recommendation
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {e}")
            return super()._generate_dynamic_recommendation(
                plant, disease, confidence, language, user_location
            )
        except Exception as e:
            self.logger.error(f"❌ GPT generation failed: {e}")
            return super()._generate_dynamic_recommendation(
                plant, disease, confidence, language, user_location
            )
    
    def ask_followup_question(self, disease_class: str, question: str) -> str:
        """Answer follow-up questions about a disease"""
        if not self.use_gpt:
            return "GPT not available. Please ask specific questions."
        
        try:
            context = self._retrieve_relevant_context(f"{disease_class} {question}")
            
            prompt = f"""Based on the following plant disease information, answer this question:

Disease: {disease_class}
Question: {question}

Context:
{context}

Provide a clear, concise, and practical answer."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful plant disease expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Follow-up question failed: {e}")
            return f"Sorry, I couldn't process that question. Error: {str(e)}"


# Export classes
__all__ = [
    'Recommendation',
    'UserFeedback',
    'RecommendationEngine',
    'GPTRecommendationEngine',
    'RecommendationCache',
    'RecommendationAnalytics'
]


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Initialize engine
    engine = RecommendationEngine(
        knowledge_base_path="models/disease_knowledge_base.json",
        enable_cache=True,
        enable_analytics=True
    )
    
    # Generate recommendation
    rec = engine.generate_recommendation(
        disease_class="Tomato___Late_blight",
        confidence=0.92,
        user_location="California, USA"
    )
    
    print(json.dumps(rec, indent=2))
    
    # Submit feedback
    feedback = UserFeedback(
        disease_class="Tomato___Late_blight",
        recommendation_id="rec_123",
        rating=5,
        was_helpful=True,
        user_comment="Very helpful recommendations!"
    )
    engine.submit_feedback(feedback)
    
    # Get analytics
    print("\nAnalytics Report:")
    print(json.dumps(engine.get_analytics_report(), indent=2))
    
    # Save data
    engine.save_knowledge_base("models/disease_knowledge_base_updated.json")
    engine.save_analytics()
