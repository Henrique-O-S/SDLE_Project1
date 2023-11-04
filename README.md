# Armazon - Class 8 Group 1

- Diogo Filipe Ferreira da Silva up202004288
- Henrique Oliveira Silva up202007242
- Tiago Nunes Moreira Branquinho up202005567

## Planned Project Design

To satisfy the need of creating a local-first shopping list application that allows data sharing among users, it is intended to implement a decentralized distributed architeture. 
Data storage will be distributed across multiple nodes, which will be able to communicate among themselves to allow data replication, thus providing fault tolerance and reducing data access times.

Each shopping list will be mapped, through consistent hashing, to one of the server nodes, which means each request to it should always be accessing the same node. In case of failure, the system will be aware through gossip and therefore look for a node that contains a replica.

Clients will hold a local data storage, that will remain updated even in case of server failure and will allow to update the server data once it is back to availability.
Clients should also be able to access the same shopping list concurrently.

At any point, in case of data discrepancies among any intervients of the system (either server to server or client to server) a merge shall be conducted. In case of conflicts, the last updated data will remain.

 ![System Design](/docs/design_draft.drawio.png "Sytem Design")

This is a reduced example of the designe architeture. In a larger scale each shopping list should contain more replicas.
