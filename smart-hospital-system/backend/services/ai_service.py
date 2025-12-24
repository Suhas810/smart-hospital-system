from abc import ABC, abstractmethod

class AIService(ABC):
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the AI service is available."""
        pass

    @abstractmethod
    def analyze_risk(self, patient_data: dict) -> dict:
        """
        Analyze patient data to determine risk level.
        Returns metadata including:
        - risk_level (High/Medium/Low)
        - explanation (str)
        - recommended_action (str)
        """
        pass
