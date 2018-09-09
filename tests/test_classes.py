#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
import pytest   # type: ignore
import ruamel.yaml as yaml

import yatiml

from .conftest import Circle, Document1, Document2, Extensible, Rectangle
from .conftest import Shape, SubA, Super, Universal, Vector2D


def test_load_class(document1_loader):
    text = 'attr1: test_value'
    data = yaml.load(text, Loader=document1_loader)
    assert isinstance(data, Document1)
    assert data.attr1 == 'test_value'


def test_recognize_subclass(shape_loader):
    text = ('center:\n'
            '  x: 10.0\n'
            '  y: 12.3\n')
    data = yaml.load(text, Loader=shape_loader)
    assert isinstance(data, Shape)
    assert data.center.x == 10.0
    assert data.center.y == 12.3


def test_missing_attribute(universal_loader):
    text = 'a: 2'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=universal_loader)


def test_extra_attribute(vector_loader):
    text = ('x: 12.3\n'
            'y: 45.6\n'
            'z: 78.9\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=vector_loader)


def test_incorrect_attribute_type(universal_loader):
    text = ('a: 2\n'
            'b: [test1, test2]\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=universal_loader)


def test_optional_attribute(document2_loader):
    text = ('cursor_at:\n'
            '  x: 42.0\n'
            '  y: 42.1\n')
    data = yaml.load(text, Loader=document2_loader)
    assert isinstance(data, Document2)
    assert data.cursor_at.x == 42.0
    assert data.cursor_at.y == 42.1
    assert data.shapes == []


def test_custom_recognize(super_loader):
    text = 'subclass: A'
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, SubA)


def test_built_in_instead_of_class(shape_loader):
    text = 'center: 10'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=shape_loader)


def test_parent_fallback(super_loader):
    text = 'subclass: x'
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, Super)


def test_missing_discriminator(super_loader):
    text = 'subclas: A'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=super_loader)


def test_kwargs(extensible_loader):
    text = ('a: 10\n'
            'b: test1\n'
            'c: 42\n')
    data = yaml.load(text, Loader=extensible_loader)
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data.kwargs['b'] == 'test1'
    assert data.kwargs['c'] == 42


def test_missing_class(missing_circle_loader):
    text = ('center:\n'
            '  x: 1.0\n'
            '  y: 2.0\n'
            'radius: 10.0\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=missing_circle_loader)


def test_user_class_override(super_loader):
    text = ('!SubA\n'
            'subclass: x\n')
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, SubA)


def test_user_class_override2(super_loader):
    text = ('!Super\n'
            'subclass: A\n')
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, Super)


def test_dump_document1(document1_dumper):
    data = Document1('test')
    text = yaml.dump(data, Dumper=document1_dumper)
    assert text == '{attr1: test}\n'


def test_dump_custom_attributes(extensible_dumper):
    data = Extensible(10, b=5, c=3)
    text = yaml.dump(data, Dumper=extensible_dumper)
    assert text == '{a: 10, b: 5, c: 3}\n'


def test_dump_complex_document(document2_dumper):
    shape1 = Circle(Vector2D(5.0, 6.0), 12.0)
    shape2 = Rectangle(Vector2D(-2.0, -5.0), 3.0, 7.0)
    data = Document2(Vector2D(3.0, 4.0), [shape1, shape2])
    text = yaml.dump(data, Dumper=document2_dumper)
    print(text)
    assert text == (
            'cursor_at: {x: 3.0, y: 4.0}\n'
            'shapes:\n'
            '- center: {x: 5.0, y: 6.0}\n'
            '  radius: 12.0\n'
            '- center: {x: -2.0, y: -5.0}\n'
            '  height: 7.0\n'
            '  width: 3.0\n'
            )


def test_broken_custom_attributes(universal_dumper):
    data = Universal(3, [4])
    with pytest.raises(RuntimeError):
        yaml.dump(data, Dumper=universal_dumper)