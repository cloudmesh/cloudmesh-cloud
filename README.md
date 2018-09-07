# cm
Cloudmesh v4

Class Assignment: Parallel Remote Jobs
In this assignment, the entire class can participate. We will use a single repo at 

 

* https://github.com/cloudmesh-community/cm 

 

to coordinate the assignment. This assignment can be useful for your projects and reused for your projects to conduct benchmarks on remote machines. The online and residential classes can be used to ask questions and work on this in person. 

 

The goal is to have a configuration file in which we add a number of computers that you can use to execute tasks via ssh calls remotely. We wiill use no fancyful ssh library, but just subprocess. As this task requires possibly more than you can do in a single week, you need to decide which task you like to work on.

 

a) develop a documentation so that the program can be managed via a command line. Use docopts for that. You are not allowed to use other tools

 

b) develop a yaml file in which we manage the remote machines and how you get access to them. This includes how many jobs on the machine can be executed in parallel. 

 

c) develop a task mechanism to manage and distribute the jobs on the machine using subprocess and a queue. Start with one job per machine, 

 

c.1) take c and do a new logic where each machine can take multiple jobs

 

d) develop a mechnism to start n vms via vagrant 

 

e) develop a test program that distributes a job to the machines calculates the job and fetches the result back. This is closely related to c, but instead of integrating it in c the movement of the data to and from the job is part of a separate mechanism, It is essentially the status of the calculation. Once all results are in do the reduction into a single result. Remember you could do result calculations in parallel even if other results are not there i

 

f) advanced: develop a string based formulation of the tasks while providing the task in a def and using the chars | for parallel, ; for sequential and + for adding results

 

For example

 

def a():

   sting to be executed via ssh on a remote machine

 

def b():

   ...

 

(a | b| c); d; a+ b+ c +d

 

this is not yet well defined hence advanced

 

all others we can easily do 
