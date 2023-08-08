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

# --------------------------------- Helpers --------------------------------


def merge_results(result1, result2):
    merged_result = {}

    for doc in result1:
        merged_result[doc['_id']] = doc

    for doc in result2:
        if doc['_id'] in merged_result:
            merged_result[doc['_id']].update(doc)
        else:
            merged_result[doc['_id']] = doc

    return list(merged_result.values())


# --------------------------------- Documents --------------------------------

def countAnnotations(db):
    """Returns count of annotations"""

    if "pages.annotations" in db.list_collection_names():
        return db.pages.annotations.count_documents({})

    return 0


def fetchTasks(db, query={}, fields: dict = {}, limit: int = 0, sampling: bool = True):
    """Returns a batch of scraping tasks"""

    num_ids = limit * 100
    num_selected = limit

    tasks = []

    # Set default fields
    default_fields = ["_id", "landing_url", "target_url",
                      "content_requests", "annotations"]
    for field in default_fields:
        fields[field] = 1

    try:
        if not sampling:
            tasks = list(db.pages.content.find(query, fields).limit(limit))
            selected_object_ids = [task["_id"] for task in tasks]

            # Query for annotations using the selected ObjectIDs
            annotations = list(db.pages.annotations.find(
                {'_id': {'$in': selected_object_ids}}))

            # print("Annotations", annotations[0])
            merge_results(tasks, annotations)

        else:
            # Generate a random skip offset
            n_total = db.pages.content.count_documents(query)
            max_skip = max(0, n_total - num_ids)
            random_skip = random.randint(0, max_skip)

            # Get ObjectIDs with the random skip
            random_documents = db.pages.content.find(
                query, {"_id": 1}).skip(random_skip).limit(num_ids)
            random_object_ids = [doc['_id'] for doc in random_documents]

            # Randomly select 100 ObjectIDs from the list
            selected_object_ids = random.sample(
                random_object_ids, num_selected)

            # Query documents using the selected ObjectIDs
            tasks = list(db.pages.content.find(
                {'_id': {'$in': selected_object_ids}}, fields))

            # Query for annotations using the selected ObjectIDs
            annotations = list(db.pages.annotations.find(
                {'_id': {'$in': selected_object_ids}}))

            # print("Annotations", annotations[0])
            merge_results(tasks, annotations)

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

    document_id = ObjectId(id)

    # Update or insert the document with the new property
    result = db.pages.annotations.update_one(
        {'_id': document_id}, {'$set': {f'annotations.{annotator_id}': values.get(annotator_id)}}, upsert=True)

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
