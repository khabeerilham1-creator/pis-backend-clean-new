from bson import ObjectId

def serialize_doc(doc):
    doc["_id"] = str(doc["_id"])

    # convert patient_id if exists
    if "patient_id" in doc:
        doc["patient_id"] = str(doc["patient_id"])

    return doc