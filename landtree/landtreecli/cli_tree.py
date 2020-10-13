'''
Provides text based tree structure
'''
import csv
from collections import namedtuple, Counter, defaultdict, deque

Company = namedtuple('Company', 'id name parent_id children_ids')
CompanyChildItr = namedtuple('CompanyChildItr', 'company child_itr')

def mk_tree(company_id, comp_reader, owner_reader, writer):
    ''' Produces tree structure - writing to writer
    - comp_reader - csv format: company_id,name,parent
    - owner_reader - csv format: land_id,company_id
    - writer output is written
    '''
    companies = read_company_map(comp_reader)
    counts = read_count_by_company(owner_reader)

    comp = companies.get(company_id)
    if comp is None:
        return

    # find the root company and build up a path
    path_to_comp = create_path(comp, companies)

    current_company = path_to_comp[0]

    # write the root
    writer.write(company_text(0, current_company.company,
        counts[current_company.company.id]))

    write_tree(path_to_comp, companies, counts, writer, company_id)

def write_tree(path_to_comp, companies, counts, writer, starred=None):
    '''
    exhaust all child iterators by starting at the root and drilling
    when needed (our path from root to node contains a child)
    '''
    level = 0
    while True:
        going_deeper = False
        for child_id in path_to_comp[level].child_itr:
            child = companies[child_id] # asuming valid data and child exists

            writer.write('  ')
            writer.write(company_text(level + 1, child, counts[child_id],
                child_id == starred))

            # if this child is on the path and is not the end
            if (level < len(path_to_comp) and
                    child_id == path_to_comp[level + 1].company.id):
                going_deeper = True
                level += 1
                break

        if not going_deeper:
            # we've reached the end of the children iterator
            if level <= 0: # end of root's children
                break
            level -= 1

def expand_tree(company_id, comp_reader, owner_reader, writer):
    ' Given a company, expand all children '

    companies = read_company_map(comp_reader)
    counts = read_count_by_company(owner_reader)

    target_company = companies[company_id]

    current_iter = CompanyChildItr(target_company,
            iter(sorted(target_company.children_ids)))
    path = deque()

    while True:
        going_deeper = False

        for child_id in current_iter.child_itr:
            child = companies[child_id] # asuming valid data and child exists
            writer.write(company_text(len(path) + 1, child, counts[child_id]))

            if child.children_ids:
                path.append(current_iter)

                current_iter = CompanyChildItr(child,
                        iter(sorted(child.children_ids)))
                going_deeper = True
                break

        if not going_deeper:
            if not path:
                break
            current_iter = path.pop()


def create_path(target_comp, companies):
    ' Creates a path from the root to a given company with child iterators '
    path_to_comp = [CompanyChildItr(target_comp, [])]

    # allow for empty string - don't compare with None
    while parent_id := path_to_comp[0].company.parent_id:
        parent = companies.get(parent_id)
        # each item has a Company and a new generator for it's children
        # this will remember where we are when we iterate the children
        child_iter = CompanyChildItr(parent, iter(sorted(parent.children_ids)))
        path_to_comp.insert(0, child_iter)

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
