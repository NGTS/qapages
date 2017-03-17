<?php
require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();
$prod_id = $_GET['prod_id'];

/* Rendering the page here */
println("<h1>$prod_id</h1>");

show_job_perf_stats($prod_id, $dbh);

show_file_locations($prod_id, $dbh);

require_once "footer.html";

$dbh->close();
?>
