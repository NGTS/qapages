<?php
$prod_id = $_GET['prod_id'];

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

check_valid_prod_id($prod_id, $dbh, 'merge');

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'merge');
?>

<div class="row">
    <div class="col-md-6">
        <h2>MergePipe <?php echo $prod_id ?></h2>
    </div>

    <div class="col-md-6">
        <?php render_job_info($dbh, $prod_id, 'merge'); ?>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <?php show_image_with_regions($prod_id, 'merge', 'qa_astrometry_stats.png', 'qa_wcsstats_regions.json'); ?>
    </div>
    <div class="col-md-6">
        <?php show_image_with_regions($prod_id, 'merge', 'qa_autoguider_stats.png', 'qa_autoguider_regions.json'); ?>
    </div>
</div>
<div class="row">
    <div class="col-md-6">
        <?php show_image_with_regions($prod_id, 'merge', 'qa_meta_stats.png', 'qa_metastats_regions.json'); ?>
    </div>
</div>

<?php require_once "fragments/job_links.php"; ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh); ?>
    </div>
</div>

<script type="text/javascript" src="/ngtsqa/js/dynamic_regions.js"></script>

<?php require_once "footer.html"; ?>
