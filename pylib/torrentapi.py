# @author : Yashovardhan Sharma
# @github : github.com/baddymaster

#   <Torrent Hound - Search torrents from multiple websites via the CLI.>
#    Copyright (C) <2017>  <Yashovardhan Sharma>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as published
#     by the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import json
import random
import re
import sys
import time
import traceback
import webbrowser
from datetime import datetime, timedelta

import humanize
import pyperclip
import requests
from bs4 import BeautifulSoup
from clint.textui import colored
from veryprettytable import VeryPrettyTable

log = logging.Logger(__name__)

defaultQuery, query = 'jason bourne', ''
results_sky = None
results_tpb_api, num_results_tpb_api = None, 0
results, results_rarbg, exit, error_detected_rarbg, error_detected_tpb = None, None, None, None, None
num_results, num_results_rarbg, num_results_sky, print_version = 0, 0, 0, 1
auth_token = 'None'
app_id = 'None'
tpb_working_domain = 'thepiratebay.org'
rarbg_url, skytorrents_url, tpb_url = '', '', ''
tpb_retries, max_tpb_retries = 0, 3

def enum(**enums):
    """
    Lets define enums
    """
    return type('Enum', (), enums)

ORDER_BY = enum(NAME = 1,
                SIZE = 3,
                UPLOADER = 5,
                SEEDERS = 7,
                LEECHERS = 9,
                TYPE = 13,
                UPLOADED = 99)

SORT_BY_TBP = enum(NAME = 'title_asc',
                   NAME_DESC = 'title_desc',
                   SEEDS = 'seeds_asc',
                   SEEDS_DESC = 'seeds_desc',
                   LEECHERS = 'leeches_asc',
                   LEECHERS_DESC = 'leeches_desc',
                   MOST_RECENT = 'time_desc',
                   OLDEST = 'time_asc',
                   UPLOADER = 'uploader_asc',
                   UPLOADER_DESC = 'uploader_desc',
                   SIZE = 'size_asc',
                   SIZE_DESC = 'size_desc',
                   FILE_TYPE = 'category_asc',
                   FILE_TYPE_DESC = 'category_desc')

ORDER_BY_SKY = enum(RELEVANCE = 'ss',
                    SEEDS_DESC = 'ed',
                    SEEDS_ASC = 'ea',
                    PEERS_DESC = 'pd',
                    PEERS_ASC = 'pa',
                    SIZE_DESC = 'sd',
                    SIZE_ASC = 'sa',
                    NEWEST = 'ad',
                    OLDEST = 'aa')


def generate_app_id(version=-1):
    if version == 0: # Product of 3 random numbers
        x, y, z = random.randint(1, 100), random.randint(1, 100), random.randint(1, 100)
        app_id = x * y * z
    else : # Hash current epoch time
        epoch_time = time.time()
        app_id = hash(epoch_time)
    return app_id


def generate_api_token(app_id):
    log.debug('torrentapi: app_id set to %s' % app_id)
    headers = {'User-Agent': 'Mozilla/5.0'}    
    url = 'https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id={}'.format(app_id)

    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            auth_token = json.loads(r.text, encoding='utf-8')['token']
            log.debug('torrentapi: auth_token set to %s' % app_id)
            return auth_token
        else:
            log.debug('torrentapi: failed to generate token')
            log.debug('torrentapi: url string was %s' % url)
    except requests.exceptions.ConnectionError as e:
        log.debug(e)


def removeAndReplaceSpaces(string):
    if string[0] == " ":
        string = string[1:]
    return string.replace(" ", "+")

def searchPirateBay(search_string = defaultQuery, page = 0, order_by = ORDER_BY.UPLOADER, domain = 'thepiratebay.org'):
    """
    Searches for the given string in The Pirate Bay.
    Returns a list of dictionaries with the information of each torrent.
    """
    global tpb_working_domain
    baseURL = 'https://' + domain + '/s/?q='
    url = baseURL + search_string + '&page=0&orderby=99'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, "html.parser")
        table = soup.find("table", {"id": "searchResult"})
        # print "TBP Response : \n"
        # print r.content
    except requests.exceptions.ConnectionError as e:
        #print e
        err_string = str(e).split(',')[2]
        #print err_string
        if 'Operation timed out' in err_string:
            if domain == 'thepiratebay.org':
                tpb_working_domain = alternate_domain ='piratebay.red'
                error_str = colored.yellow("[PirateBay] Error : Connection to ") + colored.magenta(domain) + colored.yellow(" timed out.\n")
                error_str += colored.yellow("Trying to connect via ") + colored.magenta(alternate_domain) + colored.yellow("...")
                print(error_str)
                return searchPirateBay(search_string=search_string, domain='piratebay.red')
            elif domain == 'piratebay.red':
                error_str = colored.yellow("[PirateBay] Error : Connection to ") + colored.magenta(domain) + colored.yellow(" timed out.\n")
                error_str += colored.red("Exiting. Try connecting via a proxy...")
                print(error_str)
                table = None
                #sys.exit(1)
        elif 'Connection refused' in err_string:
            if domain == 'thepiratebay.org':
                tpb_working_domain = alternate_domain = 'piratebay.red'
                error_str = colored.red("[PirateBay] Error : Connection to ") + (domain) + colored.red(" refused.\n")
                error_str += colored.red("Trying to connect via ") + (alternate_domain) + colored.red("...")
                print(error_str)
                return searchPirateBay(search_string=search_string, domain='piratebay.red')
            elif domain == 'piratebay.red':
                error_str = colored.red("[PirateBay] Error : Connection to ") + (domain) + colored.red(" refused.\n")
                error_str += colored.red("Exiting. Try connecting via a proxy...")
                print(error_str)
                table = None
                #sys.exit(1)
        elif 'failed to respond' in err_string:
            if domain == 'thepiratebay.org':
                tpb_working_domain = alternate_domain = 'piratebay.red'
                error_str = colored.red("[PirateBay] Error : Connection to ") + (domain) + colored.red(" is probably blocked.\n")
                error_str += colored.red("Trying to connect via ") + (alternate_domain) + colored.red("...")
                print(error_str)
                return searchPirateBay(search_string=search_string, domain='piratebay.red')
            elif domain == 'piratebay.red':
                error_str = colored.red("[PirateBay] Error : Connection to ") + (domain) + colored.red(" refused.\n")
                error_str += colored.red("Exiting. Try connecting via a proxy...")
                print(error_str)
                table = None
                #sys.exit(1)
        else:
            error_str = colored.red("[PirateBay] Unhandled Error : ") + colored.red(str(e)) + colored.red("\nExiting...")
            print(error_str)
            table = None
            #sys.exit(1)
    except TypeError as e:
        #print("Something's wrong...")
        table = None

    # print table
    if table == None:
        if domain == 'piratebay.red':
            error_string = str(colored.yellow('[PirateBay] Error : No results found. ')) + str(colored.magenta(domain)) + str(colored.yellow(' might be unreachable!'))
            print(error_string)
            return _parse_search_result_table(table)
        else:
            tpb_working_domain = alternate_domain = 'piratebay.red'
            # print "!!!!"
            error_string = str(colored.yellow('[PirateBay] Error  : No results found. ')) + str(colored.magenta(domain)) + str(colored.yellow(' might be unreachable!'))
            error_string += str(colored.yellow('\nTrying ')) + str(colored.magenta(alternate_domain)) + str(colored.yellow('...'))
            print (error_string)
            return searchPirateBay(search_string=search_string, domain='piratebay.red')
    else:
        return _parse_search_result_table(table)

def _parse_search_result_table(table):
    if table == None:
        results = []
        return results
    trs = table.findAll("tr")
    del trs[:1]
    # print "\n'tr' tags within table : \n"
    # print trs
    results = []
    error_detected_tpb = False
    for tr in trs:
        if(error_detected_tpb == False):
            results.append(_parse_search_result_table_row(tr))
        else:
            error_string = '[PirateBay] Error  : No results found'
            print(colored.yellow(error_string))
            break
    return results

def _parse_search_result_table_row(tr):
    global error_detected_tpb
    res = {}
    tds = tr.findAll("td")
    # print tds
    link_name = tds[1].find("a", {"class": "detLink"})
    # print "Link Name : " + str(link_name.contents)
    if link_name.contents == []:
        error_detected_tpb = True
        return {}
    else:
        res['name'] = link_name.contents[0].encode('utf-8').strip()
        res['link'] = link_name["href"].encode('utf-8')
        desc_string = tds[1].find("font").contents[0].encode('utf-8').replace(b"&nbsp;", b" ")
        m = re.search(r"^Uploaded (Today|Y-day|\d\d-\d\d)\xc2\xa0(\d{4}|\d\d:\d\d), " + r"Size (\d+(?:.\d*)?\xc2\xa0(?:[KMG]iB))", desc_string.decode('utf-8'))
        try :
            temp_size = str(m.group(3)).replace('\xc2\xa0', ' ')
            s1 = temp_size.split('.')
            try:
                s2 = s1[1].split(' ')
            except IndexError as e: # Special case where size is an integer (eg. s1 = 2 GiB), i.e, no decimal place
                s1 = s1.split(' ')
                s2 = ['0']
                s2.append(s1[1])
                temp_size = s1[0] + '.0 ' + s1[1]
            if(len(s1[0]) == 4):
                res['size'] = s1[0] + s2[1]
            elif(len(s1[0]) == 3):
                res['size'] = s1[0] + '.' + s2[0][0] + " " + s2[1]
            else:
                res['size'] = temp_size
        except AttributeError as e:
            error_detected_tpb = True
            #print e
            #print "\nRegex misbehaving. Try running the script again!\n"
            return {}
        now = datetime.today()
        if re.match(r"\d{4}", m.group(2)) == None:
            hour =" " + m.group(2)
            if m.group(1) == "Today":
                res['time'] = datetime.strptime(
                        now.strftime("%m-%d-%Y") + hour,
                        "%m-%d-%Y %H:%M")
            elif m.group(1) == "Y-day":
                res['time'] = datetime.strptime(
                        (now + timedelta(-1)).strftime("%m-%d-%Y") + hour,
                         "%m-%d-%Y %H:%M")
            else:
                res['time'] = datetime.strptime(
                        m.group(1) + "-" + str(now.year) + hour,
                        "%m-%d-%Y %H:%M")
        else:
            res['time'] = datetime.strptime(m.group(1) + "-" + m.group(2),
                    "%m-%d-%Y")
        res['seeders'] = int(tds[2].contents[0])
        res['leechers'] = int(tds[3].contents[0])
        try:
            res['ratio'] = format( (float(res['seeders'])/float(res['leechers'])), '.1f' )
        except ZeroDivisionError:
            res['ratio'] = float('inf')
        res['magnet'] = tds[1].find("img", {"alt": "Magnet link"}).parent['href']
        return res


def searchPirateBayWithAPI(search_string = defaultQuery, sort_by = SORT_BY_TBP.SEEDS_DESC, domain = 'tpbc.herokuapp.com'):
    global results_tpb_api, tpb_url
    base_url = 'https://' + domain
    url = base_url + '/search/' + removeAndReplaceSpaces(search_string) + '/?sort=' + sort_by
    tpb_url = url

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response_json = json.loads(response.text)
        results_tpb_api = parse_results_tpb_api(response_json)
    except Exception as e:
        print(colored.red("[PirateBay] : Error while searching"))
        print(colored.yellow('ERR_MSG : ' + str(e)))
        #traceback.print_exc()
    
    # try:
    #     results_tpb_api = parse_results_tpb_api(response_json)
    # except Exception, e:
    #     print colored.red("[PirateBay] : Error while parsing search results.")
    #     print colored.yellow('ERR_MSG : ' + str(e))
    
    return results_tpb_api


def parse_results_tpb_api(response_json):
    #global results_tpb_api
    results_list = []
    if response_json == []:
        error_string = '[PirateBay] Error : No results found'
        print(colored.magenta(error_string))
        return []
    else:
        for post in response_json:
            res = {}
            res['name'] = post['title'].encode('utf-8')
            res['link'] = ''

            temp_size = humanize.naturalsize(post['size'], binary=True, format='%.2f')
            s1 = temp_size.split('.')
            if(len(s1[0]) == 4):
                res['size'] = humanize.naturalsize(post['size'], binary=True, format='%.0f')
            else:
                res['size'] = temp_size
            #res['time'] = Implement later
            res['seeders'] = post['seeds']
            res['leechers'] = post['leeches']
            try:
                res['ratio'] = format( (float(res['seeders'])/float(res['leechers'])), '.1f' )
            except ZeroDivisionError:
                res['ratio'] = float('inf')
            res['magnet'] = post['magnet'].encode('utf-8')
            results_list.append(res)
    
    return results_list


def search_rarbg(query=defaultQuery):
    global error_detected_rarbg
    # API Documentaion : https://torrentapi.org/apidocs_v2.txt
    # https://torrentapi.org/pubapi_v2.php?mode=search&search_string=Suits%20S06E10&format=json_extended&ranked=0&token=7dib9orxpa&app_id=0
    app_id = generate_app_id(2)
    auth_token = generate_api_token(app_id)

    if not auth_token:
        log.debug('Search Failed, no auth_token')
        return

    query = query.replace(" ", "%20")
    base_url = 'https://torrentapi.org/pubapi_v2.php?'
    search_criteria = 'mode=search&search_string={}&'.format(query)
    options = 'format=json_extended&ranked=0&token={}&app_id={}'.format(auth_token, app_id)
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = '{}{}{}'.format(base_url, search_criteria, options)
    
    try:
        response = requests.get(url, headers=headers)
        rt = response.text
        response_json = json.loads(rt)
    except ValueError as e:
        print(colored.red('[RARBG] Error : ' + str(e)))
        if response.status_code == '429': # Too Many Requests
            print(colored.yellow('<HTTP 429> : Too Many Requests. Please try again after a while!'))
        return []

    error_detected_rarbg = checkResponseForErrors(response_json)
    if(error_detected_rarbg == False):
        results_rarbg = parse_results_rarbg(response_json)
    return results_rarbg


def parse_results_rarbg(response_json):
    results = []
    if error_detected_rarbg == False:
        for post in response_json['torrent_results']:
            res = {}
            res['name'] = post['title']
            res['link'] = post['info_page']

            temp_size = humanize.naturalsize(post['size'], binary=True, format='%.2f')
            s1 = temp_size.split('.')
            if(len(s1[0]) == 4):
                res['size'] = humanize.naturalsize(post['size'], binary=True, format='%.0f')
            elif(len(s1[1]) == 3):
                res['size'] = humanize.naturalsize(post['size'], binary=True, format='%.1f')
            else:
                res['size'] = temp_size
            #res['time'] = Implement later
            res['seeders'] = post['seeders']
            res['leechers'] = post['leechers']
            try:
                res['ratio'] = format( (float(res['seeders'])/float(res['leechers'])), '.1f' )
            except ZeroDivisionError:
                res['ratio'] = float('inf')
            res['magnet'] = post['download']
            results.append(res)
    else:
        log.error('No Results Found!')
        return []
    return results


def checkResponseForErrors(response_json):
    global results_rarbg, error_detected_rarbg, query, auth_token
    search_string = query.replace(" ", "%20")

    if 'error_code' in response_json:
        #print 'In function'
        error_string = '[RARBG] Error : ' + response_json['error']
        print(colored.magenta(error_string))
        
        if response_json['error_code'] == 4:
            generateNewTorrentAPIToken(error=True)
            results_rarbg = searchRarbg(search_string)
        # elif response_json['error_code'] == 20:
        #     print "No results found. Try different keywords!\n"
        return True #Some error detected
    else:
        return False #No errors. Print results
