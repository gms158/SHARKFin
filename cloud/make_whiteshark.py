import numpy as np
import yaml
import math
import os

np.random.seed(1234) # Set seed for reprodusability
#number_of_repeats = 10
number_of_repeats = 25
rnd_seeds = np.random.randint(0, high = 100000, size = number_of_repeats)
days_to_simulate = 480
rpc_host = ""

#attention_values = [0.00, 0.005, 0.02, 0.08, 0.15, 0.30] # 0.01, 0.99
#p1_values = [0.01, 0.1, 0.3, 0.7, 0.9, 0.99]
#p2_values = [ 0.05, 0.3, 0.7, 0.95]
#dividend_growth_rates = [1.0, ...., 1.002]  ############# ?? 1.0, 1.002
#dphms = [20000,150000]


attention_values = [0.01, 0.99] # 0.01, 0.99
p1_values = [0.01, 0.99]
p2_values = [ 0.05, 0.95]
dividend_growth_rates = [ 1.0, 1.002]  ############# ?? 1.0, 1.002
dphms = [20000,150000]
quarters = 8

n = 0
n_files = 0
sims_in_yaml = 10
configs = list()
segment = 3

for attention_value in attention_values:
    for p1_value in p1_values:
        for p2_value in p2_values:
            for dividend_growth_rate in dividend_growth_rates:
                for dphm in dphms:
                    for seed in rnd_seeds:

                        # 20 rabbit mq containers
                        if segment > 21:
                            segment = 3

                        rpc_host = "10.11." + str(segment) + ".4"
                        segment += 1

                        configs.append({"simid" : n,
                        "seed" : "&seedref" + str(n) + " " + str(seed),
                        "rabbitMQHost": "&hostref" + str(n) + " " + rpc_host,
                        "rabbitMQqueue" : "&queueref" + str(n) + " " + "whitesharkqueue" + str(n),
                        "ammps_config" : "&ammpsconfigref" + str(n) + " " + "test_conf.xlsx",    ################ ??
                        "sharkfin" : { "save_as" : "../../output/whiteshark-babyrunv2" + str(n),
                            "parameters" : {
                                "simulation" : "Attention",
                                "tag" : "tag",
                                "seed" : "*seedref" + str(n),
                                "popn" : 25,
                                "quarters" : quarters,
                                "runs" : 60,
                                "attention" : attention_value,
                                "dphm" : dphm,
                                "market" : "ClientRPCMarket",
                                "dividend_growth_rate" : dividend_growth_rate, # just vary this  dr_rate_return_values? 1.0, 1.002
                                "dividend_std" : 0.011988, # look at paper
                                "queue" : "*queueref" + str(n),
                                "rhost" : "*hostref" + str(n),
                                "p1" : p1_value,
                                "p2" : p2_value,
                                "d1" : 0.1, # constnt, look at paper
                                "d2" : 0.1, # constant
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
                                "days" : quarters*60,
                                "out-dir" : "/usr/simulation/",
                            }
                        }});

                        n += 1
                        if len(configs) == sims_in_yaml:
                            f = open('whiteshark_config_temp{}.yaml'.format(n_files), encoding = 'utf-8', mode = "w")
                            yaml_content = {"SIMULATIONS" : configs}
                            yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
                            configs = list() #make new list

                            f.close()

                            fin = open('whiteshark_config_temp{}.yaml'.format(n_files), encoding = 'utf-8', mode = "r")
                            fout = open('whitesharkbabyv2-{}.yaml'.format(n_files), encoding = 'utf-8', mode = "w")
                            #for each line in the input file
                            for line in fin:
                            	#read replace the string and write to output file
                            	fout.write(line.replace('\'', ''))
                            #close input and output files
                            fin.close()
                            fout.close()

                            os.remove('whiteshark_config_temp{}.yaml'.format(n_files));

                            n_files += 1
