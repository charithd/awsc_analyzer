#!/usr/bin/python


import boto3
import os
import sys
import csv
import datetime
import io
import re

# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


#---------------------------------------------------------------------------------------------------------
# AUTHOR 		: L.B.Charith Deshapriya (charith079atgmail.com)
# USAGE 	   	: AWS Analyzer (Volumes,AMIs,Snapshots and ELBs)
# DATE			: 25/10/2017
#---------------------------------------------------------------------------------------------------------


#---------------------------------------------------------------------------------------------------------
#Global variables
#---------------------------------------------------------------------------------------------------------

#Account id is necessary to get snapshots info

if len(sys.argv) == 3:
	ownerid = sys.argv[1];
	region = sys.argv[2];
else:
	print"--------------------------------------------------";
	print "Please provide account id and region ";
	print __file__+" [acountid] [region]";
	print "eg:- >"+__file__+" 43553535345 us-west-1";
	print"--------------------------------------------------";

	sys.exit(1);


total_unattached =0;
total_snap_size =0;
total_old_snap_size =0;
total_amivol_size =0;
total_idle_elb_num =0;

dry_run =False; #True or False, to check permissions
debug_run =False; #True or False, to enable debug prints


timestamp = '{:%Y-%m-%d-%H:%M:%S}'.format(datetime.datetime.now());
timestampY = '{:%Y}'.format(datetime.datetime.now());


vol_fileout = ownerid+"-"+region+"_vol-"+timestamp+".csv";
snap_fileout = ownerid+"-"+region+"_snap-"+timestamp+".csv";
ami_fileout = ownerid+"-"+region+"_ami-"+timestamp+".csv";
elb_fileout = ownerid+"-"+region+"_elb-"+timestamp+".csv";


print "[]working on region: {0}".format(region);
print "[]working on Account: {0}".format(ownerid);
print "";

ec2client = boto3.client('ec2',region_name=region);


#---------------------------------------------------------------------------------------------------------
#Get Volumes info
#----------------------------------
def GetVolumes():

	global total_unattached;
	csv = open(vol_fileout, "w");
	
	columnTitleRow = "VolumeId, Size(GB), VolumeType, State, Attached Instnace, Device, Tags\n";
	csv.write(columnTitleRow);

	print "Retrieving Volume info [Started]";
	vol_c = 0;
	for volume in ec2client.describe_volumes(DryRun=dry_run)['Volumes']:
		row =[];
	 	#print(volume)
		if debug_run: print "Vol: " +volume['VolumeId'] + " Size: "+ str(volume['Size']) + "GB",;
		row.append(volume['VolumeId']);
		row.append(volume['Size']);
		row.append(volume['VolumeType']);
		

		if volume['Attachments']:
			Attachment=volume['Attachments'];
			for i in Attachment:	
		  		if debug_run: print i['State'] + " to "+ i['InstanceId'] +" as "+ i['Device'],;
		  		row.append(i['State']);
		  		row.append(i['InstanceId']);
		  		row.append(i['Device']);

		else:
		  	if debug_run:  print "[This volume not attached to any instance]",;
		  	row.append("[This volume not attached to any instance]");
		  	total_unattached += volume['Size'];

		
		if 'Tags' in volume.keys():
			Tag=volume['Tags'];
			if debug_run: print "Tags:- ",;

			for j in sorted(Tag):	
		  		if debug_run: print j['Key'] + " : "+ j['Value'],;
		  		row.append(j['Key'] + " : "+ j['Value']);
		  	if debug_run: print " ";	
		else:
		  	if debug_run: print "[This volume doesn't have tags]";
		  	row.append("[This volume doesn't have tags]");

		if debug_run: print "Array out----------------------------------"  	
		row.append("\n");


		csv.write(','.join(map(str, row)));
		vol_c +=1;

	print "Retrieving Volume info [Completed]";	
	total_vol ="Total "+str(vol_c)+" Volumes and total unattached Volumes size on " + region +" is "+ str(total_unattached)+" GB";
	print "---------------------------------------------------------------------------------------"
	print total_vol;
	print "---------------------------------------------------------------------------------------"
	print "Please refer '"+vol_fileout+"' for more details\n";
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write(total_vol+"\n");
	csv.write("-----------------------------------------------------------------------------------------------\n");

	csv.close();
	return;

#---------------------------------------------------------------------------------------------------------
#Get Snapshot info
#----------------------------------
def GetSnap():

	global total_snap_size;
	global total_old_snap_size;
	csv = open(snap_fileout, "w");
	columnTitleRow = "SnapshotId, StartTime, Base VolumeId, VolumeSize(GB), Tags\n";
	csv.write(columnTitleRow);

	print "Retrieving Snapshot info [Started]";
	snap_c = 0;
	for snapshot in ec2client.describe_snapshots(DryRun=dry_run,OwnerIds=[ownerid])['Snapshots']:
		row =[];
	 	
		if debug_run: print snapshot['SnapshotId'];
		if debug_run: print snapshot['StartTime'];
		if debug_run: print snapshot['VolumeId'];
		if debug_run: print snapshot['VolumeSize'];
		
		row.append(snapshot['SnapshotId']);
		row.append(snapshot['StartTime']);
		row.append(snapshot['VolumeId']);
		row.append(snapshot['VolumeSize']);

		total_snap_size += snapshot['VolumeSize'];
		
		timestamp = '{:%Y-%m-%d}'.format(snapshot['StartTime']);

		if re.match(timestampY, timestamp) is None:
			if debug_run: print "snap is old";
			total_old_snap_size += snapshot['VolumeSize']; 
 		

		if 'Tags' in snapshot.keys():
			Tag=snapshot['Tags'];
			if debug_run: print "Tags:- ",;
			for j in sorted(Tag):	
		  		if debug_run: print j['Key'] + " : "+ j['Value'],;
		  		row.append(j['Key'] + " : "+ j['Value']);
		  	if debug_run: print " ";	
		else:
		  	if debug_run: print "[This snapshot doesn't have tags]";
		  	row.append("[This snapshot doesn't have tags]");

		row.append("\n");
		csv.write(','.join(map(str, row)));
		snap_c +=1;

	print "Retrieving Snapshot info [Completed]";	
	total_snap ="Total "+str(snap_c)+" Snapshots and total Snapshots size on " + region +" is "+ str(total_snap_size)+" GB";
	total_old_snap ="Total Old Snapshots (Created a year before) size on " + region +" is "+ str(total_old_snap_size)+" GB";
	print "---------------------------------------------------------------------------------------"
	print total_snap;
	print total_old_snap;
	print "---------------------------------------------------------------------------------------"
	print "Please refer '"+snap_fileout+"' for more details\n";
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write(total_snap+"\n");
	csv.write(total_old_snap+"\n");
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write("*Amazon EBS snapshots are stored incrementally: only the blocks that have changed after your last snapshot are saved,\n");
	csv.write("and you are billed only for the changed blocks\n");
	csv.write("*When an EBS snapshot is copied new EBS snapshot volume ID shows as vol-ffffffff\n");

	csv.close();
	return;

#*When an EBS snapshot is copied (whether within the same region, or to another region),
# the Volume ID attached to the new EBS snapshot copy does not reflect the originating EBS volume.
# volume ID shows as vol-ffffffff


#---------------------------------------------------------------------------------------------------------
#Get AMI info
#----------------------------------
def GetAmi():

	global total_amivol_size;
	csv = open(ami_fileout, "w");
	
	columnTitleRow = "ImageId, CreationDate, State, BlockDeviceMappings 01:, BlockDeviceMappings 02, BlockDeviceMappings 03, Tags\n";
	csv.write(columnTitleRow);

	print "Retrieving AMI info [Started]";
	ami_c = 0;
	for ami in ec2client.describe_images(DryRun=dry_run,Owners=['self'])['Images']:
		#filter"ImageIds=['ami-7ae6541a']
		row =[];
	 	#print(volume)
		if debug_run: print "AMI: " +ami['ImageId'] + " Creation date: "+ str(ami['CreationDate']),;
		row.append(ami['ImageId']);
		row.append(ami['CreationDate']);
		row.append(ami['State']);


		if 'BlockDeviceMappings' in ami.keys():
			EBS=ami['BlockDeviceMappings'];
			if debug_run: print "EBSs:- ",;
			
			for j in EBS:	
				#if debug_run: print j;
				if "Ebs" in j:
					Ebs_d = j['Ebs'];
					Ebs_dn = j['DeviceName'];

					#print Ebs_d;

					if 'SnapshotId' in Ebs_d.keys():

						if debug_run: print Ebs_d['SnapshotId']+" : "+str(Ebs_d['VolumeSize']),;
						row.append(j['DeviceName']+":"+Ebs_d['SnapshotId'] + " :"+ str(Ebs_d['VolumeSize'])+"GB");
				
						total_amivol_size += Ebs_d['VolumeSize'];
					else:
						if debug_run: print "No Snapshot info available";
						row.append("No Snapshot info available");	

				else:
					if debug_run: print "This is ephemeral  not a EBS"
					row.append(j['DeviceName']+" : Ephemeral");	

		  	if debug_run: print " ";	
		else:
		  	if debug_run: print "[This AMI doesn't have BlockDeviceMappings]";
		  	row.append("No EBS");
		  	
		
		if 'Tags' in ami.keys():
			Tag=ami['Tags'];
			if debug_run: print "Tags:- ",;
			for j in sorted(Tag):	
		  		if debug_run: print j['Key'] + " : "+ j['Value'],;
		  		row.append(j['Key'] + " : "+ j['Value']);
		  	if debug_run: print " ";	
		else:
		  	if debug_run: print "[This AMI doesn't have tags]";
		  	row.append("[This AMI doesn't have tags]");
		  	

		if debug_run: print "Array out----------------------------------"  	
		row.append("\n");


		csv.write(','.join(map(str, row)));
		ami_c +=1;

	print "Retrieving AMI info [Completed]";	
	total_amivol ="Total "+str(ami_c)+" AMIs and total Volumes size attached to AMIs on " + region +" is "+ str(total_amivol_size)+" GB";
	print "---------------------------------------------------------------------------------------"
	print total_amivol;
	print "---------------------------------------------------------------------------------------"
	print "Please refer '"+ami_fileout+"' for more details\n";
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write(total_amivol+"\n");
	csv.write("-----------------------------------------------------------------------------------------------\n");

	csv.close();
	return;


#---------------------------------------------------------------------------------------------------------
#Get Elastc load Balancers info
#----------------------------------
def GetElb():

	global total_idle_elb_num;
	elbclient = boto3.client('elb',region_name=region);
	csv = open(elb_fileout, "w");
	
	columnTitleRow = "LoadBalancerName, CreatedTime, DNSName, Instances:\n";
	csv.write(columnTitleRow);

	print "Retrieving ELB info [Started]";
	
	elb_c=0;
	for elb in elbclient.describe_load_balancers()['LoadBalancerDescriptions']:
		#filter:LoadBalancerNames=['pos4-idm-loadbalancer','qa-vpc-pg-web-loadbalancer']
		row =[];
		
		row.append(elb['LoadBalancerName']);
		row.append(elb['CreatedTime']);
		row.append(elb['DNSName']);
		
		if elb['Instances']:
			elbs=elb['Instances'];
			#print elbs;
			i=0;
			for j in elbs:	
		  		#print j['InstanceId'],;
		  		i += 1;
		  		row.append(j['InstanceId']);
		  		#row.append(j['Key'] + " : "+ j['Value']);
		  		#if debug_run: print " ";
		  	if debug_run: print "ELB: " +elb['LoadBalancerName'] + " Creation date: "+ str(elb['CreatedTime'])+"attached "+str(i)+" instance(s) ";
		  	row.append(i);		
		else:
			if debug_run: print "ELB: " +elb['LoadBalancerName'] + " Creation date: "+ str(elb['CreatedTime'])+"[This ELB doesn't have Instance attached]";
			row.append("[This ELB doesn't have Instance attached]");
			total_idle_elb_num+=1;

		row.append("\n");
		csv.write(','.join(map(str, row)));
		elb_c +=1;

	print "Retrieving ELB info [Completed]";	
	total_elb ="Total "+str(elb_c)+" ELBs and total number of idle ELBs on " + region +" : "+ str(total_idle_elb_num);
	print "---------------------------------------------------------------------------------------"
	print total_elb;
	print "---------------------------------------------------------------------------------------"
	print "Please refer '"+elb_fileout+"' for more details\n";
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write(total_elb+"\n");
	csv.write("-----------------------------------------------------------------------------------------------\n");

	csv.close();
	return;		


#---------------------------------------------------------------------------------------------------------
GetVolumes();
GetSnap();
GetAmi();
GetElb();
#---------------------------------------------------------------------------------------------------------