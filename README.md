# Dreamhost hook for dehydrated ACME client

This a hook for the [Let's Encrypt](https://letsencrypt.org/) ACME client [dehydrated](https://github.com/lukas2511/dehydrated), that enables using DNS records on [Dreamhost](https://www.dreamhost.com/) to respond to `dns-01` challenges. Requires your Dreamhost API key being in the environment.

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ErinMorelli_dehydrated-dreamhost-hook&metric=alert_status)](https://sonarcloud.io/dashboard?id=ErinMorelli_dehydrated-dreamhost-hook)

---

## Setup
```
$ git clone https://github.com/lukas2511/dehydrated
$ cd dehydrated
$ mkdir hooks
$ git clone https://github.com/ErinMorelli/dehydrated-dreamhost-hook hooks/dreamhost
$ pip install -r hooks/dreamhost/requirements.txt
$ export DREAMHOST_API_KEY='K9uX2HyUjeWg5AhAb'
$ mkdir -p ~/.config/dehydrated
$ cp hooks/dreamhost/sample_deploy.conf ~/.config/dehydrated/deploy.conf
```

Open the `~/.config/dehydrated/deploy.conf` file in your favorite text editor and update it for your personal needs.

Get your Dreamhost API key by logging in to your control panel, and navigating to the [Web Panel API page](https://panel.dreamhost.com/index.cgi?tree=home.api). Make sure that the "All dns functions" option is checked before clicking on "Generate a new API Key now!".

## Usage

```
$ ./dehydrated -c -d example.com -t dns-01 -k 'hooks/dreamhost/hook.py'
#
# !! WARNING !! No main config file found, using default config!
#
Processing example.com
 + Signing domains...
 + Creating new directory /home/user/dehydrated/certs/example.com ...
 + Generating private key...
 + Generating signing request...
 + Requesting challenge for example.com...
 + Checking if TXT record for _acme-challenge.example.com exists...
 + Adding new TXT record KuJORHNYWBU3QVp9vS6tlkMFh5A6WHxMbsTp2-Ufz-Y...
 + record_added: success
 + Settling down for 10s...
 + DNS not propagated, waiting 30s...
 + DNS not propagated, waiting 30s...
 + Responding to challenge for example.com...
 + Dreamhost hook executing: clean_challenge
 + Checking if TXT record for _acme-challenge.home.example.com exists...
 + Old TXT record found, removing...
 + record_removed: success
 + Challenge is valid!
 + Requesting certificate...
 + Checking certificate...
 + Done!
 + Creating fullchain.pem...
 + Dreamhost hook executing: deploy_cert
 + Private Key: /home/user/dehydrated/certs/example.com/privkey.pem
 + Certificate: /home/user/dehydrated/certs/example.com/cert.csr
 + Full Chain: /home/user/dehydrated/certs/example.com/fullchain.pem
Starting new file deployment
# INFO: Using deployment config file /home/user/.config/dehydrated/deploy.conf
Deploying new files for: example.com
 + Succesfully deployed new cert to /opt/lampp/etc/ssl.crt/server.crt
 + Succesfully deployed new privkey to /opt/lampp/etc/ssl.key/server.key
Starting post-deployment actions
 + Attempting action: /opt/lampp/lampp restart
 + Action exited with status 0
New file deployment done.
 + Done!
```
