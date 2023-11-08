import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

from dotenv import load_dotenv
load_dotenv()


scylla_username = os.getenv('SCYLLA_USERNAME')
scylla_password = os.getenv('SCYLLA_PASSWORD')

if os.getenv('LOCAL_ENV') == 'true':
    cluster = Cluster(['127.0.0.1'], protocol_version=4)
else:
  auth_provider = PlainTextAuthProvider(username=scylla_username, password=scylla_password)
  cluster = Cluster(['127.0.0.1'], auth_provider=auth_provider)

def setup_db_connection():
    # The code to establish a connection and confirm it
    try:
        session = cluster.connect()
        # Confirm connection
        row = session.execute("SELECT cluster_name FROM system.local").one()
        if row:
            print(f"Successfully connected to ScyllaDB cluster: {row.cluster_name}")
        else:
            print("Connection to ScyllaDB cluster established, but couldn't retrieve cluster name.")
    except Exception as e:
        print(f"Failed to connect to ScyllaDB: {e}")
        # You might want to exit the program or handle reconnection here

