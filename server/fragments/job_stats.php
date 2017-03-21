<div class="row">
    <div class="col-md-4">
        <h3>Previous jobs</h3>
        <ul class="pre-scrollable">
            <?php
            foreach ($previous_jobs as $p) {
                $pretty_job = htmlspecialchars("$p->typ $p->prod_id");
                println("<li><a href=\"$p->href\">$pretty_job</a></li>"); // $p->prod_id</a></li>");
            }
            ?>
        </ul>
    </div>

    <div class="col-md-4">
        <h3>Next jobs</h3>
        <ul class="pre-scrollable">
            <?php
            foreach ($next_jobs as $p) {
                $pretty_job = htmlspecialchars("$p->typ $p->prod_id");
                println("<li><a href=\"$p->href\">$pretty_job</a></li>"); // $p->prod_id</a></li>");
            }
            ?>
        </ul>
    </div>

    <div class="col-xs-2">
        <?php show_job_perf_stats($prod_id, $dbh); ?>
    </div>
</div>
