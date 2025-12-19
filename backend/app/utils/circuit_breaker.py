"""
Circuit breaker pattern for external API resilience.

Prevents cascading failures when external services are down by:
- Tracking failure counts per service
- Opening circuit after threshold failures
- Auto-recovering after cooldown period
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, TypeVar, Any
from functools import wraps

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _half_open_calls: int = field(default=0, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
        return self._state
    
    @property
    def is_available(self) -> bool:
        state = self.state
        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls
        return False
    
    async def record_success(self) -> None:
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._half_open_calls += 1
                if self._half_open_calls >= self.half_open_max_calls:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0
    
    async def record_failure(self) -> None:
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
    
    def reset(self) -> None:
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0


class CircuitOpenError(Exception):
    def __init__(self, circuit_name: str):
        self.circuit_name = circuit_name
        super().__init__(f"Circuit '{circuit_name}' is open")


_circuits: dict[str, CircuitBreaker] = {}


def get_circuit(name: str, **kwargs) -> CircuitBreaker:
    if name not in _circuits:
        _circuits[name] = CircuitBreaker(name=name, **kwargs)
    return _circuits[name]


def with_circuit_breaker(
    circuit_name: str,
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
):
    """
    Decorator to wrap async functions with circuit breaker protection.
    
    Usage:
        @with_circuit_breaker("openai_api")
        async def call_openai(prompt: str) -> str:
            ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            circuit = get_circuit(
                circuit_name,
                failure_threshold=failure_threshold,
                recovery_timeout=recovery_timeout,
            )
            
            if not circuit.is_available:
                raise CircuitOpenError(circuit_name)
            
            try:
                result = await func(*args, **kwargs)
                await circuit.record_success()
                return result
            except Exception as e:
                await circuit.record_failure()
                raise
        
        return wrapper
    return decorator


def get_all_circuit_states() -> dict[str, dict]:
    return {
        name: {
            "state": circuit.state.value,
            "failure_count": circuit._failure_count,
            "is_available": circuit.is_available,
        }
        for name, circuit in _circuits.items()
    }
