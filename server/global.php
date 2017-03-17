<?php

error_reporting(E_ERROR | E_WARNING | E_PARSE | E_NOTICE);

function println($msg) {
    echo $msg . PHP_EOL;
}

function show_file_locations($prod_id, $dbh) {
    $query = "SELECT type, sub_type, CONCAT_WS('/', directory, filename) AS path
    FROM prod_cat
    JOIN prod_dir USING (prod_id)
    WHERE prod_id = :prod_id;";
    $stmt = $dbh->prepare($query);
    $stmt->execute(array('prod_id' => $prod_id));

    println("<h3>File locations</h3>");

    println("<dl class=\"dl-horizontal\">");
    foreach ($stmt as $row) {
        println("<dt>$row[sub_type]<dt><dd>$row[path]</dd>");
    }
    println("</dl>");
}

function show_job_perf_stats($prod_id, $dbh) {
    $query = "SELECT * FROM job_perfstats
    WHERE job_id = :prod_id";
    $stmt = $dbh->prepare($query);
    $stmt->execute(array('prod_id' => $prod_id));

    println("<h3>Job performance</h3>");
    println("<table class=\"table\"><thead><tr><th>Stage</th><th>Time taken</th></thead><tbody>");
    foreach ($stmt as $row) {
        println("<tr><td>$row[command]</td><td>$row[wallclock]</td></tr>");
    }

    $query = "SELECT SUM(wallclock) AS total_time FROM job_perfstats
    WHERE job_id = :prod_id";
    $stmt = $dbh->prepare($query);
    $stmt->execute(array('prod_id' => $prod_id));
    $row = $stmt->fetch();
    $total_time = $row["total_time"];

    println("<tr><td>TOTAL</td><td>$total_time</td></tr>");

    println("</tbody></table>");
}

?>
