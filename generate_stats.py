#!/usr/bin/python2

import ConfigParser
import os
from datetime import date
from datetime import timedelta
from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from kitchen.text.converters import to_bytes

DATADIR = 'data'
OUTPUTDIR = 'output'
TEMPLATEDIR = 'templates'

if not os.path.exists(OUTPUTDIR):
    os.mkdir(OUTPUTDIR)


def get_data(section):
    """ From a given data section of a file, return a dict with as key
    the week number and as value a list of everything else on the line
    that is comma separated.
    """
    output = {}
    for row in section.split('\n'):
        if not row:
            continue
        row = row.split(',')
        output[int(row[0].strip())] = [cel.strip() for cel in row[1:]]
    return output


def main():
    """ Generate the HTML pages used to display statistics about the
    project.
    """
    
    for filename in os.listdir(DATADIR):
        filepath = os.path.join(DATADIR, filename)
        if os.path.isfile(filepath) and filename.startswith('release_'):
            generate_release_stats(filepath)
            


def generate_release_stats(data_file):
    """ Generate statistics for each release for which we have data.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(data_file))
    
    # Handle the yum data
    data = get_data(config.get('yum_data', 'data'))
    keys = data.keys()
    keys.sort()
    yum_data = [int(data[key][0]) for key in keys]

    data = get_data(config.get('direct_download', 'data'))
    keys = data.keys()
    keys.sort()
    dd_data = [int(data[key][0]) for key in keys]

    release = config.get('info', 'release_number')
    release_date = config.get('info', 'release_date').split('-')
    release_date = date(int(release_date[0]), int(release_date[1]),
        int(release_date[2]))

    try:
        env = Environment()
        env.filters['filter_format_date_for_js'] = filter_format_date_for_js
        env.filters['filter_format_week_date'] = filter_format_week_date
        env.loader = FileSystemLoader(TEMPLATEDIR)
        mytemplate = env.get_template('release.html')
        # Fill the template
        html = mytemplate.render(
            release=release,
            release_name=config.get('info', 'release_name'),
            release_date=release_date,
            yum_data=yum_data,
            dd_data=dd_data,
            keys=keys,
        )
        # Write down the page
        stream = open('output/release_%s.html' % release, 'w')
        stream.write(to_bytes(html))
        stream.close()
    except IOError, err:
        print 'ERROR: %s' % err


def filter_format_date_for_js(value, format='%Y, %m, %d'):
    """ Filter used to format correctly the date for the json. """
    return value.strftime(format)


def filter_format_week_date(value, cnt, format='%Y-%m-%d'):
    """ Filter used to format correctly the date for the table of data.
    """
    date0 = (value + timedelta(days=7 * (cnt - 1)))
    date1 = (date0 + timedelta(days=6))
    return '%s -- %s' % (date0.strftime(format), date1.strftime(format))



if __name__ == '__main__':
    main()

