<?php
//  Make sure the user is posting
if ( $_SERVER['REQUEST_METHOD'] === 'POST' ){
    //Read the input from stdin into variable $postText
    $postText = trim(file_get_contents('php://input'));
}

// Generate time stamp for the new file
$datetime=date('ymdHis');

// Create an xml file, and write the contents of $postText to it
$xmlfile = "myfile" . $datetime . ".xml";
$FileHandle = fopen($xmlfile, 'w') or die("can't open file");
fwrite($FileHandle, $postText);
fclose($FileHandle); 
?>