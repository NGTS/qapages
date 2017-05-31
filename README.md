# QA pages for the production pipeline

There are two components to the QA system:

* the code that generates any qa plots and/or data
* the server that hosts it

## Deployment

The database connection info is stored in `server/db.php`, so when
pushing to the webserver, change the connection parameters.

## Development

Currently development is performed using `vagrant` which means we don't
have to install php/apache to the developer machine. To get set up:

```sh
mkdir static
vagrant up
yarn install # or npm install
open http://192.168.33.10/ngtsqa/
```

Alternatively if you have access to an Apache web server and php
installation, you can add your own host config. See the example in
`provisioning/templates/001-ngtsqa.conf`.

## Plot generation

The system goes as such:

* a master per-pipeline script calls into sub-scripts to render the qa
pages for a given pipeline, e.g. the photpipe script calls on
flux-vs-rms, astrometry stats etc.
* the sub-pipeline scripts take the input filenames, and an output
argument.
* the master script calls each QA plot in turn, and defines the output
filenames for the scripts, and then once all are complete, copies the
png files to a directory on the webserver

SCRIPTS MUST BE DUMB AND NOT USE THE DATABASE - these QA scripts may be
run before the photometry job has been registered in the database.
Therefore, the scripts must not use the database at all.

## Server

The server should simply build the image urls and let the webserver
handle serving the static images.

This could be written in PHP, which would be easier for Richard to
manage, and easier to deploy.

## Flow

We take the example of a mergepipe job.

* during the `MergePipe` polaris module, the output root filename is
built up using the following line: 

```perl
my $outroot="P.$$args{'prod id'}_F.$$args{'field'}_C.$$args{'camera id'}_S.$$args{'campaign'}_T.$$args{'output tag'}";
```

We can use this line to define what the filenames are for each of the
input files. For example, the sub-scripts can take the output root as an
argument on the command line, and know how to find the e.g. flux file.

The master script will pass this output root down to the sub-scripts and
they will render QA pngs (with filenames defined by the master script)
to the current directory (`/local` on the compute nodes).

The master script then copies the png files to the specified location on
the webserver. The server then takes over serving these pngs.

vim: ft=markdown:tw=72:nowrap
