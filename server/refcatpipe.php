<?php
$prod_id = $_GET['prod_id'];

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

check_valid_prod_id($prod_id, $dbh, 'refcat');

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'refcat');
$job_info = fetch_job_info($dbh, $prod_id, 'refcat');
?>

<div class="row">
    <div class="col-md-6">
        <h2>RefCatPipe <?php echo $prod_id ?></h2>
    </div>

    <div class="col-md-6">
        <?php
            /* TODO: remove the double call to the database here,
            /* as render_job_info calls fetch_job_info
            */
            render_job_info($dbh, $prod_id, 'refcat');
        ?>
    </div>
</div>

<?php
?>

<div class="row">
    <div class="col-md-6">
        <?php show_image($prod_id, 'refcat', 'AG_REFERENCE_IMAGE_NG0522-2518_802_5006373_hists.png'); ?>
    </div>
</div>

<?php require_once "fragments/job_links.php"; ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh, true); ?>
    </div>
</div>

<?php require_once "footer.html"; ?>
