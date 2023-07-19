# ===========================================================================
#                            Database Operation Helpers
# ===========================================================================

# from typing import List
from dotenv import load_dotenv
from bson import ObjectId
import pymongo as pm
import random
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


def fetchTasks(db, query={}, fields: dict = {}, limit: int = 0, sampling: bool = True):
    """Returns a batch of scraping tasks"""

    tasks = []

    # Set default fields
    default_fields = ["_id", "landing_url", "target_url",
                      "content_requests", "annotations"]
    for field in default_fields:
        fields[field] = 1

    try:
        if not sampling:
            tasks = list(db.pages.content.find(query, fields).limit(limit))
        else:
            n_total = db.pages.content.count_documents(query)
            n = min(limit, n_total)
            random_indexes = random.sample(range(n_total), n)
            tasks = [db.pages.content.find(query, fields).limit(
                n).skip(index)[0] for index in random_indexes]

        if not tasks:
            raise ValueError("No tasks matching the query were found.")

    except Exception as e:
        raise RuntimeError(f"Failed to fetch tasks: {str(e)}")

    return tasks


def fetchTask(db, id: str, fields: dict = {}):
    """Returns a single scraping tasks"""

    # Sorting requires a lot of memory
    query = {"_id": id}
    task = db.pages.content.find_one(query, fields)

    return task


def updateTask(db, id: str, annotator_id, values: dict = {}):
    """Updates scraping task in database"""
    ...

    # TODO: Commented out for testing purposes

    # filter = {"_id": ObjectId(id)}
    # values = {
    #     '$set': {
    #         "annotated": True,
    #         'annotations': {
    #             annotator_id: values,
    #         }
    #     }
    # }
    # r = db.pages.content.update_one(filter, values)
    # return r

# --------------------------------- Files --------------------------------


def getPageContent(fs: gridfs, id: str, encoding="UTF-8"):
    """Retrieves a file from GridFS"""
    f = fs.get(ObjectId(id))
    return f.read().decode(encoding)


def getPageContentInfo(db, id: str):
    """Retrieves a file from GridFS"""
    info = db.fs.files.find_one({"_id": ObjectId(id)})
    return dict(info)
