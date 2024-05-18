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
#   ./svg.cgi

# load GitHub token and username from .env file
set -a
source .env
set +a

URL="https://api.github.com/users/${GITHUB_USER}/repos?per_page=100&type=all"

REPOS=""
while [ "$URL" ]; do
  # get response
#  RESP=$(curl -i -Ss -H "Authorization: token ${GITHUB_AUTH_TOKEN}" "${URL}")
  RESP=$(curl -i -Ss "${URL}") # uncomment to test rate limiting

  # seperate out headers
  HEADERS=$(echo "${RESP}" | sed '/^\r$/q')

  # check for rate limiting
  RATELIM=$(echo ${HEADERS} | pcregrep -o1 'x-ratelimit-remaining: ([0-9]*)')
  if [ $RATELIM -gt 0 ]; then
    REPOS="${REPOS} $(echo "${RESP}" | sed '1,/^\r$/d')"
    URL=$(echo "${HEADERS}" | pcregrep -o1 'link:.*<(http[^>]*)>; rel="next"')
  else
    # do normal HTTP 200 response otherwise image does not show
    # echo "Status: 503 Service Unavailable"
    # echo "Retry-After: 3600"
    echo "Content-type: image/svg+xml"
    echo "Cache-Control: no-cache"
    echo ""
    cat svgtemplate.svg | sed 's/{{text}}/rate limit reached :(/g'
    exit 0
  fi
done

echo "Content-type: image/svg+xml"
echo "Cache-Control: no-cache"
echo ""
REPO=$(echo "${REPOS}" | jq -r '.[].html_url' | shuf | head -n1)
cat svgtemplate.svg | sed 's#{{text}}#'"${REPO}"'#g'
