import json
import logging
import shutil
import subprocess
from django.conf import settings

logger = logging.getLogger(__name__)

class NucleiScannerService:
    """
    Executes Nuclei template-based security checks against authorized targets
    and streams parsed JSON findings.
    """
    def __init__(self):
        self.nuclei_bin = shutil.which('nuclei') or '/usr/local/bin/nuclei'
        self.templates_dir = getattr(settings, 'NUCLEI_TEMPLATES_DIR', None)

    def is_available(self) -> bool:
        return shutil.which('nuclei') is not None

    def execute_scan(self, target_url: str, severity_filter: str = "critical,high,medium,low,info") -> list[dict]:
        """
        Executes Nuclei with strict timeouts and rate limits, returning normalized findings.
        """
        if not self.is_available():
            logger.warning("Nuclei binary not detected in PATH. Returning mock diagnostic check.")
            return []

        cmd = [
            self.nuclei_bin,
            "-target", target_url,
            "-jsonl",
            "-rate-limit", "150",
            "-timeout", "5",
            "-retries", "1",
            "-severity", severity_filter,
            "-silent"
        ]

        if self.templates_dir:
            cmd.extend(["-t", self.templates_dir])

        findings = []
        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes maximum execution time
            )

            for line in process.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    findings.append(data)
                except json.JSONDecodeError:
                    continue

        except subprocess.TimeoutExpired:
            logger.error(f"Nuclei scan timed out against target: {target_url}")
        except Exception as e:
            logger.error(f"Failed to execute Nuclei scan: {e}")

        return findings
