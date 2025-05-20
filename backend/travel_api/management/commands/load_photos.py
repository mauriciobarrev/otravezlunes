import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from datetime import datetime
import pathlib

from travel_api.models import Lugar, Fotografia

THUMBNAIL_SIZE = (256, 256)

class Command(BaseCommand):
    help = 'Loads photos from a specified directory, extracts EXIF data, gets location info, generates thumbnails, and saves to database.'

    def add_arguments(self, parser):
        parser.add_argument('photos_dir', type=str, help='The directory path where photos are located.')
        parser.add_argument(
            '--author',
            type=str,
            default='Default Author',
            help='Author of the photos.'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing Fotografia entries and regenerate thumbnails if files are reprocessed.'
        )

    def handle(self, *args, **options):
        photos_dir_path_str = options['photos_dir']
        photo_author = options['author']
        overwrite = options['overwrite']

        geolocator = Nominatim(user_agent="travel_blog_photo_loader_v1.1")

        # Resolve the photos directory to an absolute path
        # manage.py is in backend/, so photos_dir_path_str like '../photos' is relative to backend/
        base_execution_path = pathlib.Path(settings.BASE_DIR) # backend/
        photos_dir_absolute = (base_execution_path / photos_dir_path_str).resolve()

        if not photos_dir_absolute.is_dir():
            raise CommandError(f'Directory "{photos_dir_absolute}" does not exist.')

        # Define thumbnail directory (inside the resolved photos_dir_absolute)
        thumbnail_dir_absolute = photos_dir_absolute / "thumbnails"
        thumbnail_dir_absolute.mkdir(parents=True, exist_ok=True) # Create if not exists

        self.stdout.write(self.style.SUCCESS(f'Processing photos from: {photos_dir_absolute}'))
        self.stdout.write(self.style.SUCCESS(f'Thumbnails will be saved to: {thumbnail_dir_absolute}'))
        if overwrite:
            self.stdout.write(self.style.WARNING('Overwrite mode enabled: Existing photo entries may be updated.'))

        for item in photos_dir_absolute.iterdir():
            if item.is_file() and item.suffix.lower() in ('.jpg', '.jpeg'):
                file_path_absolute = item
                filename = item.name
                self.stdout.write(f'Processing file: {file_path_absolute}')
                
                try:
                    img = Image.open(file_path_absolute)
                    exif_data = self._get_exif_data(img)
                    
                    gps_info = self._get_gps_info(exif_data)
                    date_taken_str = self._get_date_taken(exif_data)
                    
                    date_taken = None
                    if date_taken_str:
                        try:
                            date_taken = datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f'Could not parse date_taken "{date_taken_str}" for {filename}. Skipping date.'))

                    lugar_instance = None
                    direccion_captura_text = ""

                    if gps_info:
                        lat = gps_info['lat']
                        lon = gps_info['lon']
                        self.stdout.write(f'  GPS: Lat {lat}, Lon {lon}')

                        location_details = self._get_location_details(geolocator, lat, lon)
                        direccion_captura_text = location_details.get('full_address', '')
                        
                        lugar_nombre = location_details.get('name', 'Unknown Location')
                        ciudad = location_details.get('city', '')
                        pais = location_details.get('country', '')

                        lugar_defaults = {
                            'nombre': lugar_nombre,
                            'ciudad': ciudad,
                            'pais': pais,
                        }
                        lugar_instance, created = Lugar.objects.update_or_create(
                            latitud=lat, 
                            longitud=lon,
                            defaults=lugar_defaults
                        )
                        if created:
                            self.stdout.write(self.style.SUCCESS(f'  Created new Lugar: {lugar_instance.nombre}'))
                        else:
                            self.stdout.write(f'  Updated/Found existing Lugar: {lugar_instance.nombre}')
                    else:
                        self.stdout.write(self.style.WARNING(f'  No GPS info found for {filename}. Fotografia will not be associated with a Lugar.'))
                        # Optionally, you could associate with a generic "Unknown Location" Lugar or skip photo creation

                    if not lugar_instance:
                        self.stdout.write(self.style.WARNING(f'  Cannot create Fotografia for {filename} as Lugar could not be determined.'))
                        continue # Skip to next photo if no Lugar

                    # Paths relative to project root (settings.BASE_DIR.parent)
                    project_root = settings.BASE_DIR.parent
                    relative_photo_path = os.path.relpath(file_path_absolute, project_root)

                    # Generate and save thumbnail
                    thumb_filename = f"{file_path_absolute.stem}_thumb{file_path_absolute.suffix}"
                    thumb_path_absolute = thumbnail_dir_absolute / thumb_filename
                    self._create_thumbnail(img, thumb_path_absolute, THUMBNAIL_SIZE)
                    relative_thumb_path = os.path.relpath(thumb_path_absolute, project_root)
                    self.stdout.write(f'    Thumbnail saved: {thumb_path_absolute}')

                    fotografia_defaults = {
                        'autor_fotografia': photo_author,
                        'fecha_toma': date_taken,
                        'descripcion': f"Photo taken at {lugar_instance.nombre}" if lugar_instance else "Photo with no specific location",
                        'thumbnail_url': str(pathlib.Path(relative_thumb_path)), # Ensure it's a string path
                        'direccion_captura': direccion_captura_text,
                        # es_foto_principal_lugar needs manual setting or other logic
                    }

                    if overwrite:
                        fotografia, foto_created = Fotografia.objects.update_or_create(
                            lugar=lugar_instance,
                            url_imagen=str(pathlib.Path(relative_photo_path)),
                            defaults=fotografia_defaults
                        )
                        if foto_created:
                            self.stdout.write(self.style.SUCCESS(f'    Created new Fotografia: {relative_photo_path}'))
                        else:
                            self.stdout.write(self.style.SUCCESS(f'    Updated existing Fotografia: {relative_photo_path}'))
                    else:
                        fotografia, foto_created = Fotografia.objects.get_or_create(
                            lugar=lugar_instance,
                            url_imagen=str(pathlib.Path(relative_photo_path)),
                            defaults=fotografia_defaults
                        )
                        if foto_created:
                            self.stdout.write(self.style.SUCCESS(f'    Saved new Fotografia: {relative_photo_path}'))
                        else:
                            self.stdout.write(self.style.WARNING(f'    Fotografia already exists (use --overwrite to update): {relative_photo_path}'))

                except FileNotFoundError:
                    self.stdout.write(self.style.ERROR(f'File not found: {file_path_absolute}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {filename}: {e}'))
                    import traceback
                    traceback.print_exc() # Print full traceback for debugging
        
        self.stdout.write(self.style.SUCCESS('Finished processing photos.'))

    def _create_thumbnail(self, image, thumb_path, size):
        img_copy = image.copy()
        # Use ImageOps.fit to crop and resize to the exact dimensions, maintaining aspect ratio via cropping
        # If you prefer letterboxing (black bars), use thumbnail() and then paste onto a new background.
        thumb = ImageOps.fit(img_copy, size, Image.Resampling.LANCZOS)
        thumb.save(thumb_path)

    def _get_exif_data(self, image):
        exif = {}
        info = image._getexif() # Use _getexif() which can be None
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_decoded = GPSTAGS.get(t, t)
                        gps_data[sub_decoded] = value[t]
                    exif[decoded] = gps_data
                else:
                    exif[decoded] = value
        return exif

    def _get_gps_info(self, exif_data):
        gps_info = exif_data.get("GPSInfo")
        if not gps_info:
            return None

        def to_degrees(value):
            # value can be a tuple of IFDRational objects or floats
            d = float(value[0].numerator) / float(value[0].denominator) if hasattr(value[0], 'numerator') else float(value[0])
            m = float(value[1].numerator) / float(value[1].denominator) if hasattr(value[1], 'numerator') else float(value[1])
            s = float(value[2].numerator) / float(value[2].denominator) if hasattr(value[2], 'numerator') else float(value[2])
            return d + (m / 60.0) + (s / 3600.0)

        lat_ref = gps_info.get("GPSLatitudeRef")
        lat_val = gps_info.get("GPSLatitude")
        lon_ref = gps_info.get("GPSLongitudeRef")
        lon_val = gps_info.get("GPSLongitude")

        if lat_val and lon_val and lat_ref and lon_ref:
            lat = to_degrees(lat_val)
            if lat_ref != "N":
                lat = -lat
            lon = to_degrees(lon_val)
            if lon_ref != "E":
                lon = -lon
            return {"lat": round(lat, 6), "lon": round(lon, 6)}
        return None

    def _get_date_taken(self, exif_data):
        date_tags = ["DateTimeOriginal", "DateTimeDigitized", "DateTime"]
        for tag in date_tags:
            if tag in exif_data:
                return exif_data[tag]
        return None

    def _get_location_details(self, geolocator, lat, lon):
        try:
            location = geolocator.reverse((lat, lon), exactly_one=True, language='es', timeout=15)
            if location and location.address:
                address_components = location.raw.get('address', {})
                
                name_priority = ['tourism', 'historic', 'natural', 'amenity', 'shop', 'leisure', 'aerodrome', 'building']
                place_name = ""
                for key in name_priority:
                    if address_components.get(key):
                        place_name = address_components.get(key)
                        break
                
                if not place_name:
                    # Fallback to more general terms if specific ones not found or to refine
                    road = address_components.get('road', '')
                    suburb = address_components.get('suburb', '')
                    # Prefer suburb over road if available, otherwise first part of address
                    place_name = suburb if suburb else (road if road else location.address.split(',')[0])

                # Ensure place_name is not just a house number if possible
                if place_name.replace('.','',1).isdigit() and address_components.get('road'):
                    place_name = address_components.get('road')

                city = address_components.get('city', address_components.get('town', address_components.get('village', address_components.get('county', ''))))
                country = address_components.get('country', '')
                
                return {
                    "name": place_name.strip(),
                    "city": city.strip(),
                    "country": country.strip(),
                    "full_address": location.address
                }
            else:
                 return {"name": "Unknown Location", "city": "", "country": "", "full_address": ""}
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Geocoding error for ({lat},{lon}): {e}"))
            return {"name": "Geocoding Error", "city": "", "country": "", "full_address": "Error during geocoding"} 