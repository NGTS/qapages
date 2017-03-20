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

