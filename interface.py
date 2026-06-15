from pathlib import Path
from io import BytesIO
import os

from flask import Flask, abort, render_template, request, send_from_directory, Response
import mysql.connector
from PIL import Image, ImageOps


DB_NAME = "photo_archive"
IMAGE_FOLDER = Path("photo_archive")

app = Flask(__name__)

THUMBNAIL_CACHE = {}


def open_database():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "photo_archive"),
    )


def format_file_size(size_in_bytes):
    if size_in_bytes is None:
        return "keine Angabe"

    size = float(size_in_bytes)
    units = ["B", "KB", "MB", "GB"]

    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024


def display_value(value):
    return value if value not in (None, "") else "keine Angabe"


def load_images(date_from="", date_to="", search=""):
    connection = open_database()
    cursor = connection.cursor()

    query = """
        SELECT
            i.id,
            i.filename,
            i.filesize,
            i.image_width,
            i.image_height,
            i.format,
            px.datetime_original,
            px.camera_make,
            px.camera_model
        FROM images i
        LEFT JOIN photoexif px ON px.image_id = i.id
        WHERE 1=1
    """

    params = []

    if search.strip():
        query += " AND i.filename LIKE %s"
        params.append(f"%{search.strip()}%")

    if date_from.strip():
        query += " AND SUBSTRING(px.datetime_original,1,10) >= %s"
        params.append(date_from.replace("-", ":"))

    if date_to.strip():
        query += " AND SUBSTRING(px.datetime_original,1,10) <= %s"
        params.append(date_to.replace("-", ":"))

    query += " ORDER BY i.id DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    images = []

    for row in rows:
        camera = " ".join(part for part in [row[7], row[8]] if part)

        images.append({
            "id": row[0],
            "filename": row[1],
            "filesize": format_file_size(row[2]),
            "dimensions": f"{row[3]} × {row[4]}",
            "format": row[5],
            "date": row[6],
            "camera": camera if camera else "keine Kamera-Daten",
        })

    return images


def load_image_details(image_id):
    connection = open_database()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            i.id,
            i.filename,
            i.filepath,
            i.filesize,
            i.image_width,
            i.image_height,
            i.format,
            i.mode,
            i.animated,
            i.frames,
            i.dpi_x,
            i.dpi_y,
            i.compression,
            i.icc_profile,
            px.camera_make,
            px.camera_model,
            px.lens_model,
            px.exposure_time,
            px.aperture,
            px.iso,
            px.focal_length,
            px.focal_length_35mm,
            px.datetime_original,
            px.datetime_digitized,
            px.software
        FROM images i
        LEFT JOIN photoexif px ON px.image_id = i.id
        WHERE i.id = %s
    """, (image_id,))

    image = cursor.fetchone()

    cursor.close()
    connection.close()

    return image


def build_metadata_sections(image):
    image_data = [
        ("ID", image["id"]),
        ("Dateiname", image["filename"]),
        ("Dateigrösse", format_file_size(image["filesize"])),
        ("Bildgrösse", f"{image['image_width']} × {image['image_height']}"),
        ("Format", image["format"]),
        ("Farbmodus", image["mode"]),
        ("Animiert", "Ja" if image["animated"] else "Nein"),
        ("Frames", image["frames"]),
        ("DPI", f"{image['dpi_x']} × {image['dpi_y']}" if image["dpi_x"] or image["dpi_y"] else None),
        ("Kompression", image["compression"]),
        ("ICC-Profil", "vorhanden" if image["icc_profile"] else None),
    ]

    photo_data = [
        ("Kamerahersteller", image["camera_make"]),
        ("Kameramodell", image["camera_model"]),
        ("Objektiv", image["lens_model"]),
        ("ISO", image["iso"]),
        ("Blende", f"f/{image['aperture']}" if image["aperture"] else None),
        ("Belichtungszeit", f"{image['exposure_time']} s" if image["exposure_time"] else None),
        ("Brennweite", f"{image['focal_length']} mm" if image["focal_length"] else None),
        ("Brennweite 35mm", f"{image['focal_length_35mm']} mm" if image["focal_length_35mm"] else None),
        ("Aufnahmedatum", image["datetime_original"]),
        ("Digitalisiert", image["datetime_digitized"]),
        ("Software", image["software"]),
    ]

    return [
        {"title": "Bilddaten", "items": image_data},
        {"title": "Fotodaten", "items": photo_data},
    ]




def load_image_blob(image_id):
    connection = open_database()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT filename, mime_type, image_data
        FROM images
        WHERE id = %s
    """, (image_id,))

    image = cursor.fetchone()

    cursor.close()
    connection.close()

    return image


@app.route("/db-thumbnail/<int:image_id>")
def serve_db_thumbnail(image_id):
    max_size = request.args.get("size", default=520, type=int)
    max_size = max(120, min(max_size, 1200))

    cache_key = (image_id, max_size)

    if cache_key in THUMBNAIL_CACHE:
        thumbnail_bytes, mime_type = THUMBNAIL_CACHE[cache_key]
        return Response(thumbnail_bytes, mimetype=mime_type)

    image_record = load_image_blob(image_id)

    if not image_record or not image_record.get("image_data"):
        abort(404)

    with Image.open(BytesIO(image_record["image_data"])) as source:
        source = ImageOps.exif_transpose(source)
        source.thumbnail((max_size, max_size))

    if source.mode in ("RGBA", "LA"):
        background = Image.new("RGB", source.size, (255, 255, 255))
        background.paste(source, mask=source.getchannel("A"))
        source = background
    elif source.mode != "RGB":
        source = source.convert("RGB")

    output = BytesIO()
    source.save(output, format="JPEG", quality=82, optimize=True)

    if source.mode not in ("RGB", "L"):
       source = source.convert("RGB")

       output = BytesIO()
       source.save(output, format="JPEG", quality=82, optimize=True)

    thumbnail_bytes = output.getvalue()
    mime_type = "image/jpeg"

    THUMBNAIL_CACHE[cache_key] = (thumbnail_bytes, mime_type)

    return Response(thumbnail_bytes, mimetype=mime_type)


@app.route("/db-image/<int:image_id>")
def serve_db_image(image_id):
    connection = open_database()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT filename, mime_type, image_data
        FROM images
        WHERE id = %s
    """, (image_id,))

    image = cursor.fetchone()

    cursor.close()
    connection.close()

    if not image or not image.get("image_data"):
        abort(404)

    return Response(
        image["image_data"],
        mimetype=image.get("mime_type") or "application/octet-stream",
        headers={"Content-Disposition": f"inline; filename={image['filename']}"},
    )


@app.route("/images/<filename>")
def serve_image(filename):
    if ".." in filename or filename.startswith("/"):
        abort(404)
    return send_from_directory(IMAGE_FOLDER, filename)


@app.route("/")
def index():
    search = request.args.get("search", "")
    date_from = request.args.get("from", "")
    date_to = request.args.get("to", "")

    return render_template(
        "index.html",
        images=load_images(date_from, date_to, search),
    )


@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = load_image_details(image_id)

    if not image:
        return "Bild nicht gefunden", 404

    return render_template(
        "image.html",
        image=image,
        sections=build_metadata_sections(image),
        display_value=display_value,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
