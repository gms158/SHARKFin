import azure.storage.fileshare as fs
import asyncio
import re
import os
import json
import pandas as pd
import whitesharkprocesshelper as wph

# add this
conn_str = '###########'

# TODO : mak a directory based on the below
results_dir = 'whiteshark_results1'

# TODO : update pattern for run
pattern_run = 'whiteshark-babyrun'

def download(fname, dirname=results_dir, share_name='sharkfin-ammps-fs'):
        file_client = fs.ShareFileClient.from_connection_string(
                conn_str=conn_str,
                share_name=share_name,
                file_path=fname)

        if not os.path.isdir(dirname):
                os.mkdir(dirname)

        with open(f'{dirname}/{fname}', 'wb+') as file_handle:
                data = file_client.download_file()
                data.readinto(file_handle)

def list_files(share_name='sharkfin-ammps-fs'):
        connstr = "az storage file list --share-name sharkfin-ammps-fs --connection-string '" + conn_str + "'"
        print(connstr)
        file_list_json = os.popen(connstr).read()
        file_info = json.loads(file_list_json)
        names = [item['name'] for item in file_info]

        return names

if __name__ == '__main__':

        regex = pattern_run + '\d+-tag_sim_stats.txt'
        pattern = re.compile(regex)
        regex_1 = pattern_run + '\d+-tag_class_stats.csv'
        pattern_1 = re.compile(regex_1)

        fl = list_files()

        for fname in fl:
                if pattern.search(fname) or pattern_1.search(fname):
                        print(f'downloading {fname}')
                        download(fname)

        wph.create_headers()
        for fname in os.listdir(results_dir):
                try:
                        if '-tag_class_stats.csv' in fname:
                                prefix = fname.index('-tag_class_stats.csv')
                                sim_stats = fname[:prefix] + "-tag_sim_stats.txt"
                                wph.process_run(results_dir + '/' + sim_stats,results_dir + '/' + fname)
                except Exception as e:
                        print("error", e)
