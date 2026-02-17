import asyncio
import logging
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

class AutomationEngine:
    """Manages background Cron jobs and Subagent task execution."""

    def __init__(self, data_path: str):
        self.data_path = data_path
        self.scheduler = AsyncIOScheduler()
        self.task_queue = asyncio.Queue()
        self.worker_task = None
        self.cron_config_path = os.path.join(data_path, "cron_jobs.json")
        self.automation_config_path = os.path.join(data_path, "automations.json")
        self.logs_path = os.path.join(data_path, "execution_logs.json")

    async def start(self):
        """Initialize scheduler and start background worker."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Automation scheduler started.")

        self._load_and_schedule_cron()
        
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._subagent_worker())
            logger.info("Subagent worker thread started.")

    async def stop(self):
        """Gracefully shutdown scheduler and worker."""
        if self.scheduler.running:
            self.scheduler.shutdown()
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Automation engine stopped.")

    def _load_and_schedule_cron(self):
        """Loads jobs from cron_jobs.json and registers them with APScheduler."""
        self.scheduler.remove_all_jobs()
        if not os.path.exists(self.cron_config_path):
            return

        try:
            with open(self.cron_config_path, "r") as f:
                data = json.load(f)
            
            jobs = data.get("cronJobs", [])
            for job in jobs:
                if job.get("status") != "active":
                    continue
                
                try:
                    self.scheduler.add_job(
                        self._execute_job,
                        CronTrigger.from_crontab(job["schedule"]),
                        args=[job],
                        id=job["id"],
                        replace_existing=True
                    )
                    logger.info("Scheduled Cron job: %s (%s)", job["name"], job["schedule"])
                except Exception as e:
                    logger.error("Failed to schedule job %s: %s", job.get("name"), e)
        except Exception as e:
            logger.error("Failed to load cron config: %s", e)

    async def _subagent_worker(self):
        """Continuously processes tasks from the subagent queue."""
        while True:
            task = await self.task_queue.get()
            try:
                await self._execute_job(task)
            except Exception as e:
                logger.error("Subagent task failed: %s", e)
            finally:
                self.task_queue.task_done()

    async def _execute_job(self, job_def: Dict[str, Any]):
        """Executes a job (Cron or Subagent) and logs the result."""
        job_id = job_def.get("id", "unknown")
        job_name = job_def.get("name", "Unnamed Job")
        start_time = time.time()
        
        logger.info("Executing job: %s", job_name)
        
        log_entry = {
            "id": f"log_{int(time.time()*1000)}",
            "scriptId": job_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "status": "success",
            "message": f"Completed: {job_name}",
            "durationMs": 0
        }

        try:
            # Placeholder for actual target execution logic
            # In a real scenario, this would call a script, an LLM prompt, etc.
            script_path = job_def.get("target")
            if script_path:
                # Real implementation would run subprocess or internal function
                await asyncio.sleep(1) 
            else:
                await asyncio.sleep(0.5)

            log_entry["durationMs"] = int((time.time() - start_time) * 1000)
            self._save_log(log_entry)
            logger.info("Job %s finished in %dms", job_name, log_entry["durationMs"])
            
        except Exception as e:
            log_entry["status"] = "error"
            log_entry["message"] = f"Error: {str(e)}"
            self._save_log(log_entry)
            logger.error("Error executing job %s: %s", job_name, e)

    def _save_log(self, entry: Dict[str, Any]):
        """Appends an execution log entry to data/execution_logs.json."""
        os.makedirs(os.path.dirname(self.logs_path), exist_ok=True)
        logs = {"logs": []}
        if os.path.exists(self.logs_path):
            try:
                with open(self.logs_path, "r") as f:
                    logs = json.load(f)
            except:
                pass
        
        logs["logs"].append(entry)
        # Trim logs to 500 entries
        logs["logs"] = logs["logs"][-500:]
        
        try:
            with open(self.logs_path, "w") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.error("Failed to save execution log: %s", e)

    async def dispatch_task(self, task_def: Dict[str, Any]):
        """Adds a task to the subagent execution queue."""
        await self.task_queue.put(task_def)
        logger.info("Dispatched subagent task: %s", task_def.get("name"))
