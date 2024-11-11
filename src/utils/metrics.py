"""
Metrics collection and reporting utilities.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import time
from contextlib import contextmanager
from .logger import logger
from .config import get_settings

class MetricsCollector:
    """Collects and reports application metrics."""
    
    def __init__(self):
        self.settings = get_settings()
        self.metrics: Dict[str, Any] = {
            'counters': {},
            'timers': {},
            'gauges': {}
        }
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict] = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name
            value: Value to increment by
            tags: Optional metric tags
        """
        if name not in self.metrics['counters']:
            self.metrics['counters'][name] = 0
        self.metrics['counters'][name] += value
        
        if self.settings.ENABLE_METRICS:
            self._report_metric('counter', name, value, tags)
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict] = None):
        """
        Set a gauge metric.
        
        Args:
            name: Metric name
            value: Gauge value
            tags: Optional metric tags
        """
        self.metrics['gauges'][name] = value
        
        if self.settings.ENABLE_METRICS:
            self._report_metric('gauge', name, value, tags)
    
    @contextmanager
    def timer(self, name: str, tags: Optional[Dict] = None):
        """
        Context manager for timing operations.
        
        Args:
            name: Timer name
            tags: Optional metric tags
        """
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if name not in self.metrics['timers']:
                self.metrics['timers'][name] = []
            self.metrics['timers'][name].append(duration)
            
            if self.settings.ENABLE_METRICS:
                self._report_metric('timing', name, duration, tags)
    
    def _report_metric(
        self,
        metric_type: str,
        name: str,
        value: float,
        tags: Optional[Dict] = None
    ):
        """
        Report a metric to the backend.
        
        Args:
            metric_type: Type of metric
            name: Metric name
            value: Metric value
            tags: Optional metric tags
        """
        metric_data = {
            'type': metric_type,
            'name': name,
            'value': value,
            'timestamp': datetime.utcnow().isoformat(),
            'tags': tags or {}
        }
        
        try:
            # Here you would typically send to your metrics backend
            # For now, we'll just log it
            logger.debug(f"Metric: {metric_data}")
        except Exception as e:
            logger.error(f"Failed to report metric: {e}")

# Global metrics collector instance
metrics = MetricsCollector()