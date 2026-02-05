"""
Anomaly Detection Engine - 100% Local ML
محرك كشف الشذوذات باستخدام ML محلي
"""
import os
import pickle
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
from app.core.config import get_settings
from app.utils.logger import log_info, log_warning

# محاولة استيراد numpy (اختياري)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None
    log_warning("numpy not available, using rule-based detection only")

# محاولة استيراد scikit-learn (اختياري)
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    log_warning("scikit-learn not available, using rule-based detection only")


class AnomalyDetector:
    """
    محرك كشف الشذوذات - محلي 100%
    يستخدم ML محلي (Isolation Forest) + Rules بسيطة
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.models_dir = Path("models/security_ai")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Baseline metrics
        self.baseline: Dict[str, Any] = {}
        self.metrics_history: deque = deque(maxlen=10000)
        
        # ML Models (محلية)
        self.isolation_forest: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.use_ml = SKLEARN_AVAILABLE and self.settings.SECURITY_AI_ENABLED
        
        # Rules-based detection
        self.rule_thresholds = {
            "failed_logins_per_minute": 5,
            "error_rate_threshold": 0.1,  # 10% errors
            "request_rate_spike": 3.0,  # 3x normal rate
            "unusual_user_activity": True,
        }
        
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """تحميل أو تدريب نموذج ML"""
        if not self.use_ml:
            return
        
        model_path = self.models_dir / "isolation_forest.pkl"
        scaler_path = self.models_dir / "scaler.pkl"
        
        try:
            if model_path.exists() and scaler_path.exists():
                with open(model_path, 'rb') as f:
                    self.isolation_forest = pickle.load(f)
                with open(scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                log_info("Loaded existing ML models")
            else:
                # إنشاء نموذج جديد
                self.isolation_forest = IsolationForest(
                    contamination=0.1,  # 10% anomalies expected
                    random_state=42,
                    n_estimators=100
                )
                self.scaler = StandardScaler()
                log_info("Created new ML models")
        except Exception as e:
            log_warning(f"Error loading ML models: {e}, using rule-based only")
            self.use_ml = False
    
    def _save_model(self):
        """حفظ النموذج"""
        if not self.use_ml or not self.isolation_forest:
            return
        
        try:
            model_path = self.models_dir / "isolation_forest.pkl"
            scaler_path = self.models_dir / "scaler.pkl"
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.isolation_forest, f)
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            log_info("Saved ML models")
        except Exception as e:
            log_warning(f"Error saving ML models: {e}")
    
    def extract_features(self, events: List[Dict[str, Any]]):
        """استخراج features من الأحداث"""
        if not NUMPY_AVAILABLE:
            # Fallback to simple list if numpy not available
            return []
        if not events:
            return np.array([]).reshape(0, 10)
        
        if not NUMPY_AVAILABLE:
            return []
        
        features = []
        
        # حساب features
        event_counts = defaultdict(int)
        error_count = 0
        ip_counts = defaultdict(int)
        user_counts = defaultdict(int)
        time_diffs = []
        
        prev_time = None
        for event in events[-100:]:  # آخر 100 حدث
            event_type = event.get("type", "unknown")
            event_counts[event_type] += 1
            
            if "error" in event_type.lower() or event.get("level") == "error":
                error_count += 1
            
            ip = event.get("ip") or event.get("source_ip")
            if ip:
                ip_counts[ip] += 1
            
            user = event.get("user") or event.get("username")
            if user:
                user_counts[user] += 1
            
            timestamp = event.get("timestamp")
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    else:
                        event_time = timestamp
                    
                    if prev_time:
                        diff = (event_time - prev_time).total_seconds()
                        time_diffs.append(diff)
                    prev_time = event_time
                except:
                    pass
        
        # بناء feature vector
        feature_vector = [
            len(events),  # total events
            error_count,  # error count
            len(ip_counts),  # unique IPs
            max(ip_counts.values()) if ip_counts else 0,  # max requests from one IP
            len(user_counts),  # unique users
            max(user_counts.values()) if user_counts else 0,  # max actions from one user
            np.mean(time_diffs) if time_diffs else 0,  # avg time between events
            np.std(time_diffs) if time_diffs else 0,  # std of time between events
            event_counts.get("login_failed", 0),  # failed logins
            event_counts.get("error", 0),  # errors
        ]
        
        return np.array([feature_vector])
    
    def detect_with_ml(self, events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """كشف الشذوذات باستخدام ML"""
        if not self.use_ml or not self.isolation_forest:
            return None
        
        try:
            features = self.extract_features(events)
            if features.size == 0:
                return None
            
            # تطبيع البيانات
            if self.scaler:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features
            
            # التنبؤ
            prediction = self.isolation_forest.predict(features_scaled)
            anomaly_score = self.isolation_forest.score_samples(features_scaled)[0]
            
            if prediction[0] == -1:  # Anomaly detected
                return {
                    "type": "ml_anomaly",
                    "score": float(anomaly_score),
                    "severity": "high" if anomaly_score < -0.5 else "medium",
                    "method": "isolation_forest"
                }
        except Exception as e:
            log_warning(f"Error in ML detection: {e}")
        
        return None
    
    def detect_with_rules(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """كشف الشذوذات باستخدام Rules"""
        anomalies = []
        
        if not events:
            return anomalies
        
        # حساب metrics
        event_counts = defaultdict(int)
        error_count = 0
        failed_logins = 0
        ip_counts = defaultdict(int)
        user_counts = defaultdict(int)
        
        recent_events = events[-100:]  # آخر 100 حدث
        time_window = timedelta(minutes=5)
        
        cutoff_time = datetime.now() - time_window
        recent_in_window = [
            e for e in recent_events
            if self._parse_timestamp(e.get("timestamp")) > cutoff_time
        ]
        
        for event in recent_in_window:
            event_type = event.get("type", "unknown")
            event_counts[event_type] += 1
            
            if "error" in event_type.lower() or event.get("level") == "error":
                error_count += 1
            
            if "login_failed" in event_type or "authentication_failed" in event_type:
                failed_logins += 1
            
            ip = event.get("ip") or event.get("source_ip")
            if ip:
                ip_counts[ip] += 1
            
            user = event.get("user") or event.get("username")
            if user:
                user_counts[user] += 1
        
        # Rule 1: Failed logins
        if failed_logins > self.rule_thresholds["failed_logins_per_minute"]:
            anomalies.append({
                "type": "brute_force",
                "severity": "high",
                "count": failed_logins,
                "threshold": self.rule_thresholds["failed_logins_per_minute"],
                "description": f"Too many failed login attempts: {failed_logins}"
            })
        
        # Rule 2: Error rate
        if len(recent_in_window) > 0:
            error_rate = error_count / len(recent_in_window)
            if error_rate > self.rule_thresholds["error_rate_threshold"]:
                anomalies.append({
                    "type": "high_error_rate",
                    "severity": "medium",
                    "error_rate": error_rate,
                    "threshold": self.rule_thresholds["error_rate_threshold"],
                    "description": f"High error rate: {error_rate:.2%}"
                })
        
        # Rule 3: Single IP spike
        if ip_counts:
            max_ip_requests = max(ip_counts.values())
            avg_ip_requests = sum(ip_counts.values()) / len(ip_counts)
            if avg_ip_requests > 0 and max_ip_requests > avg_ip_requests * self.rule_thresholds["request_rate_spike"]:
                suspicious_ip = max(ip_counts, key=ip_counts.get)
                anomalies.append({
                    "type": "ip_spike",
                    "severity": "medium",
                    "ip": suspicious_ip,
                    "requests": max_ip_requests,
                    "avg": avg_ip_requests,
                    "description": f"Suspicious activity from IP: {suspicious_ip}"
                })
        
        # Rule 4: Unusual user activity
        if user_counts:
            max_user_actions = max(user_counts.values())
            if max_user_actions > 50:  # أكثر من 50 إجراء في 5 دقائق
                suspicious_user = max(user_counts, key=user_counts.get)
                anomalies.append({
                    "type": "unusual_user_activity",
                    "severity": "medium",
                    "user": suspicious_user,
                    "actions": max_user_actions,
                    "description": f"Unusual activity from user: {suspicious_user}"
                })
        
        return anomalies
    
    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """تحليل timestamp"""
        if timestamp is None:
            return datetime.now()
        
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                return datetime.now()
        
        return datetime.now()
    
    def detect(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """كشف الشذوذات (ML + Rules)"""
        results = {
            "anomalies": [],
            "ml_anomaly": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Rules-based detection
        rule_anomalies = self.detect_with_rules(events)
        results["anomalies"].extend(rule_anomalies)
        
        # ML-based detection
        if self.use_ml:
            ml_anomaly = self.detect_with_ml(events)
            if ml_anomaly:
                results["ml_anomaly"] = ml_anomaly
                results["anomalies"].append(ml_anomaly)
        
        # تحديث baseline
        self._update_baseline(events)
        
        # تدريب النموذج تدريجياً
        if self.use_ml and len(self.metrics_history) > 100:
            self._retrain_model()
        
        return results
    
    def _update_baseline(self, events: List[Dict[str, Any]]):
        """تحديث baseline"""
        if not events:
            return
        
        # حساب metrics
        event_counts = defaultdict(int)
        for event in events[-1000:]:  # آخر 1000 حدث
            event_type = event.get("type", "unknown")
            event_counts[event_type] += 1
        
        # تحديث baseline
        for event_type, count in event_counts.items():
            if event_type not in self.baseline:
                self.baseline[event_type] = {"count": 0, "samples": 0}
            
            self.baseline[event_type]["count"] += count
            self.baseline[event_type]["samples"] += 1
        
        # حفظ في التاريخ
        self.metrics_history.append({
            "timestamp": datetime.now().isoformat(),
            "events": len(events),
            "event_counts": dict(event_counts)
        })
    
    def _retrain_model(self):
        """إعادة تدريب النموذج"""
        if not self.use_ml or len(self.metrics_history) < 100:
            return
        
        try:
            # استخراج features من التاريخ
            features_list = []
            for i in range(0, len(self.metrics_history), 10):  # كل 10 عينات
                sample = self.metrics_history[i]
                events = [{"type": k, "timestamp": sample["timestamp"]} 
                         for k, v in sample.get("event_counts", {}).items() 
                         for _ in range(v)]
                features = self.extract_features(events)
                if features.size > 0:
                    features_list.append(features[0])
            
            if len(features_list) < 50:
                return
            
            X = np.array(features_list)
            
            # تطبيع
            if self.scaler:
                X_scaled = self.scaler.fit_transform(X)
            else:
                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)
            
            # تدريب
            self.isolation_forest.fit(X_scaled)
            
            # حفظ
            self._save_model()
            
            log_info("ML model retrained")
        except Exception as e:
            log_warning(f"Error retraining model: {e}")


# Global instance
_anomaly_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    """الحصول على مثيل كاشف الشذوذات"""
    global _anomaly_detector
    if _anomaly_detector is None:
        _anomaly_detector = AnomalyDetector()
    return _anomaly_detector

