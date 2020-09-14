#!/usr/bin/env python3

import pandas as pd
import json
from pprint import pprint
import os
import copy

def merge(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1.keys():
                dict1[key].extend(value)
        elif key not in dict1.keys():
                dict1.update({key:value})
    return dict1

def create_dataframes(data):
    dataframes = {
        "device_dataframe": {},
        "command_dataframe": {}
    }
    for device in data:
        for hname, device_data in device.items():
            dataframes["device_dataframe"][hname] =  []
            for data in device_data:
                for command, output in data.items():
                    df = {}          
                    try:        
                        for item in output:
                            for key, value in item.items():
                                if isinstance(value, list):
                                    value = [str(val) for val in value]
                                    value = " ".join(value)
                                try:
                                    value = int(value)
                                except:
                                    pass

                                try:
                                    df[key].append(value)                             
                                except KeyError:
                                    df[key] = []
                                    df[key].append(value)

                        if df:
                            df_dev = copy.deepcopy(df)
                            dataframes["device_dataframe"][hname].append({command: df_dev})

                            df_cmd = copy.deepcopy(df)

                            for values in df_cmd.values():
                                size = len(values)
                                hosts = [hname for host in range(size)]
                                break

                            df_cmd.update({"hostname": hosts})

                            if command in dataframes["command_dataframe"].keys():
                                source = copy.deepcopy(dataframes["command_dataframe"][command])
                                result = merge(source, df_cmd)
                                dataframes["command_dataframe"][command] = result
                            else:
                                dataframes["command_dataframe"][command] = df_cmd
                        else:
                            pass

                    except Exception as failure:
                        print("Failure: {}".format(failure))
    
    return dataframes
    
