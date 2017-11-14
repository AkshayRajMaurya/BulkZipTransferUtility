import os
import sys
import gzip
import logging
import datetime
import ConfigParser
import logging.config


config = ConfigParser.RawConfigParser()
config.read('appConf.properties')
inputpath = config.get('SourceDestination', 'dump.source');
outputpath = config.get('SourceDestination', 'dump.destination');
logfile = config.get('LogPath', 'log.path.filename');
skipFileFlag = config.get('SkipLogicForFiles', 'skip.logic');
skipDays = config.get('SkipLogicForFiles', 'skip.days');
logging.config.fileConfig('logging.conf', defaults={'logfilename': logfile})


	
def main():
	if inputpath in outputpath:
		logging.info('Destination Path Cannot Be a Part Of Source Path. Please Specify Correct Source & Destination Paths')
		logging.info('Found ' + inputpath + ' in ' + outputpath)
		logging.info('Exiting.....')
		exit(0)
	logging.info('Files from ' + inputpath + ' will be moved to ' + outputpath)
	for dirpath, dirnames, filenames in os.walk(inputpath):
		structure = os.path.join(outputpath, dirpath[len(inputpath):])
		logging.debug('Creating Folder Structure' + structure)
		if not os.path.isdir(structure):
			os.mkdir(structure)
		else:
			print("Folder already exists!")		
	logging.info('Folder Structure creation Successful at ' + outputpath)
	recursive_walk(inputpath)


def recursive_walk(folder):
	for folderName, subfolders, filenames in os.walk(folder):
		if subfolders:
			for subfolder in subfolders:
				recursive_walk(subfolder)
		folderPath = folderName.split(inputpath,1)[1]
		source = os.path.join(inputpath, folderPath)
		destination = os.path.join(outputpath, folderPath)
		for filename in filenames:
			if skipFileFlag.lower()=='on' and not days_between(os.path.getmtime(os.path.join(source, filename))):
				logging.debug('File '+ os.path.join(source, filename) +' will not be moved as skipFile is enabled and last modified time is less than ' + skipDays + ' days')
				continue
			logging.debug('Currently Zipping File ' + os.path.join(source, filename))
			zip_files(os.path.join(source, filename), os.path.join(destination, filename))
	logging.info('Zip and Move Completed from ' + inputpath + ' to ' + outputpath + ' Successfully')


def zip_files(source,destination):
	try:
		if source.lower().endswith(('.zip', '.gz', '.7z', '.rar', '.tar')):
			os.rename(source, destination)
		else:
			with open(source) as src, gzip.open(destination+str(datetime.date.today())+'.gz', 'wb') as dst:
				dst.writelines(src)
			os.remove(source)
		logging.debug('Zip and Move Completed to Destination ' + destination)
	except (KeyboardInterrupt, SystemExit):
		raise
	except:
		print 'Unexpected error:', sys.exc_info()[0]
		logging.info('Exception In Moving from ' + source + ' to ' + destination)
		try:
			if not source.lower().endswith(('.zip', '.gz', '.7z', '.rar', '.tar')):
				logging.debug('Going to remove ' + destination)
				os.remove(destination+str(datetime.date.today())+'.gz')
				logging.debug('File removed from destination ' + destination)
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			print 'Unexpected error:', sys.exc_info()[0]
			logging.debug('Exception in removal of file from destination '+ destination)



def days_between(time):
	d2 = datetime.datetime.strptime(datetime.date.fromtimestamp(time).strftime('%Y-%m-%d'), "%Y-%m-%d")
	d1 = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y-%m-%d'), "%Y-%m-%d")
	return abs((d2 - d1).days) > int(skipDays)

if __name__== "__main__":
  main()
