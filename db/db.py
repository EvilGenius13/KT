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
  cluster = Cluster(['scylla'], auth_provider=auth_provider)

def create_keyspace_and_tables(session):
    try:
        # Create Keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS bot_keyspace
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '3'}
            """)

        # Use the Keyspace
        session.execute("USE bot_keyspace")

        # Create Guild Table
        session.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id text PRIMARY KEY,
                guild_name text,
                voice_setting boolean
                -- Add other fields here
            )
            """)

        # Create Wishlist Table
        session.execute("""
            CREATE TABLE IF NOT EXISTS wishlists (
                user_id text,
                guild_id text,
                wishlist_items list<text>,
                PRIMARY KEY (user_id, guild_id)
                -- Add other fields here
            )
            """)

        print("Keyspace and Tables Created Successfully")
    except Exception as e:
        print(f"Error creating keyspace and tables: {e}")

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
    
        create_keyspace_and_tables(session)
        return session
    except Exception as e:
        print(f"Failed to connect to ScyllaDB: {e}")
        # You might want to exit the program or handle reconnection here

