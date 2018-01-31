"""
Requires:
    Python 3
    github3.py==1.0.0a4
    semver==2.6.0
    tabulate==0.7.5
"""
import functools
import json
import sys

import github3
import semver

from tabulate import tabulate


app_repos = set([
    "atom-format",
    "django-bookmarks",
    "django-flag",
    "django-forms-bootstrap",
    "django-friends",
    "django-mailer",
    "django-user-accounts",
    "pinax-announcements",
    "pinax-api",
    "pinax-blog",
    "pinax-boxes",
    "pinax-calendars",
    "pinax-cart",
    "pinax-cohorts",
    "pinax-comments",
    "pinax-documents",
    "pinax-eventlog",
    "pinax-events",
    "pinax-forums",
    "pinax-identity",
    "pinax-images",
    "pinax-invitations",
    "pinax-likes",
    "pinax-lms-activities",
    "pinax-messages",
    "pinax-models",
    "pinax-news",
    "pinax-notifications",
    "pinax-pages",
    "pinax-phone-confirmation",
    "pinax-points",
    "pinax-ratings",
    "pinax-referrals",
    "pinax-stripe",
    "pinax-submissions",
    "pinax-teams",
    "pinax-testimonials",
    "pinax-types",
    "pinax-waitinglist",
    "pinax-webanalytics",
    "pinax-wiki"
])

distributions = json.loads(open("distributions.json").read())
versions = list(distributions.keys())
versions.sort()
latest = versions[-1]
latest_post = "post-{}".format(latest)

distro_repos = list(distributions[latest]["apps"].keys())

gh = github3.login(sys.argv[1], token=sys.argv[2].strip())

repos = []
pinax = gh.organization("pinax")
for repo in pinax.repositories():
    if repo.name in app_repos:
        tags = list(repo.tags())
        versions = {}
        for tag in tags:
            if tag.name.startswith("v"):
                tag_name = tag.name[1:]
            else:
                tag_name = tag.name
            try:
                semver.parse(tag_name)
            except ValueError:
                continue
            versions[tag_name] = tag
        if len(versions) == 0:
            continue
        version = sorted(versions.keys(), reverse=True, key=functools.cmp_to_key(semver.compare))[0]  # noqa
        tagged_sha = versions[version].commit["sha"]
        tagged_commit = repo.commit(tagged_sha)
        since = [
            commit
            for commit in list(repo.commits(sha="master", since=tagged_commit.commit.author["date"]))  # noqa
            if commit.sha != tagged_sha
        ]
        triaged_latest = sum([m.open_issues for m in repo.milestones() if m.title == latest])  # noqa
        triaged_post = sum([m.open_issues for m in repo.milestones() if m.title == latest_post])  # noqa
        repos.append([
            u"\u2713" if repo.name in distro_repos else "",
            repo.name,
            version,
            len(since) or "",
            triaged_latest or "",
            triaged_post or "",
            (repo.open_issues_count - triaged_latest - triaged_post) or ""
        ])

repos = sorted(repos, key=lambda x: (x[0], x[1]))
headers = ["ship", "repo", "latest", "commits", latest, latest_post, "to triage"]  # noqa
print(tabulate(repos, headers))
