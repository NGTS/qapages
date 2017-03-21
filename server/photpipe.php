<?php

$prod_id = $_GET['prod_id'];

if ($prod_id === NULL) {
    header('Location: /ngtsqa/404.html');
}

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'phot');
?>

<div class="row">
    <div class="col-xs-12">
        <h2>PhotPipe <?php echo $prod_id ?></h2>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <?php show_image($prod_id, 'phot', 'qa_astrometry_stats.png'); ?>
    </div>
</div>

<?php require_once "fragments/job_stats.php" ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh); ?>
    </div>
</div>

<?php require_once "footer.html"; ?>
