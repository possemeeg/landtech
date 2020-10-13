# landtree - Corporate Land Ownership Tree
## General
- Effort was made to read the companys on only one iteration. This required storing the sets of children
from companies that had not yet been read. This slightly complicates the code.
- It is assumed that the data is in tact - no error checking is done
- Memory structures (company map and company ownership counts) will need to be replaced by storage that
is able to hold and persist large amounts of data (such as Redis or Hazelcast).
- I'm aware that I have too similar loops in cli_tree.py. Given time, I'd considering refactoring this if
it wasn't going to make it messy.
## Region information
If region information is stored in the company or land ownership files, filtering can be done when the files
are being read and the memory structures are being created.
## Cyclic company structure
This code assumes conventional tree structure using dictionaries with company id as key. Cyclic data will
not work. If one was going to allow cyclic data, a linked directed graph would be a better data structure. 
One could have each company linking to parents and children. The printing would also get messy. Sorry
I don't have enough time to go down this path. It may make the code messier!
## Requirements
Python 3.8 or higher
## Running
```
python3 landtree.py --mode=from_root <compid>
python3 landtree.py --mode=expand <compid>
```
## Modes
### From Root (from_root)
Given a node, a tree will be printed out from the root of the given node to the node. It will include all
childen of nodes visited on the rootward journey
### Expand (expand)
Given a node. it will print a tree with it as the root. It will not print it again
## Running the unit tests
```
python3 test.py
```
