"""Health check and monitoring routes."""

import logging
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Profile
from app.api.dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/health", tags=["health"])


def _is_admin(user: Profile) -> bool:
    """Check if user is admin."""
    return user.subscription_tier == "admin" or user.access_level == "admin"


async def admin_required(
    current_user: Optional[Profile] = Depends(get_current_user),
) -> Profile:
    """Dependency to ensure user is admin."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    if not _is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access monitoring endpoints"
        )
    return current_user


@router.get("/docker")
async def get_docker_health(
    _admin: Profile = Depends(admin_required),
) -> Dict[str, Any]:
    """Get Docker container health status."""
    try:
        import docker
        
        try:
            client = docker.from_env()
            containers = client.containers.list(all=True)
            
            containers_info = []
            for container in containers:
                containers_info.append({
                    "id": container.short_id,
                    "name": container.name,
                    "status": container.status,
                    "state": container.status,
                    "health": "healthy" if container.status == "running" else "unhealthy"
                })
            
            return {
                "status": "ok",
                "timestamp": datetime.utcnow().isoformat(),
                "containers": containers_info,
                "total_containers": len(containers_info)
            }
        except Exception as docker_error:
            logger.warning(f"Cannot connect to Docker daemon: {docker_error}")
            # Return unavailable instead of error when Docker daemon isn't accessible
            return {
                "status": "unavailable",
                "message": "Docker daemon not accessible (running in Docker container)",
                "timestamp": datetime.utcnow().isoformat(),
                "containers": [],
                "total_containers": 0
            }
    except ImportError:
        logger.warning("Docker SDK not available")
        return {
            "status": "unavailable",
            "message": "Docker SDK not installed",
            "timestamp": datetime.utcnow().isoformat(),
            "containers": [],
            "total_containers": 0
        }
    except Exception as e:
        logger.error(f"Error checking Docker health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "containers": [],
            "total_containers": 0
        }


@router.get("/celery")
async def get_celery_health(
    _admin: Profile = Depends(admin_required),
) -> Dict[str, Any]:
    """Get Celery worker health status."""
    try:
        # Try to import celery_app
        from app.celery_app import celery_app
        
        if celery_app is None:
            return {
                "status": "unavailable",
                "message": "Celery not configured",
                "timestamp": datetime.utcnow().isoformat(),
                "workers": [],
                "total_workers": 0,
                "total_active_tasks": 0
            }
        
        inspect = celery_app.control.inspect()
        
        if inspect is None:
            return {
                "status": "unavailable",
                "message": "Celery inspect not available",
                "timestamp": datetime.utcnow().isoformat(),
                "workers": [],
                "total_workers": 0,
                "total_active_tasks": 0
            }
        
        # Get active tasks
        active = inspect.active() or {}
        # Get registered tasks
        registered = inspect.registered() or {}
        
        workers = []
        for worker_name, worker_tasks in active.items():
            workers.append({
                "name": worker_name,
                "state": "online",
                "active_tasks": len(worker_tasks) if worker_tasks else 0,
                "registered_tasks": len(registered.get(worker_name, [])) if registered else 0
            })
        
        # If no workers responding, try to at least show that celery is configured
        if not workers:
            return {
                "status": "unavailable",
                "message": "No celery workers online",
                "timestamp": datetime.utcnow().isoformat(),
                "workers": [{
                    "name": "celery",
                    "state": "offline",
                    "active_tasks": 0,
                    "registered_tasks": 0
                }],
                "total_workers": 0,
                "total_active_tasks": 0
            }
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "workers": workers,
            "total_workers": len(workers),
            "total_active_tasks": sum(w["active_tasks"] for w in workers)
        }
    except ImportError:
        logger.warning("Celery app not available")
        return {
            "status": "unavailable",
            "message": "Celery not configured",
            "timestamp": datetime.utcnow().isoformat(),
            "workers": [],
            "total_workers": 0,
            "total_active_tasks": 0
        }
    except Exception as e:
        logger.error(f"Error checking Celery health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "workers": [],
            "total_workers": 0,
            "total_active_tasks": 0
        }


@router.get("/celery/tasks")
async def get_celery_tasks(
    status_filter: Optional[str] = None,
    _admin: Profile = Depends(admin_required),
) -> Dict[str, Any]:
    """Get Celery task status and recent tasks."""
    try:
        from app.celery_app import celery_app
        
        if celery_app is None:
            return {
                "status": "unavailable",
                "message": "Celery not configured",
                "timestamp": datetime.utcnow().isoformat(),
                "tasks": [],
                "total_tasks": 0
            }
        
        inspect = celery_app.control.inspect()
        
        if inspect is None:
            return {
                "status": "unavailable",
                "message": "Celery inspect not available",
                "timestamp": datetime.utcnow().isoformat(),
                "tasks": [],
                "total_tasks": 0
            }
        
        active = inspect.active() or {}
        reserved = inspect.reserved() or {}
        
        tasks = []
        
        # Collect active tasks
        for worker_name, worker_tasks in active.items():
            if worker_tasks:
                for task in worker_tasks:
                    if status_filter is None or status_filter == "active":
                        tasks.append({
                            "id": task.get("id", "unknown"),
                            "name": task.get("name", "unknown"),
                            "worker": worker_name,
                            "status": "active",
                            "args": str(task.get("args", [])),
                            "kwargs": str(task.get("kwargs", {})),
                            "started_at": task.get("time_start", None)
                        })
        
        # Collect reserved tasks
        for worker_name, worker_tasks in reserved.items():
            if worker_tasks:
                for task in worker_tasks:
                    if status_filter is None or status_filter == "reserved":
                        tasks.append({
                            "id": task.get("id", "unknown"),
                            "name": task.get("name", "unknown"),
                            "worker": worker_name,
                            "status": "reserved",
                            "args": str(task.get("args", [])),
                            "kwargs": str(task.get("kwargs", {})),
                            "started_at": None
                        })
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "tasks": tasks[:50],  # Return last 50 tasks
            "total_tasks": len(tasks)
        }
    except ImportError:
        logger.warning("Celery app not available")
        return {
            "status": "unavailable",
            "message": "Celery not configured",
            "timestamp": datetime.utcnow().isoformat(),
            "tasks": [],
            "total_tasks": 0
        }
    except Exception as e:
        logger.error(f"Error fetching Celery tasks: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "tasks": [],
            "total_tasks": 0
        }


@router.get("/system")
async def get_system_health(
    _admin: Profile = Depends(admin_required),
) -> Dict[str, Any]:
    """Get system health information."""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": round(cpu_percent, 2),
                "cores": psutil.cpu_count()
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": disk.percent
            }
        }
    except ImportError:
        logger.warning("psutil not available - returning mock data")
        # Return mock data when psutil not available
        return {
            "status": "unavailable",
            "message": "psutil not installed",
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": 0,
                "cores": os.cpu_count() or 1
            },
            "memory": {
                "total_gb": 0,
                "available_gb": 0,
                "percent": 0
            },
            "disk": {
                "total_gb": 0,
                "free_gb": 0,
                "percent": 0
            }
        }
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
