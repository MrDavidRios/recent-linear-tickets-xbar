#!/usr/bin/env python3

# <xbar.title>Linear Recent Tickets</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>David Rios</xbar.author>
# <xbar.desc>Shows recently updated Linear issues assigned to you</xbar.desc>
# <xbar.dependencies>python3</xbar.dependencies>
# <xbar.var>string(LINEAR_API_KEY=""): Your Linear API key</xbar.var>
# <xbar.var>select(SORT_BY="updatedAt"): Sort issues by [updatedAt, createdAt]</xbar.var>
# <xbar.var>number(NUM_RESULTS=5): Number of issues to show (1-10)</xbar.var>

import json
import os
import urllib.request

API_KEY = os.getenv("LINEAR_API_KEY", "")
SORT_BY = os.getenv("SORT_BY", "updatedAt")
NUM_RESULTS = min(10, max(1, int(os.getenv("NUM_RESULTS", "5"))))
API_URL = "https://api.linear.app/graphql"

def build_query():
    return f"""
    query {{
      viewer {{
        assignedIssues(first: {NUM_RESULTS}, orderBy: {SORT_BY}) {{
          nodes {{
            identifier
            title
            url
            state {{ name color }}
          }}
        }}
      }}
    }}
    """

def fetch_issues():
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json",
    }
    data = json.dumps({"query": build_query()}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def main():
    if not API_KEY:
        print("⚠️ Linear")
        print("---")
        print("Set LINEAR_API_KEY in xbar plugin settings")
        return

    result = fetch_issues()

    if "error" in result:
        print("⚠️ Linear")
        print("---")
        print(f"Error: {result['error']}")
        return

    if "errors" in result:
        print("⚠️ Linear")
        print("---")
        print(f"API Error: {result['errors'][0]['message']}")
        return

    issues = result.get("data", {}).get("viewer", {}).get("assignedIssues", {}).get("nodes", [])

    # Menu bar title
    print("Linear")
    print("---")

    if not issues:
        print("No assigned issues")
    else:
        for issue in issues:
            title = issue["title"][:50] + "..." if len(issue["title"]) > 50 else issue["title"]
            state = issue["state"]["name"]

            # Escape pipe characters in title
            title = title.replace("|", "\\|")
            print(f"{issue['identifier']}: {title} ({state}) | href={issue['url']}")

    print("---")
    print("Refresh | refresh=true")

if __name__ == "__main__":
    main()
