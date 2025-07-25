from dataclasses import dataclass, field
from typing import TypedDict, Union, Literal, Generic, TypeVar, List

import numpy as np

from ._utils import EmbeddingFunc


@dataclass
class QueryParam:
    mode: Literal["dynamic"] = "dynamic"
    only_need_context: bool = False
    response_type: str = "short and concise answer"
    level: int = 2
    top_k: int = 20
    et_top_k: int = 20
    topk1: int = 500 
    max_token_for_text_unit: int = 12000 

    # time constraints and entities for dynamic search
    time_constraints: dict = field(default_factory=lambda: {"start_time": None, "end_time": None})
    entities: list = field(default_factory=list)


TextChunkSchema = TypedDict(
    "TextChunkSchema",
    {
        "tokens": int, 
        "content": str, 
        "full_doc_id": str, 
        "chunk_order_index": int,
        "doc_title": str
    },
)

SingleCommunitySchema = TypedDict(
    "SingleCommunitySchema",
    {
        "level": int,
        "title": str,
        "edges": list[list[str, str]],
        "nodes": list[str],
        "chunk_ids": list[str],
        "occurrence": float,
        "sub_communities": list[str],
    },
)


class CommunitySchema(SingleCommunitySchema):
    report_string: str
    report_json: dict


T = TypeVar("T")


@dataclass
class StorageNameSpace:
    namespace: str
    global_config: dict

    async def index_start_callback(self):
        """commit the storage operations after indexing"""
        pass

    async def index_done_callback(self):
        """commit the storage operations after indexing"""
        pass

    async def query_done_callback(self):
        """commit the storage operations after querying"""
        pass


@dataclass
class BaseVectorStorage(StorageNameSpace):
    embedding_func: EmbeddingFunc
    meta_fields: set = field(default_factory=set)

    async def query(self, query: str, top_k: int) -> list[dict]:
        raise NotImplementedError

    async def upsert(self, data: dict[str, dict]):
        """Use 'content' field from value for embedding, use key as id.
        If embedding_func is None, use 'embedding' field from value
        """
        raise NotImplementedError


@dataclass
class BaseKVStorage(Generic[T], StorageNameSpace):
    async def all_keys(self) -> list[str]:
        raise NotImplementedError

    async def get_by_id(self, id: str) -> Union[T, None]:
        raise NotImplementedError

    async def get_by_ids(
        self, ids: list[str], fields: Union[set[str], None] = None
    ) -> list[Union[T, None]]:
        raise NotImplementedError

    async def filter_keys(self, data: list[str]) -> set[str]:
        """return un-exist keys"""
        raise NotImplementedError

    async def upsert(self, data: dict[str, T]):
        raise NotImplementedError

    async def drop(self):
        raise NotImplementedError


@dataclass
class BaseGraphStorage(StorageNameSpace):
    async def has_node(self, node_id: str) -> bool:
        raise NotImplementedError

    async def has_edge(self, source_node_id: str, target_node_id: str) -> bool:
        raise NotImplementedError

    async def node_degree(self, node_id: str) -> int:
        raise NotImplementedError
    
    async def node_degrees_batch(self, node_ids: List[str]) -> List[str]:
        raise NotImplementedError

    async def edge_degree(self, src_id: str, tgt_id: str) -> int:
        raise NotImplementedError

    async def edge_degrees_batch(self, edge_pairs: list[tuple[str, str]]) -> list[int]:
        raise NotImplementedError

    async def get_node(self, node_id: str) -> Union[dict, None]:
        raise NotImplementedError

    async def get_nodes_batch(self, node_ids: list[str]) -> dict[str, Union[dict, None]]:
        raise NotImplementedError

    async def get_edge(
        self, source_node_id: str, target_node_id: str
    ) -> Union[dict, None]:
        raise NotImplementedError

    async def get_edges_batch(
        self, edge_pairs: list[tuple[str, str]]
    ) -> list[Union[dict, None]]:
        raise NotImplementedError

    async def get_node_edges(
        self, source_node_id: str
    ) -> Union[list[tuple[str, str]], None]:
        raise NotImplementedError

    async def get_nodes_edges_batch(
        self, node_ids: list[str]
    ) -> list[list[tuple[str, str]]]:
        raise NotImplementedError

    async def upsert_node(self, node_id: str, node_data: dict[str, str]):
        raise NotImplementedError

    async def upsert_nodes_batch(self, nodes_data: list[tuple[str, dict[str, str]]]):
        raise NotImplementedError

    async def upsert_edge(
        self, source_node_id: str, target_node_id: str, edge_data: dict[str, str]
    ):
        raise NotImplementedError

    async def upsert_edges_batch(
        self, edges_data: list[tuple[str, str, dict[str, str]]]
    ):
        raise NotImplementedError

    async def clustering(self, algorithm: str):
        raise NotImplementedError

    async def community_schema(self) -> dict[str, SingleCommunitySchema]:
        """Return the community representation with report and nodes"""
        raise NotImplementedError

    async def embed_nodes(self, algorithm: str) -> tuple[np.ndarray, list[str]]:
        raise NotImplementedError("Node embedding is not used in nano-graphrag.")
