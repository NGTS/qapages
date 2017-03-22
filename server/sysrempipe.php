<?php
$prod_id = $_GET['prod_id'];

require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();

check_valid_prod_id($prod_id, $dbh, 'sysrem');

list($previous_jobs, $next_jobs) = fetch_linked_jobs($dbh, $prod_id, 'sysrem');
?>

<div class="row">
    <div class="col-md-6">
        <h2>SysremPipe <?php echo $prod_id ?></h2>
    </div>
    <div class="col-md-6">
        <?php render_job_info($dbh, $prod_id, 'sysrem'); ?>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <?php show_image($prod_id, 'sysrem', 'qa_post_sysrem_flux_vs_rms.png'); ?>
    </div>

    <div class="col-md-6">
        <?php show_image($prod_id, 'sysrem', 'qa_sysrem_improvement.png'); ?>
    </div>
</div>

<div class="row">
    <div class="col-lg-12">
    <?php
        $fluxbin_path = "$static_document_root/ngtsqa/SysremPipe/$prod_id/qa_fluxbin.html";
        $contents = file_get_contents($fluxbin_path);
        echo $contents;
    ?>
    </div>
</div>

<?php require_once "fragments/job_links.php"; ?>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh); ?>
    </div>
</div>


<?php require_once "footer.html"; ?>
