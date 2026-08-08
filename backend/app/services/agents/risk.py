from app.services.agents.specialist import SpecialistAgent
class RiskAgent(SpecialistAgent):
 name='risk'; display_name_ar='المخاطر'; description='المخاطر'; dependencies=('evidence',); instructions='حدد أهم المخاطر والسبب والاحتمال والأثر والإجراء المقترح. لا تختَر القرار النهائي.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'risk_level': 'low|medium|high|critical', 'top_risks': [], 'mitigations': []},"confidence":0.0,"warnings":[],"sources":[]}
