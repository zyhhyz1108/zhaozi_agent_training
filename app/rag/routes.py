import logging

from fastapi import APIRouter, HTTPException
from openai import APIConnectionError, APIStatusError, APITimeoutError
from pydantic import BaseModel, ConfigDict, Field

from app.rag.ask import ask
from app.rag.search import search_knowledge


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/knowledge", tags=["知识问答"])


class QuestionRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    question: str = Field(min_length=1, max_length=2000)


class ReferenceRead(BaseModel):
    reference: int
    source: str
    section: str
    chunk_id: str
    text: str


class AnswerResponse(BaseModel):
    answer: str
    references: list[ReferenceRead]


class SearchRequest(QuestionRequest):
    top_k: int = Field(default=3, ge=1, le=5)


class SearchHit(BaseModel):
    chunk_id: str
    source: str
    section: str
    text: str
    score: float


@router.post("/ask", response_model=AnswerResponse)
def ask_knowledge(data: QuestionRequest):
    try:
        return ask(data.question)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="知识索引不存在，请先建立索引",
        )
    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="模型服务响应超时",
        )
    except (APIConnectionError, APIStatusError):
        logger.exception("模型服务调用失败")
        raise HTTPException(
            status_code=502,
            detail="模型服务调用失败",
        )
    except ValueError:
        logger.exception("知识问答配置或索引异常")
        raise HTTPException(
            status_code=503,
            detail="知识问答配置或索引异常",
        )


@router.post("/search", response_model=list[SearchHit])
def search_documents(data: SearchRequest):
    try:
        return search_knowledge(
            data.question,
            top_k=data.top_k,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="知识索引不存在，请先建立索引",
        )
    except APITimeoutError:
        raise HTTPException(
            status_code=504,
            detail="向量服务响应超时",
        )
    except (APIConnectionError, APIStatusError):
        logger.exception("向量服务调用失败")
        raise HTTPException(
            status_code=502,
            detail="向量服务调用失败",
        )
    except ValueError:
        logger.exception("检索配置或索引异常")
        raise HTTPException(
            status_code=503,
            detail="检索配置或索引异常",
        )