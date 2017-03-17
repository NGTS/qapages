from contextlib import contextmanager
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
from matplotlib.figure import Figure
import pymysql
from pymysql.cursors import DictCursor

__all__ = [
    'figure_context',
    'find_file',
    'find_existing_job_files',
    'find_previous_job_files',
    'get_url',
    'update_manifest',
]

# Customise the figures
# plt.style.use('seaborn')
mpl.rc('figure', figsize=(6, 5), dpi=100)
mpl.rc('axes', grid=True)
mpl.rc('lines', markersize=3, markeredgewidth=0.0)
mpl.rc('text', usetex=False)
mpl.rc('font', family='sans-serif')


@contextmanager
def figure_context(filename, *args, **kwargs):
    ''' Create a saveable figure context, simplifying figure setup.

    Ensures `tight_layout` has been called on the figure, and
    automatically renders the plot to disk.
    '''
    fig = Figure(*args, **kwargs)
    canvas = Canvas(fig)
    yield fig
    fig.tight_layout()
    canvas.print_figure(filename)


def find_file(root, file_type):
    ''' Given a file root and measurement type, return the path (without
    directory) of the corresponding file.

    The code also checks that the file exists, and prints an error
    message if not.
    '''
    file_type = file_type.lower()
    stub = {
        'imagelist': '_IMAGELIST.fits',
        'catalogue': '_CATALOGUE.fits',
        'sysrem_catalogue': '_SYSREM_CATALOGUE.fits',
    }[file_type]
    path = root + stub
    assert os.path.isfile(path), 'cannot find file specified: {0}'.format(path)
    return path


def find_existing_job_files(prod_id):
    ''' Given the product id of a previous job - one that has already
    been run through the pipeline, and _must_ exist!!! - return the
    paths of the files in the prodstore.
    '''
    with connect_to_database() as cursor:
        cursor.execute(
            '''SELECT
                LOWER(sub_type) as filetype,
                CONCAT_WS('/',directory,filename) AS path
            FROM prod_dir
            JOIN prod_cat USING (prod_id)
            WHERE prod_id = %s''',
            (prod_id, )
            )
        results = cursor.fetchall()

    return {
        row['filetype']: row['path']
        for row in results
    }


def find_previous_job_files(prod_id, job_type):
    ''' Given the product id of the current job, and the type of the
    current job, compute the location of the files from the preceding
    step.

    Jobs progress in the current way:

    RefCatPipe -> PhotPipe -> MergePipe -> SysremPipe -> BLSPipe
    '''

    # TODO: finish this function for the other job types, if required
    job_type = job_type.lower()
    if job_type != 'sysrem':
        raise NotImplementedError(
            'Only sysrem jobs are supported for now')

    with connect_to_database() as cursor:
        cursor.execute(
            '''SELECT raw_prod_id
            FROM sysrempipe_prod
            WHERE prod_id = %s''',
            (prod_id, )
            )
        rows = cursor.fetchall()

    if len(rows) == 1:
        return find_existing_job_files(rows[0]['raw_prod_id'])

    elif len(rows) == 0:
        raise ValueError(
            'No results returned for {job_type} job: {prod_id}'.format(
                job_type=job_type,
                prod_id=prod_id,
                )
            )

    elif len(rows) > 1:
        raise ValueError(
            'Ambiguous number of jobs for {job_type} job: {prod_id}'.format(
                job_type=job_type,
                prod_id=prod_id,
                )
            )



def get_url(job_type, prod_id):
    ''' Given a job type and product it, return the root url of the job
    QA result.
    '''
    # TODO
    return ''


def update_manifest(filename, manifest_path):
    ''' Update the manifest file with the file path.
    '''
    with open(manifest_path, 'a') as outfile:
        outfile.write('{}\n'.format(filename))


# Private (non-exported) functions

@contextmanager
def connect_to_database(db='ngts_pipe'):
    with pymysql.connect(host='ngtsdb', db=db, cursorclass=DictCursor) as cursor:
        yield cursor
