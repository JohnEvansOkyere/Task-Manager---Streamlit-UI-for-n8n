"""
Task Manager API - FastAPI Backend
A production-ready REST API for task management with n8n integration
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import Optional

from .models import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    MessageRequest,
    MessageResponse,
    HealthResponse,
    ErrorResponse
)
from .services.n8n_service import N8NService
from .services.cache_service import CacheService
from .core.config import get_settings
from .core.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Initialize services
n8n_service = N8NService(settings.N8N_WEBHOOK_URL)
cache_service = CacheService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting Task Manager API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"n8n Webhook configured: {bool(settings.N8N_WEBHOOK_URL)}")
    
    # Test n8n connection on startup
    try:
        is_connected = await n8n_service.test_connection()
        if is_connected:
            logger.info("✅ n8n connection successful")
        else:
            logger.warning("⚠️ n8n connection failed - check webhook URL")
    except Exception as e:
        logger.error(f"❌ Error testing n8n connection: {e}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Task Manager API...")
    cache_service.clear()


# Initialize FastAPI app
app = FastAPI(
    title="Task Manager API",
    description="Production-ready REST API for task management with AI-powered n8n integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code,
            timestamp=datetime.utcnow()
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            status_code=500,
            timestamp=datetime.utcnow()
        ).dict()
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        n8n_connected = await n8n_service.test_connection()
        
        return HealthResponse(
            status="healthy" if n8n_connected else "degraded",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={
                "n8n": "connected" if n8n_connected else "disconnected",
                "cache": "active"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={
                "n8n": "error",
                "cache": "active"
            }
        )


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Task Management Endpoints

@app.get("/api/v1/tasks", response_model=TaskListResponse, tags=["Tasks"])
async def get_tasks(
    status_filter: Optional[str] = None,
    use_cache: bool = True
):
    """
    Get all tasks from the system
    
    - **status_filter**: Optional filter by status (TODO, IN PROGRESS, DONE)
    - **use_cache**: Whether to use cached results (default: True)
    """
    try:
        # Check cache first
        if use_cache:
            cached_tasks = cache_service.get("all_tasks")
            if cached_tasks:
                logger.info("Returning cached tasks")
                tasks = cached_tasks
            else:
                message = "Show me all tasks"
                if status_filter:
                    message = f"Show me all tasks with status {status_filter}"
                
                response = await n8n_service.send_message(message)
                tasks = response.get("tasks", [])
                
                # Cache the results
                cache_service.set("all_tasks", tasks, ttl=60)
        else:
            message = "Show me all tasks"
            if status_filter:
                message = f"Show me all tasks with status {status_filter}"
            
            response = await n8n_service.send_message(message)
            tasks = response.get("tasks", [])
        
        return TaskListResponse(
            tasks=tasks,
            count=len(tasks),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch tasks: {str(e)}"
        )


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task: TaskCreate):
    """
    Create a new task
    
    - **task_name**: The name of the task (required)
    - **status**: Task status (TODO, IN PROGRESS, DONE) - default: TODO
    - **description**: Optional task description
    - **deadline**: Optional deadline date (YYYY-MM-DD format)
    """
    try:
        # Build the message for n8n
        message = f"Create a new task called '{task.task_name}'"
        
        if task.status:
            message += f" with status '{task.status}'"
        
        if task.description:
            message += f" and description '{task.description}'"
        
        if task.deadline:
            message += f" with deadline '{task.deadline}'"
        
        logger.info(f"Creating task: {task.task_name}")
        response = await n8n_service.send_message(message)
        
        # Invalidate cache
        cache_service.delete("all_tasks")
        
        return TaskResponse(
            success=True,
            message=f"Task '{task.task_name}' created successfully",
            data=task.dict(),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@app.put("/api/v1/tasks/{task_name}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(task_name: str, task_update: TaskUpdate):
    """
    Update an existing task
    
    - **task_name**: The name of the task to update (in path)
    - **status**: New status (optional)
    - **description**: New description (optional)
    - **deadline**: New deadline (optional)
    """
    try:
        # Build the update message
        message = f"Update the task '{task_name}'"
        updates = []
        
        if task_update.status:
            updates.append(f"status to '{task_update.status}'")
        
        if task_update.description:
            updates.append(f"description to '{task_update.description}'")
        
        if task_update.deadline:
            updates.append(f"deadline to '{task_update.deadline}'")
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update provided"
            )
        
        message += " - change " + ", ".join(updates)
        
        logger.info(f"Updating task: {task_name}")
        response = await n8n_service.send_message(message)
        
        # Invalidate cache
        cache_service.delete("all_tasks")
        
        return TaskResponse(
            success=True,
            message=f"Task '{task_name}' updated successfully",
            data={"task_name": task_name, **task_update.dict(exclude_none=True)},
            timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@app.delete("/api/v1/tasks/{task_name}", response_model=TaskResponse, tags=["Tasks"])
async def delete_task(task_name: str):
    """
    Delete a task
    
    - **task_name**: The name of the task to delete
    """
    try:
        message = f"Delete the task '{task_name}' - yes, I'm sure"
        
        logger.info(f"Deleting task: {task_name}")
        response = await n8n_service.send_message(message)
        
        # Invalidate cache
        cache_service.delete("all_tasks")
        
        return TaskResponse(
            success=True,
            message=f"Task '{task_name}' deleted successfully",
            data={"task_name": task_name},
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )


# Natural Language Endpoint

@app.post("/api/v1/message", response_model=MessageResponse, tags=["AI Agent"])
async def send_message(message_request: MessageRequest):
    """
    Send a natural language message to the AI agent
    
    - **message**: The natural language command
    - **session_id**: Optional session ID for conversation context
    """
    try:
        logger.info(f"Processing message: {message_request.message[:50]}...")
        
        response = await n8n_service.send_message(
            message_request.message,
            session_id=message_request.session_id
        )
        
        # Invalidate cache if message might have changed data
        action_keywords = ["create", "update", "delete", "add", "remove", "change"]
        if any(keyword in message_request.message.lower() for keyword in action_keywords):
            cache_service.delete("all_tasks")
        
        return MessageResponse(
            response=response,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


# Stats endpoint (example of additional ML/analytics endpoint)
@app.get("/api/v1/stats", tags=["Analytics"])
async def get_task_stats():
    """
    Get task statistics and analytics
    """
    try:
        response = await n8n_service.send_message("Show me all tasks")
        tasks = response.get("tasks", [])
        
        # Calculate statistics
        stats = {
            "total_tasks": len(tasks),
            "by_status": {
                "TODO": sum(1 for t in tasks if t.get("status") == "TODO"),
                "IN PROGRESS": sum(1 for t in tasks if t.get("status") == "IN PROGRESS"),
                "DONE": sum(1 for t in tasks if t.get("status") == "DONE")
            },
            "completion_rate": 0.0,
            "timestamp": datetime.utcnow()
        }
        
        if stats["total_tasks"] > 0:
            stats["completion_rate"] = round(
                (stats["by_status"]["DONE"] / stats["total_tasks"]) * 100, 2
            )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )