
Installation
============

Docker
------

Docker Settings:
----------------

Here are the options you need to passthrough to docker for this
container to work:

Ports
~~~~~

Only Port 80 is required to access the container.

Volumes
~~~~~~~

You need to pass through 3 volumes to the container for it to work
properly.

/config
^^^^^^^

This is where the config database is stored. If you have the older
version of the scripts running before the GUI and database
implimentation there is a migration path where your config file is
automattically imported into the database. The config file must be in
this config directory

/logs
^^^^^

This is where the logs are stored.

/films
^^^^^^

Your plex media. You should pass though the root directory containing
all your plex media, not just the films/movies directories.

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

PUID and PGID
^^^^^^^^^^^^^

These need to match the user and group ID for the user that has read and
write access to your plex directories. On linuix this is usually 1000
for both.

If you are running on Unraid, you will need to set ``PUID=99`` and
``PGID=100``

TZ
^^

Your local timezone. Should be in the format ``Europe/London`` or
``America/New_York`` See here for more information: `TZdata
Wikipedia <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`__

--------------

Linux and mac systems:
----------------------

::

   docker run -d --name plex-utills \
   -p 80:80 \
   -v <your_config_directory>:/config \
   -v <your_logs_directory>:/logs \
   -v <your_plex_media>:/films \
   -e TZ=Europe/London \
   -e PUID=1000 \
   -e PGID=1000 \
   jkirkcaldy/plex-utills

--------------

UnRaid
------

To install on Unraid, you need to have the Community Apps plugin. If you
don't have it `click here to
install <https://unraid.net/community/apps>`__

Go to the community apps plugin page on your unraid server and search
for Plex-Utills and click install.

This is what your setup should look like: |unraid-settings|

--------------

Synology
--------

To install on synology, first make sure you have installed docker on
your synology server. Ther are many tutoials on teh web for how to do
this.

Once docker is installed, open the docker settings window on your
synology server. Then click on Registry and search for Plex-utills
|image1| Click on the result jkirkcaldy/plex-utills and click download.

For the image tag, select latest. |image2|

From there click on Image and you will see the image downloading. Once
it has finished, select the image and click launch. On the window that
pops up, click Advanced Settings. |image3|

In that window, click on Volume. We need to add three volumes for the
container to work. Click on add volume and add the three volumes. These
are: /config /logs /films

I recommend creating a folder called plex-utills on your array and then
creating two folders in there, one for your logs and one for your config
files. When done it should look like this: |image4|

The container needs only port 80 to work. By default synology will
assign random ports automatically, you can change this to any free port
on your system to make it easier to remember.

The only thing left to change now is the Timezone setting. To change
this go to the Environment tab and scroll to the bottom of the options
until you get to where it sayz TZ Europe/London

|image5|

Change this to your timezone. `Click here to find what that should
be <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>`__

Once you are done, click apply and the container will start. Click on
where it says Containers to see the running container. |image6|

Select the container and click on the action menu, then details. This
will show you the ports that your server has applied to the container if
you left these on auto. From here you can also see the container logs,
whihc is useful if something's not working correctly. |image7|

Once you have located the port number your container is running on, open
a new browser window and enter : In my case the server is running on IP
address 10.254.100.81 and the container is using port 49158 (my ports
changed when taking the images)

So I enter http://10.254.100.81:49158 into my browser window and I get the plex-utills webui

|image8|

Troubleshooting
---------------

If your container is not starting properly or you get a nginx error when
visiting the web page, it is likely that the permissions need to be
changed on the directories that you set for the config and the logs.
Change these to be read/write for everyone and try restarting the
container.

You also only need to pass through your plex media directories if you
want to use the backup posters feature. If you don't want to enable that
then you don't need to passthrough the /films volume.

.. |unraid-settings| image:: https://github.com/jkirkcaldy/plex-utills/blob/177982ee9a6b17e800f634a6c4dd1376df088f38/app/img/Examples/Unraid-CA-Plex-utills.png?raw=true
.. |image1| image:: https://i.imgur.com/KTjNIlw.png
.. |image2| image:: https://i.imgur.com/fG19eYC.png
.. |image3| image:: https://i.imgur.com/W3azpBv.png
.. |image4| image:: https://i.imgur.com/Vv5qCnk.png
.. |image5| image:: https://i.imgur.com/orNGVzc.png
.. |image6| image:: https://i.imgur.com/8mF8EwV.png
.. |image7| image:: https://i.imgur.com/zifVr8r.png
.. |image8| image:: https://i.imgur.com/EqjROo0.png
