#!/usr/bin/env python3

import logging
from netmiko import ConnectHandler
import json
import os
from celery.result import AsyncResult
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import NetMikoAuthenticationException
from paramiko.ssh_exception import AuthenticationException
import time

logging.basicConfig(filename="Netmiko.log", level=logging.DEBUG)
logger = logging.getLogger("ConnectHandler")

def progressUpdate(taskObject, taskId, valueName, value):
    progress = taskObject.AsyncResult(taskId)
    data = progress.result
    print(data)
    data[valueName] += value
    taskObject.update_state(
        state = "IN PROGRESS",
        meta = data
    )
    
def validate_hostname(prompt):
    if ":" in prompt:
        hostname = prompt.split(":")[1]
    else:
        hostname = prompt
    return hostname

class ConnectManager:

    @staticmethod
    def ssh(device_list, commands, taskObject, textfsm=False):
        commands_output = []
        taskId = taskObject.request.id
        for device in device_list:
            progressUpdate(taskObject, taskId, "progress", device["host"]+"\n")
            try:
                device["global_delay_factor"] = 3
                connection = ConnectHandler(**device)

            except AuthenticationException:
                device["username"] = "faladmin"
                device["password"] = "X3G7tf76jP5!"
                connection = ConnectHandler(**device)

            except SSHException:
                try:
                    progressUpdate(taskObject, taskId, "progress", "USING TELNET\n")
                    telnet_device = {}
                    telnet_device.update(device)
                    telnet_device["device_type"] = telnet_device["device_type"]+"_telnet"
                    connection = ConnectHandler(**telnet_device)

                except ConnectionResetError:
                    progressUpdate(taskObject, taskId, "progress", "TELNET PASSWORD ERROR RESET\n")
                    telnet_device["username"] = "faladmin"
                    telnet_device["password"] = "X3G7tf76jP5!"
                    connection = ConnectHandler(**telnet_device)

                except NetMikoAuthenticationException:
                    progressUpdate(taskObject, taskId, "progress", "TELNET PASSWORD ERROR\n")
                    telnet_device["username"] = "faladmin"
                    telnet_device["password"] = "X3G7tf76jP5!"
                    connection = ConnectHandler(**telnet_device)

                except Exception as failure:
                    progressUpdate(taskObject, taskId, "progress", "THERE IS AN ERROR WITH THE DEVICE:\n--> {} <-- and the error was {}\n".format(device["host"], failure))
                    continue

                finally:
                    try:
                        connection.write_channel("enable\n")
                        connection.write_channel("Red3s#63_1")
                        hostname = validate_hostname(connection.base_prompt)
                        progressUpdate(taskObject, taskId, "progress", hostname+"\n")
                        dcom = {hostname: []}
                        for command in commands:
                            progressUpdate(taskObject, taskId, "progress", "Collecting Information: "+command+"\n")
                            output_list = connection.send_command(command, use_textfsm=textfsm)
                            cm = command.replace(" ", "_")
                            dcom[hostname].append({cm: output_list})
                        commands_output.append(dcom)
                        connection.disconnect()
                        progressUpdate(taskObject, taskId, "current", 1)
                    except Exception as failure:
                        progressUpdate(taskObject, taskId, "progress", "THERE IS AN ERROR TRYING TO CONNECT TO THE DEVICE:\n--> {} <-- and the error was {}\n".format(device["host"], failure))
                        continue

            except Exception as failure:
                progressUpdate(taskObject, taskId, "progress", "THERE IS AN ERROR TRYING TO CONNECT TO THE DEVICE:\n--> {} <-- and the error was {}\n".format(device["host"], failure))
                continue
            
            finally:
                try:
                    connection.write_channel("enable\n")
                    connection.write_channel("Red3s#63_1")
                    hostname = validate_hostname(connection.base_prompt)
                    progressUpdate(taskObject, taskId, "progress", hostname+"\n")
                    dcom = {hostname: []}
                    for command in commands:
                        progressUpdate(taskObject, taskId, "progress", "Collecting Information: "+command+"\n")
                        output_list = connection.send_command(command, use_textfsm=textfsm)
                        cm = command.replace(" ", "_")
                        dcom[hostname].append({cm: output_list})
                    commands_output.append(dcom)
                    connection.disconnect()
                    progressUpdate(taskObject, taskId, "current", 1)
                except Exception as failure:
                    progressUpdate(taskObject, taskId, "current", 1)
                    progressUpdate(taskObject, taskId, "progress", "THERE IS AN ERROR TRYING TO CONNECT TO THE DEVICE:\n--> {} <-- and the error was {}\n".format(device["host"], failure))
                    continue

        return commands_output






