// David Winer
// 2017 - 02 - 25

//Instructions for DIRT assignment
// "unzip DIRT.zip"
// "chmod +x dirt.py"
// "python3 dirt.py <corpus.txt> <text.txt> <min_freq>"

// 2017 - 03 - 29
// pick 5-10 actions (most frequent), and create pseuedo slots. - done
// assemble corpus and clean up to create noun phrases followed by paths.
    // step 1 - split into sentences
    // step 2 - find noun phrases and find heads. and find paths between them
        // given sentence, find all pairwise adjacent noun phrases.
        // put in format used by system.
        // comma to >COMMA etc
// read new corpus and get top similar strings for each action-path