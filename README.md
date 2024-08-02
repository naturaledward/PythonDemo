This is a demo showcasing my Python and Back-End Development knowledge:



The DJ software I use recently released a version update. After downloading and installing the update, I noticed that it had changed the metadata of some of my music tracks. I color my tracks red and the update cleared not just the color of those tracks but also the Year, Genre, Rating and Play Count among other key fields. (I will be following the track ‘Sweet Child O Mine’ from artist ‘Guns N Roses’ for this demo)

![1](https://github.com/user-attachments/assets/d3a4f4e5-35d9-4104-bfcd-87bada495ea1)



I isolated all affected tracks into a filtered list

![2](https://github.com/user-attachments/assets/b4c845d5-26ec-4cc3-a526-3c53f32e47a9)



After viewing the most recent backup of the database prior to the update, in the form of an xml file, I identified and located each field that was cleared after the version update and began thinking of a way of extracting the preserved values of those fields for all affected tracks using Python (My intention was to use this data from the backup to restore the state of all tracks affected by the update)

![3](https://github.com/user-attachments/assets/3055574c-24d3-4e32-bced-a11a42148393)



It would involve extracting the pertinent data from the backup database xml and creating a SQLite database to store that data. I normalized the SQLite database by creating additional tables for Genre and Artist, then used foreign keys in the main table, Track, to link to Genre and Artist names. (NOTE: I installed DB Browser for SQLite (DB4S) just to be able to view the tables in a user interface, though not necessary for this demo. Link to download and install DB4S: https://sqlitebrowser.org/dl/)

![4](https://github.com/user-attachments/assets/df65f712-c308-45e9-8859-545957701ff5)



Then I ran sql queries on the SQLite database for each song to retrieve the preserved field values that were cleared from the actual tracks in my DJ software after the update.

![5](https://github.com/user-attachments/assets/5cb839b7-811e-4c3e-b8fa-5b49b44301c2)



I do not know how the DJ software updates its tracks, so to prevent any further unintended damage, I copied the backup preserved data from the SQL query and updated the fields using the DJ software user interface for each track.

![6](https://github.com/user-attachments/assets/1e7243be-ab23-46eb-b130-78c4a1768665)



The Python script that I’ve written(musicFiles_sqlite_demo.py) to resolve my issue and the backup database(database.xml) from the DJ Software can be pulled from this Github repository.

If on MacOS terminal, you can clone the repo to your machine with this command: % git clone https://github.com/naturaledward/PythonDemo.git

Here are some notes on the Python program(musicFiles_sqlite_demo.py):
1. copy of DJ software backup database, database.xml, located in the same directory as this Python program
2. parses the xml and creates a SQLite database, musicFiles.sqlite, in same directory
3. the parsed data from xml is transferred to the SQLite database
4. a query is run on an affected song to retrieve preserved fields prior to track corruption after DJ software update
5. enter 'guns n r' for artist and 'sweet' for track, 'q' to quit program
6. SQLite database, musicFiles.sqlite, is overwritten every time this Python program runs
