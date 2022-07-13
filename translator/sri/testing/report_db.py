from os import environ

from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

RUNNING_INSIDE_DOCKER = environ.get('RUNNING_INSIDE_DOCKER', False)

# TODO: need to figure out how to configure a more robust
#       user and password, inside the Docker Compose run
user: str = environ.get('MONGO_INITDB_ROOT_USERNAME', "root")
password: str = environ.get('MONGO_INITDB_ROOT_PASSWORD', "example")
host: str = "mongo" if RUNNING_INSIDE_DOCKER else "localhost"

_mongodb_uri = "mongodb://%s:%s@%s" % (quote_plus(user), quote_plus(password), host)

_mongodb_client = MongoClient(
    host=_mongodb_uri,    # host: Optional[Union[str, Sequence[str]]] = None,
    port=27017,  # port: Optional[int] = None,
    # document_class: Optional[Type[_DocumentType]] = None,
    # tz_aware: Optional[bool] = None,
    # connect: Optional[bool] = None,
    # type_registry: Optional[TypeRegistry] = None,
    # **kwargs: Any,
)

_sri_testing_db: Database = _mongodb_client.sri_testing

_test_results_collection: Collection = _sri_testing_db.test_results

test_item = {
    "name": "Richard",
    "role": "da Boss"
}

entry_id = _test_results_collection.insert_one(test_item)

# test_results.delete_one(entry_id.inserted_id)


class TestReportDatabase:

    def __init__(self):
        self._mongodb_uri = "mongodb://%s:%s@%s" % (quote_plus(user), quote_plus(password), host)
        