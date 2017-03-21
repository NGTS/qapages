<?php

error_reporting(E_ERROR | E_WARNING | E_PARSE | E_NOTICE);

$document_root = "/var/www";
$qa_document_root = "$document_root/ngtsqa";

function println($msg) {
    echo $msg . PHP_EOL;
}

function debug_to_console($data) {
    $output = $data;
    if (is_array($output)) {
        $output = implode(',', $output);
    }
    echo "<script>console.log('PHP DEBUG: " . $output . "' );</script>";
}

function query($dbh, $query, $args) {
    $stmt = $dbh->prepare($query);
    $stmt->execute($args);
    return $stmt;
}

function check_valid_prod_id($prod_id, $dbh, $job_type) {
    if ($prod_id == NULL) {
        header('Location: /ngtsqa/errors/no_prod_id.html');
        exit;
    }

    switch ($job_type) {
        case 'phot':
            $query = "SELECT COUNT(*) FROM photpipe_prod WHERE prod_id = :prod_id";
            break;
        case 'merge':
            $query = "SELECT COUNT(*) FROM mergepipe_prod WHERE prod_id = :prod_id";
            break;
        case 'sysrem':
            $query = "SELECT COUNT(*) FROM sysrempipe_prod WHERE prod_id = :prod_id";
            break;
        case 'refcat':
            $query = "SELECT COUNT(*) FROM refcatpipe_prod WHERE prod_id = :prod_id";
            break;
        default:
            header('Location: /ngtsqa/404.html');
            exit;
            break;
    }

    $stmt = query($dbh, $query, array('prod_id' => $prod_id));
    $nrows = $stmt->fetch()[0];

    if ($nrows != 1) {
        header("Location: /ngtsqa/errors/prod_id_not_found.php?prod_id=$prod_id");
        exit;
    }
}

function show_file_locations($prod_id, $dbh, $refcat = false) {
    $query = "SELECT type, sub_type, CONCAT_WS('/', directory, filename) AS path
    FROM prod_cat
    JOIN prod_dir USING (prod_id)
    WHERE prod_id = :prod_id
    ORDER BY sub_type ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    println("<h3>File locations</h3>");

    if ($refcat) {
        /* Have to special case the refcatpipe output, as the file naming system
         * is different */
        println("<dl class=\"pre-scrollable dl-horizontal\">");
        foreach ($stmt as $row) {
            $row_type = "$row[type]$row[sub_type]";
            println("<dt>$row_type<dt><dd><pre><code class=\"bash\">$row[path]</code></pre></dd>");
        }
        println("</dl>");
    } else {
        println("<dl class=\"pre-scrollable dl-horizontal\">");
        foreach ($stmt as $row) {
            println("<dt>$row[sub_type]<dt><dd><pre><code class=\"bash\">$row[path]</code></pre></dd>");
        }
        println("</dl>");
    }
}

function show_job_perf_stats($prod_id, $dbh) {
    $query = "SELECT * FROM job_perfstats
    WHERE job_id = :prod_id
    ORDER BY wallclock DESC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    println("<h3>Job perf</h3>");
    println("<table class=\"table\">
    <thead>
    <tr>
        <th>Stage</th>
        <th>Time taken (s)</th>
        <th>Max memory (MB)</th>
    </thead>
    <tbody>");
    foreach ($stmt as $row) {
        $maxrss_mb = number_format($row["maxrss"] / 1024, 2);
        println("<tr>
            <td>$row[command]</td>
            <td>$row[wallclock]</td>
            <td>$maxrss_mb</td>
            </tr>");
    }

    $query = "SELECT SUM(wallclock) AS total_time FROM job_perfstats
    WHERE job_id = :prod_id";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));
    $row = $stmt->fetch();
    $total_time = $row["total_time"];

    println("<tr><td>TOTAL</td><td>$total_time</td></tr>");

    println("</tbody></table>");
}

class PipelineJob {
    public $prod_id;
    public $href;
    public $typ;
    public $tag = NULL;

    function __construct($prod_id, $typ) {
        $this->prod_id = intval($prod_id);

        switch ($typ) {
            case 'sysrem':
                $this->href = "/ngtsqa/sysrempipe.php?prod_id=$this->prod_id";
                $this->typ = 'SysremPipe';
                break;
            case 'merge':
                $this->href = "/ngtsqa/mergepipe.php?prod_id=$this->prod_id";
                $this->typ = "MergePipe";
                break;
            case 'bls':
                $this->href = "/ngtsqa/blspipe.php?prod_id=$this->prod_id";
                $this->typ = "BLSPipe";
                break;
            case 'phot':
                $this->href = "/ngtsqa/photpipe.php?prod_id=$this->prod_id";
                $this->typ = "PhotPipe";
                break;
            case 'refcat':
                $this->href = "/ngtsqa/refcatpipe.php?prod_id=$this->prod_id";
                $this->typ = "RefCatPipe";
                break;
            case 'confpipe':
                $this->href = "/ngtsqa/confpipe.php?prod_id=$this->prod_id";
                $this->typ = "ConfPipe";
                break;
            case 'biaspipe':
                $this->href = "/ngtsqa/biaspipe.php?prod_id=$this->prod_id";
                $this->typ = "BiasPipe";
                break;
            case 'darkpipe':
                $this->href = "/ngtsqa/darkpipe.php?prod_id=$this->prod_id";
                $this->typ = "DarkPipe";
                break;
            case 'flatpipe':
                $this->href = "/ngtsqa/flatpipe.php?prod_id=$this->prod_id";
                $this->typ = "FlatPipe";
                break;
            default:
                println("UNIMPLEMENTED JOB CLASS: $typ");
                $this->href = "UNKNOWN";
                break;
        }
    }
}

function fetch_sysrem_previous_jobs($dbh, $prod_id) {
    $prev_jobs = array();
    $query = "SELECT raw_prod_id
        FROM sysrempipe_prod AS S
        JOIN mergepipe_prod AS M ON M.prod_id = S.raw_prod_id
        WHERE S.prod_id = :prod_id
        ORDER BY raw_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["raw_prod_id"], 'merge');
        array_push($prev_jobs, $job);
    }
    return $prev_jobs;
}

function fetch_sysrem_next_jobs($dbh, $prod_id) {
    $next_jobs = array();
    $query = "SELECT prod_id
        FROM blspipe_prod
        WHERE phot_prod_id = :prod_id
        ORDER BY prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["prod_id"], 'bls');
        array_push($next_jobs, $job);
    }
    return $next_jobs;
}

function fetch_merge_previous_jobs($dbh, $prod_id) {
    $query = "SELECT sub_prod_id
    FROM mergepipe_sub_prod
    WHERE prod_id = :prod_id
    ORDER BY sub_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        $job = new PipelineJob($row["sub_prod_id"], 'phot');
        array_push($out, $job);
    }
    return $out;
}

function fetch_merge_next_jobs($dbh, $prod_id) {
    $query = "SELECT prod_id
    FROM sysrempipe_prod
    WHERE raw_prod_id = :prod_id
    ORDER BY prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        $job = new PipelineJob($row["prod_id"], 'sysrem');
        array_push($out, $job);
    }
    return $out;
}

function fetch_phot_previous_jobs($dbh, $prod_id) {
    /* Phot jobs have two kinds of previous jobs: refcatpipe and calpipe. The
    calpipe jobs are split into flatpipe_prod, darkpipe_prod, biaspipe_prod and confmap_prod
    */
    $out = array();

    /* TODO: Fetch the calpipe jobs */
    /* confmap */
    $query = "SELECT confmap_prod_id
    FROM photpipe_prod
    WHERE prod_id = :prod_id
    ORDER BY confmap_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["confmap_prod_id"], 'confpipe');
        array_push($out, $job);
    }

    /* bias */
    $query = "SELECT bias_prod_id
    FROM photpipe_prod
    WHERE prod_id = :prod_id
    ORDER BY bias_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["bias_prod_id"], 'biaspipe');
        array_push($out, $job);
    }

    /* dark */
    $query = "SELECT dark_prod_id
    FROM photpipe_prod
    WHERE prod_id = :prod_id
    ORDER BY dark_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["dark_prod_id"], 'darkpipe');
        array_push($out, $job);
    }

    /* flat */
    $query = "SELECT flat_prod_id
    FROM photpipe_prod
    WHERE prod_id = :prod_id
    ORDER BY flat_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["flat_prod_id"], 'flatpipe');
        array_push($out, $job);
    }


    /* Fetch the refcatpipe jobs */
    $query = "SELECT ref_cat_prod_id
    FROM photpipe_prod
    WHERE prod_id = :prod_id
    ORDER BY ref_cat_prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    foreach ($stmt as $row) {
        $job = new PipelineJob($row["ref_cat_prod_id"], 'refcat');
        array_push($out, $job);
    }

    return $out;
}

function fetch_phot_next_jobs($dbh, $prod_id) {
    $query = "SELECT prod_id
    FROM mergepipe_sub_prod
    WHERE sub_prod_id = :prod_id
    ORDER BY prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        $job = new PipelineJob($row["prod_id"], 'merge');
        array_push($out, $job);
    }
    return $out;
}

function fetch_refcat_next_jobs($dbh, $prod_id) {
    $query = "SELECT prod_id
        FROM photpipe_prod
        WHERE ref_cat_prod_id = :prod_id
        ORDER BY prod_id ASC";
    $stmt = query($dbh, $query, array('prod_id' => $prod_id));

    $out = array();
    foreach ($stmt as $row) {
        $job = new PipelineJob($row["prod_id"], 'phot');
        array_push($out, $job);
    }
    return $out;
}

function fetch_linked_jobs($dbh, $prod_id, $job_type) {
    switch ($job_type) {
        case 'sysrem':
            $prev_jobs = fetch_sysrem_previous_jobs($dbh, $prod_id);
            $next_jobs = fetch_sysrem_next_jobs($dbh, $prod_id);
            break;
        case 'merge':
            $prev_jobs = fetch_merge_previous_jobs($dbh, $prod_id);
            $next_jobs = fetch_merge_next_jobs($dbh, $prod_id);
            break;
        case 'phot':
            $prev_jobs = fetch_phot_previous_jobs($dbh, $prod_id);
            $next_jobs = fetch_phot_next_jobs($dbh, $prod_id);
            break;
        case 'refcat':
            $prev_jobs = array();
            $next_jobs = fetch_refcat_next_jobs($dbh, $prod_id);
            break;
        default:
            println("UNIMPLEMENTED JOB TYPE: $job_type");
            $prev_jobs = array();
            $next_jobs = array();
            break;
    }

    usort($prev_jobs, 'sort_by_prod_id');
    usort($next_jobs, 'sort_by_prod_id');

    return array($prev_jobs, $next_jobs);
}

/* Function to sort two PipelineJob instances by prod_id */
function sort_by_prod_id($a, $b) {
    return $a->prod_id - $b->prod_id;
}

function static_path($prod_id, $job_type, $filename) {
    switch ($job_type) {
        case 'sysrem':
            return "/ngtsqa/joboutput/SysremPipe/$prod_id/$filename";
            break;
        case 'merge':
            return "/ngtsqa/joboutput/MergePipe/$prod_id/$filename";
            break;
        case 'phot':
            return "/ngtsqa/joboutput/PhotPipe/$prod_id/$filename";
            break;
        default:
            println("UNIMPLEMENTED SHOW IMAGE: $job_type");
            return NULL;
            break;
    }
}

function show_image($prod_id, $job_type, $filename) {
    $url = static_path($prod_id, $job_type, $filename);

    println("<img class=\"qaplot\" src=\"$url\"></img>");
}

function current_timestamp() {
    return date_timestamp_get(date_create());
}

function show_image_with_regions($prod_id, $job_type, $filename, $region_filename) {
    $url = static_path($prod_id, $job_type, $filename);

    /* Add the current timestamp to prevent caching */
    $region_url = static_path($prod_id, $job_type, $region_filename) . "?_t=" . current_timestamp();

    println("<img class=\"qaplot region-plot\" data-region-definition=\"$region_url\" src=\"$url\"></img>");
}

?>
