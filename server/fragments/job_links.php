<div class="row">
    <div class="col-md-6">
        <h3>Previous jobs</h3>
        <div class="scrollable-table-placeholder">
            <table class="table">
                <thead>
                    <tr><th>Product id</th><th>Job type</th><th>Field</th><th>Tag</th></tr>
                </thead>
                <tbody>
                <?php
                foreach ($previous_jobs as $p) {
                    if ($p->field) {
                        $field = $p->field;
                    } else {
                        $field = '-';
                    }

                    if ($p->tag) {
                        $tag = $p->tag;
                    } else {
                        $tag = '-';
                    }

                    present_job_table_row($p->prod_id, $p->typ, $field, $tag, $p->href);
                }
                ?>
            </table>
        </div>
    </div>

    <div class="col-md-6">
        <h3>Next jobs</h3>
        <div class="scrollable-table-placeholder">
            <table class="table">
                <thead>
                    <tr><th>Product id</th><th>Job type</th><th>Field</th><th>Tag</th></tr>
                </thead>
                <tbody>
                <?php
                foreach ($next_jobs as $p) {
                    if ($p->field) {
                        $field = $p->field;
                    } else {
                        $field = '-';
                    }

                    if ($p->tag) {
                        $tag = $p->tag;
                    } else {
                        $tag = '-';
                    }

                    println("
                        <tr>
                            <td><a href=\"$p->href\">$p->prod_id</a></td>
                            <td>$p->typ</td>
                            <td>$field</td>
                            <td>$tag</td>
                        </tr>
                        ");
                }
                ?>
            </table>
        </div>
    </div>

    <div class="col-md-12">
        <?php show_job_perf_stats($prod_id, $dbh); ?>
    </div>
</div>
