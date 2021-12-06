#By Sam Kreter
#For use by Microsoft and other parties to demo
#Azure Container Service, Azure Container Instances
#and the experimental ACI-connector
import os
from azure.storage.blob import ContainerClient
import sqlite3


COPY_PICS_NUM = 1
DATABASE_NAME = os.getenv('DB_PATH', "") + 'jobs.db'

class DbAzureBlob:
    
    def __init__(self):
        AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

        if not AZURE_STORAGE_CONNECTION_STRING:
            raise EnvironmentError("Must have env variables AZURE_STORAGE_CONNECTION_STRING set for this to work.")

        block_container_service = ContainerClient.from_connection_string(
            conn_str=AZURE_STORAGE_CONNECTION_STRING, container_name="test1")


    def getImageFromAzureBlob(self, filename_src, filename_dest):
        try:
            # self.block_blob_service.get_blob_to_path('pictures', filename_src, filename_dest)
            with open(filename_dest, "wb") as my_blob:
                blob_data = self.block_container_service.download_blob(filename_src)
                blob_data.readinto(my_blob)
            return True
        except Exception as ex:
            print("getImageFromAzureBlob: ", ex)
            return False


    def getAllImagesFromAzureBlob(self, dest_folder):
        # generator = self.block_blob_service.list_blobs('pictures')
        generator = self.block_container_service.list_blobs()

        success = []

        for blob in generator:
            try:
                # self.block_blob_service.get_blob_to_path(container, blob.name, dest_folder + blob.name)
                with open(dest_folder + blob.name, "wb") as my_blob:
                    blob_data = self.block_container_service.download_blob(blob.name)
                    blob_data.readinto(my_blob)
                success.append(True)
            except Exception as ex:
                print("getAllImagesFromAzureBlob: ", ex)
                success.append(False)
            
        return all(success)

    def doubleDatabase(self):
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.execute("SELECT * FROM jobs;")
        for row in cursor:
            conn.execute("INSERT INTO jobs (filename) \
                VALUES (\"" + row[1] + "\");")
        conn.commit()

    def setupDatabase(self):
        conn = sqlite3.connect(DATABASE_NAME)
        print("Reseting the database")

        conn.execute('''DROP TABLE IF EXISTS jobs;''')
        conn.execute('''
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename NOT NULL,
                processed INTEGER DEFAULT 0 NOT NULL,
                detected INTEGER DEFAULT NULL,
                start_time INTEGER DEFAULT NULL,
                end_time INTEGER DEFAULT NULL,
                worker_id TEXT DEFAULT NULL,
                processed_time DEFAULT NULL
            );
            ''')

        conn.commit()

        # generator = self.block_blob_service.list_blobs('pictures')
        generator = self.block_container_service.list_blobs()
        for blob in generator:
            if(blob.name[:2] == "._"):
                blob.name = blob.name[2:]
            for i in range(COPY_PICS_NUM):
                conn.execute("INSERT INTO jobs (filename) \
                    VALUES (\"" + blob.name + "\");")

        conn.commit()
