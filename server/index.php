<?php
require_once 'db.php';

$dbh = db_connect();
$query = "SELECT job_id as prod_id, job_type FROM pipe_job ORDER BY job_id DESC LIMIT 20";
$res = $dbh->query($query);
echo "<table>" . PHP_EOL;
echo "<tr><th>Product id</th><th>Job type</th></tr>" . PHP_EOL;
while ($row = $res->fetch(PDO::FETCH_ASSOC)) {
    echo "<tr>";
    switch ($row[job_type]) {
        case "SysremPipe":
            $url = "/ngtsqa/sysrempipe.php?prod_id=$row[prod_id]";
            break;
        case "MergePipe":
            $url = "/ngtsqa/mergepipe.php?prod_id=$row[prod_id]";
            break;
        case "PhotPipe":
            $url = "/ngtsqa/photpipe.php?prod_id=$row[prod_id]";
            break;
        default:
            break;
    }
    echo "<td><a href=\"$url\">$row[prod_id]</a></td><td>$row[job_type]</td>";
    echo "</tr>" . PHP_EOL;
}
echo "</table>" . PHP_EOL;

?>
