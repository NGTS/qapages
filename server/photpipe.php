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

list($previous_ids, $next_ids, $previous_stub, $next_stub) = render_job_links($dbh, $prod_id, 'merge');
?>

<div class="row">
    <div class="col-xs-12">
        <h2>PhotPipe <?php echo $prod_id ?></h2>
    </div>
</div>

<?php show_image($prod_id, 'phot', 'qa_astrometry_stats.png'); ?>

<?php require_once "fragments/job_stats.php"; ?>

<?php

show_file_locations($prod_id, $dbh);

require_once "footer.html";
?>
