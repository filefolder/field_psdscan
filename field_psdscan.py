
"""
version 0.12

python3 script to quickly view the last N days of recovered data
with the idea being to check the site is working OK before leaving

tested on windows, linux, and mac

requires: obspy

/path/to/sdcard should be the root directory! for a typical SD card this is the folder that contains STA01miniSEED/

"""

import sys

if len(sys.argv) < 2:
	print("to run:  ./field_psdscan.py </path/to/sdcard> <inst type (default TC120)>")
	exit()


########set parameters here

num_days_lookback = 3 #how many days to look at. the most recent will be taken. 
#figdir = None
figdir = "./field_psd_figs" #where to store figures (set to "" or None" if you don't want to save any)
psd_len = 1800 #length of psd window (seconds). set to lower (e.g. 600 or 10 minutes) for quick lab testing
file_struct = '*.[DGCHBE]?[NEZ]' #filename matching template (currently set for ANU LPR200 or TerraSAWR)

########


try: senstype = str(sys.argv[2]).upper()
except: senstype = "T120"
if 'TC' in senstype: senstype.replace('TC','T')
print("using PAZ for %s" % senstype)

#typical instrument/samplerates for ANSIR equipment
response_dict = {
	'3DL': {'poles':[(-4.444+4.444j), (-4.444-4.444j), (-1.083+0j)],
				'zeros':[0j, 0j, 0j],
				'gain':1, # A0
				'sensitivity': 400 * round(8589934592/4096) /1}, #overall sensitivity (400 V/m/s * logger gain * 5Vpp scaling)

	'T120': {'poles':[(-0.03691+0.03702j),(-0.03691-0.03702j), (-343+0j), (-370+467j), (-370-467j), (-836+1522j), (-836-1522j), (-4900+4700j), (-4900-4700j), (-6900+0j), (-15000+0j)],
				 'zeros':[0j, 0j, (-392+0j), (-1960+0j), (-1490+1740j), (-1490-1740j)],
				 'gain':4.34493e+17, # A0
				 'sensitivity': 754.3*round(8589934592/4096) /4}, #e.g. overall sensitivity (754.3 V/m/s * logger gain * 20Vpp scaling
	
	'T20': {'poles':[(-0.2214+0.2221j), (-0.2214-0.2221j), (-343+0j), (-370+467j), (-370-467j), (-836+1522j), (-836-1522j), (-4900+4700j), (-4900-4700j), (-6900+0j), (-15000+0j)],
				 'zeros':[0j, 0j, (-392+0j), (-1960+0j), (-1490+1740j), (-1490-1740j)],
				 'gain':4.34493e+17,
				 'sensitivity':754.3*round(8589934592/4096) /4 },
	
	'BD3C': {'poles':[(-1720.4+0j), (-1.2+0.9j), (-1.2-0.9j)], #broadband node.. insensitive to sample rate
			'zeros':[(14164+0j), (-7162+0j), 0j, 0j],
			'gain':1.69726e-05,
			'sensitivity': 702651512.6046528},
	
	'16HR': {'poles':[(-22.211059+22.217768j), (-22.211059-22.217768j)], #shortperiod node.. insensitive to sample rate
			'zeros':[0j, 0j],
			'gain':1,
			'sensitivity': 257019225.55108312},

	'AUANU': {'poles':[(-0.148032-0.148032j), (-0.148032+0.148032j), (-391.955153+850.693025j), (-391.955153-850.693025j), (-2199.114858+0j), (-471.238898+0j)], #S1.AUANU at 100hz
			'zeros':[0j, 0j],
			'gain':9.12996e+11,
			'sensitivity': 2489067360}
}


if senstype not in response_dict.keys():
	print("instrument type/samplerate %s was not found! select from:   %s"  % (senstype,list(response_dict.keys())))
	exit()


from pathlib import Path,PureWindowsPath
import glob, os
import multiprocessing as mp
from obspy import read
from obspy import UTCDateTime
from obspy.signal import PPSD #seems fine enough with the default
from obspy.imaging.cm import pqlx,viridis_white_r

outdir = None
if figdir and figdir != '': outdir = Path(figdir)

fyledir = Path(str(sys.argv[1]))

import platform
if platform.system() == "Windows":
	outdir = PureWindowsPath(outdir)
	fyledir = PureWindowsPath(fyledir)


if not os.path.isdir(outdir): os.mkdir(outdir)
if not os.path.isdir(fyledir):
	print("directory %s not found" % fyledir); exit()

all_fyles = glob.glob(os.path.join(fyledir,'**/*'+file_struct),recursive=True)
if len(all_fyles) == 0: all_fyles = glob.glob(os.path.join(fyledir,file_struct),recursive=True)
if len(all_fyles) == 0: print("no files found in directory %s"  % fyledir); exit()


#mp function
def plot_channel(cha_code):

	fyles = [ele for ele in all_fyles if ele[-1].upper() == cha_code]
	if len(fyles) == 0: print("***** NO FILES FOUND for %s ????" % cha_code); return

	fyles.sort() #put in time order descending
	fyles = fyles[-int(num_days_lookback):] #only select the last 5 days or so

	st = read(fyles[0])

	ppsd = PPSD(stats=st[0].stats,metadata=response_dict[senstype],ppsd_length=psd_len) #30 minutes TODO make dynamic
	for fyle in fyles: #now add the rest
		st = read(fyle)
		ppsd.add(st)

	if len(ppsd.psd_values) == 0: print("no valid PSD data %s" % cha_code); return

	ppsd.plot(cmap=viridis_white_r)
	if outdir:
		figname = Path("%s/%s.%s.png" % (outdir,st[0].stats.station,cha_code))
		if platform.system() == "Windows": figname = PureWindowsPath(figname)		
		ppsd.plot(filename=figname,cmap=viridis_white_r) #will only write if asked to
		print("%s %s done and %s written!" % (st[0].stats.station,cha_code,figname))		
	else:
		print("%s %s done!" % (st[0].stats.station,cha_code))
	return


if __name__ == '__main__':

	"""
	with mp.Pool(processes=3) as pool:
		pool.imap(plot_channel,['Z','N','E'])
		pool.close()
		pool.join()
	"""

	#awkward but the below works for OSX & linux
	workers = []
	for ch in ['N','E','Z']:
		p = mp.Process(target=plot_channel,args=[ch])
		workers.append(p)
		p.start()
	for p in workers:
		p.join()


