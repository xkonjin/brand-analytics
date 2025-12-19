"""
Simple application metrics collection.

Tracks:
- Request counts by endpoint
- Analysis counts by status  
- API call latencies
- Error counts by type
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Optional


@dataclass
class MetricsCollector:
    _request_counts: dict = field(default_factory=lambda: defaultdict(int))
    _analysis_counts: dict = field(default_factory=lambda: defaultdict(int))
    _api_latencies: dict = field(default_factory=lambda: defaultdict(list))
    _error_counts: dict = field(default_factory=lambda: defaultdict(int))
    _lock: Lock = field(default_factory=Lock)
    
    def record_request(self, endpoint: str, method: str = "GET") -> None:
        with self._lock:
            self._request_counts[f"{method}:{endpoint}"] += 1
    
    def record_analysis(self, status: str) -> None:
        with self._lock:
            self._analysis_counts[status] += 1
    
    def record_api_latency(self, service: str, latency_ms: float) -> None:
        with self._lock:
            latencies = self._api_latencies[service]
            latencies.append(latency_ms)
            if len(latencies) > 1000:
                self._api_latencies[service] = latencies[-500:]
    
    def record_error(self, error_type: str) -> None:
        with self._lock:
            self._error_counts[error_type] += 1
    
    def get_metrics(self) -> dict:
        with self._lock:
            api_stats = {}
            for service, latencies in self._api_latencies.items():
                if latencies:
                    api_stats[service] = {
                        "count": len(latencies),
                        "avg_ms": sum(latencies) / len(latencies),
                        "max_ms": max(latencies),
                        "min_ms": min(latencies),
                    }
            
            return {
                "requests": dict(self._request_counts),
                "analyses": dict(self._analysis_counts),
                "api_latencies": api_stats,
                "errors": dict(self._error_counts),
            }
    
    def reset(self) -> None:
        with self._lock:
            self._request_counts.clear()
            self._analysis_counts.clear()
            self._api_latencies.clear()
            self._error_counts.clear()


_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


class ApiTimer:
    """Context manager to time API calls."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time: float = 0
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        get_metrics_collector().record_api_latency(self.service_name, elapsed_ms)
        if exc_type is not None:
            get_metrics_collector().record_error(f"{self.service_name}:{exc_type.__name__}")
        return False


class AsyncApiTimer:
    """Async context manager to time API calls."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time: float = 0
    
    async def __aenter__(self):
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000
        get_metrics_collector().record_api_latency(self.service_name, elapsed_ms)
        if exc_type is not None:
            get_metrics_collector().record_error(f"{self.service_name}:{exc_type.__name__}")
        return False
