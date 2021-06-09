# cert-checker
 Help check certs and give warnings if they are about to expire.

```bash
docker run -d --name cert-checker \
    -e DOMAINS='google.com,bing.com' \
    -e SMTP_RELAY='1.1.1.1' \
    -e SENDER='cert-checker@domain.com' \
    -e NOTIFICATION_EMAIL='email@domain.com,email2@domain.com' \
    -e NOTIFICATION_TIME='30d,1d,30m,120s' \ 
    alphabet5/cert-checker
```

- DOMAINS - a comma separated list of domains to verify the certificate.
- SMTP_RELAY - SMTP server (no authentication) that is listening on port 25.
- NOTIFICATION_EMAIL - Email address to send notifications to.
- NOTIFICATION_TIME - comma separated list of time-deltas before the cert expires. d=days, m=minutes, s=seconds (default 7d)
- 