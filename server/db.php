<?php

function db_connect() {
    $db_host="ngtsdb";
    $db_name="ngts_pipe";
    $db_user="www";
    $db_pass="password";

    try {
        $dbh=new PDO("mysql:host=$db_host;dbname=$db_name;charset=utf8", $db_user, $db_pass);
        $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $dbh->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
        $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    } catch (PDOException $e) {
        die("Error connecting to database: ".$e->getMessage());
    }
    return $dbh;
}


?>
