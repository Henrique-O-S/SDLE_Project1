# Armazon - Class 8 Group 1

- Diogo Filipe Ferreira da Silva up202004288
- Henrique Oliveira Silva up202007242
- Tiago Nunes Moreira Branquinho up202005567

## Planned Project Design

To satisfy the need of creating a local-first shopping list application that allows data sharing among users, it is intended to implement a decentralized distributed architeture. 
Data storage will be distributed across multiple nodes, which will be able to communicate among themselves to allow data replication, thus providing fault tolerance and reducing data access times. The replication will be asynchronous, meaning it is designed to be an eventually consistent data store; that is all updates reach all replicas eventually.

Each shopping list will be mapped, through consistent hashing, to one of the server nodes, which means each request to it should always be accessing the same node. This also ensures load balancing. In case of failure, the system will be aware through gossip and therefore look for a node that contains a replica.

Clients will hold a local data storage, that will remain updated even in case of server failure and will allow to update the server data once it is back to availability.
Clients should also be able to access the same shopping list concurrently and it should be “always writeable”, where no updates are rejected due to failures or concurrent writes.

At any point, in case of data discrepancies among any intervients of the system (either server to server or client to server) a merge shall be conducted. In case of conflicts, the last updated data will remain. Conflicts are always solved in the reads, that way writes are never rejected.

### Interface

- get(key) and put(key, context, object), objects are associated with a key.
- get:
    - Locates object replicas (with that key) in storage system
    - Returns single object or list of objects with conflicting versions, along with a context
- put:
    - Determines where replicas should be placed (based on key)
        - MD5 hash applied on key to generate 128 bit identifier
    - Writes them to disk
    - Context stored along with the object
        - Encodes system metadata about the object, version etc...
        - Allows system to verify validity of the context object

### Sistem Design Diagram

 ![System Design](/docs/design_draft.drawio.png "Sytem Design")

This is a reduced example of the designe architeture. In a larger scale each shopping list should contain more replicas.
