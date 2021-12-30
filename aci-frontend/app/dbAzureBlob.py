#By Sam Kreter
#For use by Microsoft and other parties to demo
#Azure Container Service, Azure Container Instances
#and the experimental ACI-connector
import os
from azure.storage.blob import BlobServiceClient
import sqlite3

COPY_PICS_NUM = 1

class DbAzureBlob:
    
    def __init__(self):
        AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

        if not AZURE_STORAGE_CONNECTION_STRING:
            raise EnvironmentError("Must have env variables AZURE_STORAGE_CONNECTION_STRING set for this to work.")
        if not AZURE_STORAGE_CONTAINER_NAME:
            raise EnvironmentError("Must have env variables AZURE_STORAGE_CONTAINER_NAME set for this to work.")

        self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        self.block_container_service = self.blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)


    def getImageFromAzureBlob(self, filename_src, filename_dest):
        try:
            with open(filename_dest, "wb") as my_blob:
                blob_data = self.block_container_service.download_blob(filename_src)
                blob_data.readinto(my_blob)
            return True
        except Exception as ex:
            print("getImageFromAzureBlob: ")
            return False


    def getAllImagesFromAzureBlob(self, dest_folder):
        generator = self.block_container_service.list_blobs()

        success = []

        for blob in generator:
            try:
                with open(dest_folder + blob.name, "wb") as my_blob:
                    blob_data = self.block_container_service.download_blob(blob.name)
                    blob_data.readinto(my_blob)
                success.append(True)
            except Exception as ex:
                print("getAllImagesFromAzureBlob: ", ex)
                success.append(False)
            
        return all(success)

    def doubleDatabase(self):
        conn = sqlite3.connect('jobs.db')
        cursor = conn.execute("SELECT * FROM jobs;")
        for row in cursor:
            conn.execute("INSERT INTO jobs (filename) \
                VALUES (\"" + row[1] + "\");")
        conn.commit()

    def setupDatabase(self):
        conn = sqlite3.connect('jobs.db')

        conn.execute('''DROP TABLE IF EXISTS jobs;''')
        conn.execute('''
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename NOT NULL,
                processed INTEGER DEFAULT 0 NOT NULL,
                detected INTEGER DEFAULT NULL
            );
            ''')

        conn.execute('DROP TABLE IF EXISTS time;')
        conn.execute('''
            CREATE TABLE time (
            id INTEGER PRIMARY KEY,
            start_time TEXT,
            finish_time TEXT,
            finished INTEGER,
            started INTEGER
        );
        ''')

        conn.execute('INSERT INTO time values(1,"2017-09-23 18:28:24","2017-09-23 18:28:24",0,0);')

        generator = self.block_container_service.list_blobs()
        for blob in generator:
            if(blob.name[:2] == "._"):
                blob.name = blob.name[2:]
            for i in range(COPY_PICS_NUM):
                conn.execute("INSERT INTO jobs (filename) \
                    VALUES (\"" + blob.name + "\");")

        conn.commit()
