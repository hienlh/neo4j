import psycopg2
from faker import Faker
from py2neo import Graph, Node, Relationship
from tqdm import tqdm
import time
import random

start_time = time.time()
# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    port=7777,
    database="mydatabase",
    user="myuser",
    password="mypassword"
)

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Create a cursor object
cur = conn.cursor()

# Create tables in Postgres
cur.execute(
    "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name TEXT, email TEXT);")
cur.execute("CREATE TABLE IF NOT EXISTS relationships (id SERIAL PRIMARY KEY, node1_id INTEGER, node2_id INTEGER);")
conn.commit()

# Create a Faker object
fake = Faker()

# Set the batch size for each chunk
batch_size = 1000

# Generate some random data
num_nodes = 1000000
nodes = []
print("Generating random data...")
for i in tqdm(range(num_nodes)):
    name = fake.name()
    email = fake.email()
    node = Node("Label", name=name, email=email)
    nodes.append(node)

print("Inserting data to Neo4j and PostgreSQL...")
# Insert the nodes in batches
for i in tqdm(range(0, num_nodes, batch_size)):
    # Get the chunk of nodes for this batch
    chunk = nodes[i:i+batch_size]

    # Add the nodes to Neo4j
    subgraph = chunk[0]
    for node in chunk[1:]:
        subgraph = subgraph | node
    graph.create(subgraph)

    # Add the nodes to PostgreSQL
    cur.executemany("INSERT INTO users (name, email) VALUES (%s, %s)", [
                    (node["name"], node["email"]) for node in chunk])
    conn.commit()

# # Add the nodes to Neo4j
# subgraph = nodes[0]
# for node in nodes[1:]:
#     subgraph = subgraph | node
# graph.create(subgraph)

# # Add the nodes to PostgreSQL
# cur.executemany("INSERT INTO users (name, email) VALUES (%s, %s)", [
#                 (node["name"], node["email"]) for node in nodes])
# conn.commit()

# Create random relationships between the nodes
# print("Creating random relationships...")
# for i in tqdm(range(num_nodes)):
#     node1_id = i + 1
#     node2_id = (i + 1) % num_nodes + 1
#     rel = Relationship(nodes[node1_id - 1],
#                        "RELATIONSHIP_TYPE", nodes[node2_id - 1])
#     graph.create(rel)
#     cur.execute(
#         "INSERT INTO relationships (node1_id, node2_id) VALUES (%s, %s)", (node1_id, node2_id))
# conn.commit()
# Create random relationships between the nodes
print("Creating random relationships...")
for chunk_start in range(0, num_nodes, batch_size):
    chunk_end = min(chunk_start + batch_size, num_nodes)
    rels = []
    node2_ids_list = []

    print("Chunk: ", chunk_start, " to ", chunk_end, " of ", num_nodes, " nodes")
    for i in range(chunk_start, chunk_end):
        node1 = nodes[i]
        num_relations = random.randint(0, 2)
        node2_ids = random.sample(range(num_nodes), num_relations)
        node2_ids_list.append(node2_ids)
        for node2_id in node2_ids:
            node2 = nodes[node2_id]
            rels.append(Relationship(node1, "RELATIONSHIP", node2))

    subgraph = rels[0]
    for rel in rels[1:]:
        subgraph = subgraph | rel
    graph.create(subgraph)

    cur.executemany("INSERT INTO relationships (node1_id, node2_id) VALUES (%s, %s)",
                        [(i, node2_id) for i, node2_ids in enumerate(node2_ids_list) for node2_id in node2_ids])
    conn.commit()

# Close the cursor, database connection, and Neo4j connection
cur.close()
conn.close()

end_time = time.time()
print(f"Inserted data in: {end_time - start_time} seconds")
