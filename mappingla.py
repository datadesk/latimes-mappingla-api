"""
Python library for interacting with The Los Angeles Times Mapping L.A. API.
 
Mapping LA (http://mappingla.com) provides The Times custom boundaries
of neighborhoods and regions for all of Los Angeles County.

Data are available in KML, GeoJSON and KMZ formats.

Example usage:

>> from mappingla import mappingla
>> hood_list = mappingla.neighborhoods.all()
>> a = hood[0]
>> print a
Acton
>> a.kml
...
>> a.json
...
>> a.kmz
...
>> dtla = mappingla.neighborhoods.get(slug='downtown')
print dtla
Downtown
>> central = mappingla.regions.get(lat=34.053, lng=-118.245)
>> print central
Central
>> central.kml
...
"""
 
__author__ = "Ben Welsh (ben.welsh@latimes.com)"
__version__ = "0.0.1"
__copyright__ = "Copyright (c) 2010 Ben Welsh"
__license__ = "MIT"

import urllib, urllib2
import datetime
try:
    import json
except ImportError:
    import simplejson as json


class BaseGeographyObject(object):
    """
    An abstract version of the objects returned by the API.
    """

    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return u'<%s: %s>' % (self.__class__.__name__, self.__str__())
    
    def __str__(self):
        return unicode(self.name).encode("utf-8")
    
    def _get_url(self, url, format):
        """
        Retrieves the kml, kmz or json boundaries from the API.
        
        Caches results in a private attribute to avoid pinging the API
        more than once.
        """
        # Name the cache attribute base on the format being sought
        attr = '_cached_%s' % format
        # If it doesn't already exist...
        if not getattr(self, attr, None):
            print "Hitting API: %s" % url
            # Request the url
            response = urllib2.urlopen(url).read()
            # A little extra parsing for json results
            if format == 'json':
                response = json.loads(response)['boundaries']
            # And stuff it in the cache attribute
            setattr(self, attr, response)
        return getattr(self, attr)

    @property
    def json(self):
        """
        Return the boundaries in GeoJSON format.
        """
        return self._get_url(self.json_url, 'json')

    @property
    def kml(self):
        """
        Return the boundaries in KML format.
        """
        return self._get_url(self.kml_url, 'kml')

    @property
    def kmz(self):
        """
        Return the boundaries in KMZ format.
        """
        return self._get_url(self.kmz_url, 'kmz')

    @property
    def url(self):
        """
        Return the url for the detail page at mappingla.com.
        """
        return self.latimes_url


class Neighborhood(BaseGeographyObject):
    """
    A neighborhood returned by the API.
    """
    pass


class Region(BaseGeographyObject):
    """
    A neighborhood returned by the API.
    """
    pass


class mappingla(object):

    BASE_URL = u'http://projects.latimes.com/mapping-la-v4/api/%(version)s/%(area_type)s/%(method)s.%(format)s'

    @staticmethod
    def _makeurl(version=u'v1', area_type=None, method=None, format='json', params=None):
        """
        Creates a URL according to the API's structure.
        """
        url = mappingla.BASE_URL % {
            'version': version,
            'area_type': area_type,
            'method': method,
            'format': format,
        }
        # Add query string parameters if there are any
        if params:
           query_string = u'?%s' % urllib.urlencode(params)
           url = url + query_string
        return url

    @staticmethod
    def _apicall(**kwargs):
        """
        A private method for calling the API.
        """
        url = mappingla._makeurl(**kwargs)
        print "Hitting API: %s" % url
        response = urllib2.urlopen(url).read()
        return response

    @staticmethod
    def _getall(area_type):
        """
        Retrieves a list of all available objects.
        """
        result = mappingla._apicall(area_type=area_type[:-1], method='getList')
        return json.loads(result)[area_type]

    class neighborhoods(object):

        @staticmethod
        def all():
            """
            Retrieve all objects.
            
            Example usage:
            
                >> mappingla.neighborhoods.all()
                
            """
            object_list = mappingla._getall('neighborhoods')
            return [Neighborhood(i) for i in object_list]

        @staticmethod
        def get(slug=None, lat=None, lng=None):
            """
            Retrieve an object using either a slug or a pair of latitude
            and longitude coordinates.
            
            Example usage:
            
                >> mappingla.neighborhoods.get(slug='central-la')
                >> mappingla.neighborhoods.get(lat=34.053, lng=-118.245)

            """
            if slug:
                kwargs = {
                    'area_type': 'neighborhood',
                    'method': 'getBySlug',
                    'params': { 'slug': slug },
                }
            elif lat and lng:
                kwargs = {
                    'area_type': 'neighborhood',
                    'method': 'getByLatLng',
                    'params': { 'lat': lat, 'lng': lng },
                }
            else:
                raise ValueError("You did not include a validate keyword \
                    argument. You must include either a slug, or a pair of \
                    lat and lng coordinates.")

            # Get the data (This should be cached at some point)
            response = mappingla._apicall(**kwargs)
            obj = Neighborhood(json.loads(response))
            # Mock up the other urls
            obj.kml_url = mappingla._makeurl(format='kml', **kwargs)
            obj.kmz_url = mappingla._makeurl(format='kmz', **kwargs)
            obj.json_url = mappingla._makeurl(format='json', **kwargs)
            # Pass it out
            return obj

    class regions(object):

        @staticmethod
        def all():
            """
            Retrieve all objects.
            
            Example usage:
            
                >> mappingla.regions.all()
                
            """
            object_list = mappingla._getall('regions')
            return [Neighborhood(i) for i in object_list]

        @staticmethod
        def get(slug=None, lat=None, lng=None):
            """
            Retrieve an object using either a slug or a pair of latitude
            and longitude coordinates.
            
            Example usage:
            
                >> mappingla.regions.get(slug='central-la')
                >> mappingla.regions.get(lat=34.053, lng=-118.245)
                
            """
            if slug:
                kwargs = {
                    'area_type': 'region',
                    'method': 'getBySlug',
                    'params': { 'slug': slug },
                }
            elif lat and lng:
                kwargs = {
                    'area_type': 'region',
                    'method': 'getByLatLng',
                    'params': { 'lat': lat, 'lng': lng },
                }
            else:
                raise ValueError("You did not include a validate keyword argument.")

            # Get the data (This should be cached at some point)
            response = mappingla._apicall(**kwargs)
            obj = Region(json.loads(response))
            # Mock up the other urls
            obj.kml_url = mappingla._makeurl(format='kml', **kwargs)
            obj.kmz_url = mappingla._makeurl(format='kmz', **kwargs)
            obj.json_url = mappingla._makeurl(format='json', **kwargs)
            # Pass it out
            return obj

