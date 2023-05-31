# ===========================================================================
#                            Database Operation Helpers
# ===========================================================================

#from typing import List
from dotenv import load_dotenv
from bson import ObjectId
import pymongo as pm
import gridfs
import os

# --------------------------------- Connection --------------------------------


def getConnection(
    connection_string: str = "", database_name: str = "", use_dotenv: bool = False
):
    "Returns MongoDB and GridFS connection"

    # Load config from config file
    if use_dotenv:
        load_dotenv()
        connection_string = os.getenv("CONNECTION_STRING")
        database_name = os.getenv("DATABASE_NAME")

    # Use connection string
    conn = pm.MongoClient(connection_string)
    db = conn[database_name]
    fs = gridfs.GridFS(db)

    return fs, db


# --------------------------------- Documents --------------------------------


def fetchTasks(db, batch_id: int, status: str, limit: int = 0, fields: dict = {}):
    """Returns a batch of scraping tasks"""
    
    # Add status code to fields
    fields["status_code"] = 1
    query = {"$and": []}

    if batch_id and status:
        query["$and"] = [{"status": status}, {"batch_id": batch_id}]
    elif status:
        # Consider all batches if no batch ID specified
        query["$and"] = [{"status": status}]
    elif batch_id:
        # Consider all status if no status specified
        query["$and"] = [{"batch_id": batch_id}]

    # Sorting requires a lot of memory
    tasks = db.pages.content.find(query, fields).limit(limit)

    return list(tasks)

def fetchTask(db, id: str, fields: dict = {}):
    """Returns a single scraping tasks"""
    
    # Sorting requires a lot of memory
    query = {"_id": id}
    task = db.pages.content.find_one(query, fields)

    return task


def updateTask(db, id: str, annotator_id, values: dict = {}):
    """Updates scraping task in database"""

    filter = {"_id": ObjectId(id)}
    values = {
        '$set': {
            "annotated": True,
            'annotations': {
                annotator_id: values,
            }
        }
    }
    r = db.pages.content.update_one(filter, values)
    return r

# --------------------------------- Files --------------------------------


def getPageContent(fs: gridfs, id: str, encoding="UTF-8"):
    """Retrieves a file from GridFS"""
    f = fs.get(ObjectId(id))
    return f.read().decode(encoding)


def getPageContentInfo(db, id: str):
    """Retrieves a file from GridFS"""
    info = db.fs.files.find_one({"_id": ObjectId(id)})
    return dict(info)