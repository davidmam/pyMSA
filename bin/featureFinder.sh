#!/bin/sh

# script to run FeatureFinding, both for one file as well as multiple files. When running multiple files, give the folder in which all the files
# you want to run are located
# If you want to use this, change the output/input folder names and change the names used for ./MapAlignerPoseClustering.

# /sw/local/lib:/usr/local/Trolltech/Qt-4.7.1/lib:$LD_LIBRARY_PATH is not standard in the library path on the cluster that I used (Ningal) and therefore included here. 
# probably other users don't need it, but no harm keeping it. If you get this error: 
# ./FeatureFinderRaw: error while loading shared libraries: libOpenMS.so: cannot open shared object file: No such file or directory
# make the export point to the correct path (note taht this is an old version, you might have Qt-4.7.2 or later, and it could be in a different location)
export LD_LIBRARY_PATH=/sw/local/lib:/usr/local/Trolltech/Qt-4.7.1/lib:$LD_LIBRARY_PATH;

#### The default values. These are overwritten if an option is given to the commandline ####
# Path were FeatureFinderRaw is located."
featureFinderDefault=/sw/local/bin/
#Intensity to run the FeatureFinderRaw at. 
intensityDefault=2500
# folder to save the config file
configFolderDefault=featureFinderConfig/
# folder to write the output to
outFolderDefault=featureXML/
# amount of threads to run FeatureFinderRaw with
threadsDefault=20
####																				 	####


# bools/flags to see if values are set
a=0
i=0
c=0
o=0
f=0
t=0
# getops loops over the options f, h, a, i. An : after an option means that it needs an argument (so -f /homes/ is ok,  just -f gives an error)
while getopts "hf:i:a:c:o:" opt; do
	case $opt in
      h) 
      echo
      echo "Usage: ./featureFinder [options] <mzML file or folder containing mzML files>"
      echo "Options:"
      echo "  -f <path>				Path were FeatureFinderRaw is located. Default: "$featureFinderDefault
      echo "  -i <intensity>			Intensity cut-off to run the FeatureFinderRaw at. Can't be set with -a. Default: "$intensityDefault
      echo "  -a <start:stop:step>			Will run FeatureFinderRaw with each intensity between start-stop with steps of step. Can't be set with -i"
 	  echo "  -c <path>				Path to a folder where to write the FeatureFinderRaw config file out to. Default: "$configFolderDefault
 	  echo "  -o <path>				Path to a folder where to write the output .featureXML file to. Default: "$outFolderDefault
 	  echo "  -t <threads>				Number of threads to run FeatureFinderRaw with. Default: "$threadsDefault
 	  echo "  -h					Print this message and exit."
      exit 0
      ;;
    f)
	  # Path were FeatureFinderRaw is located
      featureFinder=$OPTARG
      f=1
      ;;
    i)
      if [[ $a == 1 ]]; then
      	echo "-i can't be set in combination with -a"
      	exit 1
      fi
      intensity=$OPTARG
	  i=1
      ;;
    a)
      if [[ $i == 1 ]]; then
      	echo "-i can't be set in combination with -a"
      	exit 1
      fi
      
      # change the inter-field separator to :, split the -a $OPTARG and change it back to the old value
      oldIFS=$IFS
      IFS=":"
      count=0
      for value in $OPTARG; do
      	count=`expr $count + 1`
  		case $count in
  			1)
  			  start=$value
  			  ;;
  	        2)
  	          stop=$value
  	          ;;
  	        3)
  	          step=$value
  		esac
      done
      IFS=$oldIFS
      
      # test if right amount of arguments was given to -a
      if [[ $count -lt 3 ]]; then
      	echo "Not enough values given to -a"
      	./featureFinder.sh -h
      	exit 1
      elif [[ $count -gt 3 ]]; then
         echo "Too many values given to -a"
         ./featureFinder.sh -h
         exit 1
      fi 
      a=1
      ;;
    c)
	  # Path to a folder where to write the FeatureFinderRaw config file out to.
      configFolder=$OPTARG
	  c=1
      ;;
    o)
	  # Path to a folder where to write the output .featureXML file to.
      outFolder=$OPTARG
      o=1
      ;;
    t)
      # number of threads to use
      threads=$OPTARG
      t=1
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ./featureFinder.sh -h
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# if a value isn't set using the getopts, set it to default value. Is done this way so that the Default: shown in usage (-h) doesn't change when
# multiple options are given, like ./featureFinder -o test/ -h test.mzml
if [[ $f -eq 0 ]]; then
  featureFinder=$featureFinderDefault
fi
if [[ $i -eq 0 ]]; then
  intensity=$intensity
fi
if [[ $c -eq 0 ]]; then
  configFolder=$configFolderDefault
fi
if [[ $o -eq 0 ]]; then
  outFolder=$outFolderDefault
fi
if [[ $t -eq 0 ]]; then
  threads=$threadsDefault
fi

# $BASH_ARGV is the last positional argument.  
mzmlFiles=$BASH_ARGV

# check if mzmlFiles is empty
if [[ -z $mzmlFiles ]]; then
	echo "featureFinder needs a location for the mzML file or a folder that contains mzML files"
	./featureFinder.sh -h
	exit 1
fi

#Check if it is a folder or file.
if ! [[ ( -d $mzmlFiles || -f $mzmlFiles ) ]]; then
	echo "file or folder '"$mzmlFiles"' does not exist"
	./featureFinder.sh -h
	exit 1
else
  if [[ -d $mzmlFiles ]]; then
  	mzmlFiles=$mzmlFiles""*
  fi
fi


# because there is a loop with start stop and step, if -i is given or -a and -i is not given change the intensity into a start, step and stop
if [[ ( $i == 1 ) || ( $i == 0 && $a == 0 ) ]]; then
	start=$intensity
	stop=$intensity
	step=1
fi

# if the config and featuxml output directories don't exist, this command creates them.
mkdir -pv $configFolder
mkdir -pv $outFolder
# get the real link to the config and output folder
configFolder=`readlink -f $configFolder` 
outFolder=`readlink -f $outFolder` 

# if there is one mzml file given, it will only create one file
for infile in $mzmlFiles
do
  filename=$(basename "$infile")
  # extension is lowered so that if someone called their file .mzml or .Mzml instead of .mzML it will still remove the extension correctly
  extension=$(echo ${filename##*.} | tr '[A-Z]' '[a-z]') 
  # name is the name of the file without the extension. So /homes/example.mzML will give example
  name=${filename%.*}
  # if the file extension is not mzml does not end with mzml, go to next file
  	if [[ ! $extension == "mzml" ]]; then
  		continue
	fi
  
  # with one intensity (e.g. -i 2500) this is set to 2500-1-2500. With multiple intensity (e.g. -a 1000:4000:500) this is set to 1000 500 4000
  for intensity in $(seq $start $step $stop)
  do
    outfile=$outFolder"/"$name"__i_"$intensity".featureXML";

    # if the .featureXML out file or the .featureXML.tmp file already exists, go to the next file, else make the tmp file and proceed
    # this is so that if there are multiple different jobs running they don't start making the same file, as that takes a lot of time
    if [[ -f $outfile ]]; then
      echo $outfile" already done, checking next file"
      continue
    elif [[ -f $outfile".tmp" ]]; then
      echo $outfile" busy in a different call, checking next file"
      continue
    else
      TMPFILE=$outfile".tmp"
      echo "busy making "$outfile > $TMPFILE
    fi
	
	# if the process is killed, remove the tmp file
    for sig in INT TERM EXIT; do
      trap "rm -f \"\$TMPFILE\"; [[ $sig == EXIT ]] || kill -$sig $$" $sig
    done
    
	echo "finding features in "$infile"with intensity "$intensity		
	config_out=$configFolder"/FFR_"$intensity"_"$name".ini";

	# names of the files to map too. Just as with $name, this has to be changed once you want to do a lot of jobs at the same time. For now it is faster to change by hand

	# cd into the location where FeatureFinderRaw is located and call FeatureFinderRaw to write the default config file
	(cd $featureFinder && ./FeatureFinderRaw -write_ini $config_out)

	# replace the default values for our own values. Need to write to .tmp file and change it back to normal because sed blanks out piping output to the same file.
	# change -in
	cat $config_out | sed -e 's#name="in" value=""#name="in" value="'$infile'"#' > $config_out".tmp"
	mv $config_out".tmp" "${config_out%.tmp}";
	# change -out
    cat $config_out| sed -e 's#name="out" value=""#name="out" value="'$outfile'"#' > $config_out".tmp"
  	mv $config_out".tmp" "${config_out%.tmp}";
    # change threads
    cat $config_out | sed -e 's#name="threads" value="1"#name="threads" value="'$threads'"#' > $config_out".tmp"
    mv $config_out".tmp" "${config_out%.tmp}";
	# change intensity
	cat $config_out | sed -e 's#name="intensity_cutoff" value="10000"#name="intensity_cutoff" value="'$intensity'"#' > $config_out".tmp"
	mv $config_out".tmp" "${config_out%.tmp}";

	# cds to the location of featureFinder and runs FeatureFinderRaw
	(cd $featureFinder && ./FeatureFinderRaw -ini $config_out)

	if [[ -f $outfile ]]; then
		rm -f $TMPFILE
	fi
  done
done

