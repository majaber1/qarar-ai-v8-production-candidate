from app.services.agents.specialist import SpecialistAgent
class StrategyAgent(SpecialistAgent):
 name='strategy'; display_name_ar='الأثر الاستراتيجي'; description='الأثر الاستراتيجي'; dependencies=('evidence',); instructions='قيّم الأهداف المذكورة فقط والقيمة طويلة المدى والمفاضلات. لا تخترع استراتيجية.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'objectives': [], 'alignment': [], 'tradeoffs': []},"confidence":0.0,"warnings":[],"sources":[]}
