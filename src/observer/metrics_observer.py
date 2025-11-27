"""Concrete observer implementations for metrics, audit, and performance monitoring."""

from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
import json

from .monitoring import Observer


class MetricsObserver(Observer):
    """Observer for collecting system metrics."""
    
    def __init__(self):
        self.metrics = {
            'requests_total': 0,
            'requests_completed': 0,
            'requests_failed': 0,
            'total_processing_time_ms': 0.0,
            'avg_processing_time_ms': 0.0,
            'diagnoses_made': 0,
            'urgency_levels': defaultdict(int)
        }
        self.start_time = datetime.now()
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """Update metrics based on event."""
        if event_type == 'request_started':
            self.metrics['requests_total'] += 1
        
        elif event_type == 'request_completed':
            self.metrics['requests_completed'] += 1
            
            # Update processing time
            if 'processing_time_ms' in data:
                self.metrics['total_processing_time_ms'] += data['processing_time_ms']
                self.metrics['avg_processing_time_ms'] = (
                    self.metrics['total_processing_time_ms'] / 
                    self.metrics['requests_completed']
                )
            
            # Update diagnosis count
            if 'diagnoses_count' in data:
                self.metrics['diagnoses_made'] += data['diagnoses_count']
            
            # Update urgency distribution
            if 'urgency_level' in data:
                self.metrics['urgency_levels'][data['urgency_level']] += 1
        
        elif event_type == 'request_failed':
            self.metrics['requests_failed'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            **self.metrics,
            'uptime_seconds': uptime,
            'requests_per_second': self.metrics['requests_total'] / uptime if uptime > 0 else 0,
            'success_rate': (
                self.metrics['requests_completed'] / self.metrics['requests_total']
                if self.metrics['requests_total'] > 0 else 0
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            'requests_total': 0,
            'requests_completed': 0,
            'requests_failed': 0,
            'total_processing_time_ms': 0.0,
            'avg_processing_time_ms': 0.0,
            'diagnoses_made': 0,
            'urgency_levels': defaultdict(int)
        }
        self.start_time = datetime.now()


class AuditObserver(Observer):
    """Observer for audit trail and compliance logging."""
    
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self.audit_entries: List[Dict[str, Any]] = []
        self.max_entries = 10000  # Keep last 10k entries in memory
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """Log audit event."""
        audit_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data
        }
        
        # Add to in-memory log
        self.audit_entries.append(audit_entry)
        
        # Trim if exceeds max
        if len(self.audit_entries) > self.max_entries:
            self.audit_entries = self.audit_entries[-self.max_entries:]
        
        # Write to file
        self._write_to_file(audit_entry)
    
    def _write_to_file(self, entry: Dict[str, Any]):
        """Write audit entry to file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Error writing to audit log: {e}")
    
    def get_audit_trail(
        self,
        start_time: datetime = None,
        end_time: datetime = None,
        event_type: str = None
    ) -> List[Dict[str, Any]]:
        """Get filtered audit trail."""
        filtered_entries = self.audit_entries
        
        if event_type:
            filtered_entries = [
                e for e in filtered_entries if e['event_type'] == event_type
            ]
        
        if start_time:
            filtered_entries = [
                e for e in filtered_entries
                if datetime.fromisoformat(e['timestamp']) >= start_time
            ]
        
        if end_time:
            filtered_entries = [
                e for e in filtered_entries
                if datetime.fromisoformat(e['timestamp']) <= end_time
            ]
        
        return filtered_entries
    
    def get_patient_audit_trail(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for specific patient."""
        return [
            e for e in self.audit_entries
            if e.get('data', {}).get('patient_id') == patient_id
        ]


class PerformanceObserver(Observer):
    """Observer for performance monitoring and alerting."""
    
    def __init__(self, alert_threshold_ms: float = 5000):
        self.alert_threshold_ms = alert_threshold_ms
        self.slow_requests: List[Dict[str, Any]] = []
        self.performance_data: List[Dict[str, Any]] = []
        self.alerts: List[str] = []
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """Monitor performance and generate alerts."""
        if event_type == 'request_completed':
            processing_time = data.get('processing_time_ms', 0)
            
            # Record performance data
            perf_entry = {
                'timestamp': datetime.now().isoformat(),
                'request_id': data.get('request_id'),
                'processing_time_ms': processing_time,
                'patient_id': data.get('patient_id')
            }
            self.performance_data.append(perf_entry)
            
            # Check for slow requests
            if processing_time > self.alert_threshold_ms:
                self.slow_requests.append(perf_entry)
                alert_msg = (
                    f"Slow request detected: {data.get('request_id')} "
                    f"took {processing_time:.2f}ms (threshold: {self.alert_threshold_ms}ms)"
                )
                self.alerts.append(alert_msg)
                print(f"PERFORMANCE ALERT: {alert_msg}")
        
        elif event_type == 'request_failed':
            alert_msg = (
                f"Request failed: {data.get('request_id')} "
                f"for patient {data.get('patient_id')} - {data.get('error')}"
            )
            self.alerts.append(alert_msg)
            print(f"FAILURE ALERT: {alert_msg}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics."""
        if not self.performance_data:
            return {
                'total_requests': 0,
                'avg_processing_time_ms': 0,
                'min_processing_time_ms': 0,
                'max_processing_time_ms': 0,
                'slow_requests_count': 0
            }
        
        processing_times = [d['processing_time_ms'] for d in self.performance_data]
        
        return {
            'total_requests': len(self.performance_data),
            'avg_processing_time_ms': sum(processing_times) / len(processing_times),
            'min_processing_time_ms': min(processing_times),
            'max_processing_time_ms': max(processing_times),
            'slow_requests_count': len(self.slow_requests),
            'alerts_count': len(self.alerts)
        }
    
    def get_recent_alerts(self, count: int = 10) -> List[str]:
        """Get most recent alerts."""
        return self.alerts[-count:]
    
    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()


class DataQualityObserver(Observer):
    """Observer for monitoring data quality issues."""
    
    def __init__(self):
        self.quality_issues: List[Dict[str, Any]] = []
        self.quality_stats = {
            'total_records': 0,
            'validation_failures': 0,
            'low_quality_data': 0,
            'missing_data': 0
        }
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """Monitor data quality."""
        if event_type == 'request_started':
            self.quality_stats['total_records'] += 1
        
        elif event_type == 'request_failed':
            error = data.get('error', '')
            if 'validation' in error.lower():
                self.quality_stats['validation_failures'] += 1
                self.quality_issues.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'validation_failure',
                    'request_id': data.get('request_id'),
                    'error': error
                })
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get data quality report."""
        total = self.quality_stats['total_records']
        if total == 0:
            quality_score = 1.0
        else:
            issues = (
                self.quality_stats['validation_failures'] +
                self.quality_stats['low_quality_data'] +
                self.quality_stats['missing_data']
            )
            quality_score = 1.0 - (issues / total)
        
        return {
            **self.quality_stats,
            'quality_score': quality_score,
            'recent_issues': self.quality_issues[-10:]
        }
