import os, sqlite3
import xml.etree.ElementTree as ET
import sys

# copy of DJ software backup database, database.xml, located in the same directory as this Python program
# parses the xml and creates a SQLite database, musicFiles.sqlite, in same directory
# the parsed data from xml is transferred to the SQLite database
# a query is run on an affected song to retrieve preserved fields prior to track corruption after DJ software update
# SQLite database, musicFiles.sqlite, is overwritten every time this Python program runs

# Extract contents of DJ software database, database.xml
srcFile = "database.xml"
tree = ET.parse(srcFile)
root = tree.getroot()

# Create SQLite database and Data Model
conn = sqlite3.connect("musicFiles.sqlite")
cur = conn.cursor()
cur.executescript(
    """
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS TrackDirectory;
DROP TABLE IF EXISTS TrackExtension;
DROP TABLE IF EXISTS Color;
DROP TABLE IF EXISTS Track;
CREATE TABLE Artist (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE);
CREATE TABLE Genre (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE);
CREATE TABLE TrackDirectory (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE);
CREATE TABLE TrackExtension (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE);
CREATE TABLE Color (
   id INTEGER UNIQUE,
   name TEXT UNIQUE);
CREATE TABLE Track (
    trackdirectory_id INTEGER,
    filename TEXT,
    trackextension_id INTEGER,
    title TEXT,
    artist_id INTEGER,
    genre_id INTEGER,
    label BOOLEAN,
    year INTEGER,
    grouping INTEGER CHECK (grouping>-4 AND grouping<4 AND grouping != 0),
    color_id INTEGER,
    bpm FLOAT,
    key VARCHAR(5),
    stars INTEGER,
    playcount INTEGER,
    firstseen DATE,
    lastplay DATETIME,
    comment TEXT,
    user1 TEXT,
    user2 TEXT,
    PRIMARY KEY (trackdirectory_id, filename)
    );
"""
)

# import parsed data from DJ software database, database.xml, into SQLite database
d = dict()
for child in root:
    d[child.tag] = d.get(child.tag, 0) + 1
    author = child.find("Tags").get("Author")
    if author != None:
        cur.execute("INSERT OR IGNORE INTO Artist (name) VALUES (?)", (author,))
        cur.execute("SELECT id FROM Artist WHERE name = ?", (author,))
        artist_id = cur.fetchone()[0]
    else:
        artist_id = None
    genre = child.find("Tags").get("Genre")
    if genre != None:
        cur.execute("INSERT OR IGNORE INTO Genre (name) VALUES (?)", (genre,))
        cur.execute("SELECT id FROM Genre WHERE name = ?", (genre,))
        genre_id = cur.fetchone()[0]
    else:
        genre_id = None
    trackfilepath = child.get("FilePath")
    trackdirectory = os.path.split(trackfilepath)[0]
    cur.execute(
        "INSERT OR IGNORE INTO TrackDirectory (name) VALUES (?)", (trackdirectory,)
    )
    cur.execute("SELECT id FROM TrackDirectory WHERE name = ?", (trackdirectory,))
    trackdirectory_id = cur.fetchone()[0]
    trackextension = os.path.splitext(trackfilepath)[1][1:].lower()
    cur.execute(
        "INSERT OR IGNORE INTO TrackExtension (name) VALUES (?)", (trackextension,)
    )
    cur.execute("SELECT id FROM TrackExtension WHERE name = ?", (trackextension,))
    trackextension_id = cur.fetchone()[0]
    usercolor = child.find("Infos").get("UserColor")
    if usercolor != None:
        cur.execute("INSERT OR IGNORE INTO Color (id) VALUES (?)", (usercolor,))
        cur.execute("SELECT id FROM Color WHERE id = ?", (usercolor,))
        color_id = cur.fetchone()[0]
    else:
        color_id = None    

    # import into main table: Track
    trackfilename = os.path.split(trackfilepath)[1]
    title = child.find("Tags").get("Title")
    if child.find("Tags").get("Label") == None:
        label = None
    elif child.find("Tags").get("Label").lower() == "x":
        label = 1
    else:
        raise Exception("Label tag should be x or NULL, fix field in VDJ")
    year = child.find("Tags").get("Year")
    grouping = child.find("Tags").get("Grouping")
    try:
        if grouping != None:
            grouping = int(grouping)
            if not (grouping > -4 and grouping < 4):
                print("grouping should only have integer values -3, -2, -1, 1, 2, 3")
                sys.exit()
    except:
        print("grouping should only have integer values")
        sys.exit()
    usercolor = child.find("Infos").get("UserColor")
    bpm = child.find("Scan")
    try:
        if bpm != None:
            bpm = float(bpm.get("Bpm"))
    except:
        print("bpm should be a floating point number")
        sys.exit()
    key = child.find("Scan")
    if key != None:
        key = key.get("Key")
    stars = child.find("Tags").get("Stars")
    playcount = child.find("Infos").get("PlayCount")
    firstseen = child.find("Infos").get("FirstSeen")
    lastplay = child.find("Infos").get("LastPlay")
    comment = child.find("Comment")
    if comment != None:
        comment = child.find("Comment").text
    user1 = child.find("Tags").get("User1")
    user2 = child.find("Tags").get("User2")

    cur.execute(
        """
    INSERT INTO Track ( trackdirectory_id, filename, trackextension_id, title, artist_id, genre_id, label, year, grouping, color_id,
    bpm, key, stars, playcount, firstseen, lastplay, comment, user1, user2)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
        (
            trackdirectory_id,
            trackfilename,
            trackextension_id,
            title,
            artist_id,
            genre_id,
            label,
            year,
            grouping,
            color_id,
            bpm,
            key,
            stars,
            playcount,
            firstseen,
            lastplay,
            comment,
            user1,
            user2,
        ),
    )  # if SQL error, duplicate filename in same folder in database file, this shouldn't happen
conn.commit()
t = list(d.keys())
if len(t) == 1 and t[0] == "Song":
    print(f".xml is a tree of {d[t[0]]} {t[0]}")
else:
    print(".xml should only have tag Song as child of root")

# import color names into Color table
colorDic = {
   4294901760: "red",
   4294967040: "yellow",
   4278255360: "green",
   4278255615: "cyan",
   4278190335: "blue",
   4294902015: "magenta",
   4294967295: "white",
}
for i in colorDic:
   cur.execute("UPDATE Color SET name = ? WHERE id = ?", (colorDic[i], i))

# Run Query on each song that was affected by DJ software upgrade & use results update track fields in DJ software user interface
while True:
    artist_search_str = ( "%" + input("\nEnter search string for artist(q to quit): ") + "%" )
    if artist_search_str == "%q%": break
    track_search_str = "%" + input("Enter search string for track(q to quit): ") + "%"
    if track_search_str == "%q%": break
    print( f"Query search results for (artist: '{artist_search_str[1:-1]}') & (track: '{track_search_str[1:-1]}'):" )
    sqlstr = "SELECT 'artist', 'track', 'genre', 'year', 'grouping', 'color', 'rating', 'playcount', 'comment', 'notes1', 'notes2'"
    for row in cur.execute(sqlstr):
        for i in range(len(row)):
            if i < len(row) - 1: print(row[i], end="|")
            else: print(row[i])
    for row in cur.execute( """
    SELECT Artist.name, title, Genre.name, year, grouping, Color.name, stars, playcount, comment, user1, user2
    FROM Track JOIN Artist JOIN Genre JOIN TrackDirectory JOIN Color
    ON Track.artist_id = Artist.id
    AND Track.genre_id = Genre.id
    AND Track.trackdirectory_id = TrackDirectory.id
    AND Track.color_id = Color.id
    WHERE Artist.name LIKE ? AND title LIKE ?
    """, (artist_search_str, track_search_str), ):
        for i in range(len(row)):
            if i < len(row) - 1: print(row[i], end="|")
            else: print(row[i])
cur.close()