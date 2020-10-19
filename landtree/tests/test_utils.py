import pytest

from landtreecli.cli_tree import (read_company_map, Company,
        count_for_company, read_count_by_company, create_path, company_text)

company_map = {
        'comp0': Company('comp0', 'Company 0', '', {'comp1', 'comp2'}),
        'comp1': Company('comp1', 'Company 1', 'comp0', set({'comp3', 'comp5'})),
        'comp2': Company('comp2', 'Company 2', 'comp0', set()),
        'comp3': Company('comp3', 'Company 3', 'comp1', set({'comp4'})),
        'comp4': Company('comp4', 'Company 4', 'comp3', set()),
        'comp5': Company('comp5', 'Company 5', 'comp1', set()),
        }

company_counts = { 'comp0': 1, 'comp1': 1, 'comp2': 2, 'comp3': 1, 'comp4': 3}

def test_company_map(companies):
    assert read_company_map(companies) == company_map

@pytest.mark.parametrize('comp, count', [('comp0', 8), ('comp2', 2), ('comp4', 3)])
def test_counter(comp, count):
    assert count_for_company(comp, company_map, company_counts) == count

def test_count_parcels(ownership):
    parcel_counts = read_count_by_company(ownership)
    assert parcel_counts == company_counts

def test_create_path(companies):
    company_map = read_company_map(companies)
    path = create_path(company_map['comp5'], company_map)

    for comp, expected_id in zip(path, ['comp0', 'comp1', 'comp5']):
       assert comp.company.id == expected_id

def test_company_text():
    companies = [
            ((1, Company('a', 'comp A', '', set()), 1), '| - a; comp A; owner of 1 land parcel\n'),
            ((2, Company('b', 'comp B', '', set()), 0), '| | - b; comp B; owner of 0 land parcels\n'),
            ((0, Company('c', 'comp C', '', set()), 10), 'c; comp C; owner of 10 land parcels\n'),
            ]
    for comp in companies:
        text = company_text(*comp[0])
        assert text == comp[1]

def test_current_company_text():
    text = company_text(1, Company('a', 'comp A', '', set()), 1, True)
    assert text == '| - a; comp A; owner of 1 land parcel ***\n'
