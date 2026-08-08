from app.services.agents.specialist import SpecialistAgent
class TimelineAgent(SpecialistAgent):
 name='timeline'; display_name_ar='الوقت والتنفيذ'; description='الوقت والتنفيذ'; dependencies=('evidence',); instructions='استخدم التواريخ والاعتماديات المذكورة فقط. حدد مخاطر الجدول والمراحل المطلوبة.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'deadlines': [], 'dependencies': [], 'schedule_risks': [], 'milestones': []},"confidence":0.0,"warnings":[],"sources":[]}
