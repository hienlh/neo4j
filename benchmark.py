import psycopg2
from py2neo import Graph
import time

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

# Define the start and end nodes for the shortest path
start_node_id = 1
end_node_id = 2

# Benchmark Neo4j
start_time = time.time()
result = graph.run("PROFILE MATCH (start:Label {id: $start_node_id}), (end:Label {id: $end_node_id}), path = shortestPath((start)-[:ACTED_IN*]-(end)) RETURN path",
                   start_node_id=start_node_id, end_node_id=end_node_id)
# path = result.single()[0]
end_time = time.time()
neo4j_time = end_time - start_time

# Benchmark PostgreSQL
cur = conn.cursor()
cur.execute("ALTER DATABASE mydatabase SET pg_pathman.enable = on;")
cur.close()

start_time = time.time()
cur = conn.cursor()
cur.execute("SELECT * FROM pg_shortest_path(%s, %s, 'RELATIONSHIP.cost')",
            (start_node_id, end_node_id))
path = cur.fetchall()
cur.close()
conn.close()
end_time = time.time()
postgres_time = end_time - start_time

# Print the benchmark results
print(f"Neo4j shortest path time: {neo4j_time} seconds")
print(f"PostgreSQL shortest path time: {postgres_time} seconds")
