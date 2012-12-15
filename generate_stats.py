#!/usr/bin/python2

import ConfigParser
from datetime import date
from datetime import timedelta
import os
import shutil
from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2.environment import Environment
from kitchen.text.converters import to_bytes

DATADIR = 'data'
OUTPUTDIR = 'output'
TEMPLATEDIR = 'templates'

if os.path.exists(OUTPUTDIR):
    shutil.rmtree(OUTPUTDIR)
if not os.path.exists(OUTPUTDIR):
    os.mkdir(OUTPUTDIR)


def get_data(section):
    """ Return the keys and values in two different, ordered, list for
    a given section.
    The values are a list of list
    """
    keys = []
    values = []
    for row in section.split('\n'):
        if not row:
            continue
        row = row.split(',')
        keys.append(row[0].strip())
        values.append([item.strip() for item in row[1:]])
    return (keys, values)

def main():
    """ Generate the HTML pages used to display statistics about the
    project.
    """
    generate_index_page()
    for filename in os.listdir(DATADIR):
        filepath = os.path.join(DATADIR, filename)
        if os.path.isfile(filepath) and filename.startswith('release_'):
            generate_release_stats(filepath)
    generate_release_index()
    generate_about_page()
    # Copy the static element into the output folder
    shutil.copytree('static', os.path.join(OUTPUTDIR, 'static'))


def generate_about_page():
    """ Generate the about page from the template. """
    try:
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATEDIR)
        mytemplate = env.get_template('about.html')
        # Fill the template
        html = mytemplate.render()
        # Write down the page
        stream = open('output/about.html', 'w')
        stream.write(to_bytes(html))
        stream.close()
    except IOError, err:
        print 'ERROR: %s' % err


def generate_index_page():
    """ Generate the front page of the project.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(DATADIR, 'monthly_data.csv')))

    # Handle data about the total repository connection
    (reporelease, repodata) = get_data(config.get('repository', 'data'))
    repodata = [int(value[0]) for value in repodata]

    # Handle the fedoraproject data
    (fpdates, fpdata) = get_data(config.get('fedoraproject', 'data'))
    fpdata = [int(value[0]) for value in fpdata]

    # Handle the fedoraproject wiki data
    (wikidates, wikidata) = get_data(config.get('fedorawiki', 'data'))
    wiki_data_edit = [int(value[0]) for value in wikidata]
    wiki_data_unique_edit = [int(value[1]) for value in wikidata]

    try:
        env = Environment()
        env.filters['filter_format_date_for_js'] = filter_format_date_for_js
        env.filters['filter_format_week_date'] = filter_format_week_date
        env.loader = FileSystemLoader(TEMPLATEDIR)
        mytemplate = env.get_template('index.html')
        # Fill the template
        html = mytemplate.render(
            reporelease=reporelease,
            repodata=repodata,
            fpdates=fpdates,
            fp_data=fpdata,
            wikidates=wikidates,
            wiki_data_edit=wiki_data_edit,
            wiki_data_unique_edit=wiki_data_unique_edit,
        )
        # Write down the page
        stream = open('output/index.html', 'w')
        stream.write(to_bytes(html))
        stream.close()
    except IOError, err:
        print 'ERROR: %s' % err


def generate_release_stats(data_file):
    """ Generate statistics for each release for which we have data.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(data_file))
    
    # Handle the yum data
    (keys, yum_data) = get_data(config.get('yum_data', 'data'))
    yum_data = [int(value[0]) for value in yum_data]
    yum_remarks = ""
    try:
        yum_remarks = config.get('yum_data', 'remarks')
    except ConfigParser.NoOptionError:
        pass

    (ddkeys, dd_data) = get_data(config.get('direct_download', 'data'))
    dd_data = [int(value[0]) for value in dd_data]
    dd_remarks=""
    try:
        dd_remarks = config.get('direct_download', 'remarks')
    except ConfigParser.NoOptionError:
        pass

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
            yum_remarks=yum_remarks,
            dd_data=dd_data,
            dd_remarks=dd_remarks,
            keys=keys,
        )
        # Write down the page
        stream = open('output/release_%s.html' % release, 'w')
        stream.write(to_bytes(html))
        stream.close()
    except IOError, err:
        print 'ERROR: %s' % err


def generate_release_index():
    """ Generates the index pages pointing to each release for which we
    have stats.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(os.path.join(DATADIR, 'index_release.csv')))
    
    releases = {}
    for option in config.options('logos'):
        tmp = { 'release' : option,
                'banner' : config.get('logos', option)
            }
        releases[int(option)] = tmp

    keys = releases.keys()
    keys.sort()
    keys.reverse()
    cnt = 0
    while cnt < len(keys):
        if not os.path.exists(os.path.join(DATADIR, 'release_%s.csv' %
            keys[cnt])):
            keys.remove(keys[cnt])
            cnt = cnt - 1
        cnt = cnt + 1
    try:
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATEDIR)
        mytemplate = env.get_template('index_release.html')
        # Fill the template
        html = mytemplate.render(
            keys=keys,
            releases=releases,
        )
        # Write down the page
        stream = open('output/index_release.html', 'w')
        stream.write(to_bytes(html))
        stream.close()
    except IOError, err:
        print 'ERROR: %s' % err


def filter_format_date_for_js(value, format='%Y, %m, %d'):
    """ Filter used to format correctly the date for the json. """
    value = value + timedelta(days=6)
    return '%s, %s, %s' % (value.year, value.month - 1, value.day)


def filter_format_week_date(value, cnt, format='%Y-%m-%d'):
    """ Filter used to format correctly the date for the table of data.
    """
    date0 = (value + timedelta(days=7 * (cnt - 1)))
    date1 = (date0 + timedelta(days=6))
    return '%s -- %s' % (date0.strftime(format), date1.strftime(format))



if __name__ == '__main__':
    main()

