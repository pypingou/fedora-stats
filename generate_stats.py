#!/usr/bin/python2

import ConfigParser
from datetime import date
from datetime import timedelta
import locale
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
    (reporelease, datatmp) = get_data(config.get('repository', 'data'))
    cnt = 0
    repodata = []
    for value in datatmp:
        repodata.append({'x': cnt, 'y': int(value[0])})
        cnt = cnt + 1
    total_ip = int(config.get('unique_ip', 'total_ip'))

    # Handle the fedoraproject data
    (fpdates, datatmp) = get_data(config.get('fedoraproject', 'data'))
    cnt = 0
    fpdata = []
    for value in datatmp:
        fpdata.append({'x': cnt, 'y': int(value[0])})
        cnt = cnt + 1

    # Handle the fedoraproject wiki data
    (wikidates, datatmp) = get_data(config.get('fedorawiki', 'data'))
    cnt = 0
    wiki_data_edit = []
    wiki_data_unique_edit = []
    for value in datatmp:
        wiki_data_edit.append({'x': wikidates[cnt], 'y': int(value[0])})
        wiki_data_unique_edit.append({'x': wikidates[cnt], 'y': int(value[1])})
        cnt = cnt + 1

    try:
        env = Environment()
        env.loader = FileSystemLoader(TEMPLATEDIR)
        env.filters['filter_format_number'] = filter_format_number
        mytemplate = env.get_template('index.html')
        # Fill the template
        html = mytemplate.render(
            reporelease=reporelease,
            repodata=repodata,
            total_ip=total_ip,
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


def generate_release_stats(data_file, write_output=True):
    """ Generate statistics for each release for which we have data.
    """
    config = ConfigParser.ConfigParser()
    config.readfp(open(data_file))
    
    # Handle the yum data
    (keys, datatmp) = get_data(config.get('yum_data', 'data'))
    cnt = 1
    yum_data = [{'x': 0, 'y': 0}]
    for value in datatmp:
        yum_data.append({'x': cnt, 'y': int(value[0])})
        cnt = cnt + 1
    yum_remarks = ""
    try:
        yum_remarks = config.get('yum_data', 'remarks')
    except ConfigParser.NoOptionError:
        pass

    dd_data = []
    try:
        datatmp = []
        (ddkeys, datatmp) = get_data(config.get('direct_download', 'data'))
        cnt = 1
        dd_data = [{'x': 0, 'y': 0}]
        for value in datatmp:
            dd_data.append({'x': cnt, 'y': int(value[0])})
            cnt = cnt + 1
    except ConfigParser.NoSectionError:
        pass

    dd_remarks=""
    try:
        dd_remarks = config.get('direct_download', 'remarks')
    except ConfigParser.Error:
        pass

    release = int(config.get('info', 'release_number'))
    release_date = config.get('info', 'release_date')

    xlabels = [get_end_week_date(release_date, cnt)
        for cnt in range(0, len(keys))]
    xlabels.insert(0, release_date)

    # Get data from previous version
    prev_yum_data = None
    prev_dd_data = None
    prev_xlabels = 'null'
    prev_release = release - 1
    prev_datafile = os.path.join(DATADIR, 'release_%s.csv' % prev_release)
    if os.path.exists(prev_datafile):
        prev_yum_data, prev_dd_data, prev_xlabels = generate_release_stats(
            prev_datafile, False)
        prev_yum_data = fix_list_length(yum_data, prev_yum_data)
        prev_dd_data = fix_list_length(dd_data, prev_dd_data)
        prev_xlabels = fix_list_length(xlabels, prev_xlabels)

    if write_output:
        try:
            env = Environment()
            env.filters['filter_format_week_date'] = filter_format_week_date
            env.filters['filter_format_number'] = filter_format_number
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
                xlabels=xlabels,
                prev_yum_data=prev_yum_data,
                prev_dd_data=prev_dd_data,
                prev_xlabels=prev_xlabels,
            )
            # Write down the page
            stream = open('output/release_%s.html' % release, 'w')
            stream.write(to_bytes(html))
            stream.close()
        except IOError, err:
            print 'ERROR: %s' % err

    return (yum_data, dd_data, xlabels)


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
        release = keys[cnt]
        if int(release) < 10:
            release = '0%s' % release
        if not os.path.exists(os.path.join(DATADIR, 'release_%s.csv' %
            release)):
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


def fix_list_length(maindata, prevdata):
    """ Make sure that the two given list are of the same length, either
    by adding null data or by removing data to the prevdata list.
    Return the prevdata adjusted to the right length.
    """
    if len(prevdata) > len(maindata):
        prevdata = prevdata[:len(maindata)]
    else:
        while len(prevdata) < len(maindata):
            prevdata.append({'x': len(prevdata) - 1, 'y': 'null'})
    return prevdata


def get_end_week_date(start_date, n_week):
    """ Filter used to format correctly the date for the json. """
    start_date = start_date.split('-')
    start_date = date(int(start_date[0]), int(start_date[1]),
        int(start_date[2]))
    start_week = start_date + timedelta(days=7 * n_week)
    end_week = start_week + timedelta(days=6)
    return end_week.strftime('%Y-%m-%d')


def filter_format_week_date(value, cnt, format='%Y-%m-%d'):
    """ Filter used to format correctly the date for the table of data.
    """
    value = value.split('-')
    value = date(int(value[0]), int(value[1]), int(value[2]))
    date0 = (value + timedelta(days=7 * (cnt - 1)))
    date1 = (date0 + timedelta(days=6))
    return '%s -- %s' % (date0.strftime(format), date1.strftime(format))


def filter_format_number(value):
    """ Format number nicely to help readibility.
    """
    locale.setlocale(locale.LC_ALL, 'en_US')
    return locale.format("%d", value, grouping=True)

if __name__ == '__main__':
    main()

