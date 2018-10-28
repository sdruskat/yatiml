from ruamel import yaml

import pytest
import yatiml


def test_is_scalar(class_node):
    assert class_node.get_attribute('attr1').is_scalar()
    assert class_node.get_attribute('attr1').is_scalar(int)
    assert class_node.get_attribute('null_attr').is_scalar(None)
    assert not class_node.is_scalar()
    with pytest.raises(ValueError):
        class_node.get_attribute('attr1').is_scalar(yaml)


def test_is_mapping(class_node):
    assert class_node.is_mapping()
    assert not class_node.get_attribute('attr1').is_mapping()
    assert not class_node.get_attribute('list1').is_mapping()


def test_is_sequence(class_node):
    assert not class_node.is_sequence()
    assert class_node.get_attribute('list1').is_sequence()
    assert not class_node.get_attribute('attr1').is_sequence()


def test_get_value(class_node):
    assert class_node.get_attribute('attr1').get_value() == 42


def test_set_value(class_node):
    assert class_node.is_mapping()
    class_node.set_value(42)
    assert class_node.is_scalar(int)
    assert class_node.yaml_node.value == '42'
    class_node.set_value(True)
    assert class_node.is_scalar(bool)
    assert class_node.yaml_node.value == 'true'


def test_make_mapping(scalar_node):
    assert scalar_node.is_scalar(int)
    scalar_node.make_mapping()
    assert isinstance(scalar_node.yaml_node, yaml.MappingNode)
    assert scalar_node.yaml_node.tag == 'tag:yaml.org,2002:map'
    assert scalar_node.yaml_node.value == []


def test_has_attribute(class_node):
    assert class_node.has_attribute('attr1')
    assert class_node.has_attribute('list1')
    assert not class_node.has_attribute('non_existent_attribute')


def test_has_attribute_type(class_node):
    assert class_node.has_attribute_type('attr1', int)
    assert not class_node.has_attribute_type('attr1', float)
    assert class_node.has_attribute_type('list1', list)
    with pytest.raises(ValueError):
        class_node.has_attribute_type('attr1', yaml)


def test_get_attribute(class_node):
    assert class_node.get_attribute('attr1').yaml_node.value == 42
    with pytest.raises(yatiml.SeasoningError):
        class_node.get_attribute('non_existent_attribute')


def test_set_attribute(class_node):
    assert class_node.get_attribute('attr1').get_value() == 42

    class_node.set_attribute('attr1', 43)
    attr1 = class_node.get_attribute('attr1')
    assert attr1.yaml_node.tag == 'tag:yaml.org,2002:int'
    assert attr1.yaml_node.value == '43'
    assert attr1.yaml_node.start_mark is not None
    assert attr1.yaml_node.end_mark is not None

    class_node.set_attribute('attr1', 'test')
    attr1 = class_node.get_attribute('attr1')
    assert attr1.yaml_node.tag == 'tag:yaml.org,2002:str'
    assert attr1.yaml_node.value == 'test'
    assert attr1.yaml_node.start_mark is not None
    assert attr1.yaml_node.end_mark is not None

    class_node.set_attribute('attr1', 3.14)
    attr1 = class_node.get_attribute('attr1')
    assert attr1.yaml_node.tag == 'tag:yaml.org,2002:float'
    assert attr1.yaml_node.value == '3.14'
    assert attr1.yaml_node.start_mark is not None
    assert attr1.yaml_node.end_mark is not None

    class_node.set_attribute('attr1', True)
    attr1 = class_node.get_attribute('attr1')
    assert attr1.yaml_node.tag == 'tag:yaml.org,2002:bool'
    assert attr1.yaml_node.value == 'true'
    assert attr1.yaml_node.start_mark is not None
    assert attr1.yaml_node.end_mark is not None

    class_node.set_attribute('attr1', None)
    attr1 = class_node.get_attribute('attr1')
    assert attr1.yaml_node.tag == 'tag:yaml.org,2002:null'
    assert attr1.yaml_node.value == ''
    assert attr1.yaml_node.start_mark is not None
    assert attr1.yaml_node.end_mark is not None

    assert not class_node.has_attribute('attr2')
    class_node.set_attribute('attr2', 'testing')
    attr2 = class_node.get_attribute('attr2')
    assert attr2.yaml_node.value == 'testing'
    assert attr2.yaml_node.start_mark is not None
    assert attr2.yaml_node.end_mark is not None

    node = yaml.ScalarNode('tag:yaml.org,2002:str', 'testnode')
    class_node.set_attribute('attr3', node)
    assert class_node.get_attribute('attr3').yaml_node == node

    with pytest.raises(TypeError):
        class_node.set_attribute('attr4', class_node)


def test_remove_attribute(class_node):
    assert class_node.has_attribute('attr1')
    class_node.remove_attribute('attr1')
    assert not class_node.has_attribute('attr1')

    class_node.set_attribute('attr1', 10)
    class_node.set_attribute('attr2', 11)
    assert class_node.has_attribute('attr2')
    class_node.remove_attribute('attr2')
    assert not class_node.has_attribute('attr2')

    class_node.remove_attribute('attr2')
    assert not class_node.has_attribute('attr2')


def test_rename_attribute(class_node):
    assert class_node.has_attribute('attr1')
    assert not class_node.has_attribute('attr2')
    attr1_value = class_node.get_attribute('attr1').get_value()
    class_node.rename_attribute('attr1', 'attr2')
    assert not class_node.has_attribute('attr1')
    assert class_node.has_attribute('attr2')
    assert class_node.get_attribute('attr2').get_value() == attr1_value

    # make sure that this does not raise
    class_node.rename_attribute('non_existent_attribute', 'attr3')


def test_seq_attribute_to_map(class_node, class_node_dup_key):
    assert class_node.has_attribute('list1')
    assert class_node.get_attribute('list1').is_sequence()

    class_node.seq_attribute_to_map('list1', 'item_id', 'price')

    assert class_node.has_attribute_type('list1', dict)
    attr_node = class_node.get_attribute('list1')
    assert attr_node.is_mapping()

    assert attr_node.has_attribute_type('item1', float)
    item1_node = attr_node.get_attribute('item1')
    assert item1_node.get_value() == 100.0

    assert attr_node.has_attribute_type('item2', dict)
    item2_node = attr_node.get_attribute('item2')
    assert not item2_node.has_attribute('item_id')
    assert item2_node.has_attribute('price')
    assert item2_node.has_attribute('on_sale')

    # check that it fails silently if the attribute is missing or not a list
    class_node.seq_attribute_to_map('non_existent_attribute', 'item_id')
    class_node.seq_attribute_to_map('attr1', 'item_id')

    # check that it raises with strict=True and duplicate keys
    with pytest.raises(yatiml.SeasoningError):
        class_node_dup_key.seq_attribute_to_map('dup_list', 'item_id', True)


def test_map_attribute_to_seq(class_node):
    assert class_node.has_attribute_type('dict1', dict)

    class_node.map_attribute_to_seq('dict1', 'item_id', 'price')

    assert class_node.has_attribute_type('dict1', list)
    attr_node = class_node.get_attribute('dict1')

    assert len(attr_node.seq_items()) == 3
    first_item_node = attr_node.seq_items()[0]
    assert first_item_node.has_attribute('item_id')
    assert first_item_node.has_attribute('price')
    first_item_id = first_item_node.get_attribute('item_id').get_value()

    second_item_node = attr_node.seq_items()[1]
    assert second_item_node.has_attribute('item_id')
    assert second_item_node.has_attribute('price')
    second_item_id = second_item_node.get_attribute('item_id').get_value()

    third_item_node = attr_node.seq_items()[2]
    assert third_item_node.has_attribute('item_id')
    assert third_item_node.has_attribute('price')
    third_item_id = third_item_node.get_attribute('item_id').get_value()

    assert first_item_id == 'item1'
    assert second_item_id == 'item2'
    assert third_item_id == 'item3'

    assert ((first_item_id == 'item1' and second_item_id == 'item2') or
            (first_item_id == 'item2' and second_item_id == 'item1'))


def test_unders_to_dashes_in_keys(class_node):
    assert class_node.has_attribute('undered_attr')
    assert class_node.has_attribute('attr1')
    class_node.unders_to_dashes_in_keys()
    assert class_node.has_attribute('undered-attr')
    assert class_node.has_attribute('attr1')


def test_dashes_to_unders_in_keys(class_node):
    assert class_node.has_attribute('dashed-attr')
    assert class_node.has_attribute('list1')
    class_node.dashes_to_unders_in_keys()
    assert class_node.has_attribute('dashed_attr')
    assert class_node.has_attribute('list1')


def test_unknown_node_str(unknown_node):
    assert str(unknown_node).startswith('UnknownNode')


def test_require_scalar(unknown_node, unknown_scalar_node):
    unknown_scalar_node.require_scalar()
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_scalar()


def test_require_mapping(unknown_node, unknown_scalar_node):
    unknown_node.require_mapping()
    with pytest.raises(yatiml.RecognitionError):
        unknown_scalar_node.require_mapping()


def test_require_sequence(unknown_node, unknown_sequence_node):
    unknown_sequence_node.require_sequence()
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_sequence()


def test_require_attribute(unknown_node):
    unknown_node.require_attribute('attr1')
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('non_existent_attribute')

    unknown_node.require_attribute('attr1', int)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('attr1', str)

    unknown_node.require_attribute('null_attr', None)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('attr1', None)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('null_attr', int)


def test_require_attribute_value(unknown_node):
    unknown_node.require_attribute_value('attr1', 42)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('attr1', 43)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('attr1', 'test')
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('non_existent_attribute', 'test')
