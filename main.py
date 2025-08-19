import time
import schedule
import paramiko
import boto3
import pytz
import shutil
import json
import datetime
from pathlib import Path
import logging
logging.basicConfig(filename='logs.log',level=logging.INFO,format='%(asctime)s-%(levelname)s-%(message)s')
from botocore.exceptions import ClientError
date=datetime.datetime.now()
forp = date.strftime("%Y-%m-%d")
fori = date - datetime.timedelta(days=2)
format=fori.strftime("%Y-%m-%d")
IP_Address=[]
Server_Name=[]
def main_proj():
    logging.info("MAINFunction started")
    name="exampleprojectbucketcodespaces"
    state = input("Instance running or not : \n")
    def ec_2(state,IP_Address,Server_Name):
        if state == 'yes':
          client = boto3.client('ec2')
          response = client.describe_instances()
          for reservation in response['Reservations']:
            for instance in reservation['Instances']:
              if "PublicIpAddress" in instance:
                IP_Address.append(instance.get('PublicIpAddress')) 
                for tags in instance['Tags']:
                  Server_Name.append(tags.get('Value'))
          logging.info("Completed getting IP and server names")
        else:
          logging.critical("Instance not ruuning")
        

    def ssh_connect_1(IP_Address,Server_Name):
      if len(IP_Address) >0:
        for i in range(len(IP_Address)):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=f"{IP_Address[i]}",
                        username="ubuntu",
                        key_filename="/content/Python_for_devops/key.pem")
            stdin, stdout, stderr =  ssh.exec_command("cat /var/log/auth.log")
            out = stdout.read().decode()
            out_lines=out.splitlines()
            for j in out_lines:
                today_date=j.split('T')[0]
                if today_date==forp:
                  ssh.exec_command(f"cd /var/log && sudo touch {Server_Name[i]}.example_log.zip && echo {j} | sudo tee -a {Server_Name[i]}.example_log.zip")
            sftp=ssh.open_sftp()
            sftp.get(f"/var/log/{Server_Name[i]}.example_log.zip",f"/content/Python_for_devops/{Server_Name[i]}_log.zip")
            sftp.close()
            ssh.close()
        logging.info("Created file in linux and got the file to remote")
      else:
        logging.error("Servers not running")

    def send_to_s3(name,Server_Name,IP_Address):
      if len(IP_Address) > 0:
        s3 = boto3.client('s3')
        res = s3.list_buckets()
        exist = 0
        for j in range(len(res['Buckets'])):
          exornot = res['Buckets'][j]['Name']
          if exornot == name:
            exist = 1
        if exist == 1:
          logging.warning(f"Bucket with name : {name} already exists")
          for k in range(len(IP_Address)):
            s3.upload_file(f'/content/Python_for_devops/{Server_Name[k]}_log.zip', name , f'{Server_Name[k]}_log.zip')
        elif exist != 1:
          try:
              s3.create_bucket(Bucket=name)
              for i in range(len(IP_Address)):
                s3.upload_file(f'/content/Python_for_devops/{Server_Name[i]}_log.zip', name , f'{Server_Name[i]}_log.zip')
          except ClientError as e:
              err = e.response['Error']['Code']
              if err == "InvalidBucketName":
                logging.error("Give the valid bucket name")
              else:
                logging.error(f"Unexcepted error {e}")
        logging.info(f"Sent the file to s3 bucket with name : {name}")
      else:
        logging.error("NO Instances found")
            
    def list_bucket():
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        check_buck = len(response['Buckets'])
        if check_buck != 0:
          for i in response['Buckets']:
              with open("/content/Python_for_devops/bucket_list.txt","a") as f:
                file=f.write(json.dumps(i,default=str))
                file=f.write(f'\n')
        else:
          logging.info("No buckets found")
        logging.info("Listed the buckets and have it in local")

    def del_file_in_server(IP_Address,Server_Name):
      if len(IP_Address) > 0:
        for i in range(len(IP_Address)):
          p = Path(f"/content/Python_for_devops/{Server_Name[i]}_log.zip")
          if p.exists():
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=f"{IP_Address[i]}",
                          username="ubuntu",
                          key_filename="/content/Python_for_devops/key.pem")
            ssh.exec_command(f"cd /var/log && sudo rm {Server_Name[i]}.example_log.zip")
            logging.info(f"Removed file in the {Server_Name[i]}")
          else:
            logging.error("file not exist in the pwd")
        logging.info("Deleted the files in remote if the files are present in local")
      else:
        logging.error("NO IP Found")

    def del_files_local(name,IP_Address,Server_Name):
      if len(IP_Address) > 0:
        s3 = boto3.client('s3')
        response = s3.head_bucket(Bucket = name)
        if (response['ResponseMetadata']['HTTPStatusCode']) == 200:
          responsee = s3.list_objects(Bucket = name)
          if (responsee['ResponseMetadata']['HTTPStatusCode']) == 200:
            for i in range(len(IP_Address)):
              p = Path(f"/content/Python_for_devops/{Server_Name[i]}_log.zip")
              if (f"{responsee['Contents'][i]['Key']}") == (f'{Server_Name[i]}_log.zip'):
                p.unlink()
        logging.info("Deleted the files in local if the files exists in s3 bucket")
      else:
        logging.error("IP NOT FOUND")

    def del_file_from_s3(name):
      s3 = boto3.client('s3')
      response = s3.list_objects(Bucket = name)
      obj_len = len(response['Contents'])
      timezone = pytz.timezone('Asia/kolkata') 
      for i in range(obj_len):
        last_modified_date = response['Contents'][i]['LastModified']
        format1 = last_modified_date + datetime.timedelta(days=3)
        last_date = format1.astimezone(timezone).strftime("%Y-%m-%d")
        del_date = date.astimezone(timezone).strftime("%Y-%m-%d")
        if last_date == del_date:
          key = response['Contents'][i]['Key']
          responsee = s3.delete_objects(
          Bucket=name,
          Delete={
              'Objects': [
                  {
                      'Key': key,
                  },
              ],
          }
      )
      logging.info("Deleted the obj in s3 bucket if the file date is existing more than 3 days")


    ec_2(state,IP_Address,Server_Name)
    ssh_connect_1(IP_Address,Server_Name)
    send_to_s3(name,Server_Name,IP_Address)
    list_bucket()
    del_file_in_server(IP_Address,Server_Name)
    del_files_local(name,IP_Address,Server_Name)
    del_file_from_s3(name)
# zone = pytz.timezone('Asia/Kolkata')
# date1=(datetime.timedelta(minutes=1)+datetime.datetime.now(zone)).strftime("%H:%M")
# schedule.every().day.at(date1).do(main_proj).tag("Every-day-at-1300-hour")
schedule.every().day.at('15:43').do(main_proj)
while True:
  schedule.run_pending()
  time.sleep(1)
