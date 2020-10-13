from unittest import TestCase, main
from io import StringIO
from landtreecli import mk_tree, expand_tree
from landtreecli.cli_tree import (read_company_map, read_count_by_company,
        Company, company_text, create_path)

TEST_COMPANIES = '''company_id,name,parent
comp1,Company 1,comp0
comp2,Company 2,comp0
comp5,Company 5,comp1
comp3,Company 3,comp1
comp0,Company 0,
comp4,Company 4,comp3
'''
TEST_OWNERSHIP = '''land_id,company_id
land0,comp1
land1,comp0
land2,comp2
land2.1,comp2
land3,comp3
land4,comp4
land4.1,comp4
land4.2,comp4
'''

class TestFromRoot(TestCase):
    def test_basic_tree(self):
        expected = [
                'comp0; Company 0; owner of 1 land parcel',
                '  | - comp1; Company 1; owner of 1 land parcel',
                '  | - comp2; Company 2; owner of 2 land parcels ***',
                ]

        comp_reader = StringIO(TEST_COMPANIES)
        owner_reader = StringIO(TEST_OWNERSHIP)
        writer = StringIO()
        mk_tree('comp2', comp_reader, owner_reader, writer)
        writer.seek(0)
        for i, line in enumerate(writer.readlines()):
            with self.subTest(i):
                self.assertEqual(line.rstrip(), expected[i])

    def test_deeper_tree(self):
        expected = [
                'comp0; Company 0; owner of 1 land parcel',
                '  | - comp1; Company 1; owner of 1 land parcel',
                '  | | - comp3; Company 3; owner of 1 land parcel',
                '  | | | - comp4; Company 4; owner of 3 land parcels ***',
                '  | | - comp5; Company 5; owner of 0 land parcels',
                '  | - comp2; Company 2; owner of 2 land parcels',
                ]

        comp_reader = StringIO(TEST_COMPANIES)
        owner_reader = StringIO(TEST_OWNERSHIP)
        writer = StringIO()
        mk_tree('comp4', comp_reader, owner_reader, writer)

        writer.seek(0)
        for i, line in enumerate(writer.readlines()):
            with self.subTest(i):
                self.assertEqual(line.rstrip(), expected[i])

class TestExpand(TestCase):
    def test_expands_node(self):
        expected = [
                '| - comp3; Company 3; owner of 1 land parcel',
                '| | - comp4; Company 4; owner of 3 land parcels',
                '| - comp5; Company 5; owner of 0 land parcels',
                ]

        comp_reader = StringIO(TEST_COMPANIES)
        owner_reader = StringIO(TEST_OWNERSHIP)
        writer = StringIO()

        expand_tree('comp1', comp_reader, owner_reader, writer)

        writer.seek(0)
        for i, line in enumerate(writer.readlines()):
            with self.subTest(i):
                self.assertEqual(line.rstrip(), expected[i])

class TestUtilities(TestCase):
    def test_company_map(self):
        expected = {
                'comp0': Company('comp0', 'Company 0', '', {'comp1', 'comp2'}),
                'comp1': Company('comp1', 'Company 1', 'comp0', set({'comp3', 'comp5'})),
                'comp2': Company('comp2', 'Company 2', 'comp0', set()),
                'comp3': Company('comp3', 'Company 3', 'comp1', set({'comp4'})),
                'comp4': Company('comp4', 'Company 4', 'comp3', set()),
                'comp5': Company('comp5', 'Company 5', 'comp1', set()),
                }
        company_map = read_company_map(StringIO(TEST_COMPANIES))
        self.assertDictEqual(company_map, expected)

    def test_create_path(self):
        company_map = read_company_map(StringIO(TEST_COMPANIES))
        path = create_path(company_map['comp5'], company_map)

        for comp, expected_id in zip(path, ['comp0', 'comp1', 'comp5']):
            with self.subTest(expected_id):
                self.assertEqual(comp.company.id, expected_id)

    def test_count_parcels(self):
        owner_reader = StringIO(TEST_OWNERSHIP)
        expected = { 'comp0': 1, 'comp1': 1, 'comp2': 2, 'comp3': 1, 'comp4': 3}
        parcel_counts = read_count_by_company(owner_reader)
        self.assertDictEqual(parcel_counts, expected)

    def test_company_text(self):
        companies = [
                ((1, Company('a', 'comp A', '', set()), 1), '| - a; comp A; owner of 1 land parcel\n'),
                ((2, Company('b', 'comp B', '', set()), 0), '| | - b; comp B; owner of 0 land parcels\n'),
                ((0, Company('c', 'comp C', '', set()), 10), 'c; comp C; owner of 10 land parcels\n'),
                ]
        for comp in companies:
            with self.subTest(comp[0][1].name):
                text = company_text(*comp[0])
                self.assertEqual(text, comp[1])

    def test_current_company_text(self):
        text = company_text(1, Company('a', 'comp A', '', set()), 1, True)
        self.assertEqual(text, '| - a; comp A; owner of 1 land parcel ***\n')

if __name__ == '__main__':
    main()
