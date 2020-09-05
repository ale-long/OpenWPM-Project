import sqlite3
import pandas as pd
import matplotlib.pyplot as plt 
import tldextract
from collections import Counter

site_data = pd.read_csv('/home/alex/Desktop/top-1m.csv')
sites = site_data.iloc[:100,1]
VANILLA_DB = '/home/alex/Desktop/OpenWPM-master/database/vanilla/crawl-data.sqlite'
ADBLOCK_DB = '/home/alex/Desktop/OpenWPM-master/database/ad-block/crawl-data.sqlite'
query_cookie_request = 'SELECT host, visit_id FROM javascript_cookies'

def fetch_data(query_type,db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(query_cookie_request)
    row_results = c.fetchall()
    c.close()
    conn.close()
    return row_results

def check_third_party(top_level_url, url):
    top_level_url_ext = tldextract.extract(top_level_url)
    url_ext = tldextract.extract(url)
    # Not a third party if extracted parts are equal to each other
    if top_level_url_ext == url_ext:
        return False
    return True

def append_third_parties(website_arr, third_party_arr, row_results):
    for result in row_results:
        host = result[0]
        visit_id = result[1] - 1
        # ignore first number if visit_id is greater than 100 
        if(visit_id >= 100):
            visit_id_string = str(visit_id)
            if(visit_id_string[1] == '0'):
                visit_id = int(visit_id_string[2])
            else:
                visit_id = int(visit_id_string[1:])
        
        if check_third_party(host, sites[visit_id]):
            website_arr.append(sites[visit_id])
            ext = tldextract.extract(host)
            third_party_domain = '.'.join(ext[1:])
            third_party_arr.append(third_party_domain)

if __name__ == "__main__":

    vanilla_websites = []
    vanilla_third_parties = []
    ad_blocked_websites = []
    ad_blocked_third_parties = []

    # get data from SQL database
    vanilla_data_rows = fetch_data(query_cookie_request, VANILLA_DB)
    ad_block_data_rows = fetch_data(query_cookie_request, ADBLOCK_DB)

    # append third parties/websites for vanilla mode and ad-block mode
    append_third_parties(vanilla_websites, vanilla_third_parties, vanilla_data_rows) 
    append_third_parties(ad_blocked_websites, ad_blocked_third_parties, ad_block_data_rows) 

    # find top-10 most popular third party domains for both vanilla and ad-block mode
    vanilla_top_10 = Counter(vanilla_third_parties).most_common(10)
    ad_block_top_10 = Counter(ad_blocked_third_parties).most_common(10)

    print('Top 10 Third Parties(Vanilla Mode)\n')
    for i in range(len(vanilla_top_10)):
        print(vanilla_top_10[i])


    print('Top 10 Third Parties(Ad-block Mode)\n')
    for i in range(len(ad_block_top_10)):
        print(ad_block_top_10[i])

    # plot data points and show graph

    vanilla_count = list(Counter(vanilla_websites).values())
    ad_block_count = list(Counter(ad_blocked_websites).values())

    # Vanilla Mode
    plt.title("Third-Party Cookies(Vanilla/Ad-Block)")
    plt.xlabel("Top 100 Websites")
    plt.ylabel("# of Third-Party Cookies")
    plt.plot(vanilla_count, label="Vanilla")
    # Ad-block Mode
    plt.plot(ad_block_count, label="Ad-Block")
    plt.legend()
    plt.show()