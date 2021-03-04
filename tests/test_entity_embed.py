import logging

import mock
from entity_embed.data_utils.helpers import AttrInfoDictParser
from entity_embed.entity_embed import DeduplicationDataModule, EntityEmbed


@mock.patch("entity_embed.BlockerNet.__init__", return_value=None)
@mock.patch("entity_embed.data_utils.helpers.Vocab.load_vectors")
def test_set_embedding_size_when_using_semantic_attrs(
    mock_load_vectors,
    mock_blocker_net_init,
    caplog,
):
    attr_info_dict = {
        "name": {
            "field_type": "SEMANTIC_MULTITOKEN",
            "tokenizer": "entity_embed.default_tokenizer",
            "vocab": "charngram.100d",
            "use_mask": True,
        },
    }

    row_dict = {x: {"id": x, "name": f"foo product {x}"} for x in range(50)}

    row_numericalizer = AttrInfoDictParser.from_dict(attr_info_dict, row_dict=row_dict)

    mock_load_vectors.assert_called_once_with("charngram.100d")

    datamodule = DeduplicationDataModule(
        row_dict=row_dict,
        cluster_attr="name",
        row_numericalizer=row_numericalizer,
        batch_size=10,
        row_batch_size=20,
        train_cluster_len=10,
        valid_cluster_len=10,
        test_cluster_len=10,
    )

    EXPECTED_EMBEDDING_SIZE = 100

    caplog.set_level(logging.WARNING)
    model = EntityEmbed(datamodule=datamodule, embedding_size=500)
    assert (
        'Overriding embedding_size=500 with embedding_size=100 from "charngram.100d" '
        'on datamodule.row_numericalizer_attr_info_dict["name"]' in caplog.text
    )

    mock_blocker_net_init.assert_called_once_with(
        row_numericalizer.attr_info_dict, embedding_size=EXPECTED_EMBEDDING_SIZE
    )

    assert model.embedding_size == EXPECTED_EMBEDDING_SIZE
