import pygeoip


gip = pygeoip.GeoIP('GeoLiteCity.dat')
res = gip.record_by_addr('103.197.152.106')

for key, val in res.items():
    print('{}: {}'.format(key, val))
