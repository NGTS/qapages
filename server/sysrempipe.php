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

show_image($prod_id, 'sysrem', 'qa_post_sysrem_flux_vs_rms.png');
show_image($prod_id, 'sysrem', 'qa_sysrem_improvement.png');

render_job_links($dbh, $prod_id, 'sysrem');

show_file_locations($prod_id, $dbh);

require_once "footer.html";
?>
