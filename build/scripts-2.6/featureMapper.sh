
# script to map features together. 

# /sw/local/lib:/usr/local/Trolltech/Qt-4.7.1/lib:$LD_LIBRARY_PATH is not standard in the library path on the cluster that I used (Ningal) and therefore included here. 
# probably other users don't need it, but no harm keeping it. If you get this error: 
# ./FeatureFinderRaw: error while loading shared libraries: libOpenMS.so: cannot open shared object file: No such file or directory
# make the export point to the correct path (note taht this is an old version, you might have Qt-4.7.2 or later, and it could be in a different location)
export LD_LIBRARY_PATH=/sw/local/lib:/usr/local/Trolltech/Qt-4.7.1/lib:$LD_LIBRARY_PATH;


#### The default values. These are overwritten if an option is given to the commandline ####
# Path were MapAlignerPoseClustering is located.
featureMapperDefault=/sw/local/bin/
# Path to a folder where to write the MapAlignerPoseClustering config file out to
#featureMapperConfigDefault=mapperConfig/
# Path to a folder where to write the .trafoXML output file t
trafoFolderDefault=trafoXML/
# Path to a folder where to write the .mapped.featureXML output file to
mappedFolderDefault=mappedFeatureXML/
# number of threads to use
threadsDefault=20
####																					####


# bools/flags to see if values are set
f=0
c=0
o=0
m=0
# getops loops over the options f, h, a, i. An : after an option means that it needs an argument (so -f /homes/ is ok,  just -f gives an error)
while getopts "hf:" opt; do
	case $opt in
      h) 
      echo
      echo "Usage: ./featureMapper [options] <featureXML file 1> <featureXML file 2"
      echo "Options:"
      echo "  -f <path>		Path were MapAlignerPoseClustering is located. Default: "$featureMapperDefault
#	  echo "  -c <path>		Path to a folder where to write the MapAlignerPoseClustering config file out to. Default: "$featureMapperConfigDefault
 	  echo "  -o <path>		Path to a folder where to write the .trafoXML output file to. Default: "$trafoFolderDefault
 	  echo "  -m <path		Path to a folder where to write the .mapped.featureXML output file to. Default: "$mappedFolderDefault
 	  echo "  -h			Print this message and exit."
      exit 0
      ;;
    f)
      featureMapper=$OPTARG
      f=1
      ;;
#    c)
#      featureMapperConfig=$OPTARG
#   	  c=1
#      ;;
    o)
      trafoFolder=$OPTARG
      o=1
      ;;
    m)
      mappedFolder=$OPTARG
      m=1
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
# multiple options are given
if [[ $f -eq 0 ]]; then
  featureMapper=$featureMapperDefault
fi
#if [[ $c -eq 0 ]]; then
#  featureMapperConfig=$featureMapperConfigDefault
#fi
if [[ $o -eq 0 ]]; then
  trafoFolder=$trafoFolderDefault
fi
if [[ $m -eq 0 ]]; then
  mappedFolder=$mappedFolderDefault
fi
if [[ $t -eq 0 ]]; then
  threads=$threadsDefault
fi

# ${@: -1} is the last argument, ${@: -2} is second last argument
file1="${@:(-2):1}"
file2="${@: -1}"

# check if they are files
if ! [[ ( -f $file1 ) ]]; then
	echo "file '"$file1"' does not exist"
	./featureFinder.sh -h
	exit 1
fi

# check if they are not the same
if [[ $file1 ==  $file2 ]];then
	echo $file1" and "$file2 " are the same. Need to be two different featureXML files"
	./featureFinder.sh -h
	exit 1
fi
if ! [[ ( -f $file2 ) ]]; then
	echo "file '"$file2"' does not exist"
	./featureFinder.sh -h
	exit 1
fi

# if the folder does not exist, make it
mkdir -pv $trafoFolder
mkdir -pv $mappedFolder
# get the real link to the config and output folder
trafoFolder=`readlink -f $trafoFolder` 
mappedFolder=`readlink -f $mappedFolder` 

# get filename out of the path
filename1=$(basename "$file1")
filename2=$(basename "$file2")
# extension is lowered so that if someone called their file .mzml or .Mzml instead of .mzML it will still remove the extension correctly
extension1=$(echo ${filename1##*.} | tr '[A-Z]' '[a-z]') 
extension2=$(echo ${filename2##*.} | tr '[A-Z]' '[a-z]') 
# name is the name of the file without the extension. So /homes/example.mzML will give example
name1=${filename1%.*}
name2=${filename2%.*}

if [[ ! $extension1 == "featurexml" ]]; then
  echo $file1" is not a featureXML file"
  ./featureMapper.sh -h
  exit 1
fi
if [[ ! $extension2 == "featurexml" ]]; then
  echo $file2" is not a featureXML file"
  ./featureMapper.sh -h
  exit 1
fi

# the MapAlignerClustering calls. Same as with name and mapName and 2. this should be changed if you want to do a lot of jobs. 
(cd $featureMapper && ./MapAlignerPoseClustering -in $file1 $file2 -out $mappedFolder$$name1".mapped.featureXML" $mappedFolder$name2".mapped.featureXML" -trafo_out $trafoFolder$name1.trafoXML $trafoFolder$name2".trafoXML" -threads $threads)
