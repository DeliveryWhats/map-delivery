import os
import zipfile
import requests
import tempfile
from typing import Optional, Dict
from shapely.geometry import Point, Polygon
from fastkml import kml
from lxml import etree
from database import DatabaseManager

class GeolocationService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def check_coverage(self, latitude: float, longitude: float, 
                      company_id: int, store_id: Optional[int] = None) -> Optional[Dict]:
        """
        Check if a geolocation is covered by a store.
        Returns the first matching store or None if no coverage found.
        """
        point = Point(longitude, latitude)  # Note: Shapely uses (lon, lat) order
        
        # Get regions from database
        regions = self.db_manager.get_active_regions(company_id, store_id)
        
        for region in regions:
            if self._point_in_region(point, region['file_path'], region['type']):
                return {
                    'store_id': str(region['store_id']),
                    'region_name': region['region_name'],
                    'company_id': str(region['company_id'])
                }
        
        return None
    
    def _point_in_region(self, point: Point, file_path: str, file_type: str) -> bool:
        """Check if a point is within a KML/KMZ region"""
        try:
            # Check if file_path is a URL or local path
            if file_path.startswith(('http://', 'https://')):
                return self._check_remote_file_coverage(point, file_path, file_type)
            else:
                # Local file handling (legacy support)
                if file_type.lower() == 'kmz':
                    return self._check_kmz_coverage(point, file_path)
                else:
                    return self._check_kml_coverage(point, file_path)
        except Exception as e:
            print(f"Error checking coverage for {file_path}: {e}")
            return False
    
    def _check_remote_file_coverage(self, point: Point, file_url: str, file_type: str) -> bool:
        """Download and check remote KML/KMZ file coverage"""
        try:
            # Download the file
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type.lower()}') as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            try:
                # Process the temporary file
                if file_type.lower() == 'kmz':
                    result = self._check_kmz_coverage(point, temp_file_path)
                else:
                    result = self._check_kml_coverage(point, temp_file_path)
                return result
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except requests.RequestException as e:
            print(f"Error downloading remote file {file_url}: {e}")
            return False
        except Exception as e:
            print(f"Error processing remote file {file_url}: {e}")
            return False
    
    def _check_kml_coverage(self, point: Point, file_path: str) -> bool:
        """Check if point is within KML polygons"""
        if not os.path.exists(file_path):
            print(f"KML file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                doc = f.read()
            
            k = kml.KML()
            k.from_string(doc)
            
            return self._check_kml_features(k.features(), point)
        
        except Exception as e:
            print(f"Error parsing KML file {file_path}: {e}")
            return False
    
    def _check_kmz_coverage(self, point: Point, file_path: str) -> bool:
        """Check if point is within KMZ polygons"""
        if not os.path.exists(file_path):
            print(f"KMZ file not found: {file_path}")
            return False
        
        try:
            with zipfile.ZipFile(file_path, 'r') as kmz:
                # Look for doc.kml or any .kml file in the archive
                kml_files = [name for name in kmz.namelist() if name.endswith('.kml')]
                
                if not kml_files:
                    print(f"No KML files found in KMZ: {file_path}")
                    return False
                
                # Use the first KML file found (usually doc.kml)
                kml_content = kmz.read(kml_files[0])
                
                k = kml.KML()
                k.from_string(kml_content)
                
                return self._check_kml_features(k.features(), point)
        
        except Exception as e:
            print(f"Error parsing KMZ file {file_path}: {e}")
            return False
    
    def _check_kml_features(self, features, point: Point) -> bool:
        """Recursively check KML features for polygon coverage"""
        for feature in features:
            # Check if this feature is a Placemark with geometry
            if hasattr(feature, 'geometry') and feature.geometry:
                if self._point_in_geometry(point, feature.geometry):
                    return True
            
            # Recursively check nested features (Folders, Documents)
            if hasattr(feature, 'features') and feature.features():
                if self._check_kml_features(feature.features(), point):
                    return True
        
        return False
    
    def _point_in_geometry(self, point: Point, geometry) -> bool:
        """Check if point is within a KML geometry"""
        try:
            # Convert KML geometry to Shapely geometry
            if hasattr(geometry, 'exterior'):
                # It's a Polygon
                coords = list(geometry.exterior.coords)
                if len(coords) >= 3:
                    # Convert to (lon, lat) tuples and create Shapely polygon
                    polygon_coords = [(coord[0], coord[1]) for coord in coords]
                    polygon = Polygon(polygon_coords)
                    return polygon.contains(point)
            
            elif hasattr(geometry, 'geoms'):
                # It's a MultiPolygon or GeometryCollection
                for geom in geometry.geoms:
                    if self._point_in_geometry(point, geom):
                        return True
        
        except Exception as e:
            print(f"Error checking geometry: {e}")
        
        return False
