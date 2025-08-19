
# LOG_AUTOMATION

Automating the server log rotation by connecting to aws and getting log information from ec-2 instances.

This project is done using python and python packages that are listed below\

    -- paramiko : Used to establish one time SSH connection with server.\
    -- boto3 : It is an module that we can access aws services like s3 buckets, etc.\
    -- logging : Logs everything into a file used instead of printing.\
    -- datetime : used to get time and dates.\
    -- pathlib : Accesing the files in local system.\
    -- schedule : Schedules the task at a specific time. **

## ABOUT THE PROJECT

The main aim of this project to create a file that contain a specific day logs and store that file in that respective server(s), after that shift that file from remote to local (used SMTP)
and delete that log file in remote after conforming the file exists in local, now move the log file to the aws s3 bucket and delete the files in local after conforming the file exists in s3 bucket, lastly delete the files after three days that exists in s3 bucket.

This project is divided into different functions and every function comes under [main_proj()] function.

Scheduled the task every day by night 00:00 - IST(24 hr format), this will run the function by starting of day without any human requirment.

## FUNCTION WORKING

The function **main_proj** where it consists several functions

    -- ec2
    -- shh_connect_1
    -- send_to_s3
    -- list_bucket
    -- del_file_in_server
    -- del_files_local
    -- del_file_from_s3

The function **ec2** will helps to get data of ip address and server names using boto3.

The function **ssh_connect_1** will connect with server using paramiko ssh connection by taking ip address, key file as inputs, after connection it creates a file in server and append the todays log data to that file and get that file from remote to local by **SMTP** connection.

The function **send_to_s3** will check the file in local and create a bucket and send that file to s3 bucket as objects.

The function **list_bucket** will write about the bucket into a file that exists locally.

The function **del_file_in_server** will checks the file exists locally, if exists then the particular file will be deleted in remote.

The function **del_files_local** will delete the file locally if that particular is existing in s3 bucket as objects.

The function **del_file_from_s3** will delete the object from s3 buckets if the object is older than 3 days.


## FILE INFORMATION
The Repo consists of below files

    -- main.py : Contains main python code.
    -- key.pem : This file needs to have key file for ssh connection.      
    -- logs.log : Contains logs about the project execution.
    -- bucket_list.txt : Contains about bucket details.




THANK YOU FOR CHECKING THE PROJECT



