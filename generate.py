import requests
import time
import datetime
import json

query = """
query($page:Int) {
  SiteStatistics {
    anime(page:$page, perPage: 25, sort: DATE_DESC) {
      nodes {
        date
        count
      }
    }
    manga(page:$page, perPage: 25, sort: DATE_DESC) {
      nodes {
        date
        count
      }
    }
    characters(page:$page, perPage: 25, sort: DATE_DESC) {
      nodes {
        date
        count
      }
    }
    staff(page:$page, perPage: 25, sort: DATE_DESC) {
      nodes {
        date
        count
      }
    }
  }
}
"""

all_data = []
page = 1
while True:
    variables = {
        'page': page
    }
    response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables})
    response.raise_for_status()
    data = response.json()
    all_data.append(data)
    if len(data['data']['SiteStatistics']['anime']['nodes']) == 0:
        break
    page += 1
    time.sleep(1)

data: dict[str, dict[datetime.date, int]] = dict(anime={}, manga={}, characters={}, staff={})
for page in all_data:
    for key in data:
        for node in page['data']['SiteStatistics'][key]['nodes']:
            date = datetime.datetime.fromtimestamp(node['date']).date()
            count = node['count']
            data[key][date] = count

rows: list[tuple[datetime.date, str, int]] = []
# Tabular format: (date (YYYY-MM-DD), category, count)
for key in data:
    for date, count in data[key].items():
        rows.append((date, key, count))

rows.sort()

json_data = [[date.isoformat(), key, count] for (date, key, count) in rows]
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(json_data, f)