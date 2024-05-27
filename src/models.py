from pydantic import BaseModel, Field

cat_prompt = (
    """All the news summaries that can be grouped into category - "{}" """
)


class NewsCategories(BaseModel):

    AI: list[str] = Field(..., description=cat_prompt.format("AI"))
    Technology: list[str] = Field(
        ..., description=cat_prompt.format("Technology")
    )
    Politics: list[str] = Field(..., description=cat_prompt.format("Politics"))
    World: list[str] = Field(..., description=cat_prompt.format("World"))
    Business: list[str] = Field(..., description=cat_prompt.format("Business"))
    Sports: list[str] = Field(..., description=cat_prompt.format("Sports"))
    Crime: list[str] = Field(..., description=cat_prompt.format("Crime"))
