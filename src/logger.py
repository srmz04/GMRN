import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    
    def __init__(self, name: str, log_file: Optional[str] = None, level: str = "INFO", console_output: bool = True):
        self.name = name
        self.level = self.LEVELS.get(level.upper(), 20)
        self.console_output = console_output
        
        if log_file:
            self.log_path = Path(log_file)
        else:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d")
            self.log_path = log_dir / f"{name}_{timestamp}.jsonl"
        
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _format_entry(self, level: str, message: str, **kwargs: Any) -> dict:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message
        }
        
        if kwargs:
            entry["data"] = kwargs
        
        return entry
    
    def _write(self, entry: dict) -> None:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        
        if self.console_output:
            level = entry["level"]
            msg = entry["message"]
            data = entry.get("data", {})
            
            data_str = ", ".join(f"{k}={v}" for k, v in data.items()) if data else ""
            console_msg = f"[{level}] {msg}"
            if data_str:
                console_msg += f" | {data_str}"
            
            print(console_msg, file=sys.stderr if level in ("ERROR", "CRITICAL") else sys.stdout)
    
    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        if self.LEVELS.get(level, 0) >= self.level:
            entry = self._format_entry(level, message, **kwargs)
            self._write(entry)
    
    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs: Any) -> None:
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs: Any) -> None:
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("CRITICAL", message, **kwargs)
    
    def operation_start(self, operation: str, **kwargs: Any) -> float:
        import time
        self.info(f"Iniciando: {operation}", operation=operation, **kwargs)
        return time.time()
    
    def operation_end(self, operation: str, start_time: float, success: bool = True, **kwargs: Any) -> None:
        import time
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        status = "completado" if success else "fallido"
        level = "INFO" if success else "ERROR"
        
        self._log(level, f"Finalizado: {operation} ({status})", operation=operation, duration_ms=duration_ms, success=success, **kwargs)


_default_logger: Optional[Logger] = None

def get_logger(name: str = "GMRN") -> Logger:
    global _default_logger
    if _default_logger is None or _default_logger.name != name:
        _default_logger = Logger(name)
    return _default_logger
