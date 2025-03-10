import csv
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# .env

jwt_payload = os.getenv("JWT_PAYLOAD")
jwt_signature = os.getenv("JWT_SIGNATURE")


url = "https://digitalskillsbern.ch/api/discussion/v1/courses/course-v1:unibe+GP+25FS/activity_stats/"

headers = {
    "Cookie": (
        f"edx-jwt-cookie-header-payload={jwt_payload}; "
        f"edx-jwt-cookie-signature={jwt_signature}"
    ),
}


response = requests.get(
    url, params={"order_by": "activity", "page": 1}, headers=headers
)
if not response.ok:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

data = response.json()
num_pages = data.get("pagination", {}).get("num_pages")
usernames = []

for page in range(1, num_pages + 1):
    print(f"Fetching page {page} of {num_pages}...")
    response = requests.get(
        url, params={"order_by": "activity", "page": page}, headers=headers
    )

    if response.ok:
        data = response.json()
        usernames.extend((item["username"], 0) for item in data.get("results", []))
    else:
        print(f"Failed to fetch page {page}: {response.status_code}")
        break

print(f"Found {len(usernames)} usernames")

leaderboard = dict(usernames)


url = "https://digitalskillsbern.ch/api/discussion/v1/threads/"

params = {
    "course_id": "course-v1:unibe+GP+25FS",
    "page": 1,
    "order_by": "last_activity_at",
    "requested_fields": "profile_image",
}

response = requests.get(url, params=params, headers=headers)
if not response.ok:
    print(f"Failed to fetch data: {response.status_code}")
    exit()

data = response.json()
num_pages = data.get("pagination", {}).get("num_pages")

comments_urls = []

for page in range(1, num_pages + 1):
    print(f"Fetching page {page} of {num_pages}...")
    params["page"] = page
    response = requests.get(url, params=params, headers=headers)

    if response.ok:
        data = response.json()
        for i, item in enumerate(data.get("results", [])):
            comments_url = item["comment_list_url"]
            if comments_url is not None:
                comments_urls.append(comments_url)
            endorsed_comment_list_url = item["endorsed_comment_list_url"]
            if endorsed_comment_list_url is not None:
                comments_urls.append(endorsed_comment_list_url)
            non_endorsed_comment_list_url = item["non_endorsed_comment_list_url"]
            if non_endorsed_comment_list_url is not None:
                comments_urls.append(non_endorsed_comment_list_url)
    else:
        print(f"Failed to fetch page {page}: {response.status_code}")
        break

params = {
    "reverse_order": "true",
    "requested_fields": "profile_image",
    "enable_in_context_sidebar": "false",
    "merge_question_type_responses": "true",
    "signal": "{}",
}


already_seen = set()


for url in comments_urls:
    print(f"Fetching {url}")

    response = requests.get(url, params={**params, "page": 1}, headers=headers)

    if not response.ok:
        print(f"Failed to fetch data: {response.status_code}")
        continue

    data = response.json()
    num_pages = data.get("pagination", {}).get("num_pages", 1)

    for page in range(1, num_pages + 1):
        response = requests.get(url, params={**params, "page": page}, headers=headers)

        if response.ok:
            data = response.json()
            for comment in data["results"]:
                if (id_ := comment["id"]) not in already_seen:
                    already_seen.add(id_)
                    author = comment["author"]
                    vote_count = comment["vote_count"]
                    print(f"Author: {author}\nVotes: {vote_count}\n")
                    leaderboard[author] += vote_count
        else:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break

leaderboard = dict(sorted(leaderboard.items(), key=lambda item: item[1], reverse=True))

print(leaderboard)

with open("upvotes_ranking.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["username", "upvotes"])  # Header
    for key, value in leaderboard.items():
        writer.writerow([key, value])

print("CSV file saved as 'upvotes_ranking.csv'")
