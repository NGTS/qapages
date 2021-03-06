<?php

$prod_id = $_GET['prod_id'];

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

check_valid_prod_id($prod_id, $dbh, 'phot');

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'phot');
?>

<div class="row">
    <div class="col-md-6">
        <h2>PhotPipe <?php echo $prod_id ?></h2>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <?php show_image($prod_id, 'phot', 'qa_astrometry_stats.png'); ?>
    </div>
    <div class="col-md-6">
        <?php show_image($prod_id, 'phot', 'qa_autoguider_stats.png'); ?>
    </div>
</div>

<?php require_once "fragments/job_links.php" ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh); ?>
    </div>
</div>

<?php require_once "footer.html"; ?>
