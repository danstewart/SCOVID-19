## Site
```
# Bootstrap
[[ -f /bootstrapped ]] || bash <(curl -s https://raw.githubusercontent.com/danstewart/server-bootstrap/master/bootstrap.sh)

# System dependencies
sudo npm install terser -g

# Link
sudo ln -s $(pwd)/site/ /data/www/scovid19.xyz

# nginx
sudo cp nginx/scovid19.xyz /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/scovid19.xyz /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Certbot
sudo certbot --nginx
```

## Script
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate

# Schedule
(crontab -l 2>/dev/null; printf "0 14 * * * export PROJECT_ROOT=/code/SCOVID-19 && /code/SCOVID-19/bin/run.sh") | uniq - | crontab -
```

## Notes
On April 2nd the death counting process changed.  
https://www.gov.scot/news/new-process-for-reporting-covid-19-deaths/

## Sources
https://www.gov.scot/coronavirus-covid-19/
https://www.gov.scot/publications/coronavirus-covid-19-tests-and-cases-in-scotland/
https://www.gov.scot/publications/coronavirus-covid-19-data-definitions-and-sources/
