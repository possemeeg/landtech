import pytest
from io import StringIO

def lines_to_strio(lines):
    strio = StringIO()
    for line in lines:
        strio.write(line)
    strio.seek(0)
    return strio

@pytest.fixture
def companies():
    lines = [
            'company_id,name,parent\n',
            'comp1,Company 1,comp0\n',
            'comp2,Company 2,comp0\n',
            'comp5,Company 5,comp1\n',
            'comp3,Company 3,comp1\n',
            'comp0,Company 0,\n',
            'comp4,Company 4,comp3\n',
            ]
    return lines_to_strio(lines)

@pytest.fixture
def ownership():
    lines = [
            'land_id,company_id\n',
            'land0,comp1\n',
            'land1,comp0\n',
            'land2,comp2\n',
            'land2.1,comp2\n',
            'land3,comp3\n',
            'land4,comp4\n',
            'land4.1,comp4\n',
            'land4.2,comp4\n',
            ]
    return lines_to_strio(lines)
