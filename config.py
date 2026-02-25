"""
Configuration management for the Autonomous Market Evolution Engine.
Centralizes all environment variables and system constants with validation.
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field, validator
from loguru import logger


class EvolutionEngineConfig(BaseSettings):
    """
    Central configuration class using Pydantic for validation.
    All environment variables are loaded and validated at startup.
    """
    
    # Firebase Configuration (CRITICAL - Ecosystem Standard)
    FIREBASE_PROJECT_ID: str = Field(..., env="FIREBASE_PROJECT_ID")
    FIREBASE_PRIVATE_KEY: str = Field(..., env="FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: str = Field(..., env="FIREBASE_CLIENT_EMAIL")
    FIREBASE_DATABASE_URL: str = Field(..., env="FIREBASE_DATABASE_URL")
    
    # Tournament Parameters
    TOURNAMENT_DAILY_SCHEDULE: str = Field(default="22:00", env="TOURNAMENT_DAILY_SCHEDULE")
    MAX_CONCURRENT_AGENTS: int = Field(default=100, env="MAX_CONCURRENT_AGENTS")
    MIN_SURVIVAL_SCORE: float = Field(default=0.0, env="MIN_SURVIVAL_SCORE")
    
    # Market Data Sources
    DATA_SOURCES: List[str] = Field(
        default=["binance", "kraken", "coinbase"],
        env="DATA_SOURCES"
    )
    
    # Risk Management
    MAX_DRAWDOWN_PERCENT: float = Field(default=20.0, env="MAX_DRAWDOWN_PERCENT")
    COMPLEXITY_TAX_RATE: float = Field(default=0.001, env="COMPLEXITY_TAX_RATE")
    
    # Performance Metrics
    SCORE_WEIGHTS: Dict[str, float] = Field(
        default={
            "profitability": 0.4,
            "sharpe_ratio": 0.25,
            "max_drawdown": 0.2,
            "win_rate": 0.15
        },
        env="SCORE_WEIGHTS"
    )
    
    # Validation Methods
    @validator("MAX_DRAWDOWN_PERCENT")
    def validate_drawdown(cls, v):
        if v <= 0 or v > 100:
            raise ValueError("MAX_DRAWDOWN_PERCENT must be between 0 and 100")
        return v
    
    @validator("SCORE_WEIGHTS")
    def validate_weights(cls, v):
        total = sum(v.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"SCORE_WEIGHTS must sum to 1.0, got {total}")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global configuration instance
config: Optional[EvolutionEngineConfig] = None


def initialize_config() -> EvolutionEngineConfig:
    """
    Initialize and validate configuration with comprehensive error handling.
    
    Returns:
        EvolutionEngineConfig: Validated configuration instance
        
    Raises:
        ValueError: If configuration validation fails
        FileNotFoundError: If .env file is missing (with specific guidance)
    """
    global config
    
    try:
        # Check for .env file existence before loading
        if not os.path.exists(".env"):
            logger.error("Missing .env file. Required environment variables:")
            logger.error("FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL")
            raise FileNotFoundError(
                ".env file not found. Create from .env.template with Firebase credentials"
            )
        
        config = EvolutionEngineConfig()
        logger.info(f"Configuration loaded successfully for project: {config.FIREBASE_PROJECT_ID}")
        
        # Log non-sensitive configuration
        logger.debug(f"Tournament schedule: {config.TOURNAMENT_DAILY_SCHEDULE}")
        logger.debug(f"Data sources: {config.DATA_SOURCES}")
        
        return config
        
    except Exception as e:
        logger.critical(f"Configuration initialization failed: {str(e)}")
        # Provide specific guidance for common failure modes
        if "FIREBASE" in str(e):
            logger.error("Firebase credentials missing. Request access via Telegram emergency contact.")
        raise ValueError(f"Configuration error: {str(e)}")


def get_config() -> EvolutionEngineConfig:
    """
    Safe accessor for global configuration with lazy initialization.
    
    Returns:
        EvolutionEngineConfig: Current configuration
        
    Raises:
        RuntimeError: If configuration hasn't been initialized
    """
    if config is None:
        # Attempt auto-initialization
        try:
            return initialize_config()
        except Exception as e:
            raise RuntimeError(
                f"Configuration not initialized and auto-init failed: {str(e)}"
            )
    return config