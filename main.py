# importations
import PyPDF2
import argparse
import re
import exifread
import sqlite3
import os

# PDF


def get_pdf_meta(file):

    pdf_file = PyPDF2.PdfFileReader({file} + "rb")
    doc_info = pdf_file.getDocumentInfo()

    for info in doc_info:
        print("[+]" + info + "" + doc_info[info])


# EXIF
def get_exif(file):
    with open(file, "rb") as file:
        exif = exifread.process_file(file)
    if not exif:
        print("No EXIF data found")
    else:
        for tag in exif.keys():
            print(tag + " " + str(exif[tag]))


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)
    return d + (m / 60.0) + (s / 3600.0)


def get_gps_from_exif(file_name):
    with open(file_name, "rb") as file:
        exif = exifread.process_file(file)
    if not exif:
        print("Aucune métadonnée EXIF.")
    else:
        latitude = exif.get("GPS GPSLatitude")
        latitude_ref = exif.get("GPS GPSLatitudeRef")
        longitude = exif.get("GPS GPSLongitude")
        longitude_ref = exif.get("GPS GPSLongitudeRef")
        altitude = exif.get("GPS GPSAltitude")
        altitude_ref = exif.get("GPS GPSAltitudeRef")
        if latitude and longitude and latitude_ref and longitude_ref:
            lat = _convert_to_degress(latitude)
            long = _convert_to_degress(longitude)
            if str(latitude_ref) != "N":
                lat = 0 - lat
            if str(longitude_ref) != "E":
                long = 0 - long
            print("LAT : " + str(lat) + " LONG : " + str(long))
            print("http://maps.google.com/maps?q=loc:%s,%s" %
                  (str(lat), str(long)))
            if altitude and altitude_ref:
                alt_ = altitude.values[0]
                alt = alt_.num / alt_.den
                if altitude_ref.values[0] == 1:
                    alt = 0 - alt
                print("ALTITUDE : " + str(alt))


def get_firefox_history(places_sqlite):
    try:
        conn = sqlite3.connect(places_sqlite)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT url, datetime(last_visit_date/100000, \"unixepoch\") FROM moz_places, moz_historyvisits where visit_count > 0 and moz_places.id==moz_historyvisits.place_id;")

        if os.path.exists("firefox_history.html"):
            os.remove("firefox_history.html")

        header = "<!DOCTYPE html><html><head><style>table, th, tr{border:1px solid black}</style><title>Firefox History</title></head><body><h1>Rapport historique</h1><table><tr><th>URL</th><th>Last Visited</th></tr>"
        with open("firefox_history.html", "w") as f:
            f.write(header)
            for row in cursor:
                url = str(row[0])
                date = str(row[1])
                f.write("<tr><td><a href='" + url + "'>" + url +
                        "</a></td><td>" + date + "</td></tr>")
            footer = "</table></body></html>"
            f.write(footer)

    except Exception as e:
        print("Exception : " + str(e))
        exit(1)


def get_firefox_cookies(cookies_sqlite):
    try:
        conn = sqlite3.connect(cookies_sqlite)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT host, name, value FROM moz_cookies;")

        if os.path.exists("firefox_cookies.html"):
            os.remove("firefox_cookies.html")

        header = "<!DOCTYPE html><html><head><style>table, th, tr{border:1px solid black}</style><title>Firefox Cookies</title></head><body><h1>Rapport cookies</h1><table><tr><th>Host</th><th>Name</th><th>Value</th></tr>"
        with open("firefox_cookies.html", "w") as f:
            f.write(header)
            for row in cursor:
                host = str(row[0])
                name = str(row[1])
                value = str(row[2])
                f.write("<tr><td>" + host + "</td><td>" + name +
                        "</td><td>" + value + "</td></tr>")
            footer = "</table></body></html>"
            f.write(footer)

    except Exception as e:
        print("Exception : " + str(e))
        exit(1)

# parsing


def get_strings(file):
    with open(file, "rb") as file:
        content = file.read()
    _re = re.compile(b"[/S/s]{4,}")
    for match in _re.finditer(content.decode("utf-8", "backslashreplace")):
        print(match.group())
    for match in _re.finditer(content.decode("utf-16", "backslashreplace")):
        print(match.group())


parser = argparse.ArgumentParser(description="Foresinc tool")
parser.add_argument(
    "-pdf", dest="pdf",
    help="Chemin du fichier pdf", required=False)

parser.add_argument(
    "-str", dest="str",
    help="Chemin du fichier pour récupérer les string", required=False)

parser.add_argument(
    "-img", dest="img",
    help="Chemin du fichier image pour extraction des donnes exif", required=False)

parser.add_argument(
    "-gps", dest="gps",
    help="Récupération des coordonnée GPS depuis l'image", required=False)

parser.add_argument(
    "-ff", dest="ff",
    help="Récupération des données historique firefox", required=False)

parser.add_argument(
    "-fc", dest="fc",
    help="Récupération des données cookies firefox", required=False)

args = parser.parse_args()

if args.pdf:
    get_pdf_meta(args.pdf)

if args.str:
    get_strings(args.str)

if args.img:
    get_exif(args.img)

if args.gps:
    get_gps_from_exif(args.gps)

if args.ff:
    get_firefox_history(args.ff)

if args.fc:
    get_firefox_cookies(args.fc)
