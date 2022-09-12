import json
import pandas as pd
import os

records_row = 0
allclean_row = 0

all_clean = "all_clean.txt"
all_records = "all_records.txt"

def create_headers():
    global all_clean
    global all_records

    if os.path.exists(all_clean):
        os.remove(all_clean)
    if os.path.exists(all_records):
        os.remove(all_records)

    all_clean_headers = ",max_buy_limt,max_sell_limit,idx_max_buy_limit,inx_max_sell_limit,mean_buy_limit,mean_sell_limit,std_buy_limit,std_sell_limit,kurtosis_buy_limit,kurtosis_sell_limit,skew_buy_limit,skew_sell_limit,min_asset_price"
    all_records_headers = ",row,attention,p1,p2,dividend_growth_rate,ror_volatility,dollars_per_hark_money_unit,aLv1_mean,CRRA,DiscFac,alvl_std,mNrm_ratio_StE_mean,mNrm_ratio_StE_std"

    append_str_to_file(all_clean, all_clean_headers)
    append_str_to_file(all_records, all_records_headers)

def append_str_to_file(f, s):
    file_append = open(f, "a")
    file_append.write(s + "\n")
    file_append.close()

def process_run(sim_stats_file, class_stats_file):

    global records_row
    global allclean_row

    # read sim stats file
    with open(sim_stats_file, 'r') as file:
        data = file.read()

        # auto magic operations to turn this into a json object
        idx = data.index('max_buy_limit') - 1
        json_data = "{" + data[idx:]
        json_data = json_data.replace(">", "")
        json_data = json_data.replace("<class", "")
        json_data = json_data.replace("'", "\"")
        json_data = json_data.replace("None", "0")
        json_obj = json.loads(json_data)

    allclean_row += 1

    # add row to clean data file
    all_clean_str = str(allclean_row) + "," + str(json_obj['max_buy_limit']) + "," + str(json_obj['max_sell_limit']) + \
        "," + str(json_obj['idx_max_buy_limit']) + "," + str(json_obj['idx_max_sell_limit']) + \
        "," + str(json_obj['mean_buy_limit']) + "," + str(json_obj['mean_sell_limit']) + \
        "," + str(json_obj['std_buy_limit']) + "," + str(json_obj['std_sell_limit']) + \
        "," + str(json_obj['kurtosis_buy_limit']) + "," + str(json_obj['kurtosis_sell_limit']) + \
        "," + str(json_obj['skew_buy_limit']) + "," + str(json_obj['skew_sell_limit']) + \
        "," + str(json_obj['min_asset_price']) + "," + str(json_obj['max_asset_price']) + \
        "," + str(json_obj['idx_min_asset_price']) + "," + str(json_obj['idx_max_asset_price']) + \
        "," + str(json_obj['std_asset_price']) + "," + str(json_obj['q']) + \
        "," + str(json_obj['r']) + "," + "[]" + \
        "," + str(json_obj['attention']) + "," + str(json_obj['ror_volatility']) + \
        "," + str(json_obj['ror_mean']) + "," + str(json_obj['total_population_aLvl_mean']) + \
        "," + str(json_obj['total_population_aLvl_std']) + "," + str(json_obj['dividend_growth_rate']) + \
        "," + str(json_obj['dividend_std']) + "," + str(json_obj['p1']) + \
        "," + str(json_obj['p2']) + "," + str(json_obj['delta_t1']) + \
        "," + str(json_obj['delta_t2']) + "," + str(json_obj['dollars_per_hark_money_unit']) + \
        "," + str(json_obj['seconds'])

    append_str_to_file(all_clean, all_clean_str)

    print(all_clean_str)

    # append to data file number 1
    df = pd.read_csv(class_stats_file)
    for ind in df.index:
        records_row += 1
        all_records_str = str(records_row) + "," + str(records_row) + "," + str(json_obj['attention']) + "," + str(json_obj['p1']) + "," + str(json_obj['p2']) + "," + \
            str(json_obj['dividend_growth_rate']) + "," + str(json_obj['ror_volatility']) + "," + str(json_obj['dollars_per_hark_money_unit']) + "," + \
            str(df['aLvl_mean'][ind]) + "," + str(df['CRRA'][ind]) + "," + str(df['DiscFac'][ind]) + "," + str(df['aLvl_std'][ind]) + "," + \
            str(df['mNrm_ratio_StE_mean'][ind]) + "," + str(df['mNrm_ratio_StE_std'][ind])

        append_str_to_file(all_records, all_records_str)

        print(all_records_str)

# test
#create_headers()
#process_run("whiteshark-babyrun10-tag_sim_stats.txt", "whiteshark-babyrun10-tag_class_stats.csv")
#process_run("whiteshark-babyrun10-tag_sim_stats.txt", "whiteshark-babyrun10-tag_class_stats.csv")
