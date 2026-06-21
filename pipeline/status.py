"""
Pipeline job status tracker.

Stores pipeline progress in-memory so the frontend can poll for real-time updates.
Thread-safe — the pipeline runs in a background thread while the frontend polls from request threads.
"""

import threading
from datetime import datetime

_lock = threading.Lock()
_jobs = {}

STEP_NAMES = {
    1: "Keyword Research",
    2: "SERP & Competitor Analysis",
    3: "Content Outline",
    4: "Full Article + FAQ + Schema",
    5: "HTML for Elementor",
}


def create_job(job_id: str, topic: str) -> dict:
    """Initialize a new pipeline job with all steps in 'pending' state."""
    job = {
        "job_id": job_id,
        "topic": topic,
        "status": "running",
        "current_step": 0,
        "steps": {
            str(i): {"name": STEP_NAMES[i], "status": "pending", "chars": 0}
            for i in range(1, 6)
        },
        "error": None,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
    }
    with _lock:
        _jobs[job_id] = job
    return job


def update_step(job_id: str, step: int, status: str, chars: int = 0):
    """
    Update a step's status.
    
    Args:
        job_id: The pipeline job ID.
        step: Step number (1-5).
        status: One of 'running', 'complete', 'error'.
        chars: Number of characters in the step output (for 'complete' status).
    """
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["steps"][str(step)]["status"] = status
        job["steps"][str(step)]["chars"] = chars
        if status == "running":
            job["current_step"] = step


def complete_job(job_id: str):
    """Mark the entire pipeline as complete."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = "complete"
            job["completed_at"] = datetime.now().isoformat()


def fail_job(job_id: str, error: str, failed_step: int = None):
    """Mark the pipeline as failed with an error message."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            job["status"] = "error"
            job["error"] = error
            job["completed_at"] = datetime.now().isoformat()
            if failed_step:
                job["steps"][str(failed_step)]["status"] = "error"


def get_job(job_id: str) -> dict | None:
    """Get the current status of a pipeline job."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            # Return a copy to avoid race conditions
            import copy
            return copy.deepcopy(job)
        return None


def cleanup_job(job_id: str):
    """Remove a completed job from memory (call after some time)."""
    with _lock:
        _jobs.pop(job_id, None)
