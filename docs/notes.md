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

- Consistent hashing variation to distribute the lead across multiple hosts (inside a circular ring)
- Each node has multiple points on the ring (virtual nodes)
- Assignment of positions on it is random
- Each node becomes responsible for the region in the ring between it and its predecessor node on the ring.
    - Departure or arrival of a node only affects immediate neighbors

### REPLICATION (N)

- Needed to achieve high availability and durability
- Each data is replicated at N hosts
- Coordinator node is responsible for the replication of data that fall within its range (N-1 successors, only distinct physical nodes)
- Preference list: list of nodes that is responsible for storing a particular key
    - Every node in the system can determine it for any key

### DATA VERSIONING

- Dynamo provides eventual consistency
    - Updates propagated to all replicas asynchronously
- Dynamo treats the result of each modification as a new and immutable version of the data
    - Multiple versions of an object can be present at the same time
- Dynamo uses vector clocks to capture causality between different versions of the same object
    - They are a list of (node, counter)
    - If the counters on the first object <= all of the nodes in the second clock then the first is an ancestor of the second and can be forgotten. Otherwise, the two changes are considered to be in conflict and require reconciliation.
- When we update an object, we must pass the context (obtained in the previous read), which contains the vector clock
    - Due to failures, a node thats not on the first N of the preference list may need to get the job done, and vector clock will grow (+1 node). Because of that its a good practice to limit vector clocks (10)

### GET AND PUT

- Coordinator: node that handles read or write (typically first of the preference list)
- R is the minimum number of nodes that must participate in a successful read operation
    - 1 Coordinator node receives request for a get of a key
    - 2 Coordinator requests all reachable highest N nodes
    - 3 Waits for R responses
    - 4 If it receives multiple versions of that key (object) it output all that are causally unrelated (except the ones explained on line 63), and then
    - 5 Reconciled version is written back --> SUCCESSFUL READ
- W is the minimum number of nodes that must participate in a successful write operation
    - 1 Coordinator node receives request for a put of a key
    - 2 Coordinator generates vector clock for new version, writes it locally
    - 3 Sends new version (and new vector clock) to the N higher reachable nodes
    - 4 If at least W-1 respond --> SUCCESSFUL WRITE
- R and W < N

