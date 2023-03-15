import psycopg2
from faker import Faker
from py2neo import Graph, Node, Relationship

# Connect to Neo4j
graph = Graph("bolt://localhost:7687", auth=("neo4j", "password"))

# Clear the data in Neo4j
graph.run("MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    port=7777,
    database="mydatabase",
    user="myuser",
    password="mypassword"
)

# Create a cursor object
cur = conn.cursor()

# Clear the data in PostgreSQL
cur.execute("TRUNCATE TABLE users;")
cur.execute("TRUNCATE TABLE relationships;")
# Drop the tables
cur.execute("DROP TABLE users;")
cur.execute("DROP TABLE relationships;")
conn.commit()

# Close the cursor and database connection
cur.close()
conn.close()
