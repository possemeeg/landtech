import pytest
from io import StringIO

from landtreecli.cli_tree import (mk_tree, expand_tree)

basic_tree_rows = [
        'comp0; Company 0; owner of 8 land parcels',
        '  | - comp1; Company 1; owner of 5 land parcels',
        '  | - comp2; Company 2; owner of 2 land parcels ***',
        ]

deeper_tree_rows = [
        'comp0; Company 0; owner of 8 land parcels',
        '  | - comp1; Company 1; owner of 5 land parcels',
        '  | | - comp3; Company 3; owner of 4 land parcels',
        '  | | | - comp4; Company 4; owner of 3 land parcels ***',
        '  | | - comp5; Company 5; owner of 0 land parcels',
        '  | - comp2; Company 2; owner of 2 land parcels',
        ]

basic_expanded_tree_rows = [
        '| - comp3; Company 3; owner of 4 land parcels',
        '| | - comp4; Company 4; owner of 3 land parcels',
        '| - comp5; Company 5; owner of 0 land parcels',
        ]

@pytest.mark.parametrize(
        "company,expected_tree",
        [
            ("comp2", basic_tree_rows),
            ("comp4", deeper_tree_rows),
            ]
        )
def test_basic_tree(companies, ownership, company, expected_tree):
    writer = StringIO()
    mk_tree(company, companies, ownership, writer)

    writer.seek(0)
    for i, line in enumerate(writer.readlines()):
        assert line.rstrip() == expected_tree[i]

@pytest.mark.parametrize(
        'company, expected_tree',
        [
            ('comp1', basic_expanded_tree_rows),
            ]
        )
def test_excpand_tree(companies, ownership, company, expected_tree):
    writer = StringIO()
    expand_tree('comp1', companies, ownership, writer)

    writer.seek(0)
    for i, line in enumerate(writer.readlines()):
        assert line.rstrip() == expected_tree[i]



