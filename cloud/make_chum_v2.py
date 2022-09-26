import numpy as np
import yaml
import math
import os

np.random.seed(1234) # Set seed for reprodusability
number_of_repeats = 1200
rnd_seeds = np.random.randint(0, high = 100000, size = number_of_repeats)
days_to_simulate = 31
rpc_host = ""

buy_sell_sizes = [(1500,500),(1000,500),(500,500),(500,1000),(500,1500),
                  (15000,5000),(10000,5000),(5000,5000),(5000,10000),(5000,15000),
                  (3600, 1200), (2400, 1200), (1200, 1200), (1200, 2400), (1200, 3600),
                  (36000,12000), (24000,12000), (12000,12000), (12000,24000), (12000,36000)]

#buy_sell_sizes = [(1500, 500), (500, 1500)]

n = 0
n_files = 0
sims_in_yaml = 10
configs = list()
segment = 2
for buy_sell in buy_sell_sizes:
    for seed in rnd_seeds:

        # 20 rabbit mq containers
        if segment > 21:
            segment = 2

        rpc_host = "10.11." + str(segment) + ".4"
        segment += 1

        configs.append({"simid" : n,
        "seed" : "&seedref" + str(n) + " " + str(seed),
        "rabbitMQHost": "&hostref" + str(n) + " " + rpc_host,
        "rabbitMQqueue" : "&queueref" + str(n) + " " + "whitesharkqueue" + str(n),
        "ammps_config" : "&ammpsconfigref" + str(n) + " " + "test_conf.xlsx",    ################ ??
        "sharkfin" : { "save_as" : "../../output/chumv2-" + str(n),
            "parameters" : {
                "simulation" : "Calibration",
                "tag" : "tag",
                "seed" : "*seedref" + str(n),
                "quarters" : 1,
                "runs" : 31,
                "attention" : 0.05,
                "dphm" : 1500,
                "market" : "ClientRPCMarket",
                "dividend_growth_rate" : 1.000628,
                "dividend_std" : 0.011988,
                "queue" : "*queueref" + str(n),
                "rhost" : "*hostref" + str(n),
                "buysize" : buy_sell[0],
                "sellsize" : buy_sell[1],
                "pad" : 30
            }
        },
        "ammps" : {
            "ammps_config_file_name": "*ammpsconfigref" + str(n),
            "ammps_output_dir": "ammps_test_out" + str(n),
            "parameters" : {
                "number" : 0,
                "rabbitMQ-host" : "*hostref" + str(n),
                "rabbitMQ-queue" : "*queueref" + str(n),
                "t" : "true",
            }
        },
        "ammps_config_gen" : {
            "parameters" : {
                "seed" : "*seedref" + str(n),
                "name" : "*ammpsconfigref" + str(n),
                "days" : 30,
                "out-dir" : "/usr/simulation/",
            }
        }});

        n += 1
        if len(configs) == sims_in_yaml:
            f = open('chum2_config_temp{}.yaml'.format(n_files), encoding = 'utf-8', mode = "w")
            yaml_content = {"SIMULATIONS" : configs}
            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
            configs = list() #make new list
            f.close()

            fin = open('chum2_config_temp{}.yaml'.format(n_files), encoding = 'utf-8', mode = "r")
            fout = open('chumv2_{}.yaml'.format(n_files), encoding = 'utf-8', mode = "w")
            #for each line in the input file
            for line in fin:
            	#read replace the string and write to output file
            	fout.write(line.replace('\'', ''))
            #close input and output files
            fin.close()
            fout.close()

            os.remove('chum2_config_temp{}.yaml'.format(n_files));
            n_files += 1
