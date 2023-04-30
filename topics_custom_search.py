from googleapiclient.discovery import build

# define key
api_key = "google spi key"
cse_key = "cse id"



# function to call custom Google api search
def google_search(search_term, cse_id, **kwargs):
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        return res['items']
    except Exception as e:
        print('Error: ' + str(e))


# function insert new search keyword and return found results
def get_data(keyword, all_link = [], all_title = [], all_snippet = []):
    try:
        # perform custom search
        results = google_search(keyword, cse_key, num=10, cr="countryUK", lr="lang_en")
        # loop through all returned results and get data
        for result in results:
            all_link.append(result.get('link'))
            all_title.append(result.get('title'))
            all_snippet.append(result.get('snippet'))

    except Exception as e:
        all_link.append('No Link Found')
        all_title.append('No Title Found')
        all_snippet.append('No Snippet Found')

    # returns searched results
    return all_link, all_title, all_snippet
