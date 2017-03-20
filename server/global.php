<?php

error_reporting(E_ERROR | E_WARNING | E_PARSE | E_NOTICE);

function println($msg) {
    echo $msg . PHP_EOL;
}

function query($dbh, $query, $args) {
    $stmt = $dbh->prepare($query);
    $stmt->execute($args);
    return $stmt;
}

function show_file_locations($prod_id, $dbh) {
    $query = "SELECT type, sub_type, CONCAT_WS('/', directory, filename) AS path
    FROM prod_cat
    JOIN prod_dir USING (prod_id)
    WHERE prod_id = :prod_id;";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    println("<h3>File locations</h3>");

    println("<dl class=\"pre-scrollable dl-horizontal\">");
    foreach ($stmt as $row) {
        println("<dt>$row[sub_type]<dt><dd><pre><code class=\"bash\">$row[path]</code></pre></dd>");
    }
    println("</dl>");
}

function show_job_perf_stats($prod_id, $dbh) {
    $query = "SELECT * FROM job_perfstats
    WHERE job_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    println("<h3>Job perf</h3>");
    println("<table class=\"table\"><thead><tr><th>Stage</th><th>Time taken</th></thead><tbody>");
    foreach ($stmt as $row) {
        println("<tr><td>$row[command]</td><td>$row[wallclock]</td></tr>");
    }

    $query = "SELECT SUM(wallclock) AS total_time FROM job_perfstats
    WHERE job_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));
    $row = $stmt->fetch();
    $total_time = $row["total_time"];

    println("<tr><td>TOTAL</td><td>$total_time</td></tr>");

    println("</tbody></table>");
}

function fetch_previous_prod_ids($dbh, $prod_id, $job_type) {
    switch ($job_type) {
        case "sysrem":
            return sysrem_previous_prod_ids($dbh, $prod_id);
            break;
        case "merge":
            return merge_previous_prod_ids($dbh, $prod_id);
            break;
        default:
            println("UNIMPLEMENTED PREVIOUS JOB: $job_type");
            break;
    }
}

function fetch_next_prod_ids($dbh, $prod_id, $job_type) {
    switch ($job_type) {
        case "sysrem":
            return sysrem_next_prod_ids($dbh, $prod_id);
            break;
        case "merge":
            return merge_next_prod_ids($dbh, $prod_id);
            break;
        case "phot":
            return phot_next_prod_ids($dbh, $prod_id);
            break;
        default:
            println("UNIMPLEMENTED PREVIOUS JOB: $job_type");
            break;
    }
}

function sysrem_previous_prod_ids($dbh, $prod_id) {
    $query = "SELECT raw_prod_id
    FROM sysrempipe_prod
    WHERE prod_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        array_push($out, $row["raw_prod_id"]);
    }
    return $out;
}

function sysrem_next_prod_ids($dbh, $prod_id) {
    $query = "SELECT prod_id
    FROM blspipe_prod
    WHERE phot_prod_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        array_push($out, $row["prod_id"]);
    }
    return $out;
}

function merge_previous_prod_ids($dbh, $prod_id) {
    $query = "SELECT sub_prod_id
    FROM mergepipe_sub_prod
    WHERE prod_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        array_push($out, $row["sub_prod_id"]);
    }
    return $out;
}

function merge_next_prod_ids($dbh, $prod_id) {
    $query = "SELECT prod_id
    FROM sysrempipe_prod
    WHERE raw_prod_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        array_push($out, $row["prod_id"]);
    }
    return $out;
}

function phot_next_prod_ids($dbh, $prod_id) {
    $query = "SELECT prod_id
    FROM mergepipe_sub_prod
    WHERE sub_prod_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        array_push($out, $row["prod_id"]);
    }
    return $out;
}

function render_job_links($dbh, $prod_id, $job_type) {
    $previous_prod_ids = fetch_previous_prod_ids($dbh, $prod_id, $job_type);
    $next_prod_ids = fetch_next_prod_ids($dbh, $prod_id, $job_type);

    switch ($job_type) {
        case 'sysrem':
            $previous_url_stub = "/ngtsqa/mergepipe.php";
            $next_url_stub = "/ngtsqa/blspipe.php";
            $previous_label = "Merge jobs";
            $next_label = "BLS jobs";
            break;
        case 'merge':
            $previous_url_stub = "/ngtsqa/photpipe.php";
            $next_url_stub = "/ngtsqa/sysrempipe.php";
            $previous_label = "Phot jobs";
            $next_label = "Sysrem jobs";
            break;
        case 'phot':
            $previous_url_stub = "/ngtsqa/photpipe.php";
            $next_url_stub = "/ngtsqa/mergepipe.php";
            $previous_label = "";
            $next_label = "Merge jobs";
            break;
        default:
            println("UNIMPLEMENTED JOB LINKS: $job_type");
            break;
    }

    return array($previous_prod_ids, $next_prod_ids, $previous_url_stub, $next_url_stub);
}

function show_image($prod_id, $job_type, $filename, $elem_id = NULL) {
    switch ($job_type) {
        case 'sysrem':
            $url = "/ngtsqa/joboutput/SysremPipe/$prod_id/$filename";
            break;
        case 'merge':
            $url = "/ngtsqa/joboutput/MergePipe/$prod_id/$filename";
            break;
        case 'phot':
            $url = "/ngtsqa/joboutput/PhotPipe/$prod_id/$filename";
            break;
        default:
            println("UNIMPLEMENTED SHOW IMAGE: $job_type");
            break;
    }

    if ($elem_id === NULL) {
        println("<img class=\"qaplot\" src=\"$url\"></img>");
    } else {
        println("<img class=\"qaplot\" id=\"$elem_id\" src=\"$url\"></img>");
    }
}

?>
