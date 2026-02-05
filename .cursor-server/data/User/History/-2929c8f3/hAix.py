"""
Base utilities for security scanners - أدوات أساسية للماسحات الأمنية
"""
from typing import Dict, Any
from app.utils.path_resolver import resolve_path as _resolve_path

# Use the shared path resolver
resolve_path = _resolve_path

def calculate_risk_score(summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate overall risk score from summary
    Returns: score, level (critical/high/medium/low), and breakdown
    """
    critical = summary.get("critical", 0) or summary.get("critical_severity", 0)
    high = summary.get("high", 0) or summary.get("high_risk", 0) or summary.get("high_severity", 0)
    medium = summary.get("medium", 0) or summary.get("medium_risk", 0) or summary.get("medium_severity", 0)
    low = summary.get("low", 0) or summary.get("low_risk", 0) or summary.get("low_severity", 0)
    
    # Calculate weighted score: critical*10 + high*5 + medium*3 + low*1
    score = critical * 10 + high * 5 + medium * 3 + low * 1
    
    # Determine risk level
    if score >= 50 or critical > 0:
        level = "critical"
        emoji = "🔴"
    elif score >= 20 or high >= 3:
        level = "high"
        emoji = "🟠"
    elif score >= 10 or medium >= 5:
        level = "medium"
        emoji = "🟡"
    else:
        level = "low"
        emoji = "🟢"
    
    return {
        "score": score,
        "level": level,
        "emoji": emoji,
        "breakdown": {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        }
    }

# Common secret patterns
SECRET_PATTERNS = {
    "api_key": [
        r'api[_-]?key["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'apikey["\s:=]+([a-zA-Z0-9_\-]{20,})',
    ],
    "password": [
        r'password["\s:=]+([^\s"\']{8,})',
        r'passwd["\s:=]+([^\s"\']{8,})',
        r'pwd["\s:=]+([^\s"\']{8,})',
    ],
    "token": [
        r'token["\s:=]+([a-zA-Z0-9_\-]{20,})',
        r'bearer["\s]+([a-zA-Z0-9_\-\.]{20,})',
    ],
    "secret": [
        r'secret["\s:=]+([a-zA-Z0-9_\-]{16,})',
        r'secret[_-]key["\s:=]+([a-zA-Z0-9_\-]{16,})',
    ],
    "aws_key": [
        r'AWS[_\s]?ACCESS[_\s]?KEY[_\s]?ID["\s:=]+([A-Z0-9]{20})',
        r'AWS[_\s]?SECRET[_\s]?ACCESS[_\s]?KEY["\s:=]+([A-Za-z0-9/+=]{40})',
    ],
    "private_key": [
        r'-----BEGIN[_\s]?(RSA|EC|DSA|OPENSSH)[_\s]?PRIVATE[_\s]?KEY-----',
    ],
}

