import requests
import argparse


def main():
    parser = argparse.ArgumentParser(prog="github-activity",
                                     description="Fetch the last 30 public events of the given GitHub user")
    parser.add_argument("username", help="username of the GitHub user", type=str)
    args = parser.parse_args()

    username = args.username
    endpoint = f"https://api.github.com/users/{username}/events?per_page=30"

    events = get_response(endpoint, username)

    handlers = get_event_handlers()

    for event in events:
        event_type = event.get("type", "")

        event_handler = handlers.get(event_type)
        if event_handler:
            event_handler(event)
        else:
            print("- Unknown Event")


def get_response(endpoint, username):

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'github-activity-cli'
    }

    try:
        r = requests.get(endpoint, headers=headers)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as err:
        raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        if r.status_code == 404:
            raise SystemExit(f"User '{username}' not found")
        elif r.status_code == 403:
            raise SystemExit("Rate limit exceeded or access forbidden")
        raise SystemExit(err)

    return r.json()

def get_event_handlers():
    return {
        "CommitCommentEvent": handle_commit_comment_event,
        "CreateEvent": handle_create_event,
        "DeleteEvent": handle_delete_event,
        "ForkEvent": handle_fork_event,
        "GollumEvent": handle_gollum_event,
        "IssueCommentEvent": handle_issue_comment_event,
        "IssuesEvent": handle_issues_event,
        "MemberEvent": handle_member_event,
        "PublicEvent": handle_public_event,
        "PullRequestEvent": handle_pull_request_event,
        "PullRequestReviewEvent": handle_pull_request_review_event,
        "PullRequestReviewCommentEvent": handle_pull_request_review_comment_event,
        "PullRequestReviewThreadEvent": handle_pull_request_review_thread_event,
        "PushEvent": handle_push_event,
        "ReleaseEvent": handle_release_event,
        "SponsorshipEvent": handle_sponsorship_event,
        "WatchEvent": handle_watch_event
    }


def handle_commit_comment_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    commit_id = event.get("payload", {}).get("comment", {}).get("commit_id", "Unknown")
    comment_text = event.get("payload", {}).get("comment", {}).get("body", "No Comment")
    print(f"- Commented on commit {commit_id[:7]} in {repo}: {comment_text[:50]}")


def handle_create_event(event):
    repo = event.get("repo", {}).get("name", "Unknown")
    ref_type = event.get("payload").get("ref_type")
    ref = event.get("payload").get("ref")
    if ref_type == "repository":
        print(f"- Created repo: {repo}")
    elif ref_type in ["branch", "tag"] and ref:
        print(f"- Created {ref_type} '{ref}' in {repo}")
    else:
        print(f"- Created {ref_type} in {repo}")


def handle_delete_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    ref_type = event.get('payload').get('ref_type')
    if ref_type == "repository":
        print(f"- Deleted repo: {repo}")
    else:
        print(f"- Deleted {ref_type} in {repo}")


def handle_fork_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    print(f"- Forked repo {repo}")


def handle_gollum_event(event):
    try:
        pages = event.get("payload", {}).get("pages", [])
        for page in pages:
            if isinstance(page, dict):
                page_title = page.get("title", "Unknown")
                page_action = page.get("action", "Unknown")
                print(f"- {page_action.capitalize()} wiki page '{page_title}'")
    except Exception as err:
        print(f"- Could not process wiki event: {err}")


def handle_issue_comment_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    issue_title = event.get("payload", {}).get("issue", "").get("title", "")
    comment_body = event.get("payload", {}).get("comment", {}).get("body", "")[:50]
    print(f"- {action.capitalize()} comment '{issue_title}' in {repo}: {comment_body}")


def handle_issues_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    issue = event.get("payload", {}).get("issue", "unknown").get("title", "")
    print(f"- {action.capitalize()} issue in {repo}: {issue}")


def handle_member_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    member = event.get("payload", {}).get("member", {}).get("login", "Unknown")

    action_messages = {
        "added": f"- Added {member} as collaborator to {repo}",
        "removed": f"- Removed {member} from {repo}",
        "edited": f"- Changed {member}'s permissions on {repo}"
    }

    print(action_messages.get(action, f"- {action} {member} on {repo}"))


def handle_public_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    print(f"- Made {repo} public")


def handle_pull_request_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    pull_request = event.get("payload", {}).get("pull_request", "unknown").get("title", "")
    print(f"- Pull request {action} on {repo}: {pull_request}")


def handle_pull_request_review_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    print(f"- {action.capitalize()} PR in {repo} ")


def handle_pull_request_review_comment_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    comment_text = event.get("payload", {}).get("comment", {}).get("body", "")[:50]
    pr_title = event.get("payload", {}).get("pull_request", {}).get("title", "")
    print(f"- {action.capitalize()} review comment on PR '{pr_title}' in {repo}: {comment_text}")


def handle_pull_request_review_thread_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    pull_request = event.get("payload", {}).get("pull_request", "unknown").get("title", "")
    print(f"- {action.capitalize()} review thread on PR '{pull_request}' in {repo}")


def handle_push_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    commits = len(event.get('payload', {}).get('commits', []))
    print(f"- Pushed {commits} commit{"s" if commits != 1 else ""} to {repo}")


def handle_release_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    action = event.get("payload", {}).get("action", "")
    release = event.get("payload", {}).get("release", {}).get("name", "")
    print(f"- {action.capitalize()} {release} of {repo}")


def handle_sponsorship_event(event):
    action = event.get("payload", {}).get("action", "unknown")
    sponsor = event.get("payload", {}).get("sponsorship", {}).get("sponsor", {}).get("login", "Unknown")
    sponsorable = event.get("payload", {}).get("sponsorship", {}).get("sponsorable", {}).get("login", "Unknown")

    match action:
        case "created":
            print(f"- {sponsor} just started sponsoring {sponsorable}!")
        case "cancelled":
            print(f"- {sponsor} cancelled their sponsorship of {sponsorable}")
        case "tier_changed":
            print(f"- {sponsor} changed their sponsorship tier for {sponsorable}")
        case _:
            print(f"- {sponsor} {action} sponsorship of {sponsorable}")


def handle_watch_event(event):
    repo = event.get('repo', {}).get('name', "Unknown")
    print(f"- Starred {repo}")


if __name__ == "__main__":
    main()
