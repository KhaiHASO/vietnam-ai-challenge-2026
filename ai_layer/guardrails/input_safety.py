from typing import Dict, Any, Tuple
import re

class InputSafetyGuardrail:
    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
        # Keywords indicating system prompt overrides or jailbreaks
        self.injection_keywords = [
            r"ignore previous instructions",
            r"bỏ qua các lệnh trước",
            r"system override",
            r"quyền root",
            r"root admin",
            r"you must now act as",
            r"hãy đóng vai là",
            r"delete all data",
            r"xóa toàn bộ cơ sở dữ liệu",
            r"sudo ",
            r"rm -rf"
        ]
        
    def evaluate_safety(self, text: str) -> Tuple[bool, float, str]:
        """
        Evaluates input safety.
        Returns:
            is_blocked (bool): True if blocked.
            risk_score (float): Score between 0.0 and 1.0.
            reason (str): Description of the violation.
        """
        risk_score = 0.0
        violations = []
        
        # Check injection keywords
        lower_text = text.lower()
        matched_keywords = []
        for kw in self.injection_keywords:
            if re.search(kw, lower_text):
                matched_keywords.append(kw)
                risk_score += 0.35
                
        if matched_keywords:
            violations.append(f"Prompt injection patterns detected: {', '.join(matched_keywords)}")
            
        # SQL Injection checks
        sql_keywords = [r"union select", r"drop table", r"insert into", r" or 1=1"]
        matched_sql = []
        for sql in sql_keywords:
            if re.search(sql, lower_text):
                matched_sql.append(sql)
                risk_score += 0.25
                
        if matched_sql:
            violations.append(f"SQL Injection patterns detected: {', '.join(matched_sql)}")
            
        # Limit risk score to 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine block status
        is_blocked = risk_score >= self.threshold
        reason = "; ".join(violations) if is_blocked else "Safe"
        
        return is_blocked, risk_score, reason
