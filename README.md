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

##Usage

1. python svbtle_subscriber.py

    This will output the list of writers, their homepage, and feed url (comma
    separated, one per line) so you can pipe it to any script that you want for
    processing.

2. python svbtle_subscriber.py -x [google_reader_subscriptions.xml]

    This will show you who you aren't following yet from all the current
    bloggers on [svbtle.com](http://svbtle.com).

You can get an xml file for your subscriptions in [Google
Reader](http://reader.google.com) by going
[here](http://www.google.com/reader/api/0/subscription/list) as saving it as
file from your browsers 'save as' option.

###Install

    git clone git://github.com/durden/svbtle_subscriber.git
    pip install -r requirements.txt
    (optional) pip install .

####Future

- Web front-end
