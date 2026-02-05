"""
AI Code Review + Auto-Fix - 100% Local
مراجعة وإصلاح تلقائي للكود
"""
import os
import re
import ast
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class CodeIssue:
    """مشكلة في الكود"""
    def __init__(
        self,
        issue_type: str,
        severity: str,
        message: str,
        file_path: str,
        line_number: int,
        code_snippet: str,
        suggestion: Optional[str] = None
    ):
        self.issue_type = issue_type
        self.severity = severity  # "low", "medium", "high", "critical"
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.code_snippet = code_snippet
        self.suggestion = suggestion
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet[:200],
            "suggestion": self.suggestion,
            "timestamp": self.timestamp.isoformat()
        }


class AICodeReviewer:
    """
    مراجع الكود بالذكاء الاصطناعي
    يكشف security smells, bugs, performance issues
    ويقترح patches جاهزة
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.security_patterns = {
            "sql_injection": {
                "pattern": r"execute\(.*\+.*\)|query\(.*\+.*\)",
                "severity": "critical",
                "message": "Possible SQL injection vulnerability",
                "suggestion": "Use parameterized queries"
            },
            "hardcoded_secret": {
                "pattern": r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
                "severity": "critical",
                "message": "Hardcoded secret detected",
                "suggestion": "Use environment variables or secret management"
            },
            "eval_usage": {
                "pattern": r"\beval\s*\(",
                "severity": "critical",
                "message": "Use of eval() is dangerous",
                "suggestion": "Avoid eval(), use safer alternatives"
            },
            "shell_injection": {
                "pattern": r"os\.system\(|subprocess\.call\(.*shell=True",
                "severity": "high",
                "message": "Possible shell injection",
                "suggestion": "Use subprocess with list arguments"
            },
            "weak_crypto": {
                "pattern": r"md5\(|sha1\(|DES\(",
                "severity": "high",
                "message": "Weak cryptographic algorithm",
                "suggestion": "Use stronger algorithms (SHA-256, AES)"
            }
        }
        
        self.performance_patterns = {
            "n_plus_one": {
                "pattern": r"for\s+\w+\s+in\s+\w+:\s*\n\s*.*\.query\(|.*\.get\(",
                "severity": "medium",
                "message": "Possible N+1 query problem",
                "suggestion": "Use eager loading or batch queries"
            },
            "inefficient_loop": {
                "pattern": r"for\s+\w+\s+in\s+range\(len\(.*\)\):",
                "severity": "low",
                "message": "Inefficient loop pattern",
                "suggestion": "Use enumerate() or direct iteration"
            }
        }
    
    def review_file(self, file_path: str) -> Dict[str, Any]:
        """مراجعة ملف"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # مراجعة security issues
            security_issues = self._check_security(content, file_path, lines)
            issues.extend(security_issues)
            
            # مراجعة performance issues
            performance_issues = self._check_performance(content, file_path, lines)
            issues.extend(performance_issues)
            
            # مراجعة code quality
            quality_issues = self._check_quality(content, file_path, lines)
            issues.extend(quality_issues)
            
            return {
                "file_path": file_path,
                "total_issues": len(issues),
                "issues": [issue.to_dict() for issue in issues],
                "severity_breakdown": self._count_by_severity(issues),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            log_warning(f"Error reviewing file {file_path}: {e}")
            return {"error": str(e)}
    
    def _check_security(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """فحص security issues"""
        issues = []
        
        for pattern_name, pattern_info in self.security_patterns.items():
            pattern = re.compile(pattern_info["pattern"], re.MULTILINE)
            matches = pattern.finditer(content)
            
            for match in matches:
                # العثور على رقم السطر
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issue = CodeIssue(
                    issue_type=f"security_{pattern_name}",
                    severity=pattern_info["severity"],
                    message=pattern_info["message"],
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content.strip(),
                    suggestion=pattern_info.get("suggestion")
                )
                issues.append(issue)
        
        return issues
    
    def _check_performance(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """فحص performance issues"""
        issues = []
        
        for pattern_name, pattern_info in self.performance_patterns.items():
            pattern = re.compile(pattern_info["pattern"], re.MULTILINE)
            matches = pattern.finditer(content)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                
                issue = CodeIssue(
                    issue_type=f"performance_{pattern_name}",
                    severity=pattern_info["severity"],
                    message=pattern_info["message"],
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line_content.strip(),
                    suggestion=pattern_info.get("suggestion")
                )
                issues.append(issue)
        
        return issues
    
    def _check_quality(self, content: str, file_path: str, lines: List[str]) -> List[CodeIssue]:
        """فحص code quality"""
        issues = []
        
        # فحص imports غير المستخدمة (مثال بسيط)
        try:
            tree = ast.parse(content)
            imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
            # يمكن إضافة منطق أكثر تعقيداً هنا
        except:
            pass
        
        # فحص functions طويلة جداً
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    if func_lines > 100:
                        issues.append(CodeIssue(
                            issue_type="quality_long_function",
                            severity="medium",
                            message=f"Function '{node.name}' is too long ({func_lines} lines)",
                            file_path=file_path,
                            line_number=node.lineno,
                            code_snippet=lines[node.lineno - 1] if node.lineno <= len(lines) else "",
                            suggestion="Break down into smaller functions"
                        ))
        except:
            pass
        
        return issues
    
    def _count_by_severity(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """حساب عدد المشاكل حسب الخطورة"""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts
    
    def generate_patch(self, issue: CodeIssue) -> Optional[str]:
        """توليد patch لإصلاح المشكلة"""
        if issue.issue_type == "security_hardcoded_secret":
            # مثال: استبدال hardcoded secret بـ environment variable
            old_code = issue.code_snippet
            if "=" in old_code:
                var_name = old_code.split("=")[0].strip()
                new_code = f"{var_name} = os.getenv('{var_name.upper()}', '')"
                return new_code
        
        elif issue.issue_type == "security_sql_injection":
            # مثال: تحويل إلى parameterized query
            return "# TODO: Convert to parameterized query\n# Use: cursor.execute('SELECT * FROM table WHERE id = ?', (id,))"
        
        elif issue.issue_type == "performance_inefficient_loop":
            # مثال: تحسين loop
            old_code = issue.code_snippet
            if "range(len(" in old_code:
                return old_code.replace("range(len(", "enumerate(")
        
        return None
    
    def auto_fix_file(self, file_path: str, apply_fixes: bool = False) -> Dict[str, Any]:
        """إصلاح تلقائي للملف"""
        review_result = self.review_file(file_path)
        
        if "error" in review_result:
            return review_result
        
        fixes = []
        
        for issue_dict in review_result["issues"]:
            issue = CodeIssue(
                issue_type=issue_dict["type"],
                severity=issue_dict["severity"],
                message=issue_dict["message"],
                file_path=issue_dict["file_path"],
                line_number=issue_dict["line_number"],
                code_snippet=issue_dict["code_snippet"],
                suggestion=issue_dict.get("suggestion")
            )
            
            patch = self.generate_patch(issue)
            if patch:
                fixes.append({
                    "issue": issue_dict,
                    "patch": patch,
                    "line_number": issue.line_number
                })
        
        if apply_fixes and fixes:
            # تطبيق الإصلاحات (للأمان، نحفظ backup أولاً)
            try:
                backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(file_path, 'r') as f:
                    content = f.read()
                
                with open(backup_path, 'w') as f:
                    f.write(content)
                
                # تطبيق الإصلاحات (مثال بسيط)
                lines = content.split('\n')
                for fix in fixes:
                    line_idx = fix["line_number"] - 1
                    if line_idx < len(lines):
                        lines[line_idx] = fix["patch"]
                
                with open(file_path, 'w') as f:
                    f.write('\n'.join(lines))
                
                log_info(f"Applied {len(fixes)} fixes to {file_path}, backup: {backup_path}")
            except Exception as e:
                log_warning(f"Error applying fixes: {e}")
                return {"error": str(e)}
        
        return {
            "file_path": file_path,
            "total_issues": review_result["total_issues"],
            "fixes_available": len(fixes),
            "fixes": fixes,
            "applied": apply_fixes,
            "backup_path": f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}" if apply_fixes else None
        }


# Global instance
_code_reviewer: Optional[AICodeReviewer] = None


def get_code_reviewer() -> AICodeReviewer:
    """الحصول على مثيل مراجع الكود"""
    global _code_reviewer
    if _code_reviewer is None:
        _code_reviewer = AICodeReviewer()
    return _code_reviewer

