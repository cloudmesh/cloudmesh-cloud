#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 00:23:36 2018

@author: yuluo
"""
from ProcessABC import ProcessABC
import subprocess, random, multiprocessing as mp, os

class ParallProcess(ProcessABC):
    
    def __init__(self, content):
        self.content = content
        
    def get_computer_list(self):
        return (self.content["cloudmesh"])["cluster"]
        
    def get_computer(self,info):
        item = ""
        username = ""
        publickey= ""
        cluster = self.get_computer_list()
        if info:
            for i in cluster:
                if (cluster[i])["label"] == info or (cluster[i])["name"] == info:
                    #print("computer "+ (cluster[i])["label"]+"/"+ (cluster[i])["name"]+ " is selected")
                    username = ((cluster[i])["credentials"])["username"]
                    publickey = ((cluster[i])["credentials"])["publickey"]
                    item = i
            
            return item, username, publickey
        else:
            index = random.randint(0,len(cluster)-1)
            key = list(cluster.keys())[index]
            #print("computer "+ (cluster[key])["label"]+"/"+ (cluster[key])["name"]+ " is selected")
            username = ((cluster[key])["credentials"])["username"]
            publickey = ((cluster[key])["credentials"])["publickey"]
            item = key
            return item, username, publickey
        
    def run_remote(self, username, publickey, script):
        s = subprocess.check_output(["ssh", "-i",publickey, username, "sh", script]).decode("utf-8").split("\n")
        return s
    
    def scp(self, username, publickey, script):
        subprocess.check_output(["scp", "-i",publickey,  script, username+":~/"])
        return  "~/"+script.split("/")[len(script.split("/"))-1]
           
    def delete(self, username, publickey, file):
        subprocess.check_output(["ssh", "-i", publickey, username, "rm", file])
        
    def run_local(self, username, publickey, script):
        
        proc = os.popen("cat " + script+ " | " + "ssh"+ " -i "+ publickey +" "+ username + " sh").read()
        return proc
    
    def parall_list(self, scripts):
        count = len(scripts)
        process = []
        c_list = self.get_computer_list()
        max_c = len(c_list)
        
        if max_c >= count:
            while count != 0:
                cp = self.get_computer("")
                if cp not in process:
                    count = count - 1
                    process.append(cp)
        else:
            rest = count % max_c
            repeat = int (count / max_c)
            while rest != 0:
                cp = self.get_computer("")
                if cp not in process:
                    rest = rest - 1
                    process.append(cp)
            while repeat != 0:
                for i in c_list.keys():
                    process.append([i,((c_list[i])["credentials"])["username"], ((c_list[i])["credentials"])["publickey"]])
                repeat = repeat - 1
        return process  
                
    
        
    def run_parall(self, scripts):
        output = mp.Queue()
        parall_list = self.parall_list(scripts)
        
        def parall_process(cp, output, script):
            result = self.run_local(cp[1], cp[2], script)
            output.put([cp[0], result])
            
        process = [mp.Process(target=parall_process, args=(parall_list[x], output, scripts[x])) for x in range(len(scripts))]
        
        for i in process:
            i.start()
        
        for i in process:
            i.join()
            
        result = [output.get() for i in process]
        
        return result
        
    def readable(self,result):
        for i in result:
            print(i[0])
            print("Running script and get the result:")
            print(i[1])