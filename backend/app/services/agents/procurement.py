from app.services.agents.specialist import SpecialistAgent
class ProcurementAgent(SpecialistAgent):
 name='procurement'; display_name_ar='المشتريات والعقود'; description='المشتريات والعقود'; dependencies=('evidence',); instructions='حدد احتياجات RFP/SOW/SLA والتزامات المورد ونقاط القبول. لا تخترع شروط عقد.'; schema={"status":"success|partial","headline":"","summary":"","findings":[],"data":{'contracting_questions': [], 'vendor_obligations_to_verify': [], 'acceptance_criteria_needed': []},"confidence":0.0,"warnings":[],"sources":[]}
