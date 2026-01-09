"""
Simplified GPT Recommendation Engine - No LangChain Required
"""

import json
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class SimpleGPTEngine:
    """Simple GPT engine without RAG/vector store complexity"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.use_gpt = False
        self.model = model
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.use_gpt = True
            logger.info(f"✅ Simple GPT engine initialized with {model}")
        except ImportError:
            logger.error("❌ OpenAI library not installed: pip install openai")
        except Exception as e:
            logger.error(f"❌ GPT initialization failed: {e}")
    
    def generate_recommendation(self, plant: str, disease: str, confidence: float) -> Dict:
        """Generate recommendation using GPT"""
        if not self.use_gpt:
            raise Exception("GPT not available")
        
        try:
            prompt = f"""You are an expert plant pathologist. Provide detailed recommendations for:

Plant: {plant}
Disease: {disease}
Confidence: {confidence:.2%}

Return ONLY valid JSON with these fields:
{{
  "severity": "Low/Moderate/High/Critical",
  "description": "2-3 sentences about the disease",
  "symptoms": ["symptom1", "symptom2", "symptom3", "symptom4"],
  "treatment": ["step1", "step2", "step3", "step4", "step5", "step6"],
  "prevention": ["measure1", "measure2", "measure3", "measure4", "measure5"],
  "organic_solutions": ["solution1", "solution2", "solution3", "solution4"],
  "chemical_solutions": ["chemical1", "chemical2", "chemical3"],
  "care_instructions": ["instruction1", "instruction2", "instruction3", "instruction4"],
  "timeline": {{"Week 1": "actions", "Week 2-3": "actions", "Week 4+": "actions"}},
  "cost_estimate": "cost range with explanation",
  "scientific_name": "pathogen scientific name"
}}

Be specific and practical."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert plant pathologist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            gpt_data = json.loads(response.choices[0].message.content)
            
            return {
                "disease_name": f"{plant} - {disease}",
                "plant_type": plant,
                "disease_type": disease,
                "confidence": round(confidence, 4),
                "source": "gpt_generated",
                "generated_at": datetime.now().isoformat(),
                **gpt_data
            }
            
        except Exception as e:
            logger.error(f"❌ GPT generation failed: {e}")
            raise
