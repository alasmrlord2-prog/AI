"""
AI Explainer - 100% Local (Ollama)
مفسر AI محلي باستخدام Ollama
"""
import os
from typing import Dict, Any, Optional
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning

# محاولة استيراد Ollama (اختياري)
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    log_warning("ollama package not available, using rule-based explanations")


class AIExplainer:
    """
    مفسر AI - محلي 100% باستخدام Ollama
    يشرح التهديدات والحوادث الأمنية
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.use_ollama = OLLAMA_AVAILABLE and self.settings.SECURITY_AI_USE_OLLAMA
        self.ollama_url = self.settings.OLLAMA_URL
        
        # التحقق من OFFLINE_MODE
        if self.settings.OFFLINE_MODE:
            # التأكد من أن Ollama محلي
            if "localhost" not in self.ollama_url and "127.0.0.1" not in self.ollama_url:
                log_warning("OFFLINE_MODE enabled but Ollama URL is not local, disabling AI explainer")
                self.use_ollama = False
    
    def _check_offline_mode(self):
        """التحقق من OFFLINE_MODE"""
        if self.settings.OFFLINE_MODE:
            # منع أي اتصال خارجي
            if not self.ollama_url.startswith(("http://localhost", "http://127.0.0.1")):
                raise RuntimeError("OFFLINE_MODE is enabled. External connections are blocked.")
    
    def explain_threat(self, threat: Dict[str, Any]) -> Dict[str, Any]:
        """شرح تهديد محدد"""
        if not self.use_ollama:
            return self._explain_rule_based(threat)
        
        try:
            self._check_offline_mode()
            
            # بناء prompt
            prompt = self._build_threat_prompt(threat)
            
            # استدعاء Ollama
            response = ollama.chat(
                model="llama3.2",  # أو أي موديل محلي آخر
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert. Explain security threats clearly and suggest solutions."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            explanation = response["message"]["content"]
            
            return {
                "explanation": explanation,
                "method": "ollama",
                "model": "llama3.2"
            }
        except Exception as e:
            log_warning(f"Error using Ollama for explanation: {e}, falling back to rule-based")
            return self._explain_rule_based(threat)
    
    def explain_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """شرح حادث أمني"""
        if not self.use_ollama:
            return self._explain_incident_rule_based(incident)
        
        try:
            self._check_offline_mode()
            
            prompt = self._build_incident_prompt(incident)
            
            response = ollama.chat(
                model="llama3.2",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity incident responder. Analyze incidents and provide actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            explanation = response["message"]["content"]
            
            return {
                "explanation": explanation,
                "method": "ollama",
                "model": "llama3.2"
            }
        except Exception as e:
            log_warning(f"Error using Ollama for incident explanation: {e}, falling back to rule-based")
            return self._explain_incident_rule_based(incident)
    
    def _build_threat_prompt(self, threat: Dict[str, Any]) -> str:
        """بناء prompt للتهديد"""
        threat_type = threat.get("pattern", "unknown")
        severity = threat.get("severity", "unknown")
        description = threat.get("description", "")
        log_line = threat.get("log_line", "")[:200]
        
        return f"""Analyze this security threat:

Type: {threat_type}
Severity: {severity}
Description: {description}
Log line: {log_line}

Please explain:
1. What this threat means
2. Why it's dangerous
3. What the attacker might be trying to do
4. Recommended immediate actions
5. Long-term prevention strategies

Keep the explanation clear and actionable."""
    
    def _build_incident_prompt(self, incident: Dict[str, Any]) -> str:
        """بناء prompt للحادث"""
        incident_type = incident.get("type", "unknown")
        severity = incident.get("severity", "unknown")
        details = incident.get("details", {})
        
        return f"""Analyze this security incident:

Type: {incident_type}
Severity: {severity}
Details: {details}

Please provide:
1. Root cause analysis
2. Impact assessment
3. Immediate response steps
4. Containment strategies
5. Recovery procedures
6. Prevention measures

Be specific and actionable."""
    
    def _explain_rule_based(self, threat: Dict[str, Any]) -> Dict[str, Any]:
        """شرح قائم على القواعد (بدون AI)"""
        threat_type = threat.get("pattern", "unknown")
        severity = threat.get("severity", "unknown")
        
        explanations = {
            "sql_injection": {
                "what": "SQL injection is an attack where malicious SQL code is inserted into input fields",
                "why_dangerous": "Can allow attackers to read, modify, or delete database data",
                "action": "Sanitize all user inputs and use parameterized queries"
            },
            "xss_attack": {
                "what": "Cross-Site Scripting (XSS) injects malicious scripts into web pages",
                "why_dangerous": "Can steal user sessions, cookies, or redirect users to malicious sites",
                "action": "Escape all user-generated content and use Content Security Policy"
            },
            "command_injection": {
                "what": "Command injection executes arbitrary system commands",
                "why_dangerous": "Can give attackers full system control",
                "action": "Never execute user input as commands, use whitelisting"
            },
            "brute_force": {
                "what": "Brute force attack attempts multiple login credentials",
                "why_dangerous": "Can compromise user accounts",
                "action": "Implement rate limiting, CAPTCHA, and account lockout"
            }
        }
        
        explanation = explanations.get(threat_type, {
            "what": f"Security threat detected: {threat_type}",
            "why_dangerous": f"Severity level: {severity}",
            "action": "Review logs and investigate further"
        })
        
        return {
            "explanation": f"""
**What happened:**
{explanation['what']}

**Why it's dangerous:**
{explanation['why_dangerous']}

**Recommended action:**
{explanation['action']}
            """.strip(),
            "method": "rule_based"
        }
    
    def _explain_incident_rule_based(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """شرح حادث قائم على القواعد"""
        incident_type = incident.get("type", "unknown")
        severity = incident.get("severity", "unknown")
        
        return {
            "explanation": f"""
**Incident Type:** {incident_type}
**Severity:** {severity}

**Immediate Actions:**
1. Isolate affected systems
2. Preserve logs and evidence
3. Assess the scope of impact
4. Notify security team

**Investigation Steps:**
1. Review all related logs
2. Check system configurations
3. Identify attack vectors
4. Document findings

**Prevention:**
1. Update security policies
2. Patch vulnerabilities
3. Enhance monitoring
4. Conduct security training
            """.strip(),
            "method": "rule_based"
        }


# Global instance
_ai_explainer: Optional[AIExplainer] = None


def get_ai_explainer() -> AIExplainer:
    """الحصول على مثيل المفسر AI"""
    global _ai_explainer
    if _ai_explainer is None:
        _ai_explainer = AIExplainer()
    return _ai_explainer

