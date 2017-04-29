import CloudFlare
import ConfigParser
import platform

Config = ConfigParser.ConfigParser()
Config.read("/opt/secure/cf_settings.ini")
try:
    CFuser = Config.get("user", "email")
except ConfigParser.NoSectionError:
    print('Missing email')
    raise SystemExit(1)
try:
    CFtoken = Config.get("user", "token")
except ConfigParser.NoSectionError:
    print('Missing token')
    raise SystemExit(1)
try:
    #CFdomain = Config.get("domain", "tld")
    CFdomain = platform.node().split('.')[0]
except ConfigParser.NoSectionError:
    print('Missing tld')
    raise SystemExit(1)
try:
    CFserver = Config.get("domain", "server")
except ConfigParser.NoSectionError:
    print('Missing domain')
    raise SystemExit(1)

cf = CloudFlare.CloudFlare(email=CFuser, token=CFtoken)
try:
    CFget = cf.zones.get(params={'name': CFdomain})
except CloudFlare.CloudFlareAPIError as e:
    print('/zones.get %s - %d %s' % (CFdomain, e, e))
    raise SystemExit(1)
except Exception as e:
    print('/zones.get %s - %s' % (CFdomain, e))
    raise SystemExit(1)
zone_id = CFget[0]['id']
dns_records = [
    { 'name': CFserver + '.external', 'type': 'A', 'content': '{{ansible_eth0.ipv4.address}}'}

]

for record in dns_records:
    try:
      CFpost = cf.zones.dns_records.put(zone_id, data=record)
    except:
       print('put failed')
       failed = 1
    try:
       if failed == 1:
        CFpost = cf.zones.dns_records.post(zone_id, data=record)
    except:
       print('/zones.dns_records.post %s' % (record['name']))
       raise SystemExit(1)
