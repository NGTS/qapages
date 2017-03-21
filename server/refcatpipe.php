<?php
$prod_id = $_GET['prod_id'];

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

check_valid_prod_id($prod_id, $dbh, 'refcat');

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'refcat');
?>

<div class="row">
    <div class="col-xs-12">
        <h2>RefCatPipe <?php echo $prod_id ?></h2>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <?php // show_image_with_regions($prod_id, 'refcat', 'qa_astrometry_stats.png', 'qa_wcsstats_regions.json'); ?>
    </div>
</div>

<?php require_once "fragments/job_stats.php"; ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh, true); ?>
    </div>
</div>

<?php require_once "footer.html"; ?>
