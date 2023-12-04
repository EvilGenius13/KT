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
  cluster = Cluster(['scylla'], auth_provider=auth_provider, protocol_version=4)

async def get_guild_settings(session, guild_id):
    """
    Retrieves the settings for a specific guild from the database.

    Args:
    session (Cluster.Session): The Cassandra session object.
    guild_id (str): The ID of the guild.

    Returns:
    dict: A dictionary containing the settings, or None if the guild is not found.
    """

    query = """
    SELECT voice_greeting, voice_break_time, voice_schedule_break, break_hours, break_minutes, time_zone
    FROM bot_keyspace.guilds WHERE guild_id = %s"""

    result = session.execute(query, [guild_id])
    row = result.one()
    if row:
        return {
            "voice_greeting": row.voice_greeting,
            "voice_break_time": row.voice_break_time,
            "voice_schedule_break": row.voice_schedule_break,
            "break_hours": row.break_hours,
            "break_minutes": row.break_minutes,
            "time_zone": row.time_zone,
        }
    else:
        return None
    
async def update_guild_settings(session, guild_id, settings):
    """
    Updates the settings for a specific guild in the database.

    Args:
    session (Cluster.Session): The Cassandra session object.
    guild_id (str): The ID of the guild.
    settings (dict): A dictionary containing the settings to be updated.
    """
    query = """
    UPDATE bot_keyspace.guilds 
    SET voice_greeting = %s, voice_break_time = %s, voice_schedule_break = %s, time_zone = %s, break_hours = %s, break_minutes = %s
    WHERE guild_id = %s
    """
    values = (
        settings['voice_greeting'], 
        settings['voice_break_time'], 
        settings['voice_schedule_break'],
        settings['time_zone'],
        settings['break_hours'],
        settings['break_minutes'],
        guild_id
    )
    session.execute(query, values)
    
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
                voice_greeting boolean,
                voice_break_time boolean,
                voice_schedule_break boolean,
                break_hours int,
                break_minutes int,
                time_zone text
            )
            """)

        # Create Wishlist Table
        session.execute("""
            CREATE TABLE IF NOT EXISTS wishlists (
                guild_id text,
                app_id text,
                app_name text,
                PRIMARY KEY (guild_id, app_id)
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

