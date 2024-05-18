#!/bin/bash
# get a random GitHub repo
#  using https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user
#  a modification of https://michaelheap.com/follow-github-link-header-bash/
# to test API use
#   curl -s https://api.github.com/users/alifeee/repos | jq '.[].html_url'
# to see rate limit information use (and/or add the auth)
#   curl -sS -i https://api.github.com/users/alifeee/repos?per_page=1 | grep ratelimit
#   curl -sS -i -H "Authorization: token <token>" https://api.github.com/users/alifeee/repos?per_page=1 | grep ratelimit
# example:
#   ./random.cgi

# load GitHub token and username from .env file
set -a
source .env
set +a

URL="https://api.github.com/users/${GITHUB_USER}/repos?per_page=100&type=all"

REPOS=""
while [ "$URL" ]; do
  if [ -z $GITHUB_AUTH_TOKEN ]; then
    # no auth token - will probably hit rate limit (only 60 tries per hour(?))
    RESP=$(curl -i -Ss "${URL}")
  else
    # auth token
    RESP=$(curl -i -Ss -H "Authorization: token ${GITHUB_AUTH_TOKEN}" "${URL}")
  fi

  # seperate out headers
  HEADERS=$(echo "${RESP}" | sed '/^\r$/q')

  # check for rate limiting
  RATELIM=$(echo ${HEADERS} | pcregrep -o1 'x-ratelimit-remaining: ([0-9]*)')
  if [ $RATELIM -gt 0 ]; then
    REPOS="${REPOS} $(echo "${RESP}" | sed '1,/^\r$/d')"
    # get next url from "link" header
    URL=$(echo "${HEADERS}" | pcregrep -o1 'link:.*<(http[^>]*)>; rel="next"')
  else
    echo "Status: 503 Service Unavailable"
    echo "Retry-After: 3600"
    echo ""
    echo "rate limit reached"
    exit 0
  fi
done

echo "Content-type: text/html"
echo "Cache-Control: no-cache"
echo ""
REPO=$(echo $REPOS | jq -r '.[].html_url' | shuf | head -n1)
echo '<!DOCTYPE html>
<html>
<head>
  <style>
    body {
      margin: 0;
      padding: 0;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 3vw;
      background: #eee;
    }
    a {
      border: 2px solid black;
      border-radius: 1vw;
      padding: 1rem;
      background: #ccc;
    }
  </style>
</head>
<body>
  <a href='"${REPO}"'>'"${REPO}"'</a>
</body>
'
