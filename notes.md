## KEYPOINTS
- Conflicts are solved in the reads, that way writes are never rejected
- Dynamo is targeted mainly at applications that need an “always writeable” data store where no updates are rejected due to failures or concurrent writes
- Some services may be stateless (aggregator services), they just redirect to other services
- We assume all nodes can be trusted
- Apps that use Dynamo don't require a complex relational schema
- Dynamo can be characterized as a zero-hop DHT, where each node maintains enough routing information locally to route a request to the appropriate node directly.
- Dynamo is designed to be an eventually consistent data store; that is all updates reach all replicas eventually.
- Dynamo targets applications that require only key/value access with primary focus on high availability where updates are not rejected even in the wake of network partitions or server failures.

### Design
- Incremental scalabilty - Ability to scale out one node
- Symmetry - Each node should have same set of responsability as its peers
- Decentralization
- Work distribution proportional to the capabilities of individual servers

## SLA - Service Level Agreements

- Formally negociated contract between server and client, where they agree on several system-related chatacteristics (expected client request rate and service latency)
- Its important to obey to these parameters because services often have multiple dependencies (call graph depth > 1)
- Example: Guarantee: Response within 300ms for 99.9% of requests for peak client load of 500 requests per second

## SYSTEM ARCHITECTURE

### INTERFACE

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

### PARTITIONING
