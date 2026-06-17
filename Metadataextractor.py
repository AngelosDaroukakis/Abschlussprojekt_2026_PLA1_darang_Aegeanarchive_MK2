from pathlib import Path
from tkinter import Tk, filedialog, messagebox
import mimetypes
import os
import mysql.connector
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS, GPSTAGS
from io import BytesIO

THUMBNAIL_SIZE = 700
THUMBNAIL_QUALITY = 90

DB_NAME = "photo_archive"

SUPPORTED_IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png",
    ".bmp", ".gif"
}

TAG_NAME_TO_ID = {name: tag_id for tag_id, name in TAGS.items()}

EXIF_IFD_TAG = 0x8769
GPS_IFD_TAG = 0x8825


def sql_safe(value):
    if value is None:
        return None

    if isinstance(value, (int, float, str)):
        return value

    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        try:
            return float(value.numerator) / float(value.denominator)
        except Exception:
            return None

    if isinstance(value, (tuple, list)):
        return str(value)

    return str(value)


def open_database():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "aegean"),
        password=os.getenv("DB_PASSWORD", "aegean"),
        port=int(os.getenv("DB_PORT", "3307")),
        database=os.getenv("DB_NAME", "photo_archive"),
    )


def column_exists(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = %s
          AND TABLE_NAME = %s
          AND COLUMN_NAME = %s
        """,
        (DB_NAME, table_name, column_name),
    )

    return cursor.fetchone()[0] > 0


def create_tables():
    connection = open_database()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            filepath VARCHAR(500) NOT NULL,
            filesize BIGINT NOT NULL,
            image_width INT NOT NULL,
            image_height INT NOT NULL,
            format VARCHAR(50) NOT NULL,
            mode VARCHAR(20) NOT NULL,
            animated BOOLEAN NOT NULL,
            frames INT NOT NULL,
            dpi_x FLOAT,
            dpi_y FLOAT,
            compression VARCHAR(50),
            icc_profile BOOLEAN NOT NULL,
            mime_type VARCHAR(100),
            image_data LONGBLOB,
            thumbnail_mime_type VARCHAR(100),
            thumbnail_data MEDIUMBLOB,
            description TEXT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS photoexif (
            image_id INT PRIMARY KEY,
            camera_make VARCHAR(100),
            camera_model VARCHAR(100),
            lens_model VARCHAR(150),
            exposure_time FLOAT,
            aperture FLOAT,
            iso INT,
            focal_length FLOAT,
            focal_length_35mm INT,
            exposure_program INT,
            metering_mode INT,
            white_balance INT,
            flash INT,
            orientation INT,
            datetime_original VARCHAR(50),
            datetime_digitized VARCHAR(50),
            software VARCHAR(100),
            FOREIGN KEY (image_id)
                REFERENCES images(id)
                ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gps (
            image_id INT PRIMARY KEY,
            latitude DOUBLE,
            longitude DOUBLE,
            altitude DOUBLE,
            latitude_ref CHAR(1),
            longitude_ref CHAR(1),
            altitude_ref TINYINT,
            FOREIGN KEY (image_id)
                REFERENCES images(id)
                ON DELETE CASCADE
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()


def extract_full_exif(image: Image.Image) -> dict:
    exif_data = image.getexif()

    if not exif_data:
        return {}

    merged = dict(exif_data)

    try:
        exif_ifd = exif_data.get_ifd(EXIF_IFD_TAG)
        if isinstance(exif_ifd, dict):
            merged.update(exif_ifd)
    except Exception:
        pass

    try:
        gps_ifd = exif_data.get_ifd(GPS_IFD_TAG)
        if isinstance(gps_ifd, dict):
            merged[GPS_IFD_TAG] = gps_ifd
    except Exception:
        pass

    return merged


def get_exif_tag(exif: dict, tag_name: str):
    tag_id = TAG_NAME_TO_ID.get(tag_name)
    return exif.get(tag_id) if tag_id else None


def coords_to_degrees(coord, reference):
    if not coord:
        return None

    parts = [sql_safe(part) for part in coord]

    if len(parts) != 3 or None in parts:
        return None

    degrees = parts[0] + parts[1] / 60 + parts[2] / 3600

    if reference in ("S", "W"):
        return -degrees

    return degrees


def read_image_bytes(path: Path) -> bytes:
    return path.read_bytes()


def detect_mime_type(path: Path, image: Image.Image):
    guessed_type, _ = mimetypes.guess_type(path.name)

    if guessed_type:
        return guessed_type

    if image.format:
        return f"image/{image.format.lower()}"

    return "application/octet-stream"

def create_thumbnail_data(image: Image.Image) -> bytes:
    """Erstellt ein kleines JPEG-Thumbnail und gibt es als Bytes zurück."""

    thumbnail = ImageOps.exif_transpose(image).copy()

    thumbnail.thumbnail(
        (THUMBNAIL_SIZE, THUMBNAIL_SIZE),
        Image.Resampling.LANCZOS,
    )

    if thumbnail.mode in ("RGBA", "LA"):
        background = Image.new(
            "RGB",
            thumbnail.size,
            (255, 255, 255),
        )

        background.paste(
            thumbnail,
            mask=thumbnail.getchannel("A"),
        )

        thumbnail = background

    elif thumbnail.mode != "RGB":
        thumbnail = thumbnail.convert("RGB")

    output = BytesIO()

    thumbnail.save(
        output,
        format="JPEG",
        quality=THUMBNAIL_QUALITY,
        optimize=True,
    )

    return output.getvalue()

def insert_image_record(
    cursor,
    source_path: Path,
    image: Image.Image,
    image_data: bytes,
    thumbnail_data: bytes,
):

    dpi = image.info.get("dpi")
    dpi_x = sql_safe(dpi[0]) if dpi else None
    dpi_y = sql_safe(dpi[1]) if dpi else None

    compression = sql_safe(image.info.get("compression"))
    icc_profile = bool(image.info.get("icc_profile"))

    animated = getattr(image, "is_animated", False)
    frames = getattr(image, "n_frames", 1)

    mime_type = detect_mime_type(source_path, image)

    cursor.execute("""
        INSERT INTO images (
            filename, filepath,
            filesize,
            image_width, image_height,
            format, mode,
            animated, frames,
            dpi_x, dpi_y,
            compression, icc_profile,
            mime_type, image_data, thumbnail_mime_type, thumbnail_data
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
       source_path.name,
    str(source_path),
    len(image_data),
    image.width,
    image.height,
    image.format,
    image.mode,
    bool(getattr(image, "is_animated", False)),
    int(getattr(image, "n_frames", 1)),
    dpi_x,
    dpi_y,
    compression,
    icc_profile,
    mime_type,
    image_data,
    "image/jpeg",
    thumbnail_data,
    ))

    return cursor.lastrowid


def insert_exif_record(cursor, image_id: int, exif: dict):
    cursor.execute("""
        INSERT INTO photoexif (
            image_id,
            camera_make, camera_model, lens_model,
            exposure_time, aperture, iso,
            focal_length, focal_length_35mm,
            exposure_program, metering_mode,
            white_balance, flash, orientation,
            datetime_original, datetime_digitized,
            software
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        image_id,
        sql_safe(get_exif_tag(exif, "Make")),
        sql_safe(get_exif_tag(exif, "Model")),
        sql_safe(get_exif_tag(exif, "LensModel")),
        sql_safe(get_exif_tag(exif, "ExposureTime")),
        sql_safe(get_exif_tag(exif, "FNumber")),
        sql_safe(get_exif_tag(exif, "ISOSpeedRatings")),
        sql_safe(get_exif_tag(exif, "FocalLength")),
        sql_safe(get_exif_tag(exif, "FocalLengthIn35mmFilm")),
        sql_safe(get_exif_tag(exif, "ExposureProgram")),
        sql_safe(get_exif_tag(exif, "MeteringMode")),
        sql_safe(get_exif_tag(exif, "WhiteBalance")),
        sql_safe(get_exif_tag(exif, "Flash")),
        sql_safe(get_exif_tag(exif, "Orientation")),
        sql_safe(get_exif_tag(exif, "DateTimeOriginal")),
        sql_safe(get_exif_tag(exif, "DateTimeDigitized")),
        sql_safe(get_exif_tag(exif, "Software")),
    ))


def insert_gps_record(cursor, image_id: int, exif: dict):
    gps_raw = exif.get(GPS_IFD_TAG)

    if not isinstance(gps_raw, dict):
        return

    gps = {GPSTAGS.get(key, key): value for key, value in gps_raw.items()}

    latitude_ref = gps.get("GPSLatitudeRef")
    longitude_ref = gps.get("GPSLongitudeRef")

    latitude = coords_to_degrees(gps.get("GPSLatitude"), latitude_ref)
    longitude = coords_to_degrees(gps.get("GPSLongitude"), longitude_ref)

    altitude = sql_safe(gps.get("GPSAltitude"))
    altitude_ref = gps.get("GPSAltitudeRef")

    cursor.execute("""
        INSERT INTO gps (
            image_id,
            latitude, longitude, altitude,
            latitude_ref, longitude_ref, altitude_ref
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        image_id,
        sql_safe(latitude),
        sql_safe(longitude),
        altitude,
        latitude_ref,
        longitude_ref,
        altitude_ref,
    ))


def store_image_and_metadata(path: Path):
    image_data = read_image_bytes(path)

    connection = open_database()
    cursor = connection.cursor()

    try:
        with Image.open(path) as image:
            exif = extract_full_exif(image)

            thumbnail_data = create_thumbnail_data(image)

            image_id = insert_image_record(
                cursor,
                path,
                image,
                image_data,
                thumbnail_data,
            )

            insert_exif_record(cursor, image_id, exif)
            insert_gps_record(cursor, image_id, exif)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def pick_paths():
    root = Tk()
    root.withdraw()

    if messagebox.askyesno(
        "Auswahl",
        "Einzelne Dateien auswählen?\nNein = ganzen Ordner scannen.",
    ):
        files = filedialog.askopenfilenames(title="Bilder auswählen")
        paths = [Path(file) for file in files]

    else:
        folder = filedialog.askdirectory(title="Ordner auswählen")

        if not folder:
            paths = []
        else:
            paths = [
                path for path in Path(folder).iterdir()
                if path.is_file()
                and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
            ]

    root.destroy()
    return paths


def main():
    create_tables()

    paths = pick_paths()

    if not paths:
        print("Keine Bilder gefunden.")
        return

    print(f"{len(paths)} Speichervorgang beginnt.")

    for path in paths:
        try:
            store_image_and_metadata(path)
            print(f"Gespeichert in DB: {path.name}")
        except Exception as error:
            print(f"Fehler bei {path.name}: {error}")

    print("Speichervorgang beendet.")


if __name__ == "__main__":
    main()
