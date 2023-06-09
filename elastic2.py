from elasticsearch import Elasticsearch


def search_supervisors(topics):
    # es_client = Elasticsearch("https://localhost:9200", basic_auth=("elastic", "TDTeGqLzhDAacK=Vuapo"), verify_certs=True, )
    es_client = Elasticsearch(
        cloud_id="elastic cloud id",
        basic_auth=("elastic", "password"),
    )

    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "Areas_of _expertise": {
                                "query": topic,
                                "analyzer": "stop",
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                    for topic in topics
                ],
                "minimum_should_match": 1
            }
        }
    }

    res = es_client.search(index="staffers", body=query)
    hits = res['hits']['hits']

    supervisors = []
    for hit in hits:
        supervisor = {
            "Name": hit['_source']['Name'],
            "Email address": hit['_source']['Email address'],
        }
        supervisors.append(supervisor)

    return supervisors


def get_supervisors(topics):
    # topics = ["Assessing the usability and effectiveness of voice recognition technology in electronic health records systems"]
    supervisors = search_supervisors(topics)
    print(supervisors)
    return supervisors
