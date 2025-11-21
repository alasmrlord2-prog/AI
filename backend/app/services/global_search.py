"""
Global Search Engine - 100% Local
محرك بحث شامل - محلي بالكامل
"""
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning


class SearchResult:
    """نتيجة بحث"""
    def __init__(
        self,
        source: str,
        content: str,
        path: Optional[str] = None,
        line_number: Optional[int] = None,
        score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source = source  # "logs", "files", "database", "workflows", etc.
        self.content = content
        self.path = path
        self.line_number = line_number
        self.score = score
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "content": self.content[:500],  # أول 500 حرف
            "path": self.path,
            "line_number": self.line_number,
            "score": self.score,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class GlobalSearchEngine:
    """
    محرك بحث شامل - محلي 100%
    يبحث في: Logs, Files, Databases, Workflows, Errors, Docs, Toolkits
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.search_paths = {
            "logs": ["/var/log", "./logs", "/app/logs"],
            "files": ["./app", "./backend"],
            "workflows": ["./workflows", "./app/workflows"],
            "docs": ["./docs", "./README.md"],
            "configs": ["./app/config", "./config"]
        }
        self.index_cache: Dict[str, List[str]] = {}
        self.max_results = 100
    
    def search(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        بحث شامل
        
        Args:
            query: نص البحث
            sources: مصادر البحث (logs, files, workflows, etc.) - None = كل المصادر
            max_results: الحد الأقصى للنتائج
        """
        if not sources:
            sources = ["logs", "files", "workflows", "docs", "configs"]
        
        max_results = max_results or self.max_results
        
        all_results = []
        
        # البحث في كل مصدر
        if "logs" in sources:
            all_results.extend(self._search_logs(query))
        
        if "files" in sources:
            all_results.extend(self._search_files(query))
        
        if "workflows" in sources:
            all_results.extend(self._search_workflows(query))
        
        if "docs" in sources:
            all_results.extend(self._search_docs(query))
        
        if "configs" in sources:
            all_results.extend(self._search_configs(query))
        
        # ترتيب حسب score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # تقليل النتائج
        results = all_results[:max_results]
        
        return {
            "query": query,
            "total_results": len(all_results),
            "returned_results": len(results),
            "results": [r.to_dict() for r in results],
            "sources_searched": sources,
            "timestamp": datetime.now().isoformat()
        }
    
    def _search_logs(self, query: str) -> List[SearchResult]:
        """البحث في الـlogs"""
        results = []
        query_lower = query.lower()
        pattern = re.compile(query_lower, re.IGNORECASE)
        
        for log_dir in self.search_paths["logs"]:
            if not os.path.exists(log_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        if file.endswith(('.log', '.txt')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    for line_num, line in enumerate(f, 1):
                                        if pattern.search(line):
                                            results.append(SearchResult(
                                                source="logs",
                                                content=line.strip(),
                                                path=file_path,
                                                line_number=line_num,
                                                score=self._calculate_score(query, line)
                                            ))
                            except Exception as e:
                                log_warning(f"Error reading log file {file_path}: {e}")
            except Exception as e:
                log_warning(f"Error searching logs in {log_dir}: {e}")
        
        return results
    
    def _search_files(self, query: str) -> List[SearchResult]:
        """البحث في الملفات"""
        results = []
        query_lower = query.lower()
        pattern = re.compile(query_lower, re.IGNORECASE)
        
        # أنواع الملفات للبحث
        file_extensions = ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt']
        
        for search_dir in self.search_paths["files"]:
            if not os.path.exists(search_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(search_dir):
                    # تخطي بعض المجلدات
                    dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.git']]
                    
                    for file in files:
                        if any(file.endswith(ext) for ext in file_extensions):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    for line_num, line in enumerate(f, 1):
                                        if pattern.search(line):
                                            results.append(SearchResult(
                                                source="files",
                                                content=line.strip(),
                                                path=file_path,
                                                line_number=line_num,
                                                score=self._calculate_score(query, line)
                                            ))
                            except Exception as e:
                                log_warning(f"Error reading file {file_path}: {e}")
            except Exception as e:
                log_warning(f"Error searching files in {search_dir}: {e}")
        
        return results
    
    def _search_workflows(self, query: str) -> List[SearchResult]:
        """البحث في الـworkflows"""
        results = []
        query_lower = query.lower()
        
        for workflow_dir in self.search_paths["workflows"]:
            if not os.path.exists(workflow_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(workflow_dir):
                    for file in files:
                        if file.endswith(('.yaml', '.yml', '.json')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if query_lower in content.lower():
                                        # البحث عن السطر المحدد
                                        for line_num, line in enumerate(content.split('\n'), 1):
                                            if query_lower in line.lower():
                                                results.append(SearchResult(
                                                    source="workflows",
                                                    content=line.strip(),
                                                    path=file_path,
                                                    line_number=line_num,
                                                    score=self._calculate_score(query, line)
                                                ))
                            except Exception as e:
                                log_warning(f"Error reading workflow {file_path}: {e}")
            except Exception as e:
                log_warning(f"Error searching workflows in {workflow_dir}: {e}")
        
        return results
    
    def _search_docs(self, query: str) -> List[SearchResult]:
        """البحث في التوثيق"""
        results = []
        query_lower = query.lower()
        
        for doc_path in self.search_paths["docs"]:
            if os.path.isfile(doc_path):
                # ملف واحد
                try:
                    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if query_lower in line.lower():
                                results.append(SearchResult(
                                    source="docs",
                                    content=line.strip(),
                                    path=doc_path,
                                    line_number=line_num,
                                    score=self._calculate_score(query, line)
                                ))
                except Exception as e:
                    log_warning(f"Error reading doc {doc_path}: {e}")
            elif os.path.isdir(doc_path):
                # مجلد
                try:
                    for root, dirs, files in os.walk(doc_path):
                        for file in files:
                            if file.endswith(('.md', '.txt', '.rst')):
                                file_path = os.path.join(root, file)
                                try:
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        for line_num, line in enumerate(f, 1):
                                            if query_lower in line.lower():
                                                results.append(SearchResult(
                                                    source="docs",
                                                    content=line.strip(),
                                                    path=file_path,
                                                    line_number=line_num,
                                                    score=self._calculate_score(query, line)
                                                ))
                                except Exception as e:
                                    log_warning(f"Error reading doc {file_path}: {e}")
                except Exception as e:
                    log_warning(f"Error searching docs in {doc_path}: {e}")
        
        return results
    
    def _search_configs(self, query: str) -> List[SearchResult]:
        """البحث في ملفات الـconfig"""
        results = []
        query_lower = query.lower()
        
        for config_dir in self.search_paths["configs"]:
            if not os.path.exists(config_dir):
                continue
            
            try:
                for root, dirs, files in os.walk(config_dir):
                    for file in files:
                        if file.endswith(('.yaml', '.yml', '.json', '.env', '.conf', '.ini')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    for line_num, line in enumerate(f, 1):
                                        if query_lower in line.lower():
                                            results.append(SearchResult(
                                                source="configs",
                                                content=line.strip(),
                                                path=file_path,
                                                line_number=line_num,
                                                score=self._calculate_score(query, line)
                                            ))
                            except Exception as e:
                                log_warning(f"Error reading config {file_path}: {e}")
            except Exception as e:
                log_warning(f"Error searching configs in {config_dir}: {e}")
        
        return results
    
    def _calculate_score(self, query: str, content: str) -> float:
        """حساب score للنتيجة"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        score = 0.0
        
        # تطابق كامل
        if query_lower == content_lower.strip():
            score += 10.0
        
        # تطابق في بداية السطر
        if content_lower.startswith(query_lower):
            score += 5.0
        
        # عدد مرات ظهور الكلمة
        count = content_lower.count(query_lower)
        score += count * 1.0
        
        # تطابق كلمات متعددة
        query_words = query_lower.split()
        matched_words = sum(1 for word in query_words if word in content_lower)
        if len(query_words) > 0:
            score += (matched_words / len(query_words)) * 3.0
        
        return score
    
    def add_search_path(self, source: str, path: str):
        """إضافة مسار بحث جديد"""
        if source not in self.search_paths:
            self.search_paths[source] = []
        
        if path not in self.search_paths[source]:
            self.search_paths[source].append(path)
            log_info(f"Added search path: {source} -> {path}")


# Global instance
_global_search: Optional[GlobalSearchEngine] = None


def get_global_search() -> GlobalSearchEngine:
    """الحصول على مثيل محرك البحث"""
    global _global_search
    if _global_search is None:
        _global_search = GlobalSearchEngine()
    return _global_search

