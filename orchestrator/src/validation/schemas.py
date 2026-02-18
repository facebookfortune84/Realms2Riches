from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

# --- Base Models ---

class BaseEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)

# --- Configuration Schemas ---

class ToolConfig(BaseModel):
    tool_id: str
    name: str
    description: str
    parameters_schema: Dict[str, Any]  # JSON Schema
    allowed_agents: List[str]

class AgentConfig(BaseEntity):
    name: str
    role: str
    description: str
    system_prompt: str
    allowed_tool_ids: List[str]
    handoff_targets: List[str] = Field(default_factory=list)
    governance_level: Literal["low", "medium", "high", "critical"] = "medium"

# --- Task & Result Schemas ---

class TaskSpec(BaseEntity):
    project_id: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)
    assigned_agent_id: Optional[str] = None
    status: Literal["pending", "in_progress", "completed", "failed", "blocked"] = "pending"
    parent_task_id: Optional[str] = None
    priority: int = 1

class ToolInvocation(BaseEntity):
    tool_id: str
    agent_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: Literal["success", "failure"] = "success"
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0

class Artifact(BaseEntity):
    project_id: str
    path: str
    type: Literal["code", "docker_image", "config", "data", "test_report"]
    sha256: str
    content_preview: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    producing_agent_id: str
    validation_status: Literal["pending", "passed", "failed"] = "pending"

class LineageRecord(BaseEntity):
    artifact_id: str
    action: str
    agent_id: str
    tool_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)

# --- Project Specs ---

class MarketingConfig(BaseModel):
    brand_name: str = Field(default="My Brand", alias="BRAND_NAME")
    product_name: str = Field(default="My Product", alias="PRODUCT_NAME")
    website_url: str = Field(default="https://example.com", alias="MARKETING_SITE_URL")
    contact_email: str = Field(default="hello@example.com", alias="CONTACT_EMAIL")
    twitter_handle: str = Field(default="mybrand", alias="SOCIAL_TWITTER_HANDLE")
    linkedin_url: str = Field(default="https://linkedin.com/company/mybrand", alias="SOCIAL_LINKEDIN_URL")
    youtube_url: str = Field(default="https://youtube.com/c/mybrand", alias="SOCIAL_YOUTUBE_URL")
    github_url: str = Field(default="https://github.com/mybrand", alias="SOCIAL_GITHUB_URL")

class DatabaseConfig(BaseModel):
    user: str = Field(default="postgres", alias="POSTGRES_USER")
    password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")
    db: str = Field(default="app_db", alias="POSTGRES_DB")
    host: str = Field(default="postgres", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    url: Optional[str] = Field(None, alias="DATABASE_URL")

    @property
    def connection_url(self) -> str:
        if self.url:
            return self.url
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

class ProjectSpec(BaseEntity):
    name: str
    description: str
    type: Literal["web_app", "api", "cli", "library"]
    requirements: List[str]
    constraints: List[str] = Field(default_factory=list)
    status: Literal["draft", "active", "archived"] = "draft"
