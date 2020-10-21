'''
Provides text based tree structure
'''
import csv
from collections import namedtuple, Counter, defaultdict, deque
from functools import partial

#Company = namedtuple('Company', 'id name parent_id children_ids')
CompanyChildItr = namedtuple('CompanyChildItr', 'company child_itr')

class Company:
    __slots__ = ['id', 'name', 'parent_id', 'children_ids', '_full_count']
    
    def __init__(self, id, name, parent_id, children_ids):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.children_ids = children_ids
        self._full_count = None
        
    #def full_count(self, counter):
    #    if self._full_count is None:
    #        self._full_count = counter(self.id)
    #    return self._full_count

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return (f'Company({self.id}, {self.name}, {self.parent_id}, ' +
                f'{self.children_ids})')

class CliCore:
    def __init__(self, comp_reader, owner_reader):
        self.companies = read_company_map(comp_reader)
        self.counts = read_count_by_company(owner_reader)
        self.company_counter = partial(count_for_company, company_map=self.companies, counts=self.counts)

    def full_count(self, company):
        return self.company_counter(company)

def mk_tree(company_id, comp_reader, owner_reader, writer):
    ''' Produces tree structure - writing to writer
    - comp_reader - csv format: company_id,name,parent
    - owner_reader - csv format: land_id,company_id
    - writer output is written
    '''
    core = CliCore(comp_reader, owner_reader)

    comp = core.companies.get(company_id)
    if comp is None:
        return

    # find the root company and build up a path
    path_to_comp = create_path(comp, core.companies)

    # write the root
    writer.write(company_text(0, path_to_comp[0], core.full_count(path_to_comp[0].id)))
    write_expanded_tree(path_to_comp[0].id, core, writer, [c.id for c in path_to_comp[1:]], '  ')

def expand_tree(company_id, comp_reader, owner_reader, writer):
    ' Given a company, expand all children '

    core = CliCore(comp_reader, owner_reader)

    return write_expanded_tree(company_id, core, writer)

def write_expanded_tree(company_id, core, writer, expand_path=None, left_margin=''):
    target_company = core.companies[company_id]

    current_iter = CompanyChildItr(target_company,
            iter(sorted(target_company.children_ids)))
    path = deque()
    level = 0

    while True:
        going_deeper = False

        for child_id in current_iter.child_itr:
            child = core.companies[child_id] # asuming valid data and child exists
            writer.write(left_margin + company_text(len(path) + 1,
                child, core.full_count(child.id),
                expand_path is not None and expand_path[-1] == child_id))

            if (expand_path is None or (
                    level < len(expand_path)
                    and expand_path[level] == child_id)):
            #if child.children_ids:
                path.append(current_iter)

                current_iter = CompanyChildItr(child,
                        iter(sorted(child.children_ids)))
                going_deeper = True
                level += 1
                break

        if not going_deeper:
            if not path:
                break
            level -= 1
            current_iter = path.pop()


def create_path(target_comp, companies):
    ' Creates a path from the root to a given company with child iterators '
    path_to_comp = [target_comp]

    # allow for empty string - don't compare with None
    while parent_id := path_to_comp[0].parent_id:
        parent = companies.get(parent_id)
        path_to_comp.insert(0, parent)

    return path_to_comp

def read_company_map(comp_reader):
    '''
    given a reader, produces a map or Company items
    A company item will include the id, name and parent,
    as well as a set of its children company ids
    Assumptions:
    - csv format: company_id,name,parent
    - input includes header
    - input is valid (no error checking)
    - one row per company id (no duplicates)
    - no striping of input data is required
    '''
    reader = csv.reader(comp_reader)
    next(reader) # consume the header

    # the return value
    companies = dict()

    # only keeps sets of children by id for companies not yet in main map
    # by the end of this function, this will be empty because all values
    # will have been added to companies (assuming all parents in source)
    child_sets = defaultdict(set)

    for row in reader:
        # add the company to the company list
        # if it has previously stored children, add them and remove
        # from parents map
        company_id = row[0]
        new_company = Company(*row, child_sets.pop(company_id, set()))
        companies[company_id] = new_company

        # parent id is either in child_sets or alreaded added to companies
        if new_company.parent_id: # allow for empty string - don't test with None
            parent = companies.get(new_company.parent_id)
            if parent:
                # parent alread in main map
                parent.children_ids.add(company_id)
            else:
                # parent not yet visited in csv iteration
                child_sets[new_company.parent_id].add(company_id)

    return companies

def read_count_by_company(ownership_reader):
    '''
    given a reader, returns a map of counts by company id
    Assumptions:
    - no duplicates
    - no stripping required
    - format of csv valid
    '''
    reader = csv.reader(ownership_reader)
    next(reader) # consume the header

    return Counter(row[1] for row in reader)

def company_text(level, company, count, is_target=False):
    'simple helper to produce company line given leve, company and parcel count'
    margin = '| ' * level + '- ' if level else ''
    plural = 's' if count != 1 else ''
    stats = f'owner of {count} land parcel{plural}'
    stars = (' ' + '*' * 3) if is_target else ''
    return f'{margin}{company.id}; {company.name}; {stats}{stars}\n'

def count_for_company(company, *, company_map, counts):
    count = counts.get(company, 0)
    for child in company_map[company].children_ids:
        count += count_for_company(child, company_map=company_map, counts=counts)
    return count
