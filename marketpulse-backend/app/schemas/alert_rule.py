from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_INDICATORS = {
    "close_price",
    "sma",
    "ema",
    "rsi",
    "macd",
    "macd_signal",
    "macd_histogram",
}

VALID_OPERATORS = {
    ">",
    ">=",
    "<",
    "<=",
    "==",
    "!=",
}

VALID_DIRECTIONS = {
    "bullish",
    "bearish",
    "neutral",
}


class AlertRuleBase(BaseModel):
    stock_id: int
    name: str = Field(..., min_length=1, max_length=255)
    indicator: str = Field(..., min_length=1, max_length=50)
    operator: str = Field(..., min_length=1, max_length=10)
    target_value: float
    direction: str = Field(..., min_length=1, max_length=20)
    timeframe: str = Field(default="1d", min_length=1, max_length=20)

    @field_validator("indicator")
    @classmethod
    def validate_indicator(cls, value: str) -> str:
        normalized_value = value.lower().strip()

        if normalized_value not in VALID_INDICATORS:
            raise ValueError(
                f"Invalid indicator. Allowed values: {sorted(VALID_INDICATORS)}"
            )

        return normalized_value

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str) -> str:
        normalized_value = value.strip()

        if normalized_value not in VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator. Allowed values: {sorted(VALID_OPERATORS)}"
            )

        return normalized_value

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str) -> str:
        normalized_value = value.lower().strip()

        if normalized_value not in VALID_DIRECTIONS:
            raise ValueError(
                f"Invalid direction. Allowed values: {sorted(VALID_DIRECTIONS)}"
            )

        return normalized_value


class AlertRuleCreate(AlertRuleBase):
    pass


class AlertRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    indicator: str | None = Field(default=None, min_length=1, max_length=50)
    operator: str | None = Field(default=None, min_length=1, max_length=10)
    target_value: float | None = None
    direction: str | None = Field(default=None, min_length=1, max_length=20)
    timeframe: str | None = Field(default=None, min_length=1, max_length=20)
    is_active: bool | None = None

    @field_validator("indicator")
    @classmethod
    def validate_indicator(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized_value = value.lower().strip()

        if normalized_value not in VALID_INDICATORS:
            raise ValueError(
                f"Invalid indicator. Allowed values: {sorted(VALID_INDICATORS)}"
            )

        return normalized_value

    @field_validator("operator")
    @classmethod
    def validate_operator(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized_value = value.strip()

        if normalized_value not in VALID_OPERATORS:
            raise ValueError(
                f"Invalid operator. Allowed values: {sorted(VALID_OPERATORS)}"
            )

        return normalized_value

    @field_validator("direction")
    @classmethod
    def validate_direction(cls, value: str | None) -> str | None:
        if value is None:
            return value

        normalized_value = value.lower().strip()

        if normalized_value not in VALID_DIRECTIONS:
            raise ValueError(
                f"Invalid direction. Allowed values: {sorted(VALID_DIRECTIONS)}"
            )

        return normalized_value


class AlertRuleRead(BaseModel):
    id: int
    stock_id: int
    name: str
    indicator: str
    operator: str
    target_value: float
    direction: str
    timeframe: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)