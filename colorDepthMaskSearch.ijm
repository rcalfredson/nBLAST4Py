masksDir = "C:\\Users\\Tracking\\nBLAST4Py\\data\\fc_th\\masks\\";

function parseCDMSearchResults(queryImage) {
	results_directory = "C:\\Users\\Tracking\\nBLAST4Py\\data\\fc_th\\";
	queryImageID = split(queryImage, "_");
	cdm_results_path = results_directory + queryImageID[0] + "_cdm_results.txt";
	cdm_results_file = File.open(cdm_results_path);
	print(cdm_results_file, "Hemibrain ID,Score");
	resultsStackPath = "Original_RGB.tif_0.0 %_" + queryImage;
	if (isOpen(resultsStackPath)) {
		for (i = 1; i < 21; i++) {
			selectWindow(resultsStackPath);
			setSlice(i);
		 	scoreAndID = split(getInfo("slice.label"), "_");
		 	print(cdm_results_file, scoreAndID[1] + "," + scoreAndID[0]);
		}
		close(resultsStackPath);
	}
	close(resultsStackPath);
	File.close(cdm_results_file);
	File.rename(cdm_results_path, results_directory + queryImageID[0] +
		"_cdm_results.csv");
	close(queryImage);
}

function runCDMSearch(queryImage) {
	open(masksDir + queryImage);
	searchOptions = "mask=[" + queryImage +
		"  (1) slice] 1.threshold=40 negative=none 2.threshold=50 data=[" +
		"EM_Hemibrain_CDM_JRC2018U_0207_2020_radi2  (43183) slices] " +
		"3.threshold=40 positive=10 pix=13 max=200 duplicated=2 thread=8 " +
		"xy=[0px    ] scoring=% show clear";
	run("Color MIP Mask Search", searchOptions);
}

list = getFileList(masksDir);
for (i = 0; i < list.length; i++) {
	print("Running CDM search for " + list[i]);
	runCDMSearch(list[i]);
	parseCDMSearchResults(list[i]);
}
