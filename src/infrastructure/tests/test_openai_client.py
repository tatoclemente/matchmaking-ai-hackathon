from unittest.mock import MagicMock, patch
from src.infrastructure.schema.embedding import ClientConfig, BatchEmbeddingRequest
from src.infrastructure.external.openai_client import OpenAIClient, init_openai_client
import src.infrastructure.external.openai_client as oc_mod


def test_singleton_behavior():
    cfg = ClientConfig(api_key="sk-test-xxxx", timeout=10, max_retries=1, model="text-embedding-3-small", max_batch_size=2)
    init_openai_client(cfg)
    c1 = OpenAIClient.get_instance()
    c2 = OpenAIClient.get_instance()
    assert c1 is c2
    assert oc_mod.openai_client is c1


@patch("src.infrastructure.external.openai_client.OpenAI")
def test_create_embedding_calls_sdk(mock_openai_cls):
    mock_sdk = MagicMock()
    mock_sdk.embeddings.create.return_value = MagicMock(data=[MagicMock(embedding=[0.1, 0.2])])
    mock_openai_cls.return_value = mock_sdk

    cfg = ClientConfig(api_key="sk-test-xxxx")
    client = OpenAIClient.get_instance(cfg)
    emb = client.create_embedding("hola mundo")
    assert emb == [0.1, 0.2]
    mock_sdk.embeddings.create.assert_called_once()
    _, kwargs = mock_sdk.embeddings.create.call_args
    assert kwargs["model"] == client.model
    assert kwargs["input"] == "hola mundo"


@patch("src.infrastructure.external.openai_client.OpenAI")
def test_batch_chunking_calls_sdk_multiple_times(mock_openai_cls):
    mock_sdk = MagicMock()

    def make_resp(texts):
        return MagicMock(data=[MagicMock(embedding=[float(i)]) for i, _ in enumerate(texts)])

    mock_sdk.embeddings.create.side_effect = lambda *args, **kwargs: make_resp(kwargs.get('input') or args[1])
    mock_openai_cls.return_value = mock_sdk

    cfg = ClientConfig(api_key="sk-test-xxxx", max_batch_size=2)
    client = OpenAIClient.get_instance(cfg)
    texts = ["a", "b", "c", "d"]
    res = client.create_embeddings_batch(BatchEmbeddingRequest(texts=texts, model=client.model))
    assert isinstance(res, list)
    assert len(res) == 4
    assert mock_sdk.embeddings.create.call_count == 2
