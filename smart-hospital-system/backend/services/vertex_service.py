import os
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting, Part
from backend.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

class VertexGemmaService(AIService):
    def __init__(self, project_id=None, location="us-central1"):
        self.enabled = False
        try:
            project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
            
            if project_id:
                vertexai.init(project=project_id, location=location)
                self.model = GenerativeModel("gemini-1.5-flash-001")
                self.enabled = True
                logger.info(f"Vertex AI Service Initialized for project {project_id}")
            else:
                logger.warning("No GOOGLE_CLOUD_PROJECT found. Vertex AI disabled.")
                
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            self.enabled = False

    def health_check(self) -> bool:
        return self.enabled

    # ... [Existing analyze_risk method] ...
    def analyze_risk(self, patient_data: dict) -> dict:
        if not self.enabled:
            return self._mock_analysis(patient_data)

        prompt = f"""
        You are an expert emergency triage AI. Analyze this patient data to assess clinical risk.
        
        Patient Profile:
        - Age: {patient_data.get('age')}
        - Reported Severity (1-10): {patient_data.get('severity')}
        - Name: {patient_data.get('name')}
        - Symptoms/Notes: {patient_data.get('symptoms', 'None provided')}
        
        Task:
        1. Determine Clinical Risk Level (Low/Medium/High/Critical).
        2. Assign a specific Risk Score (1-100).
        3. Provide a concise "Clinical Explanation" for a doctor (max 20 words).
        4. Recommend immediate resource allocation (e.g., General Ward, ICU, Home Isolation).
        
        Output EXCLUSIVELY in valid JSON format with these keys:
        {{
            "risk_level": "High/Medium/Low",
            "risk_score": 85,
            "explanation": "...",
            "recommendation": "..."
        }}
        Do not include markdown formatting or prologue.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response.text)
        except Exception as e:
            logger.error(f"Vertex AI Inference failed: {e}")
            return self._mock_analysis(patient_data)

    def analyze_prescription(self, image_data: bytes, mime_type: str) -> str:
        if not self.enabled:
            return "## AI Analysis (Simulation)\n- **Medicine**: Paracetamol 500mg\n- **Dosage**: Twice daily\n- **Notes**: Take after food."

        prompt = """
        You are an expert pharmacist AI. Analyze this image of a prescription or medicine.
        Identify:
        1. Medicine Names
        2. Dosage Instructions
        3. Warnings/Side Effects
        
        Format the output in clean Markdown.
        """
        try:
            image_part = Part.from_data(data=image_data, mime_type=mime_type)
            response = self.model.generate_content([prompt, image_part])
            return response.text
        except Exception as e:
            logger.error(f"Vertex AI Vision failed: {e}")
            return "Failed to analyze image. Please ensure it is a clear medical image."

    def chat(self, message: str) -> str:
        if not self.enabled:
            return "I am a simulated AI assistant. (Vertex AI not configured). How can I help?"

        prompt = f"""
        You are a helpful, empathetic medical assistant for 'SmartHospital'.
        User Query: {message}
        
        Guidelines:
        1. Keep answers short (max 3 sentences).
        2. Be professional but friendly.
        3. If symptoms are severe (chest pain, breathing issues), advise immediate hospital visit.
        4. Do NOT give specific medical prescriptions. reliable general advice only.
        
        Response:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.replace("```", "").strip()
        except Exception as e:
            logger.error(f"Vertex AI Chat failed: {e}")
            return "I'm having trouble connecting to the hospital brain. Please try again."

    def _parse_response(self, text):
        import json
        import re
        
        cleaned_text = re.sub(r"```json\s*|\s*```", "", text).strip()
        
        try:
            data = json.loads(cleaned_text)
            return data
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse AI JSON: {text}")
            text_lower = text.lower()
            risk = "medium"
            if "high" in text_lower or "critical" in text_lower: risk = "High"
            elif "low" in text_lower: risk = "Low"
            
            return {
                "risk_level": risk.capitalize(),
                "explanation": text[:100] + "...",
                "recommendation": "Review by Doctor (Parse Error)"
            }

    def _mock_analysis(self, patient_data: dict) -> dict:
        severity = int(patient_data.get("severity", 0))
        if severity >= 8:
            return {
                "risk_level": "High",
                "explanation": "Severity score indicates critical condition (Simulation).",
                "recommendation": "Immediate ICU Admission"
            }
        elif severity >= 5:
              return {
                "risk_level": "Medium",
                "explanation": "Patient requires monitoring (Simulation).",
                "recommendation": "General Ward"
            }
        return {
            "risk_level": "Low",
            "explanation": "Vitals stable (Simulation).",
            "recommendation": "Home Isolation"
        }
