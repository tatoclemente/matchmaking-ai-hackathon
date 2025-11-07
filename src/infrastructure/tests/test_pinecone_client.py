from unittest.mock import MagicMock, patch
from src.infrastructure.external.pinecone_client import PineconeClient, init_pinecone_client
from src.infrastructure.schema.pinecone import PineconeConfig


def test_singleton_behavior_pinecone():
    cfg = PineconeConfig(api_key="pc-test-xxxx", index_name="idx-test", environment="us-east-1")
    c1 = PineconeClient.get_instance(cfg)
    c2 = PineconeClient.get_instance()
    assert c1 is c2


@patch("src.infrastructure.external.pinecone_client.Pinecone")
def test_initialize_index_creates_when_missing(mock_pc_cls):
    mock_pc = MagicMock()
    mock_pc.list_indexes.return_value.names.return_value = []
    mock_pc.Index.return_value = MagicMock()
    mock_pc_cls.return_value = mock_pc

    cfg = PineconeConfig(api_key="pc-test-xxxx", index_name="idx-test", environment="us-east-1")
    client = PineconeClient.get_instance(cfg)
    idx = client.initialize_index()

    mock_pc.create_index.assert_called()
    mock_pc.Index.assert_called_with("idx-test")
    assert idx is not None


@patch("src.infrastructure.external.pinecone_client.Pinecone")
def test_upsert_and_query_flow(mock_pc_cls):
    mock_pc = MagicMock()
    mock_index = MagicMock()
    mock_pc.Index.return_value = mock_index
    mock_pc.list_indexes.return_value.names.return_value = ["idx-test"]

    # Simular respuesta de query con matches
    mock_index.query.return_value.matches = [
        {"id": "1", "score": 0.9, "metadata": {"name": "Juan"}}
    ]

    mock_pc_cls.return_value = mock_pc

    client = PineconeClient.get_instance(PineconeConfig(api_key="pc-test-xxxx", index_name="idx-test", environment="us-east-1"))
    client.initialize_index()

    vectors = [
        {"id": "1", "values": [0.1, 0.2], "metadata": {"name": "Juan"}}
    ]
    client.upsert_vectors(vectors)
    mock_index.upsert.assert_called()

    res = client.search_similar([0.1, 0.2])
    mock_index.query.assert_called()
    assert isinstance(res, list)
    assert res[0]["id"] == "1"
