#Svbtle subscriber

Simple app to:

- See who is blogging at [svbtle.com](http://svbtle.com)
- See who you aren't following via RSS already

##Why

I wanted to subscribe to all the awesome content on the svtble blogging
network.  However, they don't provide a master feed and new people seem to be
added daily.

I was tired of manually searching through the list and seeing if my RSS reader
had all the writer's feeds added.

###Install

This application is double threat.  It has a cli and web interface.  Thus, the
requirements are broken up accordingly.  Use whichever you are interested in or
run 'make all' to install it all.

    1. Get Code

        - git clone git://github.com/durden/svbtle_subscriber.git

    2. Install requirements (only one of these is required)

        - pip install -r cli_requirements.txt OR make cli
        - pip install -r web_requirements.txt OR make web
        - make all

** Note that requirements.txt exists and is a copy of web_requirements.txt.
** This is requirement for hosting at [heroku](http://heroku.com), which
mandates that Python applications have their requirements in a file called
requirements.txt.

    3. Install svbtle_subscriber (optional)

        - pip install .

####Usage

**If you didn't install the module with the above 'pip install' line then you
will have to make the script executable or run it with python directly such
as:**

    - python svbtle_subscriber.py


1. svbtle_subscriber.py

    This will output the list of writers, their homepage, and feed url (comma
    separated, one per line) so you can pipe it to any script that you want for
    processing.

2. svbtle_subscriber.py -x [google_reader_subscriptions.xml]

    This will show you who you aren't following yet from all the current
    bloggers on [svbtle.com](http://svbtle.com).

    You can get an xml file for your subscriptions in
    [Google Reader](http://reader.google.com) by going
    [here](http://www.google.com/reader/api/0/subscription/list) as saving it
    as file from your browsers 'save as' option.

3. svbtle_subscriber.py --web

    Browse to 127.0.0.1:5000

#####Deploy

I have this application deployed to to [heroku](http://heroku.com).  You'll
need the free
[postgres add-on](https://devcenter.heroku.com/articles/heroku-postgres-addon)
and optionally the free
[scheduler](https://devcenter.heroku.com/articles/scheduler) if you want to
keep your database updated with new authors automatically.

To deploy to [heroku](http://heroku.com):

- heroku create --stack cedar
- heroku addons:add shared-database
- heroku addons:add scheduler:standard
- git push heroku master


#####Future

- Error handling (too big of file, not xml file, unparseable, etc.)
- Add subscribe link to missing
- Add debug mode for running web locally with sqlite or no db at all.
- Remove file upload and just let user login and hit the url
