# Get Random Repository

Scripts using [GitHub's `repos` API][repo api] to grab random repositories from a user's GitHub. You can run them standalone, or you can set up CGI to use them on a server.

The SVG is particularly fun as you can put the link on a GitHub readme, or a personal website, and every visitor will see a different random image. This is harder to do with the raw text without sending your own requests with JavaScript.

| Text | SVG |
| --- | --- |
| https://server.alifeee.co.uk/github/random.cgi | https://server.alifeee.co.uk/github/svg.cgi <br> ![an SVG image showing a random one of alifeee's GitHub repositories](https://server.alifeee.co.uk/github/svg.cgi) |

```bash
$ curl https://server.alifeee.co.uk/github/random.cgi
https://github.com/alifeee/mountain-bothies

$ curl https://server.alifeee.co.uk/github/svg.cgi
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="400px" height="20px" viewbox="0 0 400 20" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
<text xml:space="preserve" style="font-size:18px;font-family:sans-serif;stroke-width:0.25;fill:red" x="0" y="15"
  >https://github.com/duphysics/duphysics.github.io</text>
</svg>
```

## Context: GitHub API

You can get a list of user repositories using `https://api.github.com/users/USERNAME/repos` ([documentation][repo api]).

For example, the first 30 of mine in JSON format are on <https://api.github.com/users/alifeee/repos>.

The API is paginated. To get all the results, you need to [deal with this pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api).

[repo api]: https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-a-user

## Scripts

The scripts [`./random.cgi`](./random.cgi) and [`./svg.cgi`](./svg.cgi) are very similar, and differ only in what they return.

## Install

### Set up folder

```bash
mkdir -p /var/www/cgi/github
cd /var/www/cgi/github
git clone git@github.com:alifeee/get-random-repository.git .
```

### Set up secrets

You do not need an auth token, but without one you will probably hit the rate limit quickly. Get one from the [GitHub token creator](https://github.com/settings/tokens?type=beta).

```bash
echo 'GITHUB_AUTH_TOKEN="github_pat_289hjf82j2......."
GITHUB_USER="alifeee"' > .env
```

After this step you can test the scripts work properly by running them as bash scripts.

```bash
./random.cgi
./svg.cgi
```

### Set up Nginx config

To set this up on a different web server, look up how to set up CGI scripts for that web server.

This passes any requests to `/github/*` to the scripts in the folder we created.

To debug this, running `sudo strace -f -e trace=file -p $(pidof fcgiwrap)` will display all attempts to do things by fastcgi, which is very helpful. You can see things like the process trying to open files that don't exist (if you've gotten filenames or number of slashes wrong).

```bash
sudo nano /etc/nginx/nginx.conf
```

```nginx
server {
  server_name server.alifeee.co.uk;

  listen 80 default_server;
  listen [::]:80 default_server;

# ...

  location /github/ {
    fastcgi_intercept_errors on;
    include fastcgi_params;
    fastcgi_param SCRIPT_FILENAME /var/www/cgi/$fastcgi_script_name;
    fastcgi_pass unix:/var/run/fcgiwrap.socket;
  }
}
```

```bash
sudo systemctl restart nginx.service
```

### Access endpoints

Try with CURL and also in your browser.

```bash
curl https://server.alifeee.co.uk/github/random.cgi
curl https://server.alifeee.co.uk/github/svg.cgi
```
