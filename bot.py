"""
Refreshes the metadata in a collection given the owner
"""
import json
from typing import List
import requests

LOOKS_RARE_GRAPHQL_ENDPOINT = "https://api.looksrare.org/graphql"
OWNER = "0x77FE1dDa1fDd034Ac69d277b0272b76B7C48c1E6"
COLLECTION = "0x8009250878eD378050eF5D2a48c70E24EB2edE7E"

def refresh_metadata():
    """Main method for the file"""
    print("refresh collection")
    all_ntfs = get_array_of_all_items(owner=OWNER, collection=COLLECTION)
    for nft in all_ntfs:
        refresh_metadata_for_item(token_id=nft, collection=COLLECTION)

def refresh_metadata_for_item(token_id: str, collection: str) -> bool:
    """Refreshes the metadata for an individual item"""
    query = get_query_for_item_metadata_refresh()
    variables = get_variables_for_item_metadata_refresh(token_id=token_id, collection=collection)
    headers = {"Content-Type": "application/json",
               "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"}
    response = requests.post(LOOKS_RARE_GRAPHQL_ENDPOINT, 
                             json={'query': query, 'variables': variables},
                             headers=headers)
    response_json = json.loads(response.text)
    if (response_json is None or
        response_json["data"] is None or
        response_json["data"]["refreshToken"] is None or
        response_json["data"]["refreshToken"]["success"] is None):
        print(f"{collection}: {token_id} - FAILED TO UPDATE")
        return False
    result = response_json["data"]["refreshToken"]["success"]
    result_wording = "FAILED TO UPDATE" if result is False else "UPDATED"
    print(f"{collection}: {token_id} - {result_wording}")
    return result

def get_array_of_all_items(owner: str, collection: str) -> List[str]:
    """Returns all of the items owned by an owner of the type specified by the collection"""
    headers = {"Content-Type": "application/json",
               "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)"}
    return_me = []
    should_continue = True
    curr_cursor = ""
    while should_continue:
        query = get_query_for_items()
        variables = get_variables_for_items(owner=owner, collection=collection,
                                   cursor=None if curr_cursor == "" else curr_cursor)
        response = requests.post(LOOKS_RARE_GRAPHQL_ENDPOINT, 
                                 json={'query': query, 'variables': variables}, 
                                 headers=headers)
        print(response.text)
        response_json = json.loads(response.text)
        if (response_json is None or
            response_json["data"] is None or
            response_json["data"]["tokens"] is None or
            len(response_json["data"]["tokens"]) == 0):
            should_continue = False
        else:
            for nft in response_json["data"]["tokens"]:
                curr_cursor = nft["id"]
                return_me.append(nft["tokenId"])
    return return_me

def get_query_for_items() -> str:
    """returns the query that will get the items in a collection owned by someone"""
    return "query GetTokens($filter: TokenFilterInput, $pagination: PaginationInput, $sort: TokenSortInput) {tokens(filter: $filter, pagination: $pagination, sort: $sort) {id, tokenId}}"

def get_variables_for_items(owner: str, collection: str, cursor: str = None):
    """returns the variables that will get the items in a collection owned by someone"""
    if cursor is not None:
        return {
                    "filter": {"collection": collection,"owner": owner},
                    "pagination": {"first": 25, "cursor": cursor },
                    "sort":"LAST_RECEIVED"
                }
    return {
                "filter": {"collection": collection,"owner": owner},
                "pagination": {"first": 25 },
                "sort":"LAST_RECEIVED"
            }

def get_query_for_item_metadata_refresh() -> str:
    """returns the query that will trigger the nft metadata to refresh"""
    return "mutation Mutation($tokenId: String!, $collection: Address!) {refreshToken(tokenId: $tokenId, collection: $collection) { success, message }}"

def get_variables_for_item_metadata_refresh(token_id: str, collection: str):
    """returns the variables that are used to refresh metadata"""
    return {"tokenId":token_id,"collection":collection}

refresh_metadata()
