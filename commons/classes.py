from datetime import datetime
from netaddr import IPAddress, IPNetwork
import math
import numpy as np

class Result():
    
    def __init__(self):
        self.rtt_list = []
        self.min_rtt = 0
        self.max_rtt = 0
        self.avg_rtt = 0
        self.med_rtt = 0
        
        self.country_origin = ''
        self.country_destination = ''
        self.as_origin = 0
        self.as_destination = 0
        self.ip_origin = 0
        self.ip_destination = 0
        
        self.date_probe = 0
        self.date_target = 0
        self.date_utc = 0
        
    def __str__(self):
        return "%s %s AS%s AS%s %.1f ms" % (self.country_origin, self.country_destination, self.as_origin, self.as_destination, self.min_rtt)
    
    def valid_ases(self):
        return self.as_origin != 0 and self.as_destination != 0
    
    def valid_countries(self):
        return self.country_origin != '' and self.country_destination != ''

    @property
    def get_graph_weight(self):
        return self.avg_rtt
        
    @staticmethod
    def parse_speedchecker_result(_json, date_format='%Y-%m-%d %H:%M:%S.%f'):
        
        r = Result()

        r.rtt_list = []
        r.min_rtt = _json['min_rtt']
        r.max_rtt = _json['max_rtt']
        r.avg_rtt = _json['avg_rtt']
        r.med_rtt = _json['med_rtt']

        if 'country_origin' in _json.keys():
            r.country_origin = _json['country_origin']
        if 'country_destination' in _json.keys():
            r.country_destination = _json['country_destination']
        if 'as_origin' in _json.keys():
            r.as_origin = _json['as_origin']
        if 'as_destination' in _json.keys():
            r.as_destination = _json['as_destination']
        if 'ip_origin' in _json.keys():
            r.ip_origin = _json['ip_origin']
        if 'ip_destination' in _json.keys():
            r.ip_destination = _json['ip_destination']

        if 'date_probe' in _json.keys():
            r.date_probe = datetime.strptime(_json['date_probe'][:-6], date_format)
        if 'date_target' in _json.keys():
            r.date_target = datetime.strptime(_json['date_target'][:-6], date_format)
        if 'date_utc' in _json.keys():
            r.date_utc = datetime.strptime(_json['date_utc'][:-6], date_format)
            
        return r
            
    @staticmethod
    def parse_javascript_result(_json):
        return Result.parse_speedchecker_result(_json, date_format='%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def _parse_atlas_commons(_json):
        r = Result()
        
        if 'prb_id' in _json.keys():
            r.prb_id = _json['prb_id']
        
        return r
        
    
    @staticmethod
    def parse_atlas_http_result(_json):
        r = Result._parse_atlas_commons(_json)

        if 'result' in _json.keys():
            r.rtt_list = [float(_['rt']) for _ in _json['result'] if 'rt' in _.keys()]
            
            if len(r.rtt_list) > 0:
                r.min_rtt = min(r.rtt_list)
                r.max_rtt = r.min_rtt
                r.avg_rtt = r.min_rtt
                r.med_rtt = r.min_rtt

#         if 'country_origin' in _json.keys():
#             r.country_origin = _json['country_origin']
#         if 'country_destination' in _json.keys():
#             r.country_destination = _json['country_destination']
#         if 'as_origin' in _json.keys():
#             r.as_origin = _json['as_origin']
#         if 'as_destination' in _json.keys():
#             r.as_destination = _json['as_destination']
        if 'result' in _json.keys() and 'src_addr' in _json['result'][0].keys():
            r.ip_origin = _json['result'][0]['src_addr']
        if 'result' in _json.keys() and 'dst_addr' in _json['result'][0].keys():
            r.ip_destination = _json['result'][0]['dst_addr']

        if 'timestamp' in _json.keys():
            r.date_utc = datetime.fromtimestamp(_json['timestamp'])
#         if 'date_target' in _json.keys():
#             r.date_target = datetime.strptime(_json['date_target'][:-6], date_format)
#         if 'date_utc' in _json.keys():
#             r.date_utc = datetime.strptime(_json['date_utc'][:-6], date_format)
        return r

    @staticmethod
    def parse_atlas_ping_result(_json):
        r = Result._parse_atlas_commons(_json)

        if 'result' in _json.keys():
            r.rtt_list = [float(_['rtt']) for _ in _json['result'] if 'rtt' in _.keys()]
            
            if len(r.rtt_list) > 0:
                r.min_rtt = min(r.rtt_list)
                r.max_rtt = max(r.rtt_list)
                r.avg_rtt = np.mean(r.rtt_list)
                r.med_rtt = np.median(r.rtt_list)

#         if 'country_origin' in _json.keys():
#             r.country_origin = _json['country_origin']
#         if 'country_destination' in _json.keys():
#             r.country_destination = _json['country_destination']
#         if 'as_origin' in _json.keys():
#             r.as_origin = _json['as_origin']
#         if 'as_destination' in _json.keys():
#             r.as_destination = _json['as_destination']
        if 'src_addr' in _json.keys():
            r.ip_origin = _json['src_addr']
        if 'dst_addr' in _json.keys():
            r.ip_origin = _json['dst_addr']

        if 'timestamp' in _json.keys():
            r.date_utc = datetime.fromtimestamp(_json['timestamp'])
#         if 'date_target' in _json.keys():
#             r.date_target = datetime.strptime(_json['date_target'][:-6], date_format)
#         if 'date_utc' in _json.keys():
#             r.date_utc = datetime.strptime(_json['date_utc'][:-6], date_format)
        return r

    @staticmethod
    def parse_atlas_tcp_result(_json):
        r = Result._parse_atlas_commons(_json)

        if 'result' in _json.keys():
            
            r.rtt_list = [float(_['rtt']) for _ in _json['result'][0]['result'] if 'rtt' in _.keys()]
            
            if len(r.rtt_list) > 0:
                r.min_rtt = min(r.rtt_list)
                r.max_rtt = max(r.rtt_list)
                r.avg_rtt = np.mean(r.rtt_list)
                r.med_rtt = np.median(r.rtt_list)

#         if 'country_origin' in _json.keys():
#             r.country_origin = _json['country_origin']
#         if 'country_destination' in _json.keys():
#             r.country_destination = _json['country_destination']
#         if 'as_origin' in _json.keys():
#             r.as_origin = _json['as_origin']
#         if 'as_destination' in _json.keys():
#             r.as_destination = _json['as_destination']
        if 'src_addr' in _json.keys():
            r.ip_origin = _json['src_addr']
        if 'dst_addr' in _json.keys():
            r.ip_origin = _json['dst_addr']

        if 'timestamp' in _json.keys():
            r.date_utc = datetime.fromtimestamp(_json['timestamp'])
#         if 'date_target' in _json.keys():
#             r.date_target = datetime.strptime(_json['date_target'][:-6], date_format)
#         if 'date_utc' in _json.keys():
#             r.date_utc = datetime.strptime(_json['date_utc'][:-6], date_format)
        return r
