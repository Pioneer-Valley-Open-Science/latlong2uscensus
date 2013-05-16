## latlong2uscensus.py
## Given US lat/long return US Census (2010) Block FIPS
## Michael Ash and Don Blair, May 2013, mash@econs.umass.edu
## With help from Ryan Action, David Arbour, and Klara Zwickl
## Creative Commons Attribution 3.0 Unported License

## Read comma-delimited input file with label,latitude,longitude
## Get census block fips for the lat/long from FCC
## http://www.broadbandmap.gov/developer/api/census-api-by-coordinates
## Output label, latitude, longitude, fips

# reference for requests library: http://www.python-requests.org/en/latest/user/quickstart/

# Usage:
# python latlong2uscensus.py [inputFilename] [trialNumber]
# Example:
# python latlong2uscensus.py rseqid_lat_long_sample.txt 3

import json, requests, pprint, sys

timeout=1

url = 'http://www.broadbandmap.gov/broadbandmap/census/block?'

## Read name of input file and trial number from the command line
inputFilename=str(sys.argv[1])
trialNum=int(sys.argv[2])

trialLabel = "%03d" % trialNum

outputFilename="trial_" + trialLabel + "_output.txt"
skippedFilename="trial_" + trialLabel + "_skippedLines.txt"
errorFilename="trial_" + trialLabel + "_errors.txt"

# appending to files -- make sure to change 'trialNum' above for different runs, unless you want to append results to existing files

outFile=open(outputFilename,'a') 
skippedFile=open(skippedFilename,'a')
errorFile=open(errorFilename,'a')

for line in open(inputFilename, 'r'):
    words = line.rstrip().split(',')
    if len(words)==3: 
        label=words[0]
        lat=words[1]
        lon=words[2]  
        params = dict(
            latitude=lat,
            longitude=lon,
            format='json',
            showall='true'
            )
        ## Warning: may time out
        try:
            data = requests.get(url=url, params=params, timeout=timeout)
            binary = data.content
            output_json = json.loads(binary)
            ## Warning: not tested when multiple blocks are returned
            blocks = output_json['Results']['block']
            for b in blocks:
                FIPS = b['FIPS']
                output = label + ", " + lat + ", " + lon + ", " + FIPS + ", " + FIPS[0:2]  + ", " + FIPS[2:5]  + ", " + FIPS[5:11] + ", " + FIPS[11:12]
                # write to screen
                print output
                # write to file
                outFile.write(output+"\n") 
        except requests.ConnectionError as e:
            #output = "\n ConnectionError:" + str(e.strerror) +", for input:" + line
            output = label + ", " + lat + ", " + lon + " -- ConnectionError\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except requests.Timeout as e:
            #output = "\n Timeout error:" + str(e.strerror) + ", for input:" + line
            output = label + ", " + lat + ", " + lon + " -- Timeout error for timeout value of " + str(timeout) + " secs\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except ValueError:
            pprint.pprint(output_json)
            output = label + ", " + lat + ", " + lon + " -- decoding JSON failed" + str(output_json['Results']) + "\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)
        except:
            output = label + ", " + lat + ", " + lon + " -- Unexpected error\n"
            print output
            errorFile.write(output)
            skippedFile.write(line)

outFile.close()
errorFile.close()
skippedFile.close()
