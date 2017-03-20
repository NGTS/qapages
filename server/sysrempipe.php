<?php
require_once "global.php";
require_once "db.php";
require_once "header.html";

/* Pre-amble */
$dbh = db_connect();
$prod_id = $_GET['prod_id'];

list($previous_ids, $next_ids, $previous_stub, $next_stub) = render_job_links($dbh, $prod_id, 'sysrem');
?>

<div class="row">
    <div class="col-xs-12">
        <h2>SysremPipe <?php echo $prod_id ?></h2>
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
    <div class="col-md-4">
        <h3>Previous jobs</h3>
        <ul class="pre-scrollable">
            <?php
            foreach ($previous_ids as $p) {
                println("<li><a href=\"$previous_stub?prod_id=$p\">$p</a></li>");
            }
            ?>
        </ul>
    </div>

    <div class="col-md-4">
        <h3>Next jobs</h3>
        <ul class="pre-scrollable">
            <?php
            foreach ($next_ids as $p) {
                println("<li><a href=\"$next_stub?prod_id=$p\">$p</a></li>");
            }
            ?>
        </ul>
    </div>

    <div class="col-xs-2">
        <?php show_job_perf_stats($prod_id, $dbh); ?>
    </div>

</div>

<div class="row">
    <div class="col-lg-12">
        <?php show_file_locations($prod_id, $dbh); ?>
    </div>
</div>


<?php require_once "footer.html"; ?>
