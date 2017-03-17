<?php
require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();
$prod_id = $_GET['prod_id'];

/* Rendering the page here */
println("<h1>MergePipe $prod_id</h1>");

show_job_perf_stats($prod_id, $dbh);

/* Main qa section */
show_image($prod_id, 'merge', 'qa_astrometry_stats.png');

render_job_links($dbh, $prod_id, 'merge');

show_file_locations($prod_id, $dbh);

println("<script type=\"text/javascript\" src=\"/ngtsqa/js/dynamic_regions.js\"></script>");

require_once "footer.html";

$dbh->close();
?>
