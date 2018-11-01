# argument of script
	# $1=JOB_FOLDER

echo "this is the console output of script.sh"
mkdir "${1}/output/"
cat "${1}"/data/test_data.txt > "${1}"/output/file_output1.txt
cat "${1}"/data/both_in_folder.txt > "${1}"/output/file_output2.txt